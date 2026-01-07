"""
QA service for natural language query processing.
"""

from typing import Any, Dict, Optional

from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from src.core.config import settings
from src.core.exceptions import LLMProviderError, QueryExecutionError
from src.core.logging import get_logger

logger = get_logger(__name__)

CYPHER_GENERATION_TEMPLATE = """Task: Generate a Cypher statement to query a Neo4j graph database for a company knowledge base.

=== DATABASE SCHEMA ===
{schema}

=== NODE TYPES AND PROPERTIES ===

1. **Employee** - Company employees
   - id: String (e.g., "EMP0001")
   - name: String (e.g., "John Smith")
   - email: String (unique email address)
   - title: String (e.g., "Software Engineer", "DevOps Engineer", "Product Manager", "ML Engineer", "Data Scientist", "AI Engineer", "Sales Manager", "UI Designer", "Cloud Architect", "Full Stack Engineer", "Staff Engineer", "Engineering Manager", "VP of Product", "Creative Director")
   - department: String (matches Department.name)
   - location: String (e.g., "San Francisco", "Austin", "Seattle", "Chicago", "New York", "Remote")
   - hire_date: Date
   - salary: Integer
   - level: String - ONE OF: "Junior", "Mid", "Senior", "Staff", "Principal"
   - bio: String
   - phone: String

2. **Department** - Company departments
   - name: String (unique) - ONE OF: "Engineering", "Data Science", "DevOps", "Product", "Sales", "Marketing", "Design", "Customer Success"

3. **Project** - Company projects
   - project_id: String (unique, e.g., "PROJ001")
   - name: String
   - description: String
   - status: String - ONE OF: "active", "planning", "on-hold", "completed", "cancelled"
   - budget: Integer
   - start_date: Date
   - end_date: Date (optional)
   - priority: String - ONE OF: "low", "medium", "high", "critical"

4. **Skill** - Technical and soft skills
   - name: String (unique, e.g., "Python", "React", "AWS", "Docker", "Kubernetes", "TypeScript", "SQL", "Machine Learning", "TensorFlow", "Go", "Java", "Leadership", "Communication")
   - category: String (e.g., "Programming", "Cloud", "Data", "DevOps", "Soft Skills")

5. **Client** - External clients
   - name: String
   - industry: String
   - revenue: Integer
   - contract_value: Integer

6. **Document** - Project documentation
   - doc_id: String (unique)
   - title: String
   - content: String
   - type: String
   - summary: String

=== RELATIONSHIPS ===
- (Employee)-[:WORKS_IN]->(Department)
- (Employee)-[:HAS_SKILL]->(Skill)
- (Employee)-[:WORKS_ON]->(Project)
- (Employee)-[:REPORTS_TO]->(Employee)
- (Project)-[:REQUIRES]->(Skill)
- (Project)-[:FOR_CLIENT]->(Client)
- (Project)-[:HAS_DOCUMENT]->(Document)

=== STRICT RULES ===
1. Use ONLY the node labels, relationships, and properties listed above
2. String comparisons are CASE-SENSITIVE - use exact values as shown
3. For partial matching on names/titles, use CONTAINS or toLower() for case-insensitive search
4. Always return meaningful properties, not just nodes
5. Use OPTIONAL MATCH when relationships might not exist
6. Return DISTINCT results when appropriate to avoid duplicates
7. For counting/aggregation, use COUNT(), SUM(), AVG() functions
8. Use ORDER BY for sorted results and LIMIT for top-N queries

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

=== YOUR TASK ===
Generate ONLY the Cypher query for the following question. Do not include any explanations.

Question: {question}
"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)


class QAService:
    """Service for processing natural language queries."""

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
        """Get or create QA chain."""
        if self._chain is None:
            # Refresh schema to ensure we have the latest data
            self.graph.refresh_schema()
            
            llm = self._get_llm()
            self._chain = GraphCypherQAChain.from_llm(
                llm=llm,
                graph=self.graph,
                verbose=settings.debug,
                allow_dangerous_requests=True,
                return_intermediate_steps=True,
                cypher_prompt=CYPHER_GENERATION_PROMPT,
            )
            logger.info(f"QA chain initialized with {settings.llm_provider} provider")
        return self._chain

    def query(self, question: str, include_cypher: bool = False) -> Dict[str, Any]:
        """
        Process a natural language query.

        Args:
            question: Natural language question
            include_cypher: Whether to include generated Cypher in response

        Returns:
            dict: Query result with answer and optional Cypher query

        Raises:
            QueryExecutionError: If query execution fails
        """
        try:
            chain = self._get_chain()

            logger.info(f"Processing query: {question}")
            result = chain.invoke({"query": question})

            response = {
                "question": question,
                "answer": result.get("result", "No answer found"),
                "metadata": {
                    "provider": settings.llm_provider,
                    "model": (
                        settings.openai_model
                        if settings.llm_provider == "openai"
                        else settings.groq_model
                    ),
                },
            }

            # Extract Cypher query if intermediate steps are available
            if include_cypher and "intermediate_steps" in result and result["intermediate_steps"]:
                cypher_query = result["intermediate_steps"][0].get("query", "")
                response["cypher_query"] = cypher_query
                logger.debug(f"Generated Cypher: {cypher_query}")

            logger.info("Query processed successfully")
            return response

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise QueryExecutionError(f"Failed to execute query: {e}", details={"question": question}) from e


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
