"""
QA service for natural language query processing.
"""

from typing import Dict, Any, Optional
from langchain.chains import GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_community.graphs import Neo4jGraph

from src.core.config import settings
from src.core.exceptions import LLMProviderError, QueryExecutionError
from src.core.logging import get_logger

logger = get_logger(__name__)


class QAService:
    """Service for processing natural language queries."""
    
    def __init__(self, graph: Neo4jGraph):
        self.graph = graph
        self._chain: Optional[GraphCypherQAChain] = None
    
    def _get_llm(self):
        """Get LLM instance based on configured provider."""
        llm_config = settings.get_llm_config()
        
        try:
            if llm_config["provider"] == "openai":
                return ChatOpenAI(
                    api_key=llm_config["api_key"],
                    model=llm_config["model"],
                    temperature=0
                )
            elif llm_config["provider"] == "groq":
                return ChatGroq(
                    api_key=llm_config["api_key"],
                    model_name=llm_config["model"],
                    temperature=0
                )
            else:
                raise LLMProviderError(
                    f"Unsupported LLM provider: {llm_config['provider']}"
                )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise LLMProviderError(f"Failed to initialize LLM: {str(e)}")
    
    def _get_chain(self) -> GraphCypherQAChain:
        """Get or create QA chain."""
        if self._chain is None:
            llm = self._get_llm()
            self._chain = GraphCypherQAChain.from_llm(
                llm=llm,
                graph=self.graph,
                verbose=settings.debug,
                allow_dangerous_requests=True,
                return_intermediate_steps=True
            )
            logger.info(f"QA chain initialized with {settings.llm_provider} provider")
        return self._chain
    
    def query(
        self,
        question: str,
        include_cypher: bool = False
    ) -> Dict[str, Any]:
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
                    "model": settings.openai_model if settings.llm_provider == "openai" else settings.groq_model
                }
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
            raise QueryExecutionError(
                f"Failed to execute query: {str(e)}",
                details={"question": question}
            )


# Sample questions for testing
SAMPLE_QUESTIONS = [
    "Which projects use Python and who worked on them?",
    "What technologies does Alice Johnson work with?",
    "Show me all active projects",
    "Who worked on the AI Chatbot project?",
    "What programming languages are used across all projects?",
    "Which person has worked on the most projects?",
    "What projects use React?",
    "List all people who are Full Stack Developers",
]
