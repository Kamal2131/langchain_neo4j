"""
Generate realistic fake data for Tech Company Knowledge Base.
Creates 1000+ entities with meaningful relationships.
"""

import random
from datetime import datetime, timedelta
from faker import Faker
import json

fake = Faker()
random.seed(42)  # For reproducibility

# ============================================================
# CONFIGURATION
# ============================================================

NUM_EMPLOYEES = 100
NUM_PROJECTS = 50
NUM_CLIENTS = 20
NUM_DEPARTMENTS = 8
NUM_DOCUMENTS = 100

# Real tech skills by category
TECH_SKILLS = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++", 
        "C#", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R"
    ],
    "Frontend": [
        "React", "Vue.js", "Angular", "Next.js", "Svelte", "Redux", 
        "Tailwind CSS", "Material-UI", "Bootstrap", "Webpack"
    ],
    "Backend": [
        "Node.js", "Django", "FastAPI", "Flask", "Spring Boot", "Express.js",
        "Ruby on Rails", "ASP.NET", "Laravel", "NestJS"
    ],
    "Databases": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
        "Neo4j", "Cassandra", "DynamoDB", "SQLite"
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform",
        "Jenkins", "GitLab CI", "GitHub Actions", "Ansible"
    ],
    "Data & ML": [
        "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
        "Apache Spark", "Airflow", "Kafka", "Hadoop"
    ],
    "Mobile": [
        "React Native", "Flutter", "iOS Development", "Android Development",
        "SwiftUI", "Jetpack Compose"
    ],
    "Testing & Quality": [
        "Jest", "Pytest", "Selenium", "Cypress", "JUnit", "Postman"
    ],
    "Soft Skills": [
        "Leadership", "Agile", "Scrum", "Product Management",
        "UI/UX Design", "Technical Writing", "Public Speaking"
    ]
}

# Realistic departments
DEPARTMENTS = [
    {"name": "Engineering", "location": "San Francisco", "budget": 5000000},
    {"name": "Product", "location": "San Francisco", "budget": 2000000},
    {"name": "Design", "location": "New York", "budget": 1500000},
    {"name": "Data Science", "location": "Austin", "budget": 3000000},
    {"name": "DevOps", "location": "Seattle", "budget": 2500000},
    {"name": "Marketing", "location": "New York", "budget": 2000000},
    {"name": "Sales", "location": "Chicago", "budget": 3000000},
    {"name": "Customer Success", "location": "Remote", "budget": 1000000},
]

# Job titles by department
JOB_TITLES = {
    "Engineering": [
        "Senior Software Engineer", "Software Engineer", "Principal Engineer",
        "Engineering Manager", "Tech Lead", "Staff Engineer", "Backend Engineer",
        "Frontend Engineer", "Full Stack Engineer"
    ],
    "Product": [
        "Product Manager", "Senior Product Manager", "Product Director",
        "Product Owner", "VP of Product"
    ],
    "Design": [
        "UX Designer", "UI Designer", "Product Designer", "Design Lead",
        "Creative Director", "UX Researcher"
    ],
    "Data Science": [
        "Data Scientist", "ML Engineer", "Data Engineer", "Analytics Lead",
        "Research Scientist", "AI Engineer"
    ],
    "DevOps": [
        "DevOps Engineer", "Site Reliability Engineer", "Platform Engineer",
        "Infrastructure Engineer", "Cloud Architect"
    ],
    "Marketing": [
        "Marketing Manager", "Growth Marketing", "Content Strategist",
        "Digital Marketing", "Brand Manager"
    ],
    "Sales": [
        "Account Executive", "Sales Manager", "Business Development",
        "Sales Director", "Enterprise Sales"
    ],
    "Customer Success": [
        "Customer Success Manager", "Support Engineer", "Account Manager"
    ]
}

# Project types and statuses
PROJECT_TYPES = [
    "Web Application", "Mobile App", "API Service", "Infrastructure",
    "Data Pipeline", "ML Model", "Internal Tool", "Customer Portal",
    "Analytics Platform", "Integration"
]

PROJECT_STATUSES = ["planning", "active", "on-hold", "completed", "cancelled"]

# Client industries
CLIENT_INDUSTRIES = [
    "FinTech", "HealthTech", "E-commerce", "EdTech", "SaaS",
    "Entertainment", "Retail", "Manufacturing", "Logistics", "Real Estate"
]

