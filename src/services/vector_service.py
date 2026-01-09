"""
Vector service for hybrid search capabilities.
"""

from typing import Any, List, Optional
from langchain_community.vectorstores import Neo4jVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import VectorError

logger = get_logger(__name__)

class VectorService:
    """Service for vector search operations."""

    def __init__(self) -> None:
        self.index_name = "hybrid_search_index"
        self._vector_store: Optional[Neo4jVector] = None
        self._embeddings: Optional[HuggingFaceEmbeddings] = None

    def _get_embeddings(self) -> HuggingFaceEmbeddings:
        """Get or initialize embeddings model."""
        if self._embeddings:
            return self._embeddings
        
        try:
            logger.info("Initializing HuggingFace Embeddings (all-MiniLM-L6-v2)...")
            self._embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            return self._embeddings
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise VectorError(f"Failed to initialize embeddings: {e}") from e

    def get_vector_store(self, create: bool = False, label: str = "Document", properties: List[str] = ["text", "page_content"]) -> Neo4jVector:
        """
        Get or create Neo4j vector store.
        
        Args:
            create: Force creation/refresh
            label: Node label to index (default: Document)
            properties: Text properties to index
        """
        # If we have a store for this label, return it. Simple caching for now.
        # Note: If label changes, we should technically re-init. For this MVP, we re-init if label differs.
        # A robust solution would maintain a dict of stores.
        
        try:
            return Neo4jVector.from_existing_graph(
                embedding=self._get_embeddings(),
                url=settings.neo4j_uri,
                username=settings.neo4j_username,
                password=settings.neo4j_password,
                index_name=f"vector_index_{label.lower()}",
                node_label=label,
                text_node_properties=properties,
                embedding_node_property="embedding",
            )
        except Exception as e:
            logger.error(f"Failed to get vector store for {label}: {e}")
            raise VectorError(f"Failed to get vector store: {e}") from e

    def create_index_from_graph(self) -> None:
        """Create or refresh the vector index from existing graph data."""
        # For this setup, we might want to index BOTH Employees and Documents.
        try:
            logger.info("Creating vector indices...")
            
            # 1. Index Employees (Bio search)
            Neo4jVector.from_existing_graph(
                embedding=self._get_embeddings(),
                url=settings.neo4j_uri,
                username=settings.neo4j_username,
                password=settings.neo4j_password,
                index_name="vector_index_employee",
                node_label="Employee",
                text_node_properties=["bio", "title", "department", "name"],
                embedding_node_property="embedding",
            )
            
            # 2. Index Documents (Policies, etc.)
            Neo4jVector.from_existing_graph(
                embedding=self._get_embeddings(),
                url=settings.neo4j_uri,
                username=settings.neo4j_username,
                password=settings.neo4j_password,
                index_name="vector_index_document",
                node_label="Document",
                text_node_properties=["text", "page_content"],
                embedding_node_property="embedding",
            )
            
            logger.info("Vector indices created successfully")
        except Exception as e:
            logger.error(f"Failed to create vector index: {e}")
            raise VectorError(f"Failed to create vector index: {e}") from e

    def similarity_search(self, query: str, k: int = 3, label: str = "Document") -> List[Document]:
        """
        Perform similarity search.
        
        Args:
            query: Search query
            k: Number of results
            label: Node label to search (default: Document)
            
        Returns:
            List[Document]: Matching documents
        """
        try:
            # Default to searching Documents for unstructured context
            store = self.get_vector_store(label=label)
            results = store.similarity_search(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise VectorError(f"Similarity search failed: {e}") from e

# Global instance
vector_service = VectorService()
