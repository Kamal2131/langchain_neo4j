"""
Query Router - Intelligent routing to optimal retrieval strategy.

Uses LLM to classify queries into:
- GRAPH: Structured queries → Cypher (list, count, relationships)
- VECTOR: Semantic queries → Qdrant (summarize, explain, describe)
- HYBRID: Mixed queries → Both (questions about entities with context)
"""

from typing import Literal, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
import re

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class QueryType(str, Enum):
    """Query classification types."""
    GRAPH = "graph"      # Structured data queries
    VECTOR = "vector"    # Semantic/document queries
    HYBRID = "hybrid"    # Mixed queries


@dataclass
class RoutingDecision:
    """Result of query routing."""
    query_type: QueryType
    confidence: float  # 0.0 - 1.0
    reasoning: str
    use_graph: bool
    use_vector: bool


# Classification prompt for the LLM
ROUTING_PROMPT = PromptTemplate.from_template("""
You are a query classifier for a knowledge base system. Classify the user's question into ONE of these categories:

1. **GRAPH** - Use when the query asks for:
   - Lists of entities (employees, projects, departments)
   - Counts or statistics
   - Relationships between entities
   - Filtering by properties (status, title, date)
   - Examples: "List all projects", "How many employees in Engineering?", "Who reports to Sarah?"

2. **VECTOR** - Use when the query asks for:
   - Summaries or explanations of documents
   - Content understanding from contracts, policies
   - Semantic search for concepts/topics
   - Vague or open-ended questions about content
   - Examples: "Summarize the contract", "What does the policy say about?", "Explain the project scope"

3. **HYBRID** - Use when the query needs BOTH:
   - Entity lookup AND document context
   - Specific person/project with details from documents
   - Questions combining structured and unstructured info
   - Examples: "Who leads Project Alpha and what are its goals?", "Tell me about John's contract"

User Query: {query}

Respond with ONLY one word: GRAPH, VECTOR, or HYBRID
""")


# Rule-based patterns for fast classification (fallback)
GRAPH_PATTERNS = [
    r"^list\s+",
    r"^show\s+(me\s+)?(all\s+)?",
    r"^how\s+many",
    r"^count\s+",
    r"^who\s+(is|are|works|reports|manages)",
    r"^which\s+(department|project|employee)",
    r"^what\s+(projects|employees|departments|skills)",
    r"^find\s+(all\s+)?",
    r"employees?\s+in\s+",
    r"projects?\s+(with|in|for)",
]

VECTOR_PATTERNS = [
    r"^summarize",
    r"^explain",
    r"^describe",
    r"^what\s+does\s+(the|this)\s+(contract|policy|document)",
    r"^tell\s+me\s+about\s+the\s+(contract|policy)",
    r"(content|terms|conditions)\s+of",
    r"^what\s+is\s+(the\s+)?meaning",
]

HYBRID_PATTERNS = [
    r"and\s+(what|how|why|their|his|her)",
    r"along\s+with",
    r"including",
    r"with\s+(details|information|context)",
    r"^tell\s+me\s+(about|everything)",
]


class QueryRouter:
    """Routes queries to optimal retrieval strategy."""
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize the router.
        
        Args:
            use_llm: Whether to use LLM for classification (slower but more accurate)
        """
        self.use_llm = use_llm
        self._llm = None
    
    def _get_llm(self):
        """Get LLM for classification."""
        if self._llm is None:
            llm_config = settings.get_llm_config()
            if llm_config["provider"] == "openai":
                self._llm = ChatOpenAI(
                    api_key=llm_config["api_key"],
                    model=llm_config["model"],
                    temperature=0,
                    max_tokens=10  # Just need one word
                )
            else:
                self._llm = ChatGroq(
                    api_key=llm_config["api_key"],
                    model_name=llm_config["model"],
                    temperature=0,
                    max_tokens=10
                )
        return self._llm
    
    def _rule_based_classify(self, query: str) -> QueryType:
        """
        Fast rule-based classification using regex patterns.
        
        Args:
            query: User query
            
        Returns:
            QueryType based on pattern matching
        """
        query_lower = query.lower().strip()
        
        # Check hybrid patterns first (most specific)
        for pattern in HYBRID_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryType.HYBRID
        
        # Check vector patterns
        for pattern in VECTOR_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryType.VECTOR
        
        # Check graph patterns
        for pattern in GRAPH_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryType.GRAPH
        
        # Default to hybrid for unknown patterns
        return QueryType.HYBRID
    
    def _llm_classify(self, query: str) -> QueryType:
        """
        Use LLM for more accurate classification.
        
        Args:
            query: User query
            
        Returns:
            QueryType from LLM
        """
        try:
            llm = self._get_llm()
            prompt = ROUTING_PROMPT.format(query=query)
            response = llm.invoke(prompt)
            
            result = response.content.strip().upper()
            
            if "GRAPH" in result:
                return QueryType.GRAPH
            elif "VECTOR" in result:
                return QueryType.VECTOR
            elif "HYBRID" in result:
                return QueryType.HYBRID
            else:
                logger.warning(f"Unexpected LLM response: {result}, defaulting to HYBRID")
                return QueryType.HYBRID
                
        except Exception as e:
            logger.error(f"LLM classification failed: {e}, using rule-based")
            return self._rule_based_classify(query)
    
    def route(self, query: str) -> RoutingDecision:
        """
        Route a query to the optimal retrieval strategy.
        
        Args:
            query: User query
            
        Returns:
            RoutingDecision with type and settings
        """
        # Get classification
        if self.use_llm:
            query_type = self._llm_classify(query)
            confidence = 0.85  # LLM classification confidence
        else:
            query_type = self._rule_based_classify(query)
            confidence = 0.70  # Rule-based confidence
        
        # Build routing decision
        decision = RoutingDecision(
            query_type=query_type,
            confidence=confidence,
            reasoning=self._get_reasoning(query_type),
            use_graph=(query_type in [QueryType.GRAPH, QueryType.HYBRID]),
            use_vector=(query_type in [QueryType.VECTOR, QueryType.HYBRID]),
        )
        
        logger.info(f"Routed query to {query_type.value}: {query[:50]}...")
        return decision
    
    def _get_reasoning(self, query_type: QueryType) -> str:
        """Get human-readable reasoning for the routing decision."""
        reasons = {
            QueryType.GRAPH: "Query asks for structured data (entities, relationships, counts)",
            QueryType.VECTOR: "Query asks for document content or semantic understanding",
            QueryType.HYBRID: "Query combines entity lookup with contextual information",
        }
        return reasons.get(query_type, "Default routing")
    
    def classify_batch(self, queries: list[str]) -> list[RoutingDecision]:
        """Classify multiple queries (for analytics)."""
        return [self.route(q) for q in queries]


# Global instance
query_router = QueryRouter(use_llm=True)
