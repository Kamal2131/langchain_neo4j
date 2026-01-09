"""
Check what clients exist in the database.
"""
from neo4j import GraphDatabase
from src.core.config import settings

driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_username, settings.neo4j_password)
)

with driver.session() as session:
    result = session.run("MATCH (cl:Client) RETURN cl.id, cl.name ORDER BY cl.name")
    
    print("=" * 60)
    print("CLIENTS IN DATABASE:")
    print("=" * 60)
    for record in result:
        print(f"- {record['cl.name']} (ID: {record['cl.id']})")
    
    # Check Acme specifically
    print("\n" + "=" * 60)
    print("CHECKING ACME:")
    print("=" * 60)
    result2 = session.run("""
        MATCH (cl:Client)
        WHERE toLower(cl.name) CONTAINS 'acme'
        RETURN cl.id, cl.name
    """)
    
    acme = list(result2)
    if acme:
        for record in acme:
            print(f"✓ Found: {record['cl.name']} ({record['cl.id']})")
    else:
        print("❌ No client with 'Acme' in name found")
    
    # Check contracts
    print("\n" + "=" * 60)
    print("ALL CONTRACTS:")
    print("=" * 60)
    result3 = session.run("""
        MATCH (c:Contract)
        OPTIONAL MATCH (c)-[:FOR_CLIENT]->(cl:Client)
        RETURN c.title, c.id, cl.name as client
    """)
    
    for record in result3:
        client = record['client'] or "NO CLIENT LINKED"
        print(f"- {record['c.title']} → {client}")

driver.close()
