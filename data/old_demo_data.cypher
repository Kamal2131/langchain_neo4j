// Sample Data for Project-Technology-Person Knowledge Graph
// Clear existing data (use with caution!)
// MATCH (n) DETACH DELETE n;

// Create People
CREATE (alice:Person {name: 'Alice Johnson', email: 'alice@example.com', role: 'Full Stack Developer', experience_years: 5})
CREATE (bob:Person {name: 'Bob Smith', email: 'bob@example.com', role: 'Data Scientist', experience_years: 3})
CREATE (charlie:Person {name: 'Charlie Davis', email: 'charlie@example.com', role: 'Backend Developer', experience_years: 4})
CREATE (diana:Person {name: 'Diana Martinez', email: 'diana@example.com', role: 'ML Engineer', experience_years: 6})
CREATE (eve:Person {name: 'Eve Wilson', email: 'eve@example.com', role: 'Frontend Developer', experience_years: 2});

// Create Technologies
CREATE (python:Technology {name: 'Python', category: 'Programming Language', description: 'High-level programming language'})
CREATE (javascript:Technology {name: 'JavaScript', category: 'Programming Language', description: 'Dynamic programming language for web'})
CREATE (react:Technology {name: 'React', category: 'Framework', description: 'JavaScript library for building UIs'})
CREATE (django:Technology {name: 'Django', category: 'Framework', description: 'Python web framework'})
CREATE (fastapi:Technology {name: 'FastAPI', category: 'Framework', description: 'Modern Python API framework'})
CREATE (tensorflow:Technology {name: 'TensorFlow', category: 'Library', description: 'Machine learning framework'})
CREATE (postgres:Technology {name: 'PostgreSQL', category: 'Database', description: 'Relational database system'})
CREATE (neo4j:Technology {name: 'Neo4j', category: 'Database', description: 'Graph database'})
CREATE (docker:Technology {name: 'Docker', category: 'DevOps', description: 'Containerization platform'})
CREATE (kubernetes:Technology {name: 'Kubernetes', category: 'DevOps', description: 'Container orchestration'});

// Create Projects
CREATE (chatbot:Project {name: 'AI Chatbot', status: 'Active', description: 'Intelligent customer support chatbot', start_date: date('2023-06-01')})
CREATE (dashboard:Project {name: 'Analytics Dashboard', status: 'Active', description: 'Real-time data visualization platform', start_date: date('2023-08-15')})
CREATE (api:Project {name: 'REST API Service', status: 'Completed', description: 'Microservices API backend', start_date: date('2023-03-01'), end_date: date('2023-09-30')})
CREATE (ml_model:Project {name: 'Recommendation Engine', status: 'Active', description: 'ML-based product recommendations', start_date: date('2023-07-01')})
CREATE (webapp:Project {name: 'E-commerce Platform', status: 'Planning', description: 'Full-stack e-commerce solution', start_date: date('2023-10-01')});

// Create WORKED_ON relationships (Person -> Project)
MATCH (alice:Person {name: 'Alice Johnson'}), (chatbot:Project {name: 'AI Chatbot'})
CREATE (alice)-[:WORKED_ON {role: 'Lead Developer', hours: 320}]->(chatbot);

MATCH (alice:Person {name: 'Alice Johnson'}), (webapp:Project {name: 'E-commerce Platform'})
CREATE (alice)-[:WORKED_ON {role: 'Full Stack Developer', hours: 120}]->(webapp);

MATCH (bob:Person {name: 'Bob Smith'}), (chatbot:Project {name: 'AI Chatbot'})
CREATE (bob)-[:WORKED_ON {role: 'ML Engineer', hours: 280}]->(chatbot);

MATCH (bob:Person {name: 'Bob Smith'}), (ml_model:Project {name: 'Recommendation Engine'})
CREATE (bob)-[:WORKED_ON {role: 'Lead Data Scientist', hours: 400}]->(ml_model);

MATCH (charlie:Person {name: 'Charlie Davis'}), (api:Project {name: 'REST API Service'})
CREATE (charlie)-[:WORKED_ON {role: 'Backend Developer', hours: 480}]->(api);

MATCH (charlie:Person {name: 'Charlie Davis'}), (dashboard:Project {name: 'Analytics Dashboard'})
CREATE (charlie)-[:WORKED_ON {role: 'Backend Developer', hours: 200}]->(dashboard);

