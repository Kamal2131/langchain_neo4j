"""
Qdrant Integration Test Script.

Tests:
1. Qdrant connection and health
2. Collection creation and management
3. Document upsert with deduplication
4. Similarity search
5. Benchmark: Qdrant vs Neo4j vectors

Usage:
    python scripts/test_qdrant.py
    python scripts/test_qdrant.py --benchmark
"""

import argparse
import time
import sys
import os
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.documents import Document

from src.core.logging import get_logger
from src.services.qdrant_service import qdrant_service
from src.services.vector_service import vector_service
from src.services.neo4j_service import neo4j_service
from src.services.qa_service import QAService

logger = get_logger(__name__)


def test_qdrant_health():
    """Test Qdrant health check."""
    print("\n🔍 Test 1: Qdrant Health Check")
    print("-" * 40)
    
    health = qdrant_service.health_check()
    print(f"Health: {'✅ Healthy' if health else '❌ Unhealthy'}")
    
    if health:
        info = qdrant_service.get_collection_info()
        print(f"Collection Info: {info}")
    
    return health


def test_collection_management():
    """Test collection creation."""
    print("\n🔍 Test 2: Collection Management")
    print("-" * 40)
    
    test_collection = "test_collection"
    
    # Create collection
    result = qdrant_service.create_collection(test_collection, recreate=True)
    print(f"Create collection: {'✅ Success' if result else '❌ Failed'}")
    
    # Check info
    info = qdrant_service.get_collection_info(test_collection)
    print(f"Collection status: {info.get('status', 'unknown')}")
    
    return result


def test_document_upsert():
    """Test document upsert with deduplication."""
    print("\n🔍 Test 3: Document Upsert")
    print("-" * 40)
    
    test_docs = [
        Document(page_content="Python is a programming language.", metadata={"doc_type": "test", "source": "test1"}),
        Document(page_content="Machine learning uses algorithms.", metadata={"doc_type": "test", "source": "test2"}),
        Document(page_content="Neo4j is a graph database.", metadata={"doc_type": "test", "source": "test3"}),
    ]
    
    # First upsert
    stats1 = qdrant_service.upsert_documents(test_docs, skip_duplicates=True)
    print(f"First upsert: inserted={stats1.get('inserted', 0)}, skipped={stats1.get('skipped_duplicates', 0)}")
    
    # Second upsert (should be skipped as duplicates)
    stats2 = qdrant_service.upsert_documents(test_docs, skip_duplicates=True)
    print(f"Second upsert: inserted={stats2.get('inserted', 0)}, skipped={stats2.get('skipped_duplicates', 0)}")
    
    dedup_works = stats2.get('skipped_duplicates', 0) > 0
    print(f"Deduplication: {'✅ Working' if dedup_works else '❌ Not working'}")
    
    return dedup_works


def test_similarity_search():
    """Test similarity search."""
    print("\n🔍 Test 4: Similarity Search")
    print("-" * 40)
    
    query = "What is Python programming?"
    results = qdrant_service.similarity_search(query, k=3)
    
    print(f"Query: {query}")
    print(f"Results: {len(results)} documents found")
    
    for i, doc in enumerate(results):
        print(f"  [{i+1}] {doc.page_content[:50]}...")
    
    return len(results) > 0


def benchmark_search(num_queries: int = 10):
    """Benchmark Qdrant vs Neo4j vector search."""
    print("\n🔍 Test 5: Search Benchmark")
    print("-" * 40)
    
    test_queries = [
        "Find Python developers",
        "Who knows machine learning?",
        "Show active projects",
        "DevOps engineering skills",
        "Data science expertise",
        "Cloud computing knowledge",
        "Frontend development",
        "Backend API development",
        "Database administrators",
        "Project managers",
    ][:num_queries]
    
    # Benchmark Qdrant
    qdrant_times = []
    print(f"\n📊 Benchmarking with {len(test_queries)} queries...")
    
    for query in test_queries:
        start = time.time()
        qdrant_service.similarity_search(query, k=5)
        qdrant_times.append(time.time() - start)
    
    qdrant_avg = sum(qdrant_times) / len(qdrant_times) * 1000  # ms
    print(f"Qdrant average: {qdrant_avg:.2f}ms")
    
    # Benchmark Neo4j (if available)
    try:
        neo4j_times = []
        for query in test_queries:
            start = time.time()
            vector_service.similarity_search(query, k=5)
            neo4j_times.append(time.time() - start)
        
        neo4j_avg = sum(neo4j_times) / len(neo4j_times) * 1000  # ms
        print(f"Neo4j average: {neo4j_avg:.2f}ms")
        
        speedup = neo4j_avg / qdrant_avg if qdrant_avg > 0 else 0
        print(f"\n🚀 Qdrant is {speedup:.1f}x {'faster' if speedup > 1 else 'slower'}")
        
    except Exception as e:
        print(f"Neo4j benchmark skipped: {e}")
    
    return True


def test_qa_with_qdrant():
    """Test QA service with Qdrant retrieval."""
    print("\n🔍 Test 6: QA Service with Qdrant")
    print("-" * 40)
    
    try:
        graph = neo4j_service.get_graph()
        qa_service = QAService(graph)
        qa_service._use_qdrant = True
        
        question = "Show me all employees"
        print(f"Query: {question}")
        
        start = time.time()
        result = qa_service.query(question=question, include_cypher=False)
        elapsed = (time.time() - start) * 1000
        
        print(f"Answer length: {len(result.get('answer', ''))} chars")
        print(f"Confidence: {result.get('confidence', {}).get('level', 'unknown')}")
        print(f"Time: {elapsed:.0f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ QA test failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Qdrant Integration Tests")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark tests")
    parser.add_argument("--queries", type=int, default=10, help="Number of benchmark queries")
    args = parser.parse_args()
    
    print("=" * 50)
    print("🧪 Qdrant Integration Tests")
    print("=" * 50)
    
    results = {
        "health": test_qdrant_health(),
        "collection": test_collection_management(),
        "upsert": test_document_upsert(),
        "search": test_similarity_search(),
    }
    
    if args.benchmark:
        results["benchmark"] = benchmark_search(args.queries)
    
    results["qa"] = test_qa_with_qdrant()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {test}: {status}")
    
    print("-" * 50)
    print(f"  Total: {passed}/{total} passed")
    print("=" * 50)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
