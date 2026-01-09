"""
QA service for natural language query processing.
"""

import time
from typing import Any, Dict, Optional, List

from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from src.core.config import settings
from src.core.exceptions import LLMProviderError, QueryExecutionError
from src.core.logging import get_logger
from src.services.vector_service import vector_service

logger = get_logger(__name__)

CYPHER_GENERATION_TEMPLATE = """Task: Generate a Cypher statement to query a Neo4j graph database for a company knowledge base.

=== DATABASE SCHEMA ===
{schema}

=== RELEVANT CONTEXT (FROM VECTOR SEARCH) ===
Use this information to map vague terms to specific node properties (e.g. if context mentions "Leadership" for "John", search for John when asked about leaders).
{context}

=== STRICT RULES ===
1. Use ONLY the node labels, relationships, and properties explicitly shown in the DATABASE SCHEMA.
2. Do not infer properties that are not present in the generated schema.
3. String comparisons are CASE-SENSITIVE unless using toLower().
4. Use CONTAINS for partial string matching.
5. Always return meaningful properties, not just nodes.
6. Use OPTIONAL MATCH when relationships might not exist.
7. Return DISTINCT results when appropriate.
8. Use COUNT(), SUM(), AVG() for aggregations.
9. Use ORDER BY and LIMIT for ranking.

=== CYPHER EXAMPLES ===

-- Finding employees by department --
Question: List employees in the Engineering department
MATCH (e:Employee)-[:WORKS_IN]->(d:Department {{name: "Engineering"}})
RETURN e.name, e.title, e.level, e.salary
ORDER BY e.name

-- Finding employees by title (partial match) --
Question: Who are the Software Engineers?
MATCH (e:Employee)
WHERE e.title CONTAINS "Software Engineer" OR e.title CONTAINS "Staff Engineer"
RETURN e.name, e.title, e.department, e.level

-- Finding employees by skill --
Question: Find employees with Python skills
MATCH (e:Employee)-[:HAS_SKILL]->(s:Skill {{name: "Python"}})
RETURN e.name, e.title, e.department, e.level
ORDER BY e.name

-- Finding employees by skill (case-insensitive) --
Question: Who knows react?
MATCH (e:Employee)-[:HAS_SKILL]->(s:Skill)
WHERE toLower(s.name) = "react"
RETURN e.name, e.title, e.department

-- Projects by status --
Question: Show me all active projects
MATCH (p:Project)
WHERE p.status = "active"
RETURN p.name, p.status, p.budget, p.priority
ORDER BY p.budget DESC

-- Projects in planning stage --
Question: What projects are in planning stage?
MATCH (p:Project)
WHERE p.status = "planning"
RETURN p.name, p.description, p.priority, p.budget

-- DevOps team members --
Question: Show me all DevOps Engineers
MATCH (e:Employee)
WHERE e.title CONTAINS "DevOps" OR e.department = "DevOps"
RETURN e.name, e.title, e.department, e.location

-- Department employee count --
Question: How many employees are in each department?
MATCH (e:Employee)-[:WORKS_IN]->(d:Department)
RETURN d.name AS department, COUNT(e) AS employee_count
ORDER BY employee_count DESC

-- Employees working on a project --
Question: Who is working on project X?
MATCH (e:Employee)-[:WORKS_ON]->(p:Project)
WHERE toLower(p.name) CONTAINS toLower("X")
RETURN e.name, e.title, p.name AS project

-- Skills required by a project --
Question: What skills are needed for project Y?
MATCH (p:Project)-[:REQUIRES]->(s:Skill)
WHERE toLower(p.name) CONTAINS toLower("Y")
RETURN p.name, COLLECT(s.name) AS required_skills

-- Senior level employees --
Question: List all senior employees
MATCH (e:Employee)
WHERE e.level = "Senior"
RETURN e.name, e.title, e.department, e.salary
ORDER BY e.salary DESC

-- Employees by location --
Question: Who works in San Francisco?
MATCH (e:Employee)
WHERE e.location = "San Francisco"
RETURN e.name, e.title, e.department

-- Top paid employees --
Question: Who are the highest paid employees?
MATCH (e:Employee)
RETURN e.name, e.title, e.department, e.salary
ORDER BY e.salary DESC
LIMIT 10

-- Count employees with specific skill --
Question: How many employees know Python?
MATCH (e:Employee)-[:HAS_SKILL]->(s:Skill {{name: "Python"}})
RETURN COUNT(e) AS python_experts

-- Employee with all their skills --
Question: What skills does John have?
MATCH (e:Employee)-[:HAS_SKILL]->(s:Skill)
WHERE toLower(e.name) CONTAINS toLower("john")
RETURN e.name, COLLECT(s.name) AS skills

-- Projects for a client --
Question: What projects are for client ABC?
MATCH (p:Project)-[:FOR_CLIENT]->(c:Client)
WHERE toLower(c.name) CONTAINS toLower("ABC")
RETURN p.name, p.status, p.budget, c.name AS client

-- Managers and their reports --
Question: Who reports to whom?
MATCH (e:Employee)-[:REPORTS_TO]->(m:Employee)
RETURN e.name AS employee, m.name AS manager, e.title, m.title AS manager_title
ORDER BY m.name

-- Department average salary --
Question: What is the average salary by department?
MATCH (e:Employee)-[:WORKS_IN]->(d:Department)
RETURN d.name AS department, ROUND(AVG(e.salary)) AS avg_salary
ORDER BY avg_salary DESC

-- Find experts (employees with specific skill in specific dept) --
Question: Find Python experts in Engineering
MATCH (e:Employee)-[:WORKS_IN]->(d:Department {{name: "Engineering"}})
MATCH (e)-[:HAS_SKILL]->(s:Skill {{name: "Python"}})
RETURN e.name, e.title, e.level

-- All employees with their department --
Question: List all employees
MATCH (e:Employee)
RETURN e.name, e.title, e.department, e.level, e.location
ORDER BY e.name
LIMIT 50

-- Contracts for a specific client --
Question: What contracts do we have with Acme Corporation?
MATCH (c:Contract)-[:FOR_CLIENT]->(cl:Client)
WHERE toLower(cl.name) CONTAINS toLower("Acme")
RETURN c.title, c.type, c.status, c.value, c.start_date, c.end_date, cl.name

-- Contract managers --
Question: Who manages our contracts with TechStartup?
MATCH (c:Contract)-[:FOR_CLIENT]->(cl:Client)
WHERE toLower(cl.name) CONTAINS toLower("TechStartup")
MATCH (c)-[:MANAGED_BY]->(e:Employee)
RETURN c.title, e.name as manager_name, e.title as manager_title, e.department

-- All active contracts --
Question: Show me all active contracts
MATCH (c:Contract)
WHERE c.status = "active"
RETURN c.title, c.type, c.value, c.start_date, c.end_date
ORDER BY c.value DESC

-- Policies for a department --
Question: What policies apply to Engineering?
MATCH (p:Policy)-[:APPLIES_TO]->(d:Department {{name: "Engineering"}})
RETURN p.title, p.type, p.effective_date, p.status

-- Contracts over a certain value --
Question: Show contracts worth over $50K
MATCH (c:Contract)
WHERE c.value > 50000
RETURN c.title, c.value, c.status
ORDER BY c.value DESC

=== YOUR TASK ===
Generate ONLY the Cypher query for the following question. Do not include any explanations.

Question: {question}
"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question", "context"], template=CYPHER_GENERATION_TEMPLATE
)

HYBRID_SYNTHESIS_TEMPLATE = """Task: Answer the user's question by combining information from the Database (Structured Data) and the Document Store (Unstructured Context).

