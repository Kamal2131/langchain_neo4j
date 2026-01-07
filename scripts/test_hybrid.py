
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.neo4j_service import neo4j_service
from src.services.qa_service import QAService
from src.core.logging import get_logger

logger = get_logger(__name__)

async def main():
    print("🚀 Testing Hybrid Search...")
    try:
        graph = neo4j_service.connect()
        qa = QAService(graph)
        
        # Query that likely relies on BIO (Vector Search)
        q = "Find employees with leadership skills"
        print(f"\n❓ Question: {q}")
        
        # We need to run this in a thread or just call it since it's sync code wrapped in async def?
        # QAService.query is synchronous.
        response = qa.query(q, include_cypher=True)
        
        print("\n✅ Result:")
        print(f"   Answer: {response['answer']}")
        print(f"   Cypher: {response.get('cypher_query')}")
        print(f"   Context Used: {len(response['metadata']['context_used'])} docs")
        print(f"   Execution Time: {response['metadata'].get('execution_time_ms')}ms")
        for doc in response['metadata']['context_used']:
            print(f"      - {doc[:50]}...")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
