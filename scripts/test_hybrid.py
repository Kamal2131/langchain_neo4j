"""
Test script for the enhanced hybrid search (BM25 + Vector).

This script tests:
1. Vector-only search
2. Hybrid BM25+Vector search
3. Keyword-only search
4. Comparison between search types
5. QA service with hybrid retrieval

Usage:
    python scripts/test_hybrid.py
"""

import asyncio
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.vector_service import vector_service
from src.services.qa_service import get_qa_service
from src.core.config import settings
from src.core.logging import setup_logging

# Setup logging
setup_logging()


def test_search_comparison():
    """Compare different search types on the same query."""
    print("\n" + "=" * 60)
    print("🔍 Search Type Comparison")
    print("=" * 60)
    
    queries = [
        ("Python developer", "Employee"),
        ("contract agreement", "Contract"),
        ("active projects", "Document"),
    ]
    
    for query, label in queries:
        print(f"\n📝 Query: '{query}' (Label: {label})")
        print("-" * 50)
        
        # Try each search type
        for search_type in ["vector", "hybrid"]:
            try:
                start = time.time()
                results = vector_service.similarity_search(
                    query=query,
                    k=3,
                    label=label,
                    search_type=search_type
                )
                elapsed = (time.time() - start) * 1000
                
                print(f"\n  🔷 {search_type.upper()} ({elapsed:.1f}ms): {len(results)} results")
                for i, doc in enumerate(results[:2]):
                    content = doc.page_content[:80] + "..." if len(doc.page_content) > 80 else doc.page_content
                    print(f"     {i+1}. {content}")
                    
            except Exception as e:
                print(f"  ⚠️  {search_type}: Error - {str(e)[:50]}...")


def test_similarity_with_scores():
    """Test search with similarity scores."""
    print("\n" + "=" * 60)
    print("📊 Search with Scores")
    print("=" * 60)
    
    query = "software engineering"
    
    try:
        results = vector_service.similarity_search_with_score(
            query=query,
            k=5,
            label="Employee",
            search_type="hybrid"
        )
        
        print(f"\nQuery: '{query}'")
        print("-" * 50)
        
        for doc, score in results:
            content = doc.page_content[:60] + "..." if len(doc.page_content) > 60 else doc.page_content
            print(f"  Score: {score:.4f} | {content}")
            
    except Exception as e:
        print(f"⚠️  Error: {e}")


async def test_qa_hybrid():
    """Test the QA service with hybrid retrieval."""
    print("\n" + "=" * 60)
    print("🤖 QA Service Hybrid Test")
    print("=" * 60)
    
    qa_service = get_qa_service()
    
    test_questions = [
        "How many employees are in Engineering?",
        "Who knows Python?",
        "What is the vacation policy for Engineers?",
        "Show me active contracts",
    ]
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        print("-" * 50)
        
        try:
            start = time.time()
            result = qa_service.query(question, include_cypher=True)
            elapsed = (time.time() - start) * 1000
            
            print(f"💬 Answer: {result['answer'][:200]}...")
            print(f"⏱️  Time: {elapsed:.1f}ms")
            print(f"📚 Context docs: {len(result['metadata'].get('context_used', []))}")
            
            if "cypher_query" in result:
                cypher = result["cypher_query"][:100] + "..." if len(result.get("cypher_query", "")) > 100 else result.get("cypher_query", "N/A")
                print(f"🔧 Cypher: {cypher}")
                
        except Exception as e:
            print(f"⚠️  Error: {e}")


def test_config():
    """Display current configuration."""
    print("\n" + "=" * 60)
    print("⚙️  Current Configuration")
    print("=" * 60)
    print(f"  Embedding Model: {settings.embedding_model}")
    print(f"  Search Type: {settings.search_type}")
    print(f"  Chunk Size: {settings.chunk_size}")
    print(f"  Chunk Overlap: {settings.chunk_overlap}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 RAG Improvements Test Suite")
    print("   Testing: Semantic Chunking, Upgraded Embeddings, Hybrid Search")
    print("=" * 60)
    
    # Show config
    test_config()
    
    # Test search comparison
    test_search_comparison()
    
    # Test with scores
    test_similarity_with_scores()
    
    # Test QA service
    await test_qa_hybrid()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
