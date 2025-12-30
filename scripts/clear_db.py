"""
Clear all data from Neo4j database.
WARNING: This will delete ALL nodes and relationships!
"""

from neo4j import GraphDatabase
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.core.config import settings


def clear_database():
    """Clear all data from Neo4j."""
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password)
    )
    
    print("="*60)
    print("  ⚠️  Neo4j Database Clear Utility")
    print("="*60)
    print("\n🔌 Connected to Neo4j at", settings.neo4j_uri)
    
    try:
        with driver.session() as session:
            # Get current counts
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = result.single()["count"]
            
            print(f"\n📊 Current database:")
            print(f"  Nodes: {node_count}")
            print(f"  Relationships: {rel_count}")
            
            if node_count == 0:
                print("\n✅ Database is already empty!")
                return
            
            # Confirm deletion
            print(f"\n⚠️  WARNING: This will delete {node_count} nodes and {rel_count} relationships!")
            
            # Delete all nodes and relationships
            print("\n🗑️  Deleting all data...")
            session.run("MATCH (n) DETACH DELETE n")
            
            print("✅ All data deleted!")
            
            # Verify
            result = session.run("MATCH (n) RETURN count(n) as count")
            remaining = result.single()["count"]
            
            print(f"\n📊 After deletion:")
            print(f"  Nodes: {remaining}")
            print(f"  Relationships: 0")
            
    finally:
        driver.close()
        print("\n🔌 Disconnected from Neo4j")
    
    print("\n" + "="*60)
    print("  ✅ Database cleared successfully!")
    print("="*60)
    print("\n🚀 Next step:")
    print("  Run: python scripts/load_company_kb.py")
    print()


if __name__ == "__main__":
    clear_database()
