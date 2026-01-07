
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.vector_service import vector_service
from src.core.logging import get_logger

logger = get_logger(__name__)

async def main():
    print("🚀 Starting Vector Index Creation...")
    try:
        # This will query nodes labeled 'Employee' and index their properties
        # specified in vector_service (bio, title, department, name)
        vector_service.create_index_from_graph()
        print("✅ Vector index created successfully!")
        
        # Test similarity search
        print("\n🔎 Running test search: 'Leader in engineering'")
        results = vector_service.similarity_search("Leader in engineering")
        for doc in results:
            print(f"   - {doc.page_content[:100]}...")
            
    except Exception as e:
        print(f"❌ Failed to create index: {e}")

if __name__ == "__main__":
    asyncio.run(main())
