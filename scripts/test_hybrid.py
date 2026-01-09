import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.qa_service import get_qa_service
from src.core.logging import setup_logging

# Setup logging
setup_logging()

async def test_hybrid_query():
    print("\n=== Testing Hybrid Query ===")
    qa_service = get_qa_service()
    
    # Test 1: Standard structured query
    q1 = "How many employees are in Engineering?"
    print(f"\nQuestion: {q1}")
    try:
        res1 = qa_service.query(q1)
        print(f"Answer: {res1['answer']}")
        print(f"Structured Source: {res1['metadata'].get('structured_source')}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Hybrid query (simulate policy)
    # Note: effectively acts as structured only if no docs found
    q2 = "What is the vacation policy for Engineers?"
    print(f"\nQuestion: {q2}")
    try:
        res2 = qa_service.query(q2)
        print(f"Answer: {res2['answer']}")
        print(f"Context Docs Retrieved: {len(res2['metadata']['context_used'])}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_hybrid_query())
