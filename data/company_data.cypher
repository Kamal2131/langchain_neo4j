// Sample Company Knowledge Base Data
// Realistic company structure with employees, projects, skills, and relationships

// ============================================================
// DEPARTMENTS
// ============================================================

CREATE (eng:Department {
    name: 'Engineering',
    description: 'Software development and infrastructure',
    location: 'San Francisco'
});

CREATE (product:Department {
    name: 'Product',
    description: 'Product management and design',
    location: 'San Francisco'
});

CREATE (marketing:Department {
    name: 'Marketing',
    description: 'Marketing and brand management',
    location: 'New York'
});

CREATE (sales:Department {
    name: 'Sales',
    description: 'Sales and business development',
    location: 'New York'
});

// ============================================================
// EMPLOYEES
// ============================================================

CREATE (john:Employee {
    email: 'john.doe@company.com',
    name: 'John Doe',
    title: 'Senior Software Engineer',
    hire_date: date('2020-01-15'),
    bio: 'Full-stack engineer with expertise in Python and React. Led migration to microservices architecture.',
    phone: '+1-415-555-0101',
    level: 'Senior'
});

CREATE (sarah:Employee {
    email: 'sarah.smith@company.com',
    name: 'Sarah Smith',
    title: 'Product Manager',
    hire_date: date('2021-03-20'),
    bio: 'Product leader with 8 years experience. Launched 5+ successful SaaS products.',
    phone: '+1-415-555-0102',
    level: 'Senior'
});

CREATE (mike:Employee {
    email: 'mike.jones@company.com',
    name: 'Mike Jones',
    title: 'DevOps Engineer',
    hire_date: date('2019-07-10'),
    bio: 'Infrastructure expert specializing in Kubernetes and AWS. Reduced deployment time by 70%.',
    phone: '+1-415-555-0103',
    level: 'Staff'
});

CREATE (lisa:Employee {
    email: 'lisa.wang@company.com',
    name: 'Lisa Wang',
    title: 'UX Designer',
    hire_date: date('2022-05-01'),
    bio: 'User experience designer passionate about accessible design. Previously at Google.',
    phone: '+1-415-555-0104',
    level: 'Mid'
});

CREATE (david:Employee {
    email: 'david.chen@company.com',
    name: 'David Chen',
    title: 'Engineering Manager',
    hire_date: date('2018-09-15'),
    bio: 'Engineering leader managing team of 10 engineers. Expert in system design and mentorship.',
    phone: '+1-415-555-0105',
    level: 'Manager'
});

CREATE (emily:Employee {
    email: 'emily.brown@company.com',
    name: 'Emily Brown',
    title: 'Marketing Director',
    hire_date: date('2020-11-01'),
    bio: 'Growth marketing expert. Scaled user base from 10K to 500K users.',
    phone: '+1-212-555-0106',
    level: 'Director'
});

CREATE (alex:Employee {
    email: 'alex.kumar@company.com',
    name: 'Alex Kumar',
    title: 'Data Scientist',
    hire_date: date('2021-08-15'),
    bio: 'ML engineer specializing in recommendation systems and NLP.',
    phone: '+1-415-555-0107',
    level: 'Senior'
});

CREATE (jen:Employee {
    email: 'jennifer.lee@company.com',
    name: 'Jennifer Lee',
    title: 'Sales Manager',
    hire_date: date('2019-04-20'),
    bio: 'Enterprise sales leader. Closed $10M+ in annual contracts.',
    phone: '+1-212-555-0108',
    level: 'Manager'
});

// ============================================================
// SKILLS
// ============================================================

CREATE (python:Skill {name: 'Python', category: 'Programming Language'});
CREATE (javascript:Skill {name: 'JavaScript', category: 'Programming Language'});
CREATE (react:Skill {name: 'React', category: 'Frontend Framework'});
CREATE (django:Skill {name: 'Django', category: 'Backend Framework'});
CREATE (fastapi:Skill {name: 'FastAPI', category: 'Backend Framework'});
CREATE (aws:Skill {name: 'AWS', category: 'Cloud Platform'});
CREATE (kubernetes:Skill {name: 'Kubernetes', category: 'DevOps'});
CREATE (docker:Skill {name: 'Docker', category: 'DevOps'});
CREATE (postgresql:Skill {name: 'PostgreSQL', category: 'Database'});
CREATE (mongodb:Skill {name: 'MongoDB', category: 'Database'});
CREATE (ml:Skill {name: 'Machine Learning', category: 'AI/ML'});
CREATE (tensorflow:Skill {name: 'TensorFlow', category: 'AI/ML'});
CREATE (figma:Skill {name: 'Figma', category: 'Design Tool'});
CREATE (productStrategy:Skill {name: 'Product Strategy', category: 'Soft Skill'});
CREATE (agile:Skill {name: 'Agile', category: 'Methodology'});
CREATE (leadership:Skill {name: 'Leadership', category: 'Soft Skill'});
CREATE (sales:Skill {name: 'Enterprise Sales', category: 'Business'});
CREATE (marketing:Skill {name: 'Growth Marketing', category: 'Business'});