# Document types
DOCUMENT_TYPES = [
    "API Documentation", "Architecture Design", "User Guide",
    "Technical Specification", "Runbook", "Onboarding Guide",
    "Security Policy", "Code Review Guidelines", "Best Practices"
]


def generate_employees():
    """Generate realistic employee data."""
    employees = []
    
    for i in range(NUM_EMPLOYEES):
        dept = random.choice(DEPARTMENTS)
        dept_name = dept["name"]
        title = random.choice(JOB_TITLES[dept_name])
        
        # Hire date between 6 months and 5 years ago
        days_ago = random.randint(180, 1825)
        hire_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Salary based on title
        if "Senior" in title or "Lead" in title or "Manager" in title:
            salary = random.randint(120000, 180000)
            level = "Senior"
        elif "Principal" in title or "Director" in title or "VP" in title:
            salary = random.randint(180000, 250000)
            level = "Principal"
        elif "Staff" in title:
            salary = random.randint(150000, 200000)
            level = "Staff"
        else:
            salary = random.randint(80000, 120000)
            level = "Mid"
        
        employee = {
            "id": f"EMP{i+1:04d}",
            "name": fake.name(),
            "email": fake.email(),
            "title": title,
            "department": dept_name,
            "location": dept["location"],
            "hire_date": hire_date,
            "salary": salary,
            "level": level,
            "bio": fake.text(max_nb_chars=200),
            "phone": fake.phone_number()
        }
        employees.append(employee)
    
    return employees


def generate_skills():
    """Generate all available skills."""
    skills = []
    skill_id = 1
    
    for category, skill_list in TECH_SKILLS.items():
        for skill_name in skill_list:
            skills.append({
                "id": f"SKILL{skill_id:04d}",
                "name": skill_name,
                "category": category
            })
            skill_id += 1
    
    return skills


def generate_projects():
    """Generate realistic project data."""
    projects = []
    
    for i in range(NUM_PROJECTS):
        proj_type = random.choice(PROJECT_TYPES)
        status = random.choice(PROJECT_STATUSES)
        
        # Start date between 2 years ago and 6 months from now
        days_offset = random.randint(-180, 730)
        start_date = (datetime.now() - timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        # Budget between 50K and 2M
        budget = random.randint(50000, 2000000)
        
        # Priority
        priority = random.choice(["High", "Medium", "Low"])
        
        # Project name
        adjective = random.choice(["Smart", "Next-Gen", "Advanced", "Modern", "Cloud", "AI-Powered"])
        noun = random.choice(["Platform", "System", "Portal", "Dashboard", "Engine", "Hub"])
        project_name = f"{adjective} {noun} {random.choice(['v2', 'Pro', 'Enterprise', ''])}"
        
        project = {
            "id": f"PRJ{i+1:04d}",
            "name": project_name.strip(),
            "type": proj_type,
            "status": status,
            "start_date": start_date,
            "budget": budget,
            "priority": priority,
            "description": fake.text(max_nb_chars=300)
        }
        
        # Add end date if completed
        if status == "completed":
            end_days = random.randint(30, 365)
            end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=end_days)).strftime("%Y-%m-%d")
            project["end_date"] = end_date
        
        projects.append(project)
    
    return projects


