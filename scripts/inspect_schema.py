
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.neo4j_service import neo4j_service
from src.core.logging import get_logger

logger = get_logger(__name__)

def main():
    print("🚀 Inspecting Neo4j Schema...")
    try:
        graph = neo4j_service.connect()
        # triggering refresh just in case
        graph.refresh_schema()
        schema_str = graph.schema
        print("\n=== GENERATED SCHEMA ===")
        print(schema_str)
        print("========================")
            
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    main()
