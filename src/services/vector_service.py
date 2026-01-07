"""
Vector service for hybrid search capabilities.
"""

from typing import Any, List, Optional
from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings
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

    def get_vector_store(self, create: bool = False) -> Neo4jVector:
        """Get or create Neo4j vector store."""
        if self._vector_store and not create:
            return self._vector_store

        try:
            self._vector_store = Neo4jVector.from_existing_graph(
                embedding=self._get_embeddings(),
                url=settings.neo4j_uri,
                username=settings.neo4j_username,
                password=settings.neo4j_password,
                index_name=self.index_name,
                node_label="Employee", # Primary label, but we can search others if configured
                text_node_properties=["bio", "title", "department"],
                embedding_node_property="embedding",
            )
            return self._vector_store
        except Exception as e:
            # If index doesn't exist and we requested get, it might fail in some versions
            # But from_existing_graph usually tries to load it.
            logger.error(f"Failed to get vector store: {e}")
            raise VectorError(f"Failed to get vector store: {e}") from e

    def create_index_from_graph(self) -> None:
        """Create or refresh the vector index from existing graph data."""
        try:
            logger.info(f"Creating vector index '{self.index_name}'...")
            # We want to index multiple node types, but Neo4jVector usually targets one label per index 
            # or requires specific configuration.
            # For this showcase, let's create a specialized index for Employees as they have 'bio'.
            
            # Note: Neo4jVector.from_existing_graph automatically populates the index
            Neo4jVector.from_existing_graph(
                embedding=self._get_embeddings(),
                url=settings.neo4j_uri,
                username=settings.neo4j_username,
                password=settings.neo4j_password,
                index_name=self.index_name,
                node_label="Employee",
                text_node_properties=["bio", "title", "department", "name"],
                embedding_node_property="embedding",
            )
            logger.info("Vector index created successfully")
        except Exception as e:
            logger.error(f"Failed to create vector index: {e}")
            raise VectorError(f"Failed to create vector index: {e}") from e

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """
        Perform similarity search.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List[Document]: Matching documents
        """
        try:
            store = self.get_vector_store()
            results = store.similarity_search(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise VectorError(f"Similarity search failed: {e}") from e

# Global instance
vector_service = VectorService()
