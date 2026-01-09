"""
Schema migration script for Document Linking feature.
Adds Client, Contract, and Policy nodes with relationships.
"""

from neo4j import GraphDatabase
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

SCHEMA_MIGRATION = """
// ============================================
// DOCUMENT LINKING SCHEMA MIGRATION
// ============================================

// 1. Create Constraints for uniqueness
CREATE CONSTRAINT client_id IF NOT EXISTS
FOR (c:Client) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT contract_id IF NOT EXISTS
FOR (c:Contract) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT policy_id IF NOT EXISTS
FOR (p:Policy) REQUIRE p.id IS UNIQUE;

// 2. Create indexes for performance
CREATE INDEX client_name IF NOT EXISTS
FOR (c:Client) ON (c.name);

CREATE INDEX contract_title IF NOT EXISTS
FOR (c:Contract) ON (c.title);

CREATE INDEX policy_title IF NOT EXISTS
FOR (p:Policy) ON (p.title);

CREATE INDEX policy_type IF NOT EXISTS
FOR (p:Policy) ON (p.type);

// 3. Sample Client nodes (for testing)
MERGE (c1:Client {
    id: 'client-001',
    name: 'Acme Corporation',
    industry: 'Technology',
    tier: 'Enterprise',
    contact_email: 'contact@acmecorp.com',
    start_date: date('2020-01-15'),
    status: 'active'
});

MERGE (c2:Client {
    id: 'client-002',
    name: 'TechStartup Inc',
    industry: 'SaaS',
    tier: 'Startup',
    contact_email: 'info@techstartup.io',
    start_date: date('2022-06-01'),
    status: 'active'
});

MERGE (c3:Client {
    id: 'client-003',
    name: 'Global Enterprises',
    industry: 'Manufacturing',
    tier: 'Enterprise',
    contact_email: 'sales@globalent.com',
    start_date: date('2019-03-10'),
    status: 'active'
});

// 4. Sample Policy nodes (for testing)
// Note: These will be replaced by actual ingested policies
MERGE (p1:Policy {
    id: 'policy-001',
    title: 'Engineering Vacation Policy',
    type: 'HR',
    effective_date: date('2023-01-01'),
    version: '2.0',
    status: 'active',
    text: 'Engineering team members are entitled to 20 days of paid vacation per year, plus 5 sick days.'
});

MERGE (p2:Policy {
    id: 'policy-002',
    title: 'Remote Work Policy',
    type: 'HR',
    effective_date: date('2023-06-01'),
    version: '1.0',
    status: 'active',
    text: 'All employees are eligible for hybrid work with a minimum of 2 days in office per week.'
});

// 5. Link sample policies to departments
MATCH (p:Policy {id: 'policy-001'})
MATCH (d:Department {name: 'Engineering'})
MERGE (p)-[:APPLIES_TO]->(d);

MATCH (p:Policy {id: 'policy-002'})
MATCH (d:Department)
MERGE (p)-[:APPLIES_TO]->(d);

// 6. Sample Contract nodes (for testing)
MERGE (contract1:Contract {
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
});

MERGE (contract2:Contract {
    id: 'contract-002',
    title: 'NDA - TechStartup Inc',
    type: 'NDA',
    start_date: date('2024-01-15'),
    end_date: date('2026-01-15'),
    value: 0.0,
    status: 'active',
    terms: 'Non-disclosure agreement covering confidential business information.',
    text: 'This mutual non-disclosure agreement protects both parties...',
    created_at: datetime()
});

MERGE (contract3:Contract {
    id: 'contract-003',
    title: 'SOW - Global Enterprises',
    type: 'SOW',
    start_date: date('2024-03-01'),
    end_date: date('2024-12-31'),
    value: 75000.00,
    status: 'active',
    terms: 'Statement of Work for cloud migration project.',
    text: 'This SOW defines deliverables for migrating legacy systems to cloud...',
    created_at: datetime()
});

// 7. Link contracts to clients
MATCH (c:Contract {id: 'contract-001'})
MATCH (cl:Client {id: 'client-001'})
MERGE (c)-[:FOR_CLIENT]->(cl);

MATCH (c:Contract {id: 'contract-002'})
MATCH (cl:Client {id: 'client-002'})
MERGE (c)-[:FOR_CLIENT]->(cl);

MATCH (c:Contract {id: 'contract-003'})
MATCH (cl:Client {id: 'client-003'})
MERGE (c)-[:FOR_CLIENT]->(cl);

// 8. Link contracts to account managers (employees)
// Find employees and assign as contract managers
MATCH (c:Contract {id: 'contract-001'})
MATCH (e:Employee)
WHERE e.title CONTAINS 'Manager' OR e.title CONTAINS 'Lead'
WITH c, e LIMIT 1
MERGE (c)-[:MANAGED_BY]->(e);

MATCH (c:Contract {id: 'contract-002'})
MATCH (e:Employee)
WHERE e.department = 'Engineering'
WITH c, e LIMIT 1
MERGE (c)-[:MANAGED_BY]->(e);

MATCH (c:Contract {id: 'contract-003'})
MATCH (e:Employee)
WHERE e.title CONTAINS 'Senior'
WITH c, e LIMIT 1
MERGE (c)-[:MANAGED_BY]->(e);

// 9. Link sample clients to primary contacts
MATCH (cl:Client {id: 'client-001'})
MATCH (e:Employee)
WITH cl, e LIMIT 1
MERGE (cl)-[:PRIMARY_CONTACT]->(e);
"""

