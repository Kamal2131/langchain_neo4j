"""
Generate realistic fake data for CSV templates.

This script creates interconnected fake company data for testing
the Neo4j Knowledge Base application.

Usage:
    python scripts/generate_template_data.py
"""

import csv
import random
from pathlib import Path
from datetime import datetime, timedelta

# Output directory
TEMPLATES_DIR = Path(__file__).parent.parent / "data" / "templates"

# Ensure directory exists
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION - Customize these for your needs
# ============================================================

NUM_EMPLOYEES = 2000
NUM_PROJECTS = 200
NUM_CLIENTS = 100

DEPARTMENTS = [
    ("Engineering", "Software development and technical architecture"),
    ("Data Science", "Analytics, machine learning, and AI initiatives"),
    ("DevOps", "Infrastructure, deployment, and site reliability"),
    ("Product", "Product management and strategy"),
    ("Sales", "Revenue generation and customer acquisition"),
    ("Marketing", "Brand awareness and demand generation"),
    ("Design", "User experience and visual design"),
    ("Customer Success", "Client support and retention"),
]

SKILLS_BY_CATEGORY = {
    "Programming": ["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++"],
    "Frontend": ["React", "Vue.js", "Angular", "Next.js", "Tailwind CSS", "HTML/CSS"],
    "Backend": ["Node.js", "Django", "FastAPI", "Spring Boot", "REST API", "GraphQL"],
    "Cloud": ["AWS", "Azure", "GCP", "Terraform", "CloudFormation"],
    "DevOps": ["Docker", "Kubernetes", "CI/CD", "Jenkins", "GitHub Actions", "Ansible"],
    "Database": ["PostgreSQL", "MongoDB", "Redis", "MySQL", "Elasticsearch", "Neo4j"],
    "Data Science": ["Machine Learning", "TensorFlow", "PyTorch", "Pandas", "SQL", "Spark"],
    "Soft Skills": ["Leadership", "Communication", "Agile", "Scrum", "Project Management"],
}

LOCATIONS = ["San Francisco", "New York", "Austin", "Seattle", "Chicago", "Remote"]

LEVELS = ["Junior", "Mid", "Senior", "Staff", "Principal"]

FIRST_NAMES = [
    "Sarah", "Michael", "Emily", "David", "Jessica", "Robert", "Amanda", "James",
    "Lisa", "Kevin", "Jennifer", "Christopher", "Michelle", "Daniel", "Rachel",
    "Brian", "Stephanie", "Andrew", "Nicole", "Jason", "Katherine", "Ryan",
    "Laura", "Mark", "Angela", "Thomas", "Rebecca", "Joshua", "Megan", "William",
    "Emma", "John", "Ashley", "Matthew", "Elizabeth", "Anthony", "Amber", "Joseph",
    "Heather", "Charles", "Samantha", "Steven", "Kelly", "Timothy", "Victoria",
    "Patrick", "Brittany", "Gregory", "Christina", "Benjamin", "Lauren", "Kenneth",
    "Danielle", "Jonathan", "Hannah", "Eric", "Courtney", "Adam", "Kayla", "Brandon",
    "Tiffany", "Justin", "Allison", "Richard", "Alexandra", "Nathan", "Natalie",
    "Scott", "Chelsea", "Tyler", "Melissa", "Aaron", "Lindsay", "Jacob", "Diana",
    "Sean", "Erica", "Ethan", "Maria", "Kyle", "Vanessa", "Peter", "Casey",
    "Luke", "Monica", "Zachary", "Sara", "Paul", "Jamie", "Samuel", "Lindsey",
    "Ian", "Tracy", "Alex", "Veronica", "Connor", "Brenda", "Cole", "Kristen",
    "Cameron", "Kathryn", "Owen", "Crystal", "Dylan", "Bethany", "Hunter", "Alexis"
]

