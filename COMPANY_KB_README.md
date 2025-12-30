# Company Knowledge Base - Quick Start

## 🚀 Implementation Complete!

Your Neo4j + LangChain API now includes a **real-world Company Knowledge Base** use case.

## 📊 What's Included

### Data Model
- **8 Employees** with realistic profiles, skills, and experience
- **4 Departments** (Engineering, Product, Marketing, Sales)
- **5 Projects** (Mobile App, Payment API, Customer Dashboard, ML Model, Infrastructure)
- **18 Skills** across programming, frameworks, cloud, and soft skills
- **3 Documents** (API docs, design system, onboarding)
- **Multiple relationship types**: WORKS_IN, HAS_SKILL, WORKS_ON, REQUIRES, MANAGES, REPORTS_TO

### Custom API Endpoints

#### 1. Get Employees
```http
GET /api/v1/company/employees
GET /api/v1/company/employees?department=Engineering
```

#### 2. Get Projects
```http
GET /api/v1/company/projects
GET /api/v1/company/projects?status=active
```

#### 3. Find Skill Experts
```http
GET /api/v1/company/skills/Python/experts
GET /api/v1/company/skills/Kubernetes/experts
```

#### 4. Department Statistics
```http
GET /api/v1/company/departments/stats
```

#### 5. Employee's Projects
```http
GET /api/v1/company/employees/john.doe@company.com/projects
```

#### 6. Project Team
```http
GET /api/v1/company/projects/PRJ001/team
```

## 🎯 Load the Data

```bash
# Make sure Neo4j is running
docker-compose up -d

# Load company knowledge base
python scripts/load_company_kb.py
```

Expected output:
```
============================================================
  🏢 Company Knowledge Base Loader
============================================================
✅ Connected to Neo4j at bolt://localhost:7687

📋 Loading company_schema.cypher...
  ✅ Completed: 20 successful, 0 failed

📋 Loading company_data.cypher...
  ✓ Executed 10/100 statements...
  ✓ Executed 20/100 statements...
  ...
  ✅ Completed: 120 successful, 0 failed

🔍 Verifying data...

============================================================
  📊 Database Statistics
============================================================

  Nodes:
    Department           :    4
    Document             :    3
    Employee             :    8
    Project              :    5
    Skill                :   18
    TOTAL                :   38

  Relationships:
    HAS_DOCUMENT         :    2
    HAS_SKILL            :   14
    MANAGES              :    2
    REPORTS_TO           :    4
    REQUIRES             :    8
    WORKS_IN             :    8
    WORKS_ON             :   11
    TOTAL                :   49

============================================================
```

## 💬 Try the API

### Start the server:
```bash
python -m uvicorn src.main:app --reload
```

### Visit Swagger UI:
http://localhost:8000/api/v1/docs

## 🎯 Sample Questions (Natural Language)

Try these questions with the **POST /api/v1/query** endpoint:

1. **"Who is the Python expert in Engineering?"**
   - Expected: John Doe, Alex Kumar (both Expert level)

2. **"What projects is John Doe working on?"**
   - Expected: Mobile App Redesign (Tech Lead), Payment API v2 (Senior Developer)

3. **"Show me all employees working on the Mobile App Redesign"**
   - Expected: John Doe, Sarah Smith, Lisa Wang, David Chen

4. **"Which employees have Kubernetes skills?"**
   - Expected: Mike Jones (Expert, 5 years)

5. **"What are the active projects?"**
   - Expected: Mobile App Redesign, Customer Dashboard, Recommendation Engine

6. **"Who manages the Infrastructure Modernization project?"**
   - Expected: David Chen

7. **"Find all employees in the Engineering department"**
   - Expected: John Doe, Mike Jones, David Chen, Alex Kumar

8. **"What skills does Sarah Smith have?"**
   - Expected: Product Strategy (Expert), Agile (Expert)

9. **"Which projects require Machine Learning skills?"**
   - Expected: Recommendation Engine

10. **"Who reports to David Chen?"**
    - Expected: John Doe, Mike Jones, Alex Kumar

## 📊 Sample REST API Calls

### Get all Engineering employees:
```bash
curl "http://localhost:8000/api/v1/company/employees?department=Engineering"
```

### Find Python experts:
```bash
curl "http://localhost:8000/api/v1/company/skills/Python/experts"
```

### Get active projects:
```bash
curl "http://localhost:8000/api/v1/company/projects?status=active"
```

### Get project team:
```bash
curl "http://localhost:8000/api/v1/company/projects/PRJ001/team"
```

## 🔧 Customization

### Add Your Own Data

1. **Add Employees**: Edit `data/company_data.cypher`
2. **Add Projects**: Add new project nodes
3. **Add Skills**: Add new skill nodes
4. **Create Relationships**: Link employees to projects and skills

### Reload Data
```bash
# Clear old data first (if needed)
# Then reload
python scripts/load_company_kb.py
```

## 🎓 What This Demonstrates

✅ **Real-world schema** - Employees, departments, projects, skills  
✅ **Complex relationships** - Multiple connection types  
✅ **Custom endpoints** - Domain-specific REST APIs  
✅ **Natural language queries** - Ask questions in plain English  
✅ **Graph traversal** - Find experts, teams, reporting structures  
✅ **Production-ready** - Error handling, logging, validation  

## 🚀 Next Steps

1. **Load your own company data** - Replace with real employees/projects
2. **Connect to HR systems** - Import from Workday, BambooHR, etc.
3. **Integrate with Jira** - Sync projects automatically
4. **Add authentication** - Secure with API keys
5. **Deploy to cloud** - AWS, Azure, or GCP

---
