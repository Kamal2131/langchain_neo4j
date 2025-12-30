"""
Load Company Knowledge Base data into Neo4j.
Real-world use case implementation.
"""

from neo4j import GraphDatabase
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.core.config import settings


class CompanyKBLoader:
    """Loader for company knowledge base data."""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password)
        )
        print(f"✅ Connected to Neo4j at {settings.neo4j_uri}")
    
    def execute_cypher_file(self, filepath: str) -> None:
        """Execute all statements from a Cypher file."""
        print(f"\n📋 Loading {Path(filepath).name}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by semicolon and filter out comments
        statements = []
        for stmt in content.split(';'):
            # Remove single-line comments
            lines = [line for line in stmt.split('\n') 
                    if line.strip() and not line.strip().startswith('//')]
            clean_stmt = '\n'.join(lines).strip()
            
            if clean_stmt:
                statements.append(clean_stmt)
        
        # Execute each statement
        successful = 0
        failed = 0
        
        with self.driver.session() as session:
            for i, statement in enumerate(statements, 1):
                try:
                    result = session.run(statement)
                    summary = result.consume()
                    successful += 1
                    
                    # Show progress for data statements
                    if i % 10 == 0:
                        print(f"  ✓ Executed {i}/{len(statements)} statements...")
                        
                except Exception as e:
                    failed += 1
                    print(f"  ✗ Statement {i} failed: {str(e)[:100]}")
        
        print(f"  ✅ Completed: {successful} successful, {failed} failed")
    
    def verify_data(self) -> dict:
        """Verify loaded data and return statistics."""
        print("\n🔍 Verifying data...")
        
        with self.driver.session() as session:
            # Count nodes by type
            node_result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY type
            """)
            
            nodes = {}
            total_nodes = 0
            for record in node_result:
                if record["type"]:
                    count = record["count"]
                    nodes[record["type"]] = count
                    total_nodes += count
            
            # Count relationships by type
            rel_result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY type
            """)
            
            relationships = {}
            total_rels = 0
            for record in rel_result:
                count = record["count"]
                relationships[record["type"]] = count
                total_rels += count
            
            stats = {
                "nodes": nodes,
                "relationships": relationships,
                "total_nodes": total_nodes,
                "total_relationships": total_rels
            }
            
            return stats
    
    def print_stats(self, stats: dict) -> None:
        """Print statistics in a formatted way."""
        print("\n" + "="*60)
        print("  📊 Database Statistics")
        print("="*60)
        
        print("\n  Nodes:")
        for node_type, count in sorted(stats["nodes"].items()):
            print(f"    {node_type:20} : {count:4}")
        print(f"    {'TOTAL':20} : {stats['total_nodes']:4}")
        
        print("\n  Relationships:")
        for rel_type, count in sorted(stats["relationships"].items()):
            print(f"    {rel_type:20} : {count:4}")
        print(f"    {'TOTAL':20} : {stats['total_relationships']:4}")
        
        print("\n" + "="*60)
    
    def load_sample_queries(self) -> None:
        """Display sample queries users can try."""
        print("\n💡 Sample Questions to Try:")
        print("""
  1. "Who is the Python expert in Engineering?"
  2. "What projects is John Doe working on?"
  3. "Show me all employees working on the Mobile App Redesign"
  4. "Which employees have Kubernetes skills?"
  5. "What are the active projects in the company?"
  6. "Who manages the Infrastructure Modernization project?"
  7. "Find all employees in the Engineering department"
  8. "What skills does Sarah Smith have?"
  9. "Which projects require Machine Learning skills?"
  10. "Show me documentation related to the Payment API project"
        """)
    
    def close(self):
        """Close database connection."""
        self.driver.close()
        print("\n🔌 Disconnected from Neo4j")


def main():
    """Main loading function."""
    print("="*60)
    print("  🏢 Company Knowledge Base Loader")
    print("="*60)
    
    loader = CompanyKBLoader()
    
    try:
        # Load schema
        schema_file = Path(__file__).parent.parent / "data" / "company_schema.cypher"
        if schema_file.exists():
            loader.execute_cypher_file(str(schema_file))
        else:
            print(f"⚠️  Schema file not found: {schema_file}")
        
        # Load data
        data_file = Path(__file__).parent.parent / "data" / "company_data.cypher"
        if data_file.exists():
            loader.execute_cypher_file(str(data_file))
        else:
            print(f"⚠️  Data file not found: {data_file}")
        
        # Verify and display stats
        stats = loader.verify_data()
        loader.print_stats(stats)
        
        # Show sample queries
        loader.load_sample_queries()
        
        print("\n" + "="*60)
        print("  ✅ Company Knowledge Base loaded successfully!")
        print("="*60)
        print("\n🚀 Next steps:")
        print("  1. Start API: python -m uvicorn src.main:app --reload")
        print("  2. Visit: http://localhost:8000/api/v1/docs")
        print("  3. Try the sample questions above!\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        loader.close()


if __name__ == "__main__":
    main()