def generate_clients():
    """Generate client/customer data."""
    clients = []
    
    for i in range(NUM_CLIENTS):
        industry = random.choice(CLIENT_INDUSTRIES)
        company_name = fake.company()
        
        # Revenue
        revenue = random.randint(1000000, 100000000)
        
        client = {
            "id": f"CLI{i+1:04d}",
            "name": company_name,
            "industry": industry,
            "revenue": revenue,
            "country": fake.country(),
            "website": fake.url(),
            "contract_start": (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d")
        }
        clients.append(client)
    
    return clients


def generate_documents():
    """Generate documentation."""
    documents = []
    
    for i in range(NUM_DOCUMENTS):
        doc_type = random.choice(DOCUMENT_TYPES)
        
        document = {
            "id": f"DOC{i+1:04d}",
            "title": f"{doc_type} - {fake.catch_phrase()}",
            "type": doc_type,
            "url": f"https://docs.company.com/{fake.slug()}",
            "created_date": (datetime.now() - timedelta(days=random.randint(1, 730))).strftime("%Y-%m-%d"),
            "summary": fake.text(max_nb_chars=200),
            "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 20)}"
        }
        documents.append(document)
    
    return documents


def generate_relationships(employees, skills, projects, clients, documents):
    """Generate relationships between entities."""
    relationships = {
        "employee_skills": [],
        "employee_projects": [],
        "project_clients": [],
        "project_skills": [],
        "project_documents": [],
        "employee_reports_to": []
    }
    
    # Employee skills (each employee has 3-8 skills)
    for emp in employees:
        num_skills = random.randint(3, 8)
        emp_skills = random.sample(skills, num_skills)
        
        for skill in emp_skills:
            proficiency = random.choice(["Beginner", "Intermediate", "Advanced", "Expert"])
            years = random.randint(1, 10)
            
            relationships["employee_skills"].append({
                "employee_id": emp["id"],
                "skill_id": skill["id"],
                "proficiency": proficiency,
                "years": years
            })
    
    # Employee projects (each project has 3-10 team members)
    for proj in projects:
        team_size = random.randint(3, 10)
        team = random.sample(employees, min(team_size, len(employees)))
        
        for i, emp in enumerate(team):
            role = random.choice([
                "Tech Lead", "Developer", "Designer", "QA Engineer",
                "Product Manager", "DevOps Engineer", "Data Scientist"
            ])
            hours_per_week = random.randint(10, 40)
            
            relationships["employee_projects"].append({
                "employee_id": emp["id"],
                "project_id": proj["id"],
                "role": role,
                "hours_per_week": hours_per_week
            })
    
    # Project clients (each project has 1 client)
    for proj in projects:
        if random.random() > 0.3:  # 70% of projects have clients
            client = random.choice(clients)
            relationships["project_clients"].append({
                "project_id": proj["id"],
                "client_id": client["id"]
            })
    
    # Project required skills (each project needs 2-6 skills)
    for proj in projects:
        num_skills = random.randint(2, 6)
        proj_skills = random.sample(skills, num_skills)
        
        for skill in proj_skills:
            relationships["project_skills"].append({
                "project_id": proj["id"],
                "skill_id": skill["id"]
            })
    
    # Project documents (each project has 1-5 documents)
    for proj in projects:
        num_docs = random.randint(1, 5)
        proj_docs = random.sample(documents, min(num_docs, len(documents)))
        
        for doc in proj_docs:
            relationships["project_documents"].append({
                "project_id": proj["id"],
                "document_id": doc["id"]
            })
    
    # Employee reporting structure
    managers = [emp for emp in employees if "Manager" in emp["title"] or "Lead" in emp["title"] or "Director" in emp["title"]]
    for emp in employees:
        if emp not in managers and random.random() > 0.2:  # 80% have managers
            manager = random.choice(managers)
            if emp["id"] != manager["id"]:
                relationships["employee_reports_to"].append({
                    "employee_id": emp["id"],
                    "manager_id": manager["id"]
                })
    
    return relationships


def main():
    """Generate all data."""
    print("🎲 Generating realistic tech company data...")
    
    print("\n📊 Generating entities...")
    employees = generate_employees()
    skills = generate_skills()
    projects = generate_projects()
    clients = generate_clients()
    documents = generate_documents()
    
    print(f"  ✓ {len(employees)} employees")
    print(f"  ✓ {len(skills)} skills")
    print(f"  ✓ {len(projects)} projects")
    print(f"  ✓ {len(clients)} clients")
    print(f"  ✓ {len(documents)} documents")
    print(f"  ✓ {len(DEPARTMENTS)} departments")
    
    print("\n🔗 Generating relationships...")
    relationships = generate_relationships(employees, skills, projects, clients, documents)
    
    total_rels = sum(len(v) for v in relationships.values())
    print(f"  ✓ {total_rels} total relationships")
    for rel_type, rels in relationships.items():
        print(f"    - {rel_type}: {len(rels)}")
    
    # Save to JSON files
    print("\n💾 Saving data...")
    data = {
        "employees": employees,
        "skills": skills,
        "projects": projects,
        "clients": clients,
        "documents": documents,
        "departments": DEPARTMENTS,
        "relationships": relationships
    }
    
    with open('data/generated_kb_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Generated {len(employees) + len(skills) + len(projects) + len(clients) + len(documents) + len(DEPARTMENTS)} entities")
    print(f"✅ Generated {total_rels} relationships")
    print("\n📁 Data saved to: data/generated_kb_data.json")


if __name__ == "__main__":
    main()
