# 🏢 Company Knowledge Base - Quick Start Template

## Overview

This template shows how to build a **Company Knowledge Base** using your Neo4j + LangChain API.

**What employees can ask:**
- "Who is the Python expert in Engineering?"
- "What projects is Sarah working on?"
- "Find documentation about our payment API"
- "Who worked on the mobile app redesign?"

---

## 📊 Step 1: Design Your Schema

**File: `data/company_schema.cypher`**

```cypher
// Clear existing data (CAREFUL in production!)
// MATCH (n) DETACH DELETE n;

// Create constraints
CREATE CONSTRAINT employee_email IF NOT EXISTS 
  FOR (e:Employee) REQUIRE e.email IS UNIQUE;

CREATE CONSTRAINT department_name IF NOT EXISTS 
  FOR (d:Department) REQUIRE d.name IS UNIQUE;

CREATE CONSTRAINT project_id IF NOT EXISTS 
  FOR (p:Project) REQUIRE p.project_id IS UNIQUE;

CREATE CONSTRAINT skill_name IF NOT EXISTS 
  FOR (s:Skill) REQUIRE s.name IS UNIQUE;

// Create indexes for fast lookups
CREATE INDEX employee_name IF NOT EXISTS 
  FOR (e:Employee) ON (e.name);

CREATE INDEX project_name IF NOT EXISTS 
  FOR (p:Project) ON (p.name);

CREATE INDEX project_status IF NOT EXISTS 
  FOR (p:Project) ON (p.status);

// Full-text search index
CREATE FULLTEXT INDEX employee_search IF NOT EXISTS
  FOR (e:Employee) ON EACH [e.name, e.bio, e.title];
```

---

## 📝 Step 2: Prepare Your Data

Create a CSV file with your company data:

**File: `data/company_employees.csv`**
```csv
email,name,title,department,hire_date,bio
john.doe@company.com,John Doe,Senior Engineer,Engineering,2020-01-15,Full-stack developer with 10 years experience
sarah.smith@company.com,Sarah Smith,Product Manager,Product,2021-03-20,Led 5+ successful product launches
mike.jones@company.com,Mike Jones,DevOps Engineer,Engineering,2019-07-10,Kubernetes and AWS expert
```

**File: `data/company_projects.csv`**
```csv
project_id,name,status,start_date,description
PRJ001,Mobile App Redesign,active,2024-01-01,Complete redesign of iOS and Android apps
PRJ002,Payment API v2,completed,2023-06-15,New payment processing API
PRJ003,Customer Dashboard,active,2024-03-01,Self-service customer portal
```

**File: `data/company_skills.csv`**
```csv
skill_name,category
Python,Programming Language
React,Framework
AWS,Cloud Platform
Kubernetes,DevOps
Product Strategy,Soft Skill
```

**File: `data/employee_skills.csv`**
```csv
employee_email,skill_name,proficiency_level
john.doe@company.com,Python,Expert
john.doe@company.com,React,Intermediate
sarah.smith@company.com,Product Strategy,Expert
mike.jones@company.com,AWS,Expert
mike.jones@company.com,Kubernetes,Expert
```

**File: `data/project_assignments.csv`**
```csv
employee_email,project_id,role,hours_allocated
john.doe@company.com,PRJ001,Tech Lead,160
sarah.smith@company.com,PRJ001,Product Owner,80
mike.jones@company.com,PRJ002,DevOps Lead,120
```

---

## 🔧 Step 3: Create Data Loader

**File: `scripts/load_company_kb.py`**

```python
"""
Load company knowledge base data from CSV files.
"""
import pandas as pd
from neo4j import GraphDatabase
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.core.config import settings

class CompanyKBLoader:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password)
        )
    
    def load_schema(self):
        """Load schema from cypher file."""
        print("📋 Loading schema...")
        with open('data/company_schema.cypher', 'r') as f:
            schema_cypher = f.read()
        
        # Split by semicolon and execute
        with self.driver.session() as session:
            for statement in schema_cypher.split(';'):
                clean = statement.strip()
                if clean and not clean.startswith('//'):
                    try:
                        session.run(clean)
                        print(f"  ✓ Executed: {clean[:50]}...")
                    except Exception as e:
                        print(f"  ✗ Error: {e}")
        print()
    
    def load_employees(self):
        """Load employees from CSV."""
        print("👥 Loading employees...")
        df = pd.read_csv('data/company_employees.csv')
        
        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (e:Employee {email: $email})
                    SET e.name = $name,
                        e.title = $title,
                        e.hire_date = date($hire_date),
                        e.bio = $bio
                    MERGE (d:Department {name: $department})
                    MERGE (e)-[:WORKS_IN]->(d)
                """, **row.to_dict())
        
        print(f"  ✓ Loaded {len(df)} employees\n")
    
    def load_projects(self):
        """Load projects from CSV."""
        print("📁 Loading projects...")
        df = pd.read_csv('data/company_projects.csv')
        
        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (p:Project {project_id: $project_id})
                    SET p.name = $name,
                        p.status = $status,
                        p.start_date = date($start_date),
                        p.description = $description
                """, **row.to_dict())
        
        print(f"  ✓ Loaded {len(df)} projects\n")
    
    def load_skills(self):
        """Load skills from CSV."""
        print("💻 Loading skills...")
        df = pd.read_csv('data/company_skills.csv')
        
        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (s:Skill {name: $skill_name})
                    SET s.category = $category
                """, **row.to_dict())
        
        print(f"  ✓ Loaded {len(df)} skills\n")
    
    def load_employee_skills(self):
        """Load employee-skill relationships."""
        print("🔗 Loading employee skills...")
        df = pd.read_csv('data/employee_skills.csv')
        
        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MATCH (e:Employee {email: $employee_email})
                    MATCH (s:Skill {name: $skill_name})
                    MERGE (e)-[r:HAS_SKILL]->(s)
                    SET r.proficiency_level = $proficiency_level
                """, **row.to_dict())
        
        print(f"  ✓ Loaded {len(df)} skill relationships\n")
    
    def load_project_assignments(self):
        """Load project assignments."""
        print("📊 Loading project assignments...")
        df = pd.read_csv('data/project_assignments.csv')
        
        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MATCH (e:Employee {email: $employee_email})
                    MATCH (p:Project {project_id: $project_id})
                    MERGE (e)-[r:WORKS_ON]->(p)
                    SET r.role = $role,
                        r.hours_allocated = $hours_allocated
                """, **row.to_dict())
        
        print(f"  ✓ Loaded {len(df)} project assignments\n")
    
    def verify_data(self):
        """Verify loaded data."""
        print("🔍 Verifying data...")
        with self.driver.session() as session:
            # Count nodes
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY type
            """)
            
            print("\n  Node counts:")
            for record in result:
                print(f"    {record['type']}: {record['count']}")
            
            # Count relationships
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY type
            """)
            
            print("\n  Relationship counts:")
            for record in result:
                print(f"    {record['type']}: {record['count']}")
        print()
    
    def close(self):
        self.driver.close()

def main():
    """Main loading function."""
    print("="*60)
    print("  🏢 Loading Company Knowledge Base")
    print("="*60 + "\n")
    
    loader = CompanyKBLoader()
    
    try:
        loader.load_schema()
        loader.load_employees()
        loader.load_projects()
        loader.load_skills()
        loader.load_employee_skills()
        loader.load_project_assignments()
        loader.verify_data()
        
        print("="*60)
        print("  ✅ Company knowledge base loaded successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        loader.close()

if __name__ == "__main__":
    main()
```