// ============================================================
// PROJECTS
// ============================================================

CREATE (mobileApp:Project {
    project_id: 'PRJ001',
    name: 'Mobile App Redesign',
    status: 'active',
    start_date: date('2024-01-15'),
    description: 'Complete redesign of iOS and Android mobile applications with new UI/UX',
    budget: 500000,
    priority: 'High'
});

CREATE (paymentAPI:Project {
    project_id: 'PRJ002',
    name: 'Payment API v2',
    status: 'completed',
    start_date: date('2023-06-15'),
    end_date: date('2024-01-10'),
    description: 'New payment processing API with support for multiple payment providers',
    budget: 300000,
    priority: 'High'
});

CREATE (dashboard:Project {
    project_id: 'PRJ003',
    name: 'Customer Dashboard',
    status: 'active',
    start_date: date('2024-03-01'),
    description: 'Self-service customer portal with analytics and reporting',
    budget: 400000,
    priority: 'Medium'
});

CREATE (mlModel:Project {
    project_id: 'PRJ004',
    name: 'Recommendation Engine',
    status: 'active',
    start_date: date('2023-11-01'),
    description: 'ML-based product recommendation system',
    budget: 600000,
    priority: 'High'
});

CREATE (infrastructure:Project {
    project_id: 'PRJ005',
    name: 'Infrastructure Modernization',
    status: 'planning',
    start_date: date('2024-04-01'),
    description: 'Migration to Kubernetes and cloud-native architecture',
    budget: 800000,
    priority: 'High'
});

// ============================================================
// DOCUMENTS
// ============================================================

CREATE (apiDoc:Document {
    doc_id: 'DOC001',
    title: 'Payment API Documentation',
    type: 'API Documentation',
    url: 'https://docs.company.com/payment-api',
    created_date: date('2023-12-15'),
    summary: 'Complete API reference for Payment API v2',
    content: 'Comprehensive documentation covering authentication, endpoints, webhooks, and error handling'
});

CREATE (designSystem:Document {
    doc_id: 'DOC002',
    title: 'Design System Guide',
    type: 'Design Documentation',
    url: 'https://docs.company.com/design-system',
    created_date: date('2024-01-20'),
    summary: 'Company-wide design system and UI component library',
    content: 'Guidelines for typography, colors, spacing, and reusable components'
});

CREATE (onboarding:Document {
    doc_id: 'DOC003',
    title: 'Engineering Onboarding',
    type: 'Process Documentation',
    url: 'https://docs.company.com/onboarding',
    created_date: date('2023-08-10'),
    summary: 'Step-by-step guide for new engineering hires',
    content: 'Setup instructions, team introductions, and first week tasks'
});

// ============================================================
// RELATIONSHIPS: Employee -> Department
// ============================================================

MATCH (john:Employee {email: 'john.doe@company.com'}), (eng:Department {name: 'Engineering'})
CREATE (john)-[:WORKS_IN]->(eng);

MATCH (sarah:Employee {email: 'sarah.smith@company.com'}), (product:Department {name: 'Product'})
CREATE (sarah)-[:WORKS_IN]->(product);

MATCH (mike:Employee {email: 'mike.jones@company.com'}), (eng:Department {name: 'Engineering'})
CREATE (mike)-[:WORKS_IN]->(eng);

MATCH (lisa:Employee {email: 'lisa.wang@company.com'}), (product:Department {name: 'Product'})
CREATE (lisa)-[:WORKS_IN]->(product);

MATCH (david:Employee {email: 'david.chen@company.com'}), (eng:Department {name: 'Engineering'})
CREATE (david)-[:WORKS_IN]->(eng);

MATCH (emily:Employee {email: 'emily.brown@company.com'}), (marketing:Department {name: 'Marketing'})
CREATE (emily)-[:WORKS_IN]->(marketing);

MATCH (alex:Employee {email: 'alex.kumar@company.com'}), (eng:Department {name: 'Engineering'})
CREATE (alex)-[:WORKS_IN]->(eng);

MATCH (jen:Employee {email: 'jennifer.lee@company.com'}), (sales:Department {name: 'Sales'})
CREATE (jen)-[:WORKS_IN]->(sales);

// ============================================================
// RELATIONSHIPS: Employee -> Skill
// ============================================================

MATCH (john:Employee {email: 'john.doe@company.com'}), (python:Skill {name: 'Python'})
CREATE (john)-[:HAS_SKILL {proficiency: 'Expert', years: 8}]->(python);

