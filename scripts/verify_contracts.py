"""
Quick script to verify contract data exists in Neo4j.
"""
from neo4j import GraphDatabase
from src.core.config import settings

driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_username, settings.neo4j_password)
)

with driver.session() as session:
    # Check contracts
    result = session.run("""
        MATCH (c:Contract)-[:FOR_CLIENT]->(cl:Client)
        RETURN c.title, cl.name, c.value, c.status
        ORDER BY c.value DESC
    """)
    
    print("=" * 60)
    print("CONTRACTS IN DATABASE:")
    print("=" * 60)
    contracts = list(result)
    
    if contracts:
        for record in contracts:
            print(f"✓ {record['c.title']}")
            print(f"  Client: {record['cl.name']}")
            print(f"  Value: ${record['c.value']:,.0f}")
            print(f"  Status: {record['c.status']}")
            print()
    else:
        print("❌ No contracts found!")
    
    # Check contract managers
    result2 = session.run("""
        MATCH (c:Contract)-[:MANAGED_BY]->(e:Employee)
        RETURN c.title, e.name, e.title
    """)
    
    print("=" * 60)
    print("CONTRACT MANAGERS:")
    print("=" * 60)
    managers = list(result2)
    
    if managers:
        for record in managers:
            print(f"✓ {record['c.title']}")
            print(f"  Manager: {record['e.name']} ({record['e.title']})")
            print()
    else:
        print("⚠️  No managers linked yet")

driver.close()
print("\n✅ Verification complete")