LAST_NAMES = [
    "Chen", "Rodriguez", "Johnson", "Kim", "Martinez", "Thompson", "Wilson", "Brown",
    "Wang", "Patel", "Lee", "Davis", "Garcia", "Anderson", "Taylor", "White",
    "Clark", "Miller", "Harris", "Moore", "Wright", "Scott", "Adams", "Robinson",
    "Turner", "Baker", "Green", "Hill", "King", "Young", "Walker", "Hall",
    "Allen", "Sanchez", "Lopez", "Nelson", "Carter", "Mitchell", "Perez", "Roberts",
    "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Gonzalez",
    "Morris", "Murphy", "Cook", "Rogers", "Morgan", "Peterson", "Cooper", "Reed",
    "Bailey", "Bell", "Gomez", "Kelly", "Howard", "Ward", "Cox", "Diaz",
    "Richardson", "Wood", "Watson", "Brooks", "Bennett", "Gray", "James", "Reyes",
    "Cruz", "Hughes", "Price", "Myers", "Long", "Foster", "Sanders", "Ross",
    "Morales", "Powell", "Sullivan", "Russell", "Ortiz", "Jenkins", "Gutierrez", "Perry",
    "Butler", "Barnes", "Fisher", "Henderson", "Coleman", "Simmons", "Patterson", "Jordan",
    "Reynolds", "Hamilton", "Graham", "Wallace", "Freeman", "Wells", "Webb", "Fox"
]

TITLES_BY_DEPT = {
    "Engineering": [
        ("Junior Software Engineer", "Junior", 75000, 95000),
        ("Software Engineer", "Mid", 95000, 120000),
        ("Senior Software Engineer", "Senior", 120000, 150000),
        ("Staff Engineer", "Staff", 150000, 180000),
        ("Engineering Manager", "Senior", 140000, 170000),
        ("VP of Engineering", "Principal", 180000, 220000),
    ],
    "Data Science": [
        ("Data Analyst", "Junior", 70000, 90000),
        ("Data Scientist", "Mid", 100000, 130000),
        ("Senior Data Scientist", "Senior", 130000, 160000),
        ("ML Engineer", "Mid", 110000, 140000),
        ("Head of Data Science", "Principal", 170000, 210000),
    ],
    "DevOps": [
        ("DevOps Engineer", "Mid", 100000, 130000),
        ("Senior DevOps Engineer", "Senior", 130000, 160000),
        ("DevOps Lead", "Senior", 150000, 180000),
        ("Platform Engineer", "Mid", 105000, 135000),
    ],
    "Product": [
        ("Associate Product Manager", "Junior", 80000, 100000),
        ("Product Manager", "Mid", 110000, 140000),
        ("Senior Product Manager", "Senior", 140000, 170000),
        ("Chief Product Officer", "Principal", 200000, 250000),
    ],
    "Sales": [
        ("Sales Development Rep", "Junior", 55000, 75000),
        ("Account Executive", "Mid", 80000, 120000),
        ("Senior Account Executive", "Senior", 120000, 160000),
        ("Sales Director", "Principal", 160000, 200000),
    ],
    "Marketing": [
        ("Marketing Coordinator", "Junior", 55000, 70000),
        ("Marketing Manager", "Mid", 85000, 110000),
        ("Content Marketing Manager", "Mid", 80000, 105000),
        ("Marketing Director", "Senior", 140000, 180000),
    ],
    "Design": [
        ("UI Designer", "Mid", 80000, 105000),
        ("Product Designer", "Mid", 90000, 115000),
        ("Senior Product Designer", "Senior", 115000, 145000),
        ("Design Lead", "Senior", 135000, 165000),
    ],
    "Customer Success": [
        ("Support Specialist", "Junior", 50000, 65000),
        ("Customer Success Manager", "Mid", 80000, 110000),
        ("Senior CSM", "Senior", 110000, 140000),
        ("VP of Customer Success", "Principal", 160000, 200000),
    ],
}

CLIENT_INDUSTRIES = ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Education", "Media"]