MATCH (diana:Person {name: 'Diana Martinez'}), (ml_model:Project {name: 'Recommendation Engine'})
CREATE (diana)-[:WORKED_ON {role: 'Senior ML Engineer', hours: 450}]->(ml_model);

MATCH (diana:Person {name: 'Diana Martinez'}), (chatbot:Project {name: 'AI Chatbot'})
CREATE (diana)-[:WORKED_ON {role: 'ML Consultant', hours: 80}]->(chatbot);

MATCH (eve:Person {name: 'Eve Wilson'}), (dashboard:Project {name: 'Analytics Dashboard'})
CREATE (eve)-[:WORKED_ON {role: 'Frontend Developer', hours: 300}]->(dashboard);

MATCH (eve:Person {name: 'Eve Wilson'}), (webapp:Project {name: 'E-commerce Platform'})
CREATE (eve)-[:WORKED_ON {role: 'UI Developer', hours: 150}]->(webapp);

// Create USES relationships (Project -> Technology)
MATCH (chatbot:Project {name: 'AI Chatbot'}), (python:Technology {name: 'Python'})
CREATE (chatbot)-[:USES {purpose: 'Backend logic and ML'}]->(python);

MATCH (chatbot:Project {name: 'AI Chatbot'}), (fastapi:Technology {name: 'FastAPI'})
CREATE (chatbot)-[:USES {purpose: 'API framework'}]->(fastapi);

MATCH (chatbot:Project {name: 'AI Chatbot'}), (tensorflow:Technology {name: 'TensorFlow'})
CREATE (chatbot)-[:USES {purpose: 'NLP model'}]->(tensorflow);

MATCH (dashboard:Project {name: 'Analytics Dashboard'}), (react:Technology {name: 'React'})
CREATE (dashboard)-[:USES {purpose: 'Frontend UI'}]->(react);

MATCH (dashboard:Project {name: 'Analytics Dashboard'}), (javascript:Technology {name: 'JavaScript'})
CREATE (dashboard)-[:USES {purpose: 'Frontend logic'}]->(javascript);

MATCH (dashboard:Project {name: 'Analytics Dashboard'}), (python:Technology {name: 'Python'})
CREATE (dashboard)-[:USES {purpose: 'Data processing'}]->(python);

MATCH (dashboard:Project {name: 'Analytics Dashboard'}), (postgres:Technology {name: 'PostgreSQL'})
CREATE (dashboard)-[:USES {purpose: 'Data storage'}]->(postgres);

MATCH (api:Project {name: 'REST API Service'}), (python:Technology {name: 'Python'})
CREATE (api)-[:USES {purpose: 'Backend development'}]->(python);

MATCH (api:Project {name: 'REST API Service'}), (django:Technology {name: 'Django'})
CREATE (api)-[:USES {purpose: 'Web framework'}]->(django);

MATCH (api:Project {name: 'REST API Service'}), (docker:Technology {name: 'Docker'})
CREATE (api)-[:USES {purpose: 'Containerization'}]->(docker);

MATCH (ml_model:Project {name: 'Recommendation Engine'}), (python:Technology {name: 'Python'})
CREATE (ml_model)-[:USES {purpose: 'ML development'}]->(python);

MATCH (ml_model:Project {name: 'Recommendation Engine'}), (tensorflow:Technology {name: 'TensorFlow'})
CREATE (ml_model)-[:USES {purpose: 'Deep learning'}]->(tensorflow);

MATCH (ml_model:Project {name: 'Recommendation Engine'}), (postgres:Technology {name: 'PostgreSQL'})
CREATE (ml_model)-[:USES {purpose: 'User data storage'}]->(postgres);

MATCH (webapp:Project {name: 'E-commerce Platform'}), (react:Technology {name: 'React'})
CREATE (webapp)-[:USES {purpose: 'Frontend framework'}]->(react);

MATCH (webapp:Project {name: 'E-commerce Platform'}), (python:Technology {name: 'Python'})
CREATE (webapp)-[:USES {purpose: 'Backend services'}]->(python);

MATCH (webapp:Project {name: 'E-commerce Platform'}), (postgres:Technology {name: 'PostgreSQL'})
CREATE (webapp)-[:USES {purpose: 'Database'}]->(postgres);

MATCH (webapp:Project {name: 'E-commerce Platform'}), (docker:Technology {name: 'Docker'})
CREATE (webapp)-[:USES {purpose: 'Deployment'}]->(docker);
