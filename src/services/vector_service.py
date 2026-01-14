"""
Vector service for hybrid search capabilities.
Enhanced with upgraded embeddings and BM25+Vector hybrid search.
"""

from typing import Any, List, Literal, Optional
from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import VectorError

logger = get_logger(__name__)


class VectorService:
    """Service for vector search operations with hybrid BM25+Vector support."""

    def __init__(self) -> None:
        self._embeddings: Optional[HuggingFaceEmbeddings] = None
        self._vector_stores: dict = {}  # Cache stores by label

    def _get_embeddings(self) -> HuggingFaceEmbeddings:
        """Get or initialize embeddings model."""
        if self._embeddings:
            return self._embeddings
        
        try:
            model_name = settings.embedding_model
            logger.info(f"Initializing HuggingFace Embeddings ({model_name})...")
            self._embeddings = HuggingFaceEmbeddings(
                model_name=model_name
            )
            logger.info(f"Embeddings model loaded: {model_name}")
            return self._embeddings
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise VectorError(f"Failed to initialize embeddings: {e}") from e

    def get_vector_store(
        self, 
        label: str = "Document", 
        properties: List[str] = None,
        search_type: Literal["vector", "hybrid", "keyword"] = None
    ) -> Neo4jVector:
        """
        Get or create Neo4j vector store with hybrid search support.
        
        Args:
            label: Node label to index (default: Document)
            properties: Text properties to index
            search_type: Search type override (uses config default if not specified)
        """
        if properties is None:
            properties = ["text", "page_content"]
        
        search_type = search_type or settings.search_type
        cache_key = f"{label}_{search_type}"
        
        # Return cached store if available
        if cache_key in self._vector_stores:
            return self._vector_stores[cache_key]
        
        try:
            logger.info(f"Creating vector store for {label} with search_type={search_type}")
            
            store_kwargs = {
                "embedding": self._get_embeddings(),
                "url": settings.neo4j_uri,
                "username": settings.neo4j_username,
                "password": settings.neo4j_password,
                "index_name": f"vector_index_{label.lower()}",
                "node_label": label,
                "text_node_properties": properties,
                "embedding_node_property": "embedding",
            }
            
            # Add hybrid search configuration
            if search_type == "hybrid":
                store_kwargs["keyword_index_name"] = f"keyword_index_{label.lower()}"
                store_kwargs["search_type"] = "hybrid"
                logger.info(f"Hybrid search enabled with keyword index: keyword_index_{label.lower()}")
            elif search_type == "keyword":
                store_kwargs["keyword_index_name"] = f"keyword_index_{label.lower()}"
                store_kwargs["search_type"] = "keyword"
            # else: default vector search
            
            store = Neo4jVector.from_existing_graph(**store_kwargs)
            
            self._vector_stores[cache_key] = store
            logger.info(f"Vector store created for {label}")
            return store
            
        except Exception as e:
            logger.error(f"Failed to get vector store for {label}: {e}")
            raise VectorError(f"Failed to get vector store: {e}") from e

    def create_index_from_graph(self, search_type: Literal["vector", "hybrid"] = None) -> None:
        """
        Create or refresh vector indices from existing graph data.
        Creates both vector and keyword indices for hybrid search.
        """
        search_type = search_type or settings.search_type
        
        try:
            logger.info(f"Creating vector indices with search_type={search_type}...")
            
            base_kwargs = {
                "embedding": self._get_embeddings(),
                "url": settings.neo4j_uri,
                "username": settings.neo4j_username,
                "password": settings.neo4j_password,
                "embedding_node_property": "embedding",
            }
            
            # 1. Index Employees (Bio search)
            employee_kwargs = {
                **base_kwargs,
                "index_name": "vector_index_employee",
                "node_label": "Employee",
                "text_node_properties": ["bio", "title", "department", "name"],
            }
            if search_type == "hybrid":
                employee_kwargs["keyword_index_name"] = "keyword_index_employee"
            
            Neo4jVector.from_existing_graph(**employee_kwargs)
            logger.info("✅ Created Employee vector index")
            
            # 2. Index Documents (Policies, etc.)
            document_kwargs = {
                **base_kwargs,
                "index_name": "vector_index_document",
                "node_label": "Document",
                "text_node_properties": ["text", "page_content"],
            }
            if search_type == "hybrid":
                document_kwargs["keyword_index_name"] = "keyword_index_document"
            
            Neo4jVector.from_existing_graph(**document_kwargs)
            logger.info("✅ Created Document vector index")
            
            # 3. Index Contracts
            contract_kwargs = {
                **base_kwargs,
                "index_name": "vector_index_contract",
                "node_label": "Contract",
                "text_node_properties": ["title", "terms", "text"],
            }
            if search_type == "hybrid":
                contract_kwargs["keyword_index_name"] = "keyword_index_contract"
            
            try:
                Neo4jVector.from_existing_graph(**contract_kwargs)
                logger.info("✅ Created Contract vector index")
            except Exception as e:
                logger.warning(f"Contract index creation skipped (no Contract nodes?): {e}")
            
            # 4. Index Policies
            policy_kwargs = {
                **base_kwargs,
                "index_name": "vector_index_policy",
                "node_label": "Policy",
                "text_node_properties": ["title", "text"],
            }
            if search_type == "hybrid":
                policy_kwargs["keyword_index_name"] = "keyword_index_policy"
            
            try:
                Neo4jVector.from_existing_graph(**policy_kwargs)
                logger.info("✅ Created Policy vector index")
            except Exception as e:
                logger.warning(f"Policy index creation skipped (no Policy nodes?): {e}")
            
            # Clear cache to force reload with new indices
            self._vector_stores.clear()
            
            logger.info("✅ All vector indices created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create vector index: {e}")
            raise VectorError(f"Failed to create vector index: {e}") from e

    def similarity_search(
        self, 
        query: str, 
        k: int = 3, 
        label: str = "Document",
        search_type: Literal["vector", "hybrid", "keyword"] = None
    ) -> List[Document]:
        """
        Perform similarity search with configurable search type.
        
        Args:
            query: Search query
            k: Number of results
            label: Node label to search (default: Document)
            search_type: Override search type (uses config default if not specified)
            
        Returns:
            List[Document]: Matching documents
        """
        search_type = search_type or settings.search_type
        
        try:
            store = self.get_vector_store(label=label, search_type=search_type)
            results = store.similarity_search(query, k=k)
            logger.debug(f"Search ({search_type}) returned {len(results)} results for: {query[:50]}...")
            return results
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise VectorError(f"Similarity search failed: {e}") from e

    def similarity_search_with_score(
        self, 
        query: str, 
        k: int = 3, 
        label: str = "Document",
        search_type: Literal["vector", "hybrid", "keyword"] = None
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search and return documents with scores.
        
        Args:
            query: Search query
            k: Number of results
            label: Node label to search
            search_type: Override search type
            
        Returns:
            List[tuple[Document, float]]: Documents with similarity scores
        """
        search_type = search_type or settings.search_type
        
        try:
            store = self.get_vector_store(label=label, search_type=search_type)
            results = store.similarity_search_with_score(query, k=k)
            logger.debug(f"Search with scores ({search_type}) returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Similarity search with score failed: {e}")
            raise VectorError(f"Similarity search with score failed: {e}") from e

    def get_retriever(
        self, 
        label: str = "Document", 
        k: int = 3,
        search_type: Literal["vector", "hybrid", "keyword"] = None
    ):
        """
        Get a LangChain retriever for the vector store.
        
        Args:
            label: Node label to search
            k: Number of results to retrieve
            search_type: Override search type
            
        Returns:
            VectorStoreRetriever
        """
        store = self.get_vector_store(label=label, search_type=search_type)
        return store.as_retriever(search_kwargs={"k": k})


# Global instance
vector_service = VectorService()
