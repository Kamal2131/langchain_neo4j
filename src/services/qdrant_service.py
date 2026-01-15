"""
Service for managing Qdrant vector database operations.
Provides collection management, vector upsert, and similarity search.
"""

import hashlib
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# Embedding dimension for configured model
EMBEDDING_DIMENSIONS = {
    "all-MiniLM-L6-v2": 384,
    "all-mpnet-base-v2": 768,
    "all-distilroberta-v1": 768,
}


class QdrantService:
    """Service for Qdrant vector database operations."""
    
    def __init__(self):
        self._client: Optional[QdrantClient] = None
        self._embeddings: Optional[HuggingFaceEmbeddings] = None
        self._embedding_dim: int = EMBEDDING_DIMENSIONS.get(
            settings.embedding_model, 768
        )
    
    def _get_client(self) -> QdrantClient:
        """Get or initialize Qdrant client."""
        if self._client is None:
            logger.info(f"Connecting to Qdrant at {settings.qdrant_host}:{settings.qdrant_port}")
            self._client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key,
                timeout=30,
            )
            logger.info("Qdrant client connected successfully")
        return self._client
    
    def _get_embeddings(self) -> HuggingFaceEmbeddings:
        """Get or initialize embeddings model."""
        if self._embeddings is None:
            logger.info(f"Initializing embeddings model: {settings.embedding_model}")
            self._embeddings = HuggingFaceEmbeddings(
                model_name=settings.embedding_model
            )
        return self._embeddings
    
    def _generate_doc_hash(self, content: str, source: str = "") -> str:
        """Generate a hash for deduplication."""
        hash_input = f"{source}:{content[:1000]}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def create_collection(
        self, 
        collection_name: Optional[str] = None,
        recreate: bool = False
    ) -> bool:
        """
        Create a Qdrant collection with the configured embedding dimension.
        
        Args:
            collection_name: Name of the collection (default: from settings)
            recreate: If True, delete existing collection first
            
        Returns:
            bool: True if collection was created/exists
        """
        client = self._get_client()
        collection = collection_name or settings.qdrant_collection
        
        try:
            # Check if collection exists
            collections = client.get_collections().collections
            exists = any(c.name == collection for c in collections)
            
            if exists and recreate:
                logger.warning(f"Deleting existing collection: {collection}")
                client.delete_collection(collection)
                exists = False
            
            if not exists:
                logger.info(f"Creating collection: {collection} (dim={self._embedding_dim})")
                client.create_collection(
                    collection_name=collection,
                    vectors_config=models.VectorParams(
                        size=self._embedding_dim,
                        distance=models.Distance.COSINE
                    ),
                    # Enable payload indexing for filtering
                    optimizers_config=models.OptimizersConfigDiff(
                        indexing_threshold=0,  # Index immediately
                    ),
                )
                
                # Create payload indices for common filters
                for field in ["doc_type", "source", "doc_hash"]:
                    client.create_payload_index(
                        collection_name=collection,
                        field_name=field,
                        field_schema=models.PayloadSchemaType.KEYWORD
                    )
                
                logger.info(f"✅ Collection '{collection}' created successfully")
            else:
                logger.info(f"Collection '{collection}' already exists")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def check_duplicate(
        self, 
        doc_hash: str, 
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Check if a document with the given hash already exists.
        
        Args:
            doc_hash: MD5 hash of the document
            collection_name: Collection to check
            
        Returns:
            bool: True if duplicate exists
        """
        client = self._get_client()
        collection = collection_name or settings.qdrant_collection
        
        try:
            result = client.scroll(
                collection_name=collection,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="doc_hash",
                            match=models.MatchValue(value=doc_hash)
                        )
                    ]
                ),
                limit=1
            )
            return len(result[0]) > 0
            
        except Exception as e:
            logger.warning(f"Error checking duplicate: {e}")
            return False
    
    def upsert_documents(
        self,
        documents: List[Document],
        collection_name: Optional[str] = None,
        batch_size: int = 100,
        skip_duplicates: bool = True
    ) -> Dict[str, Any]:
        """
        Upsert documents with embeddings into Qdrant.
        
        Args:
            documents: List of LangChain documents
            collection_name: Target collection
            batch_size: Number of documents per batch
            skip_duplicates: Whether to skip duplicate documents
            
        Returns:
            dict: Upsert statistics
        """
        client = self._get_client()
        embeddings = self._get_embeddings()
        collection = collection_name or settings.qdrant_collection
        
        # Ensure collection exists
        self.create_collection(collection)
        
        stats = {
            "total": len(documents),
            "inserted": 0,
            "skipped_duplicates": 0,
            "errors": 0
        }
        
        points = []
        
        for doc in documents:
            # Generate document hash
            source = doc.metadata.get("source", "")
            doc_hash = self._generate_doc_hash(doc.page_content, source)
            
            # Check for duplicates
            if skip_duplicates and self.check_duplicate(doc_hash, collection):
                stats["skipped_duplicates"] += 1
                continue
            
            try:
                # Generate embedding
                vector = embeddings.embed_query(doc.page_content)
                
                # Create point
                point = models.PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload={
                        "content": doc.page_content,
                        "doc_hash": doc_hash,
                        "doc_type": doc.metadata.get("doc_type", "general"),
                        "source": source,
                        "page": doc.metadata.get("page", 0),
                        **{k: v for k, v in doc.metadata.items() 
                           if k not in ["doc_type", "source", "page"]}
                    }
                )
                points.append(point)
                
                # Batch upsert
                if len(points) >= batch_size:
                    client.upsert(collection_name=collection, points=points)
                    stats["inserted"] += len(points)
                    logger.debug(f"Upserted batch of {len(points)} documents")
                    points = []
                    
            except Exception as e:
                logger.error(f"Error processing document: {e}")
                stats["errors"] += 1
        
        # Upsert remaining points
        if points:
            client.upsert(collection_name=collection, points=points)
            stats["inserted"] += len(points)
        
        logger.info(f"✅ Upsert complete: {stats}")
        return stats
    
    def search(
        self,
        query: str,
        k: int = 5,
        collection_name: Optional[str] = None,
        doc_type: Optional[str] = None,
        score_threshold: float = 0.0
    ) -> List[Tuple[Document, float]]:
        """
        Similarity search with optional filtering.
        
        Args:
            query: Search query text
            k: Number of results
            collection_name: Collection to search
            doc_type: Filter by document type
            score_threshold: Minimum similarity score
            
        Returns:
            List of (Document, score) tuples
        """
        client = self._get_client()
        embeddings = self._get_embeddings()
        collection = collection_name or settings.qdrant_collection
        
        # Generate query embedding
        query_vector = embeddings.embed_query(query)
        
        # Build filter
        filter_conditions = None
        if doc_type:
            filter_conditions = models.Filter(
                must=[
                    models.FieldCondition(
                        key="doc_type",
                        match=models.MatchValue(value=doc_type)
                    )
                ]
            )
        
        try:
            results = client.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=k,
                query_filter=filter_conditions,
                score_threshold=score_threshold
            )
            
            documents = []
            for hit in results:
                doc = Document(
                    page_content=hit.payload.get("content", ""),
                    metadata={
                        "score": hit.score,
                        "doc_type": hit.payload.get("doc_type"),
                        "source": hit.payload.get("source"),
                        "page": hit.payload.get("page"),
                    }
                )
                documents.append((doc, hit.score))
            
            logger.debug(f"Search returned {len(documents)} results")
            return documents
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        collection_name: Optional[str] = None,
        doc_type: Optional[str] = None
    ) -> List[Document]:
        """
        Simple similarity search returning just documents.
        
        Args:
            query: Search query text
            k: Number of results
            collection_name: Collection to search
            doc_type: Filter by document type
            
        Returns:
            List of Documents
        """
        results = self.search(query, k, collection_name, doc_type)
        return [doc for doc, score in results]
    
    def delete_by_source(
        self,
        source: str,
        collection_name: Optional[str] = None
    ) -> int:
        """
        Delete all documents from a specific source.
        
        Args:
            source: Source identifier (e.g., filename)
            collection_name: Target collection
            
        Returns:
            int: Number of documents deleted
        """
        client = self._get_client()
        collection = collection_name or settings.qdrant_collection
        
        try:
            # Count documents first
            count_result = client.count(
                collection_name=collection,
                count_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="source",
                            match=models.MatchValue(value=source)
                        )
                    ]
                )
            )
            count = count_result.count
            
            # Delete documents
            client.delete(
                collection_name=collection,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="source",
                                match=models.MatchValue(value=source)
                            )
                        ]
                    )
                )
            )
            
            logger.info(f"Deleted {count} documents from source: {source}")
            return count
            
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return 0
    
    def get_collection_info(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Get collection statistics."""
        client = self._get_client()
        collection = collection_name or settings.qdrant_collection
        
        try:
            info = client.get_collection(collection)
            # Handle different qdrant-client versions (attribute names vary)
            return {
                "name": collection,
                "points_count": getattr(info, 'points_count', None) or getattr(info, 'indexed_vectors_count', 0),
                "status": str(getattr(info, 'status', 'unknown')),
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> bool:
        """Check if Qdrant is healthy."""
        try:
            client = self._get_client()
            client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False


# Global instance
qdrant_service = QdrantService()
