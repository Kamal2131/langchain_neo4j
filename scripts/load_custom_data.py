"""
Custom CSV Data Loader for Neo4j Knowledge Base

This script loads your company data from CSV files into Neo4j.
Place your filled-out CSV files in data/templates/ and run this script.

Usage:
    python scripts/load_custom_data.py
"""

import csv
import os
from pathlib import Path
from typing import Dict, List, Any

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

# Neo4j connection settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Path to CSV templates
TEMPLATES_DIR = Path(__file__).parent.parent / "data" / "templates"


def read_csv(filename: str) -> List[Dict[str, Any]]:
    """Read a CSV file and return list of dictionaries."""
    filepath = TEMPLATES_DIR / filename
    if not filepath.exists():
        print(f"  ⚠️  File not found: {filename}")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def clear_database(driver):
    """Clear all existing data from the database."""
    print("\n🗑️  Clearing existing data...")
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    print("  ✓ Database cleared")


def load_departments(driver, data: List[Dict]):
    """Load departments into Neo4j."""
    print("\n🏢 Loading departments...")
    with driver.session() as session:
        for dept in data:
            session.run("""
                MERGE (d:Department {name: $name})
                SET d.description = $description
            """, name=dept['name'], description=dept.get('description', ''))
    print(f"  ✓ Loaded {len(data)} departments")


def load_employees(driver, data: List[Dict]):
    """Load employees into Neo4j."""
    print("\n👥 Loading employees...")
    with driver.session() as session:
        for emp in data:
            # Create employee
            session.run("""
                MERGE (e:Employee {id: $id})
                SET e.name = $name,
                    e.email = $email,
                    e.title = $title,
                    e.department = $department,
                    e.location = $location,
                    e.hire_date = $hire_date,
                    e.salary = toInteger($salary),
                    e.level = $level,
                    e.bio = $bio,
                    e.phone = $phone
            """, **emp)
            
            # Link to department
            if emp.get('department'):
                session.run("""
                    MATCH (e:Employee {id: $emp_id})
                    MATCH (d:Department {name: $dept_name})
                    MERGE (e)-[:WORKS_IN]->(d)
                """, emp_id=emp['id'], dept_name=emp['department'])
    
    print(f"  ✓ Loaded {len(data)} employees")


def load_skills(driver, data: List[Dict]):
    """Load skills into Neo4j."""
    print("\n💻 Loading skills...")
    with driver.session() as session:
        for skill in data:
            session.run("""
                MERGE (s:Skill {name: $name})
                SET s.category = $category
            """, name=skill['name'], category=skill.get('category', ''))
    print(f"  ✓ Loaded {len(data)} skills")


def load_projects(driver, data: List[Dict]):
    """Load projects into Neo4j."""
    print("\n📊 Loading projects...")
    with driver.session() as session:
        for proj in data:
            session.run("""
                MERGE (p:Project {project_id: $project_id})
                SET p.name = $name,
                    p.description = $description,
                    p.status = $status,
                    p.budget = toInteger($budget),
                    p.priority = $priority,
                    p.start_date = $start_date,
                    p.end_date = $end_date
            """, **proj)
    print(f"  ✓ Loaded {len(data)} projects")


def load_clients(driver, data: List[Dict]):
    """Load clients into Neo4j."""
    print("\n🏛️  Loading clients...")
    with driver.session() as session:
        for client in data:
            session.run("""
                MERGE (c:Client {id: $id})
                SET c.name = $name,
                    c.industry = $industry,
                    c.revenue = toInteger($revenue),
                    c.contract_value = toInteger($contract_value)
            """, **client)
    print(f"  ✓ Loaded {len(data)} clients")


def load_employee_skills(driver, data: List[Dict]):
    """Create HAS_SKILL relationships between employees and skills."""
    print("\n🔗 Linking employees to skills...")
    count = 0
    with driver.session() as session:
        for row in data:
            result = session.run("""
                MATCH (e:Employee {id: $emp_id})
                MATCH (s:Skill {name: $skill_name})
                MERGE (e)-[:HAS_SKILL]->(s)
                RETURN e, s
            """, emp_id=row['employee_id'], skill_name=row['skill_name'])
            if result.single():
                count += 1
    print(f"  ✓ Created {count} HAS_SKILL relationships")


