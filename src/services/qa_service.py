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

CYPHER_GENERATION_TEMPLATE = """Task: Generate Cypher statement to query a graph database.

Schema:
{schema}

Instructions:
- Use only the provided relationship types and properties in the schema.
- Do not use any other relationship types or properties that are not provided.
- Return only the Cypher statement, no explanations.

Important Property Values:
- Project.status can be: "active", "planning", "on-hold", "completed", "cancelled"
- Employee.level can be: "Junior", "Mid", "Senior", "Staff", "Principal"
- Employee.department matches Department.name
- Skill.name contains skill names like "Python", "React", "AWS", "Docker"

Examples:

Question: Show me all active projects
MATCH (p:Project)
WHERE p.status = "active"
RETURN p.name, p.status, p.budget

Question: List employees in the Engineering department
MATCH (e:Employee)-[:WORKS_IN]->(d:Department {{name: "Engineering"}})
RETURN e.name, e.title

Question: Find employees with Python skills
MATCH (e:Employee)-[:HAS_SKILL]->(s:Skill {{name: "Python"}})
RETURN e.name, e.title, e.department

Question: Who are the Software Engineers?
MATCH (e:Employee)
WHERE e.title CONTAINS "Software Engineer"
RETURN e.name, e.title, e.department

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
]