MATCH (john:Employee {email: 'john.doe@company.com'}), (react:Skill {name: 'React'})
CREATE (john)-[:HAS_SKILL {proficiency: 'Advanced', years: 5}]->(react);

MATCH (john:Employee {email: 'john.doe@company.com'}), (aws:Skill {name: 'AWS'})
CREATE (john)-[:HAS_SKILL {proficiency: 'Advanced', years: 6}]->(aws);

MATCH (mike:Employee {email: 'mike.jones@company.com'}), (kubernetes:Skill {name: 'Kubernetes'})
CREATE (mike)-[:HAS_SKILL {proficiency: 'Expert', years: 5}]->(kubernetes);

MATCH (mike:Employee {email: 'mike.jones@company.com'}), (aws:Skill {name: 'AWS'})
CREATE (mike)-[:HAS_SKILL {proficiency: 'Expert', years: 7}]->(aws);

MATCH (mike:Employee {email: 'mike.jones@company.com'}), (docker:Skill {name: 'Docker'})
CREATE (mike)-[:HAS_SKILL {proficiency: 'Expert', years: 6}]->(docker);

MATCH (sarah:Employee {email: 'sarah.smith@company.com'}), (productStrategy:Skill {name: 'Product Strategy'})
CREATE (sarah)-[:HAS_SKILL {proficiency: 'Expert', years: 8}]->(productStrategy);

MATCH (sarah:Employee {email: 'sarah.smith@company.com'}), (agile:Skill {name: 'Agile'})
CREATE (sarah)-[:HAS_SKILL {proficiency: 'Expert', years: 7}]->(agile);

MATCH (lisa:Employee {email: 'lisa.wang@company.com'}), (figma:Skill {name: 'Figma'})
CREATE (lisa)-[:HAS_SKILL {proficiency: 'Expert', years: 4}]->(figma);

MATCH (alex:Employee {email: 'alex.kumar@company.com'}), (ml:Skill {name: 'Machine Learning'})
CREATE (alex)-[:HAS_SKILL {proficiency: 'Expert', years: 5}]->(ml);

MATCH (alex:Employee {email: 'alex.kumar@company.com'}), (python:Skill {name: 'Python'})
CREATE (alex)-[:HAS_SKILL {proficiency: 'Expert', years: 6}]->(python);

MATCH (alex:Employee {email: 'alex.kumar@company.com'}), (tensorflow:Skill {name: 'TensorFlow'})
CREATE (alex)-[:HAS_SKILL {proficiency: 'Advanced', years: 4}]->(tensorflow);

MATCH (david:Employee {email: 'david.chen@company.com'}), (leadership:Skill {name: 'Leadership'})
CREATE (david)-[:HAS_SKILL {proficiency: 'Expert', years: 6}]->(leadership);

MATCH (emily:Employee {email: 'emily.brown@company.com'}), (marketing:Skill {name: 'Growth Marketing'})
CREATE (emily)-[:HAS_SKILL {proficiency: 'Expert', years: 9}]->(marketing);

MATCH (jen:Employee {email: 'jennifer.lee@company.com'}), (sales:Skill {name: 'Enterprise Sales'})
CREATE (jen)-[:HAS_SKILL {proficiency: 'Expert', years: 10}]->(sales);

// ============================================================
// RELATIONSHIPS: Employee -> Project
// ============================================================

MATCH (john:Employee {email: 'john.doe@company.com'}), (mobileApp:Project {project_id: 'PRJ001'})
CREATE (john)-[:WORKS_ON {role: 'Tech Lead', hours_per_week: 32, start_date: date('2024-01-15')}]->(mobileApp);

MATCH (john:Employee {email: 'john.doe@company.com'}), (paymentAPI:Project {project_id: 'PRJ002'})
CREATE (john)-[:WORKS_ON {role: 'Senior Developer', hours_per_week: 40, start_date: date('2023-06-15'), end_date: date('2024-01-10')}]->(paymentAPI);

MATCH (sarah:Employee {email: 'sarah.smith@company.com'}), (mobileApp:Project {project_id: 'PRJ001'})
CREATE (sarah)-[:WORKS_ON {role: 'Product Owner', hours_per_week: 20, start_date: date('2024-01-15')}]->(mobileApp);

MATCH (sarah:Employee {email: 'sarah.smith@company.com'}), (dashboard:Project {project_id: 'PRJ003'})
CREATE (sarah)-[:WORKS_ON {role: 'Product Manager', hours_per_week: 20, start_date: date('2024-03-01')}]->(dashboard);