PROJECT_TEMPLATES = [
    ("Platform Modernization", "Complete rebuild of legacy systems into modern microservices architecture", "critical", 500000, 800000),
    ("Mobile App Redesign", "Major redesign of customer mobile application with new features", "high", 250000, 400000),
    ("AI Assistant Integration", "Integrate LLM-powered assistant for automation", "high", 300000, 500000),
    ("Data Lake Migration", "Migrate analytics infrastructure to cloud-native data lake", "high", 400000, 600000),
    ("Security Compliance", "SOC2 and GDPR compliance implementation", "critical", 150000, 250000),
    ("Enterprise SSO", "Single sign-on integration for enterprise customers", "medium", 100000, 200000),
    ("Customer Portal", "Self-service portal with reporting and admin features", "medium", 200000, 350000),
    ("API Gateway", "New API gateway with rate limiting and developer portal", "medium", 150000, 250000),
    ("Real-time Analytics", "Live dashboards with real-time metrics and alerting", "high", 250000, 400000),
    ("Marketplace Platform", "Third-party app marketplace for partner ecosystem", "medium", 350000, 550000),
    ("Payment Integration", "New payment processor integration with multi-currency support", "high", 200000, 350000),
    ("Search Optimization", "Elasticsearch-based search with ML ranking", "medium", 180000, 300000),
    ("Cloud Migration", "Migrate on-premise infrastructure to cloud", "critical", 600000, 900000),
    ("DevOps Pipeline", "Automated CI/CD pipeline implementation", "high", 150000, 250000),
    ("Monitoring System", "Comprehensive monitoring and alerting platform", "high", 200000, 350000),
    ("Documentation Portal", "Developer documentation and API reference site", "low", 80000, 150000),
    ("Performance Optimization", "System-wide performance improvements", "medium", 180000, 280000),
    ("Data Warehouse", "Enterprise data warehouse implementation", "high", 450000, 700000),
    ("User Management", "Centralized user and access management system", "medium", 200000, 350000),
    ("Reporting Dashboard", "Executive reporting and analytics dashboard", "medium", 150000, 250000),
    ("Integration Hub", "Third-party API integration platform", "high", 280000, 450000),
    ("Workflow Automation", "Business process automation platform", "medium", 220000, 380000),
    ("Notification System", "Multi-channel notification service", "medium", 120000, 200000),
    ("Content Management", "Enterprise content management system", "medium", 250000, 400000),
    ("E-commerce Platform", "Online commerce and checkout system", "high", 400000, 650000),
    ("Inventory System", "Real-time inventory management", "medium", 180000, 300000),
    ("CRM Integration", "Customer relationship management integration", "high", 220000, 380000),
    ("Chat Platform", "Real-time messaging and collaboration", "medium", 280000, 450000),
    ("Video Conferencing", "Enterprise video meeting solution", "high", 350000, 550000),
    ("File Storage", "Cloud file storage and sharing platform", "medium", 200000, 350000),
]

PROJECT_STATUSES = ["active", "planning", "on-hold", "completed"]


def generate_email(first_name: str, last_name: str) -> str:
    return f"{first_name.lower()}.{last_name.lower()}@techcorp.com"


def generate_phone(location: str) -> str:
    area_codes = {
        "San Francisco": "415", "New York": "212", "Austin": "512",
        "Seattle": "206", "Chicago": "312", "Remote": "555"
    }
    area = area_codes.get(location, "555")
    return f"+1-{area}-555-{random.randint(1000, 9999)}"


def generate_hire_date() -> str:
    days_ago = random.randint(30, 2000)
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d")


def write_csv(filename: str, data: list, fieldnames: list):
    filepath = TEMPLATES_DIR / filename
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"  ✓ Generated {filename} ({len(data)} rows)")


def generate_departments():
    data = [{"name": name, "description": desc} for name, desc in DEPARTMENTS]
    write_csv("departments.csv", data, ["name", "description"])
    return [d["name"] for d in data]


def generate_skills():
    data = []
    for category, skills in SKILLS_BY_CATEGORY.items():
        for skill in skills:
            data.append({"name": skill, "category": category})
    write_csv("skills.csv", data, ["name", "category"])
    return [d["name"] for d in data]


def generate_employees(departments: list):
    employees = []
    used_names = set()
    
    # Ensure at least one person per department
    dept_assignments = departments.copy()
    random.shuffle(dept_assignments)
    
    for i in range(NUM_EMPLOYEES):
        # Generate unique name
        while True:
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            if (first, last) not in used_names:
                used_names.add((first, last))
                break
        
        # Assign department (ensure coverage first, then random)
        if i < len(dept_assignments):
            dept = dept_assignments[i]
        else:
            dept = random.choice(departments)
        
        # Get title and salary range for department
        titles = TITLES_BY_DEPT.get(dept, TITLES_BY_DEPT["Engineering"])
        title, level, min_sal, max_sal = random.choice(titles)
        salary = random.randint(min_sal, max_sal)
        
        location = random.choice(LOCATIONS)
        
        emp = {
            "id": f"EMP{i+1:03d}",
            "name": f"{first} {last}",
            "email": generate_email(first, last),
            "title": title,
            "department": dept,
            "location": location,
            "hire_date": generate_hire_date(),
            "salary": salary,
            "level": level,
            "bio": f"{title} with expertise in {dept.lower()} initiatives",
            "phone": generate_phone(location),
        }
        employees.append(emp)
    
    write_csv("employees.csv", employees, [
        "id", "name", "email", "title", "department", "location",
        "hire_date", "salary", "level", "bio", "phone"
    ])
    return employees