ROLLBACK_MIGRATION = """
// Rollback script - removes all Document Linking nodes and relationships

// Remove relationships first
MATCH (c:Contract)-[r]-() DELETE r;
MATCH (p:Policy)-[r]-() DELETE r;
MATCH (cl:Client)-[r]-() DELETE r;

// Remove nodes
MATCH (c:Contract) DELETE c;
MATCH (p:Policy) DELETE p;
MATCH (cl:Client) DELETE cl;

// Drop constraints
DROP CONSTRAINT client_id IF EXISTS;
DROP CONSTRAINT contract_id IF EXISTS;
DROP CONSTRAINT policy_id IF EXISTS;

// Drop indexes
DROP INDEX client_name IF EXISTS;
DROP INDEX contract_title IF EXISTS;
DROP INDEX policy_title IF EXISTS;
DROP INDEX policy_type IF EXISTS;
"""

def run_migration():
    """Execute the schema migration."""
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password)
    )
    
    try:
        with driver.session() as session:
            logger.info("Starting Document Linking schema migration...")
            
            # Split and execute each statement
            statements = [s.strip() for s in SCHEMA_MIGRATION.split(';') if s.strip() and not s.strip().startswith('//')]
            
            for i, statement in enumerate(statements, 1):
                try:
                    session.run(statement)
                    logger.info(f"Executed statement {i}/{len(statements)}")
                except Exception as e:
                    logger.error(f"Failed to execute statement {i}: {e}")
                    logger.error(f"Statement: {statement[:100]}...")
                    raise
            
            logger.info("✅ Schema migration completed successfully!")
            logger.info("Created: Client, Contract, Policy nodes with sample data")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        driver.close()

def rollback_migration():
    """Rollback the schema migration."""
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password)
    )
    
    try:
        with driver.session() as session:
            logger.info("Rolling back Document Linking schema...")
            
            statements = [s.strip() for s in ROLLBACK_MIGRATION.split(';') if s.strip() and not s.strip().startswith('//')]
            
            for statement in statements:
                try:
                    session.run(statement)
                except Exception as e:
                    logger.warning(f"Rollback statement warning: {e}")
            
            logger.info("✅ Rollback completed")
            
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        raise
    finally:
        driver.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        rollback_migration()
    else:
        run_migration()
