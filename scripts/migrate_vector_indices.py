"""
Script to migrate vector indices to new embedding model and hybrid search.

This script:
1. Drops existing vector indices (old 384-dim embeddings)
2. Creates new vector indices with 768-dim embeddings
3. Creates keyword indices for BM25 hybrid search
4. Re-embeds existing documents

Usage:
    python scripts/migrate_vector_indices.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import settings
from src.core.logging import get_logger
from src.services.neo4j_service import neo4j_service
from src.services.vector_service import vector_service

logger = get_logger(__name__)


def drop_existing_indices():
    """Drop old vector and keyword indices."""
    graph = neo4j_service.get_graph()
    
    # List of old index names to drop
    old_indices = [
        "vector_index_employee",
        "vector_index_document", 
        "vector_index_contract",
        "vector_index_policy",
        "keyword_index_employee",
        "keyword_index_document",
        "keyword_index_contract", 
        "keyword_index_policy",
        "hybrid_search_index",  # Old name if exists
    ]
    
    for index_name in old_indices:
        try:
            graph.query(f"DROP INDEX {index_name} IF EXISTS")
            logger.info(f"✅ Dropped index: {index_name}")
        except Exception as e:
            logger.warning(f"⚠️  Could not drop index {index_name}: {e}")


def clear_old_embeddings():
    """Remove old embedding properties from nodes."""
    graph = neo4j_service.get_graph()
    
    node_labels = ["Employee", "Document", "Contract", "Policy"]
    
    for label in node_labels:
        try:
            result = graph.query(f"""
                MATCH (n:{label})
                WHERE n.embedding IS NOT NULL
                SET n.embedding = null
                RETURN count(n) as cleared
            """)
            count = result[0]["cleared"] if result else 0
            logger.info(f"✅ Cleared embeddings from {count} {label} nodes")
        except Exception as e:
            logger.warning(f"⚠️  Could not clear embeddings for {label}: {e}")


def create_new_indices():
    """Create new vector indices with upgraded embeddings and hybrid search."""
    logger.info(f"Creating new indices with embedding model: {settings.embedding_model}")
    logger.info(f"Search type: {settings.search_type}")
    
    try:
        vector_service.create_index_from_graph(search_type=settings.search_type)
        logger.info("✅ All new indices created successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to create indices: {e}")
        raise


def verify_indices():
    """Verify that indices were created successfully."""
    graph = neo4j_service.get_graph()
    
    try:
        result = graph.query("SHOW INDEXES")
        
        print("\n📊 Current Indices:")
        print("-" * 60)
        
        vector_indices = []
        keyword_indices = []
        
        for record in result:
            name = record.get("name", "")
            index_type = record.get("type", "")
            state = record.get("state", "")
            
            if "vector" in name.lower():
                vector_indices.append(f"  {name} ({index_type}) - {state}")
            elif "keyword" in name.lower():
                keyword_indices.append(f"  {name} ({index_type}) - {state}")
        
        print("\n🔷 Vector Indices:")
        for idx in vector_indices:
            print(idx)
        
        if settings.search_type == "hybrid":
            print("\n🔶 Keyword (BM25) Indices:")
            for idx in keyword_indices:
                print(idx)
        
        print("-" * 60)
        
    except Exception as e:
        logger.warning(f"Could not verify indices: {e}")


def test_hybrid_search():
    """Quick test of the new hybrid search."""
    print("\n🧪 Testing Hybrid Search...")
    print("-" * 60)
    
    try:
        # Test query
        query = "Python developer"
        results = vector_service.similarity_search(
            query=query, 
            k=3, 
            label="Employee",
            search_type="hybrid"
        )
        
        print(f"Query: '{query}'")
        print(f"Results: {len(results)} documents")
        
        for i, doc in enumerate(results[:3]):
            content = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            print(f"  {i+1}. {content}")
        
        print("✅ Hybrid search working!")
        
    except Exception as e:
        logger.warning(f"⚠️  Hybrid search test failed (this is OK if no Employee nodes exist): {e}")


def main():
    """Run the full migration."""
    print("=" * 60)
    print("🔄 Vector Index Migration")
    print(f"   Embedding Model: {settings.embedding_model}")
    print(f"   Search Type: {settings.search_type}")
    print("=" * 60)
    
    # Step 1: Drop old indices
    print("\n1️⃣ Dropping old indices...")
    drop_existing_indices()
    
    # Step 2: Clear old embeddings
    print("\n2️⃣ Clearing old embeddings...")
    clear_old_embeddings()
    
    # Step 3: Create new indices
    print("\n3️⃣ Creating new indices with hybrid search...")
    create_new_indices()
    
    # Step 4: Verify
    print("\n4️⃣ Verifying indices...")
    verify_indices()
    
    # Step 5: Test
    print("\n5️⃣ Testing hybrid search...")
    test_hybrid_search()
    
    print("\n" + "=" * 60)
    print("✅ Migration Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