MATCH (mike:Employee {email: 'mike.jones@company.com'}), (infrastructure:Project {project_id: 'PRJ005'})
CREATE (mike)-[:WORKS_ON {role: 'DevOps Lead', hours_per_week: 40, start_date: date('2024-04-01')}]->(infrastructure);

MATCH (mike:Employee {email: 'mike.jones@company.com'}), (paymentAPI:Project {project_id: 'PRJ002'})
CREATE (mike)-[:WORKS_ON {role: 'Infrastructure', hours_per_week: 15, start_date: date('2023-06-15'), end_date: date('2024-01-10')}]->(paymentAPI);

MATCH (lisa:Employee {email: 'lisa.wang@company.com'}), (mobileApp:Project {project_id: 'PRJ001'})
CREATE (lisa)-[:WORKS_ON {role: 'Lead Designer', hours_per_week: 30, start_date: date('2024-01-15')}]->(mobileApp);

MATCH (lisa:Employee {email: 'lisa.wang@company.com'}), (dashboard:Project {project_id: 'PRJ003'})
CREATE (lisa)-[:WORKS_ON {role: 'UX Designer', hours_per_week: 10, start_date: date('2024-03-01')}]->(dashboard);

MATCH (alex:Employee {email: 'alex.kumar@company.com'}), (mlModel:Project {project_id: 'PRJ004'})
CREATE (alex)-[:WORKS_ON {role: 'ML Engineer', hours_per_week: 40, start_date: date('2023-11-01')}]->(mlModel);

MATCH (david:Employee {email: 'david.chen@company.com'}), (mobileApp:Project {project_id: 'PRJ001'})
CREATE (david)-[:MANAGES]->(mobileApp);

MATCH (david:Employee {email: 'david.chen@company.com'}), (infrastructure:Project {project_id: 'PRJ005'})
CREATE (david)-[:MANAGES]->(infrastructure);

// ============================================================
// RELATIONSHIPS: Project -> Skill (Required Skills)
// ============================================================

MATCH (mobileApp:Project {project_id: 'PRJ001'}), (react:Skill {name: 'React'})
CREATE (mobileApp)-[:REQUIRES]->(react);

MATCH (mobileApp:Project {project_id: 'PRJ001'}), (figma:Skill {name: 'Figma'})
CREATE (mobileApp)-[:REQUIRES]->(figma);

MATCH (paymentAPI:Project {project_id: 'PRJ002'}), (python:Skill {name: 'Python'})
CREATE (paymentAPI)-[:REQUIRES]->(python);

MATCH (paymentAPI:Project {project_id: 'PRJ002'}), (fastapi:Skill {name: 'FastAPI'})
CREATE (paymentAPI)-[:REQUIRES]->(fastapi);

MATCH (mlModel:Project {project_id: 'PRJ004'}), (ml:Skill {name: 'Machine Learning'})
CREATE (mlModel)-[:REQUIRES]->(ml);

MATCH (mlModel:Project {project_id: 'PRJ004'}), (python:Skill {name: 'Python'})
CREATE (mlModel)-[:REQUIRES]->(python);

MATCH (infrastructure:Project {project_id: 'PRJ005'}), (kubernetes:Skill {name: 'Kubernetes'})
CREATE (infrastructure)-[:REQUIRES]->(kubernetes);

MATCH (infrastructure:Project {project_id: 'PRJ005'}), (aws:Skill {name: 'AWS'})
CREATE (infrastructure)-[:REQUIRES]->(aws);

// ============================================================
// RELATIONSHIPS: Project -> Document
// ============================================================

MATCH (paymentAPI:Project {project_id: 'PRJ002'}), (apiDoc:Document {doc_id: 'DOC001'})
CREATE (paymentAPI)-[:HAS_DOCUMENT]->(apiDoc);

MATCH (mobileApp:Project {project_id: 'PRJ001'}), (designSystem:Document {doc_id: 'DOC002'})
CREATE (mobileApp)-[:HAS_DOCUMENT]->(designSystem);

// ============================================================
// RELATIONSHIPS: Employee -> Employee (Reporting)
// ============================================================

MATCH (john:Employee {email: 'john.doe@company.com'}), (david:Employee {email: 'david.chen@company.com'})
CREATE (john)-[:REPORTS_TO]->(david);

MATCH (mike:Employee {email: 'mike.jones@company.com'}), (david:Employee {email: 'david.chen@company.com'})
CREATE (mike)-[:REPORTS_TO]->(david);

MATCH (alex:Employee {email: 'alex.kumar@company.com'}), (david:Employee {email: 'david.chen@company.com'})
CREATE (alex)-[:REPORTS_TO]->(david);

MATCH (lisa:Employee {email: 'lisa.wang@company.com'}), (sarah:Employee {email: 'sarah.smith@company.com'})
CREATE (lisa)-[:REPORTS_TO]->(sarah);