def load_employee_projects(driver, data: List[Dict]):
    """Create WORKS_ON relationships between employees and projects."""
    print("\n🔗 Linking employees to projects...")
    count = 0
    with driver.session() as session:
        for row in data:
            result = session.run("""
                MATCH (e:Employee {id: $emp_id})
                MATCH (p:Project {project_id: $proj_id})
                MERGE (e)-[r:WORKS_ON]->(p)
                SET r.role = $role
                RETURN e, p
            """, emp_id=row['employee_id'], proj_id=row['project_id'], role=row.get('role', ''))
            if result.single():
                count += 1
    print(f"  ✓ Created {count} WORKS_ON relationships")


def load_project_clients(driver, data: List[Dict]):
    """Create FOR_CLIENT relationships between projects and clients."""
    print("\n🔗 Linking projects to clients...")
    count = 0
    with driver.session() as session:
        for row in data:
            result = session.run("""
                MATCH (p:Project {project_id: $proj_id})
                MATCH (c:Client {id: $client_id})
                MERGE (p)-[:FOR_CLIENT]->(c)
                RETURN p, c
            """, proj_id=row['project_id'], client_id=row['client_id'])
            if result.single():
                count += 1
    print(f"  ✓ Created {count} FOR_CLIENT relationships")


def load_reporting_structure(driver, data: List[Dict]):
    """Create REPORTS_TO relationships between employees."""
    print("\n🔗 Setting up reporting structure...")
    count = 0
    with driver.session() as session:
        for row in data:
            result = session.run("""
                MATCH (e:Employee {id: $emp_id})
                MATCH (m:Employee {id: $manager_id})
                MERGE (e)-[:REPORTS_TO]->(m)
                RETURN e, m
            """, emp_id=row['employee_id'], manager_id=row['manager_id'])
            if result.single():
                count += 1
    print(f"  ✓ Created {count} REPORTS_TO relationships")


def print_summary(driver):
    """Print summary of loaded data."""
    print("\n" + "=" * 50)
    print("📊 DATA LOAD SUMMARY")
    print("=" * 50)
    
    with driver.session() as session:
        # Count nodes
        result = session.run("""
            MATCH (n)
            RETURN labels(n)[0] as label, count(n) as count
            ORDER BY label
        """)
        print("\nNodes:")
        for record in result:
            print(f"  • {record['label']}: {record['count']}")
        
        # Count relationships
        result = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) as type, count(r) as count
            ORDER BY type
        """)
        print("\nRelationships:")
        for record in result:
            print(f"  • {record['type']}: {record['count']}")
    
    print("\n" + "=" * 50)
    print("✅ Data load complete!")
    print("=" * 50)


def main():
    print("=" * 50)
    print("🚀 CUSTOM CSV DATA LOADER")
    print("=" * 50)
    print(f"\nConnecting to: {NEO4J_URI}")
    print(f"Templates dir: {TEMPLATES_DIR}")
    
    # Verify templates directory exists
    if not TEMPLATES_DIR.exists():
        print(f"\n❌ Error: Templates directory not found: {TEMPLATES_DIR}")
        print("Please create the directory and add your CSV files.")
        return
    
    # Connect to Neo4j
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("  ✓ Connected to Neo4j")
    except Exception as e:
        print(f"\n❌ Error connecting to Neo4j: {e}")
        return
    
    try:
        # Ask for confirmation before clearing
        print("\n⚠️  WARNING: This will DELETE ALL existing data!")
        response = input("Continue? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Aborted.")
            return
        
        # Clear existing data
        clear_database(driver)
        
        # Load nodes (order matters - departments first, then employees)
        departments = read_csv("departments.csv")
        load_departments(driver, departments)
        
        skills = read_csv("skills.csv")
        load_skills(driver, skills)
        
        employees = read_csv("employees.csv")
        load_employees(driver, employees)
        
        projects = read_csv("projects.csv")
        load_projects(driver, projects)
        
        clients = read_csv("clients.csv")
        load_clients(driver, clients)
        
        # Load relationships
        employee_skills = read_csv("employee_skills.csv")
        load_employee_skills(driver, employee_skills)
        
        employee_projects = read_csv("employee_projects.csv")
        load_employee_projects(driver, employee_projects)
        
        project_clients = read_csv("project_clients.csv")
        load_project_clients(driver, project_clients)
        
        reporting = read_csv("reporting_structure.csv")
        load_reporting_structure(driver, reporting)
        
        # Print summary
        print_summary(driver)
        
    finally:
        driver.close()


if __name__ == "__main__":
    main()