def generate_clients():
    client_prefixes = [
        "Acme", "Global", "United", "Pacific", "Atlantic", "Summit", "Prime", 
        "Apex", "Vertex", "Horizon", "Fusion", "Nexus", "Stellar", "Quantum",
        "Infinity", "Elite", "Crown", "Royal", "Diamond", "Golden"
    ]
    client_suffixes = [
        "Corporation", "Industries", "Solutions", "Systems", "Technologies",
        "Enterprises", "Partners", "Group", "Holdings", "Dynamics"
    ]
    
    clients = []
    for i in range(NUM_CLIENTS):
        prefix = client_prefixes[i % len(client_prefixes)]
        suffix = client_suffixes[i % len(client_suffixes)]
        version = "" if i < len(client_prefixes) else f" {(i // len(client_prefixes)) + 1}"
        
        clients.append({
            "id": f"CLIENT{i+1:04d}",
            "name": f"{prefix} {suffix}{version}",
            "industry": random.choice(CLIENT_INDUSTRIES),
            "revenue": random.randint(5, 500) * 1000000,
            "contract_value": random.randint(100, 1000) * 1000,
        })
    
    write_csv("clients.csv", clients, ["id", "name", "industry", "revenue", "contract_value"])
    return clients


def generate_projects(clients: list):
    projects = []
    
    for i in range(NUM_PROJECTS):
        # Cycle through templates, adding version for duplicates
        template_idx = i % len(PROJECT_TEMPLATES)
        version = (i // len(PROJECT_TEMPLATES)) + 1
        
        name, desc, priority, min_budget, max_budget = PROJECT_TEMPLATES[template_idx]
        
        # Add version suffix if not first cycle
        if version > 1:
            name = f"{name} v{version}"
            desc = f"{desc} (Phase {version})"
        
        status = random.choice(PROJECT_STATUSES)
        
        start_date = datetime.now() - timedelta(days=random.randint(30, 730))
        end_date = start_date + timedelta(days=random.randint(90, 365))
        
        projects.append({
            "project_id": f"PROJ{i+1:04d}",
            "name": name,
            "description": desc,
            "status": status,
            "budget": random.randint(min_budget, max_budget),
            "priority": priority,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d") if status != "planning" else "",
        })
    
    write_csv("projects.csv", projects, [
        "project_id", "name", "description", "status", "budget", "priority", "start_date", "end_date"
    ])
    return projects


def generate_employee_skills(employees: list, skills: list):
    """Assign 3-7 relevant skills to each employee based on their department."""
    dept_skill_map = {
        "Engineering": ["Programming", "Frontend", "Backend", "Database"],
        "Data Science": ["Programming", "Data Science", "Database"],
        "DevOps": ["DevOps", "Cloud", "Programming"],
        "Product": ["Soft Skills"],
        "Sales": ["Soft Skills"],
        "Marketing": ["Soft Skills"],
        "Design": ["Frontend", "Soft Skills"],
        "Customer Success": ["Soft Skills"],
    }
    
    # Build skill lookup by category
    skills_by_cat = {}
    for skill in skills:
        for cat, skill_list in SKILLS_BY_CATEGORY.items():
            if skill in skill_list:
                skills_by_cat.setdefault(cat, []).append(skill)
    
    data = []
    for emp in employees:
        dept = emp["department"]
        relevant_cats = dept_skill_map.get(dept, ["Soft Skills"])
        
        # Get skills from relevant categories
        available_skills = []
        for cat in relevant_cats:
            available_skills.extend(skills_by_cat.get(cat, []))
        
        # Add some general skills too
        available_skills.extend(skills_by_cat.get("Soft Skills", []))
        
        # Assign 3-7 unique skills (but not more than available)
        unique_skills = list(set(available_skills))
        num_skills = min(random.randint(3, 7), len(unique_skills))
        if num_skills > 0 and unique_skills:
            emp_skills = random.sample(unique_skills, num_skills)
        else:
            emp_skills = []
        
        for skill in emp_skills:
            data.append({"employee_id": emp["id"], "skill_name": skill})
    
    write_csv("employee_skills.csv", data, ["employee_id", "skill_name"])
    return data


def generate_employee_projects(employees: list, projects: list):
    """Assign employees to projects based on department relevance."""
    tech_depts = ["Engineering", "Data Science", "DevOps", "Design"]
    
    data = []
    for proj in projects:
        # Each project gets 2-5 team members
        team_size = random.randint(2, 5)
        
        # Prefer tech employees for projects
        tech_employees = [e for e in employees if e["department"] in tech_depts]
        other_employees = [e for e in employees if e["department"] not in tech_depts]
        
        # Mix of tech and non-tech
        team = random.sample(tech_employees, min(team_size - 1, len(tech_employees)))
        if other_employees and team_size > len(team):
            team.extend(random.sample(other_employees, min(1, len(other_employees))))
        
        roles = ["Developer", "Tech Lead", "Designer", "Product Owner", "Contributor"]
        for emp in team:
            data.append({
                "employee_id": emp["id"],
                "project_id": proj["project_id"],
                "role": random.choice(roles),
            })
    
    write_csv("employee_projects.csv", data, ["employee_id", "project_id", "role"])
    return data


def generate_project_clients(projects: list, clients: list):
    """Assign some projects to clients."""
    data = []
    # About 60% of projects have a client
    client_projects = random.sample(projects, int(len(projects) * 0.6))
    
    for proj in client_projects:
        client = random.choice(clients)
        data.append({
            "project_id": proj["project_id"],
            "client_id": client["id"],
        })
    
    write_csv("project_clients.csv", data, ["project_id", "client_id"])
    return data


def generate_reporting_structure(employees: list):
    """Create realistic reporting hierarchy."""
    data = []
    
    # Find managers by level
    principals = [e for e in employees if e["level"] == "Principal"]
    seniors = [e for e in employees if e["level"] in ["Senior", "Staff"]]
    others = [e for e in employees if e["level"] in ["Junior", "Mid"]]
    
    # Seniors report to principals in same department
    for senior in seniors:
        managers = [p for p in principals if p["department"] == senior["department"]]
        if not managers:
            managers = principals
        if managers:
            data.append({
                "employee_id": senior["id"],
                "manager_id": random.choice(managers)["id"],
            })
    
    # Others report to seniors in same department
    for emp in others:
        managers = [s for s in seniors if s["department"] == emp["department"]]
        if not managers:
            managers = seniors
        if managers:
            data.append({
                "employee_id": emp["id"],
                "manager_id": random.choice(managers)["id"],
            })
    
    write_csv("reporting_structure.csv", data, ["employee_id", "manager_id"])
    return data


def main():
    print("=" * 50)
    print("🚀 GENERATING TEMPLATE DATA")
    print("=" * 50)
    print(f"\nOutput directory: {TEMPLATES_DIR}")
    print(f"Generating {NUM_EMPLOYEES} employees, {NUM_PROJECTS} projects, {NUM_CLIENTS} clients\n")
    
    # Generate all data
    departments = generate_departments()
    skills = generate_skills()
    employees = generate_employees(departments)
    clients = generate_clients()
    projects = generate_projects(clients)
    
    # Generate relationships
    print("\n🔗 Generating relationships...")
    generate_employee_skills(employees, skills)
    generate_employee_projects(employees, projects)
    generate_project_clients(projects, clients)
    generate_reporting_structure(employees)
    
    print("\n" + "=" * 50)
    print("✅ All template data generated!")
    print("=" * 50)
    print(f"\nNext steps:")
    print(f"  1. Review the CSV files in: {TEMPLATES_DIR}")
    print(f"  2. Customize the data as needed")
    print(f"  3. Run: python scripts/load_custom_data.py")


if __name__ == "__main__":
    main()
