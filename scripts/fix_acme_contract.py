"""
Fix script to add the missing Acme Corp contract.
"""
from neo4j import GraphDatabase
from src.core.config import settings

driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_username, settings.neo4j_password)
)

with driver.session() as session:
    # Create the Acme Corp contract
    session.run("""
        MERGE (c:Contract {
            id: 'contract-001',
            title: 'Master Service Agreement - Acme Corp',
            type: 'Service Agreement',
            start_date: date('2023-06-01'),
            end_date: date('2024-06-01'),
            value: 150000.00,
            status: 'active',
            terms: 'Annual software development services with quarterly milestones.',
            text: 'This agreement outlines the terms for software development services...',
            created_at: datetime()
        })
    """)
    
    # Link to Acme Corporation client
    session.run("""
        MATCH (c:Contract {id: 'contract-001'})
        MATCH (cl:Client {id: 'client-001'})
        MERGE (c)-[:FOR_CLIENT]->(cl)
    """)
    
    # Link to a manager
    result = session.run("""
        MATCH (c:Contract {id: 'contract-001'})
        MATCH (e:Employee)
        WHERE e.title CONTAINS 'Manager' OR e.title CONTAINS 'Lead'
        WITH c, e LIMIT 1
        MERGE (c)-[:MANAGED_BY]->(e)
        RETURN e.name, e.title
    """)
    
    manager = result.single()
    
    print("✅ Created Acme Corp contract")
    if manager:
        print(f"✅ Linked to manager: {manager['e.name']} ({manager['e.title']})")
    
    # Verify
    result = session.run("""
        MATCH (c:Contract)-[:FOR_CLIENT]->(cl:Client)
        WHERE toLower(cl.name) CONTAINS 'acme'
        RETURN c.title, cl.name, c.value
    """)
    
    contract = result.single()
    if contract:
        print(f"\n✓ Verification: {contract['c.title']}")
        print(f"  Client: {contract['cl.name']}")
        print(f"  Value: ${contract['c.value']:,.0f}")
    else:
        print("\n❌ Verification failed - contract not found")

driver.close()
