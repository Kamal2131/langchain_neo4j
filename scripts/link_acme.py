"""
Final fix: Link Acme Corp contract to Acme Corporation client.
"""
from neo4j import GraphDatabase
from src.core.config import settings

driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_username, settings.neo4j_password)
)

with driver.session() as session:
    # Link the contract to Acme Corporation client
    session.run("""
        MATCH (c:Contract {id: 'contract-001'})
        MATCH (cl:Client)
        WHERE toLower(cl.name) CONTAINS 'acme'
        WITH c, cl LIMIT 1
        MERGE (c)-[:FOR_CLIENT]->(cl)
    """)
    
    print("✅ Linked Acme contract to client")
    
    # Verify  
    result = session.run("""
        MATCH (c:Contract)-[:FOR_CLIENT]->(cl:Client)
        WHERE toLower(cl.name) CONTAINS 'acme'
        RETURN c.title, cl.name, c.value
    """)
    
    record = result.single()
    if record:
        print(f"\n✓ VERIFIED: {record['c.title']}")
        print(f"  Client: {record['cl.name']}")
        print(f"  Value: ${record['c.value']:,.0f}")
        print("\n🎉 Now try the query: 'What contracts do we have with Acme Corporation?'")
    else:
        print("\n❌ Linkage failed")

driver.close()
