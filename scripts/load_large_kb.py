"""
Load generated fake data into Neo4j.
Clears existing data and loads comprehensive tech company knowledge base.
"""

import json
from pathlib import Path
import sys
from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.core.config import settings


class LargeKBLoader:
    """Loader for large knowledge base data."""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password)
        )
        print(f"✅ Connected to Neo4j at {settings.neo4j_uri}\n")
    
    def clear_database(self):
        """Clear all existing data and constraints."""
        print("🗑️  Clearing existing data...")
        
        with self.driver.session() as session:
            # Get counts before deletion
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]
            
            if node_count > 0:
                print(f"  Found {node_count} nodes to delete")
                # Delete all
                session.run("MATCH (n) DETACH DELETE n")
                print("  ✓ All data cleared")
            else:
                print("  ✓ Database already empty")
            
            # Drop all constraints
            print("\n🔧 Dropping old constraints...")
            result = session.run("SHOW CONSTRAINTS")
            constraints = list(result)
            
            if constraints:
                for constraint in constraints:
                    constraint_name = constraint.get("name")
                    if constraint_name:
                        try:
                            session.run(f"DROP CONSTRAINT {constraint_name}")
                            print(f"  ✓ Dropped constraint: {constraint_name}")
                        except Exception as e:
                            print(f"  ⚠ Could not drop {constraint_name}: {e}")
            else:
                print("  ✓ No constraints to drop")
            
            print()
    
    def load_data(self, data_file: str):
        """Load data from JSON file."""
        print(f"📂 Loading data from {data_file}...")
        
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        with self.driver.session() as session:
            # Load departments
            print("\n🏢 Loading departments...")
            for dept in data['departments']:
                session.run("""
                    CREATE (d:Department {
                        name: $name,
                        location: $location,
                        budget: $budget
                    })
                """, **dept)
            print(f"  ✓ Loaded {len(data['departments'])} departments")
            
            # Load employees
            print("\n👥 Loading employees...")
            for emp in data['employees']:
                session.run("""
                    CREATE (e:Employee {
                        employee_id: $id,
                        name: $name,
                        email: $email,
                        title: $title,
                        hire_date: date($hire_date),
                        salary: $salary,
                        level: $level,
                        bio: $bio,
                        phone: $phone,
                        location: $location
                    })
                """, **emp)
            print(f"  ✓ Loaded {len(data['employees'])} employees")
            
            # Link employees to departments
            print("\n🔗 Linking employees to departments...")
            for emp in data['employees']:
                session.run("""
                    MATCH (e:Employee {employee_id: $id})
                    MATCH (d:Department {name: $department})
                    CREATE (e)-[:WORKS_IN]->(d)
                """, id=emp['id'], department=emp['department'])
            print(f"  ✓ Created {len(data['employees'])} WORKS_IN relationships")
            
            # Load skills
            print("\n💻 Loading skills...")
            for skill in data['skills']:
                session.run("""
                    CREATE (s:Skill {
                        skill_id: $id,
                        name: $name,
                        category: $category
                    })
                """, **skill)
            print(f"  ✓ Loaded {len(data['skills'])} skills")
            
            # Load projects
            print("\n📊 Loading projects...")
            for proj in data['projects']:
                query = """
                    CREATE (p:Project {
                        project_id: $id,
                        name: $name,
                        type: $type,
                        status: $status,
                        start_date: date($start_date),
                        budget: $budget,
                        priority: $priority,
                        description: $description
                    })
                """
                session.run(query, **proj)
                
                # Add end_date if exists
                if 'end_date' in proj:
                    session.run("""
                        MATCH (p:Project {project_id: $id})
                        SET p.end_date = date($end_date)
                    """, id=proj['id'], end_date=proj['end_date'])
            print(f"  ✓ Loaded {len(data['projects'])} projects")
            
            # Load clients
            print("\n🏛️  Loading clients...")
            for client in data['clients']:
                session.run("""
                    CREATE (c:Client {
                        client_id: $id,
                        name: $name,
                        industry: $industry,
                        revenue: $revenue,
                        country: $country,
                        website: $website,
                        contract_start: date($contract_start)
                    })
                """, **client)
            print(f"  ✓ Loaded {len(data['clients'])} clients")
            
            # Load documents
            print("\n📄 Loading documents...")
            for doc in data['documents']:
                session.run("""
                    CREATE (d:Document {
                        doc_id: $id,
                        title: $title,
                        type: $type,
                        url: $url,
                        created_date: date($created_date),
                        summary: $summary,
                        version: $version
                    })
                """, **doc)
            print(f"  ✓ Loaded {len(data['documents'])} documents")
            
            # Load relationships
            print("\n🔗 Creating relationships...")
            rels = data['relationships']
            
            # Employee skills
            for rel in rels['employee_skills']:
                session.run("""
                    MATCH (e:Employee {employee_id: $employee_id})
                    MATCH (s:Skill {skill_id: $skill_id})
                    CREATE (e)-[:HAS_SKILL {
                        proficiency: $proficiency,
                        years: $years
                    }]->(s)
                """, **rel)
            print(f"  ✓ Created {len(rels['employee_skills'])} HAS_SKILL relationships")
            
            # Employee projects
            for rel in rels['employee_projects']:
                session.run("""
                    MATCH (e:Employee {employee_id: $employee_id})
                    MATCH (p:Project {project_id: $project_id})
                    CREATE (e)-[:WORKS_ON {
                        role: $role,
                        hours_per_week: $hours_per_week
                    }]->(p)
                """, **rel)
            print(f"  ✓ Created {len(rels['employee_projects'])} WORKS_ON relationships")
            
            # Project clients
            for rel in rels['project_clients']:
                session.run("""
                    MATCH (p:Project {project_id: $project_id})
                    MATCH (c:Client {client_id: $client_id})
                    CREATE (p)-[:FOR_CLIENT]->(c)
                """, **rel)
            print(f"  ✓ Created {len(rels['project_clients'])} FOR_CLIENT relationships")
            
            # Project skills
            for rel in rels['project_skills']:
                session.run("""
                    MATCH (p:Project {project_id: $project_id})
                    MATCH (s:Skill {skill_id: $skill_id})
                    CREATE (p)-[:REQUIRES]->(s)
                """, **rel)
            print(f"  ✓ Created {len(rels['project_skills'])} REQUIRES relationships")
            
            # Project documents
            for rel in rels['project_documents']:
                session.run("""
                    MATCH (p:Project {project_id: $project_id})
                    MATCH (d:Document {doc_id: $document_id})
                    CREATE (p)-[:HAS_DOCUMENT]->(d)
                """, **rel)
            print(f"  ✓ Created {len(rels['project_documents'])} HAS_DOCUMENT relationships")
            
            # Employee reporting
            for rel in rels['employee_reports_to']:
                session.run("""
                    MATCH (e:Employee {employee_id: $employee_id})
                    MATCH (m:Employee {employee_id: $manager_id})
                    CREATE (e)-[:REPORTS_TO]->(m)
                """, **rel)
            print(f"  ✓ Created {len(rels['employee_reports_to'])} REPORTS_TO relationships")
    
    def verify_data(self):
        """Verify loaded data."""
        print("\n🔍 Verifying data...")
        
        with self.driver.session() as session:
            # Count nodes
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY type
            """)
            
            nodes = {}
            total_nodes = 0
            for record in result:
                if record["type"]:
                    count = record["count"]
                    nodes[record["type"]] = count
                    total_nodes += count
            
            # Count relationships
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY type
            """)
            
            relationships = {}
            total_rels = 0
            for record in result:
                count = record["count"]
                relationships[record["type"]] = count
                total_rels += count
            
            print("\n" + "="*60)
            print("  📊 Database Statistics")
            print("="*60)
            
            print("\n  Nodes:")
            for node_type, count in sorted(nodes.items()):
                print(f"    {node_type:20} : {count:5}")
            print(f"    {'TOTAL':20} : {total_nodes:5}")
            
            print("\n  Relationships:")
            for rel_type, count in sorted(relationships.items()):
                print(f"    {rel_type:20} : {count:5}")
            print(f"    {'TOTAL':20} : {total_rels:5}")
            
            print("\n" + "="*60)
            
            return total_nodes, total_rels
    
    def show_sample_queries(self):
        """Show sample queries for the data."""
        print("\n💡 Sample Questions to Try:\n")
        queries = [
            "Find Python experts in Engineering",
            "What projects are currently active?",
            "Who works on the highest budget projects?",
            "Which employees have Machine Learning skills?",
            "Show me all projects for FinTech clients",
            "Find Senior Engineers with AWS experience",
            "What skills are most in demand across projects?",
            "Who reports to the Engineering Managers?",
            "List all employees in San Francisco",
            "Which projects require React and Python?"
        ]
        for i, q in enumerate(queries, 1):
            print(f"  {i:2}. \"{q}\"")
        print()
    
    def close(self):
        self.driver.close()


def main():
    """Main loading function."""
    print("="*60)
    print("  🚀 Large Tech Company Knowledge Base Loader")
    print("="*60 + "\n")
    
    data_file = Path(__file__).parent.parent / "data" / "generated_kb_data.json"
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        print("\n💡 Run this first:")
        print("   python scripts/generate_fake_data.py\n")
        return
    
    loader = LargeKBLoader()
    
    try:
        # Clear existing data
        loader.clear_database()
        
        # Load new data
        loader.load_data(str(data_file))
        
        # Verify
        total_nodes, total_rels = loader.verify_data()
        
        # Show sample queries
        loader.show_sample_queries()
        
        print("="*60)
        print(f"  ✅ Successfully loaded {total_nodes} nodes and {total_rels} relationships!")
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