=== QUESTION ===
{question}

=== STRUCTURED FACTS (From Graph Database) ===
{structured_data}

=== UNSTRUCTURED CONTEXT (From Documents) ===
{context_docs}

=== INSTRUCTIONS ===
1. Synthesize the answer using BOTH sources.
2. If the Structured Facts provide specific data (lists, counts, names), include them.
3. If the Unstructured Context provides policies, definitions, or descriptive details, explain them.
4. If there is a conflict, note it, but prefer the official policy (Unstructured) for rules and Database (Structured) for current stats.
5. Provide a cohesive, professional response.
"""

HYBRID_SYNTHESIS_PROMPT = PromptTemplate(
    input_variables=["question", "structured_data", "context_docs"], template=HYBRID_SYNTHESIS_TEMPLATE
)

class QAService:
    """Service for processing natural language queries using GraphRAG (Hybrid Retrieval)."""

    def __init__(self, graph: Neo4jGraph) -> None:
        self.graph = graph
        self._chain: Optional[GraphCypherQAChain] = None

    def _get_llm(self) -> Any:
        """Get LLM instance based on configured provider."""
        llm_config = settings.get_llm_config()

        try:
            if llm_config["provider"] == "openai":
                return ChatOpenAI(
                    api_key=llm_config["api_key"], model=llm_config["model"], temperature=0
                )
            elif llm_config["provider"] == "groq":
                return ChatGroq(
                    api_key=llm_config["api_key"], model_name=llm_config["model"], temperature=0
                )
            else:
                raise LLMProviderError(f"Unsupported LLM provider: {llm_config['provider']}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise LLMProviderError(f"Failed to initialize {llm_config['provider']} LLM: {e}") from e

    def _get_chain(self) -> GraphCypherQAChain:
        """Get or create QA chain (Structured Retriever)."""
        if self._chain is not None:
            return self._chain
            
        logger.info("Initializing GraphCypherQAChain...")
        
        llm = self._get_llm()
        self._chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=self.graph,
            verbose=settings.debug,
            allow_dangerous_requests=True,
            return_intermediate_steps=True,
            cypher_prompt=CYPHER_GENERATION_PROMPT,
            validate_cypher=True
        )
        logger.info(f"QA chain initialized with {settings.llm_provider} provider")
        return self._chain

    def _synthesize_answer(self, question: str, structured_data: str, context_docs: List[Document]) -> str:
        """Combine structured and unstructured data into a final answer."""
        try:
            llm = self._get_llm()
            
            # Format context documents
            formatted_docs = "\n".join([f"- {d.page_content}" for d in context_docs])
            if not formatted_docs:
                formatted_docs = "No relevant document context found."

            prompt = HYBRID_SYNTHESIS_PROMPT.format(
                question=question,
                structured_data=structured_data,
                context_docs=formatted_docs
            )
            
            response = llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return f"Error synthesizing answer: {e}. Structured Data: {structured_data}"

    def query(self, question: str, include_cypher: bool = False) -> Dict[str, Any]:
        """
        Process a natural language query using Hybrid Retrieval.

        Args:
            question: Natural language question
            include_cypher: Whether to include generated Cypher in response

        Returns:
            dict: Query result with answer and optional Cypher query
        """
        try:
            start_time = time.time()
            chain = self._get_chain()

            logger.info(f"Processing query: {question}")
            
            # --- PARALLEL RETRIEVAL ---
            
            # 1. Unstructured Retrieval (Vector Store)
            try:
                # Get more broad context for the synthesis layer
                docs = vector_service.similarity_search(question, k=3)
                logger.info(f"Retrieved {len(docs)} context documents")
            except Exception as e:
                logger.warning(f"Vector search failed: {e}")
                docs = []

            # 2. Structured Retrieval (Graph Database)
            # We use the existing chain, but we treat its output as "Structured Facts"
            # We inject the docs into the chain's context to help it generate better Cypher if needed 
            # (though mainly we want the data it returns)
            
            chain_context = "\n".join([f"- {d.page_content}" for d in docs])
            if not chain_context:
                chain_context = "No additional context available."

            graph_result = chain.invoke({"query": question, "context": chain_context})
            
            structured_data = graph_result.get("result", "No data found in graph.")
            cypher_query = ""
            
            if "intermediate_steps" in graph_result and graph_result["intermediate_steps"]:
                steps = graph_result["intermediate_steps"]
                # intermediate_steps is a list of (query, context) tuples or dicts depending on version
                # In standard LangChain: keys are 'query' and 'context'
                if len(steps) > 0 and isinstance(steps[0], dict):
                     cypher_query = steps[0].get("query", "")

            # 3. Synthesis
            # If the graph returned a direct "I don't know" or empty, we still want to check the docs.
            # But the synthesis prompt handles combining them.
            
            final_answer = self._synthesize_answer(question, structured_data, docs)
            
            end_time = time.time()
            execution_time_ms = int((end_time - start_time) * 1000)

            response = {
                "question": question,
                "answer": final_answer,
                "metadata": {
                    "provider": settings.llm_provider,
                    "model": (
                        settings.openai_model
                        if settings.llm_provider == "openai"
                        else settings.groq_model
                    ),
                    "context_used": [d.page_content for d in docs] if docs else [],
                    "execution_time_ms": execution_time_ms,
                    "structured_source": structured_data
                },
            }

            if include_cypher and cypher_query:
                response["cypher_query"] = cypher_query
                logger.debug(f"Generated Cypher: {cypher_query}")

            logger.info(f"Query processed successfully in {execution_time_ms}ms")
            return response

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise QueryExecutionError(f"Failed to execute query: {e}", details={"question": question}) from e

    def refresh_schema(self) -> None:
        """
        Refresh the graph schema and invalidate the cached chain.
        This forces the next query to rebuild the chain with the new schema.
        """
        logger.info("Refreshing graph schema...")
        self.graph.refresh_schema()
        self._chain = None
        logger.info("Schema refreshed and chain cache invalidated.")


# Global instance for singleton pattern
_global_qa_service: Optional[QAService] = None


def get_qa_service() -> QAService:
    """
    Get or create the global QAService instance.
    This ensures we share the same graph connection and chain cache across requests.
    """
    global _global_qa_service
    if _global_qa_service is None:
        from src.services.neo4j_service import neo4j_service
        
        # Ensure we have a graph connection
        graph = neo4j_service.get_graph()
        _global_qa_service = QAService(graph)
        logger.info("Initialized global QAService instance")
    
    return _global_qa_service


# Sample questions for testing - based on actual generated data
SAMPLE_QUESTIONS = [
    "Show me all active projects",
    "List employees in the Engineering department",
    "Who are the Software Engineers?",
    "Find employees with Python skills",
    "What projects are in planning stage?",
    "Show me all DevOps Engineers",
    "List employees in Data Science department",
    "Who has React skills?",
    "Who has Python skills?",
    "Show me senior employees in Data Science",
    "What is the average salary by department?",
    "List employees working in Seattle",
    "Find Python experts in Engineering",
    "Who reports to whom?",
]