---

## 🚀 Step 4: Load Your Data

```bash
# Make sure Neo4j is running
docker-compose up -d

# Load the company data
python scripts/load_company_kb.py
```

---

## 💬 Step 5: Test Queries

Start the API:
```bash
python -m uvicorn src.main:app --reload
```

Try these queries at http://localhost:8000/api/v1/docs:

**Query 1: Find Expert**
```json
{
  "question": "Who is the Python expert in our company?",
  "include_cypher": true
}
```

**Query 2: Project Team**
```json
{
  "question": "Who is working on the Mobile App Redesign project?",
  "include_cypher": true
}
```

**Query 3: Employee Skills**
```json
{
  "question": "What skills does John Doe have?",
  "include_cypher": false
}
```

**Query 4: Active Projects**
```json
{
  "question": "Show me all active projects",
  "include_cypher": false
}
```

---

## 📈 Step 6: Customize for Your Company

### Add More Node Types

```cypher
// Add documents
CREATE CONSTRAINT document_id IF NOT EXISTS 
  FOR (doc:Document) REQUIRE doc.id IS UNIQUE;

// Add meetings
CREATE CONSTRAINT meeting_id IF NOT EXISTS 
  FOR (m:Meeting) REQUIRE m.id IS UNIQUE;

// Add teams
CREATE CONSTRAINT team_name IF NOT EXISTS 
  FOR (t:Team) REQUIRE t.name IS UNIQUE;
```

### Add More Relationships

```cypher
// Employee attended meeting
(e:Employee)-[:ATTENDED]->(m:Meeting)

// Project has document
(p:Project)-[:HAS_DOCUMENT]->(doc:Document)

// Employee leads team
(e:Employee)-[:LEADS]->(t:Team)

// Team owns project
(t:Team)-[:OWNS]->(p:Project)
```

### Real Data Integration

**Connect to HR System:**
```python
import requests

def fetch_from_hr_api():
    """Fetch employees from HR system API."""
    response = requests.get(
        "https://hr-system.company.com/api/employees",
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    )
    return response.json()

def sync_employees():
    """Sync employees from HR to Neo4j."""
    employees = fetch_from_hr_api()
    
    with driver.session() as session:
        for emp in employees:
            session.run("""
                MERGE (e:Employee {email: $email})
                SET e.name = $name,
                    e.title = $title,
                    e.department = $department,
                    e.updated_at = datetime()
            """, **emp)
```

**Connect to Jira:**
```python
from jira import JIRA

jira = JIRA('https://company.atlassian.net', basic_auth=('email', 'token'))

def sync_projects():
    """Sync projects from Jira."""
    projects = jira.projects()
    
    for project in projects:
        issues = jira.search_issues(f'project={project.key}')
        # Load to Neo4j
```

---

## 🎯 Next Steps

1. **Customize Schema**: Add your company-specific entities
2. **Load Real Data**: Connect to your HR, project management systems
3. **Add Security**: Implement authentication and authorization
4. **Deploy**: Choose AWS, Azure, or Google Cloud
5. **Monitor**: Set up logging and alerts
6. **Iterate**: Improve based on user feedback

---

## 💡 Pro Tips

1. **Start Small**: Begin with employees and projects only
2. **Incremental Loading**: Load data incrementally, don't try everything at once
3. **Test Queries**: Test with small dataset before full load
4. **Document Relationships**: Keep a diagram of your schema
5. **Use Constraints**: Always add constraints before loading data
6. **Backup Data**: Regular Neo4j backups

---

**Ready to build your company knowledge base!** 🚀

For more use cases, see [REAL_WORLD_USECASES.md](REAL_WORLD_USECASES.md)
