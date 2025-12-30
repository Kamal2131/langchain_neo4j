# Real-World Use Cases Guide

## 🎯 Transforming Demo to Production

This guide shows how to adapt the Neo4j + LangChain API for real business use cases.

---

## 📚 Use Case 1: Company Knowledge Base

### Business Problem
Employees spend hours searching for information across multiple systems. Need a unified way to query company knowledge.

### Solution: Knowledge Graph
```
(Employee)-[:WORKS_IN]->(Department)-[:OWNS]->(Project)
(Project)-[:USES]->(Technology)
(Project)-[:HAS]->(Document)
(Document)-[:CONTAINS]->(Topic)
(Employee)-[:EXPERT_IN]->(Topic)
```

### Sample Schema

**File: `data/company_kb_schema.cypher`**
```cypher
// Constraints
CREATE CONSTRAINT employee_email IF NOT EXISTS FOR (e:Employee) REQUIRE e.email IS UNIQUE;
CREATE CONSTRAINT department_name IF NOT EXISTS FOR (d:Department) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.project_id IS UNIQUE;
CREATE CONSTRAINT document_id IF NOT EXISTS FOR (doc:Document) REQUIRE doc.doc_id IS UNIQUE;

// Indexes
CREATE INDEX employee_name IF NOT EXISTS FOR (e:Employee) ON (e.name);
CREATE INDEX project_status IF NOT EXISTS FOR (p:Project) ON (p.status);
CREATE INDEX document_type IF NOT EXISTS FOR (doc:Document) ON (doc.type);
```

### Sample Queries Users Would Ask
- "Who is the expert on Python in the Engineering department?"
- "What projects is the Marketing team working on?"
- "Find all documentation about our authentication system"
- "Which employees worked on the AWS migration project?"
- "Show me all active projects in Q4 2024"

### Data Loading from Real Sources

**File: `scripts/load_company_data.py`**
```python
"""
Load company data from various sources.
"""
import pandas as pd
from neo4j import GraphDatabase
from src.core.config import settings

def load_from_hr_system():
    """Load employee data from HR CSV export."""
    employees_df = pd.read_csv('data/employees.csv')
    
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password)
    )
    
    with driver.session() as session:
        for _, row in employees_df.iterrows():
            session.run("""
                MERGE (e:Employee {email: $email})
                SET e.name = $name,
                    e.title = $title,
                    e.hire_date = date($hire_date)
                MERGE (d:Department {name: $department})
                MERGE (e)-[:WORKS_IN]->(d)
            """, 
                email=row['email'],
                name=row['name'],
                title=row['title'],
                hire_date=row['hire_date'],
                department=row['department']
            )
    
    driver.close()
    print(f"✅ Loaded {len(employees_df)} employees")

def load_from_jira():
    """Load project data from Jira API."""
    # Use Jira API to fetch projects
    import requests
    
    jira_url = "https://your-company.atlassian.net"
    headers = {"Authorization": "Bearer YOUR_API_TOKEN"}
    
    response = requests.get(f"{jira_url}/rest/api/3/project", headers=headers)
    projects = response.json()
    
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password)
    )
    
    with driver.session() as session:
        for project in projects:
            session.run("""
                MERGE (p:Project {project_id: $project_id})
                SET p.name = $name,
                    p.key = $key,
                    p.status = $status
            """,
                project_id=project['id'],
                name=project['name'],
                key=project['key'],
                status=project.get('status', 'active')
            )
    
    driver.close()
    print(f"✅ Loaded {len(projects)} projects")

if __name__ == "__main__":
    load_from_hr_system()
    load_from_jira()
```

---

## 📚 Use Case 2: E-commerce Product Recommendation

### Business Problem
Customers need help finding products. Manual search is inefficient.

### Solution: Product Knowledge Graph
```
(Customer)-[:PURCHASED]->(Product)
(Product)-[:IN_CATEGORY]->(Category)
(Product)-[:HAS_TAG]->(Tag)
(Customer)-[:INTERESTED_IN]->(Category)
(Product)-[:SIMILAR_TO]->(Product)
```

### Sample Schema

**File: `data/ecommerce_schema.cypher`**
```cypher
// Product graph
CREATE CONSTRAINT product_sku IF NOT EXISTS FOR (p:Product) REQUIRE p.sku IS UNIQUE;
CREATE CONSTRAINT customer_id IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE;
CREATE CONSTRAINT category_name IF NOT EXISTS FOR (cat:Category) REQUIRE cat.name IS UNIQUE;

CREATE INDEX product_name IF NOT EXISTS FOR (p:Product) ON (p.name);
CREATE INDEX product_price IF NOT EXISTS FOR (p:Product) ON (p.price);
```

### Sample Queries
- "Show me products similar to what I bought last month"
- "What are the best-selling products in Electronics?"
- "Find wireless headphones under $100"
- "Which products are frequently bought together?"
- "Recommend products for customers who bought iPhone 15"

---

## 📚 Use Case 3: Customer Support Knowledge Base

### Business Problem
Support agents waste time searching for solutions. Need instant access to resolution history.

### Solution: Support Ticket Graph
```
(Customer)-[:CREATED]->(Ticket)
(Ticket)-[:TAGGED_AS]->(Issue)
(Ticket)-[:RESOLVED_BY]->(Solution)
(Agent)-[:SOLVED]->(Ticket)
(Product)-[:HAS_ISSUE]->(Issue)
```

### Sample Queries
- "How do we typically resolve login issues?"
- "Which agent is best at handling billing questions?"
- "Show me all unresolved issues for Product X"
- "What solutions worked for similar tickets?"

---

## 🔧 Customization Steps

### Step 1: Design Your Schema

**File: `data/your_domain_schema.cypher`**

```cypher
// 1. Define your node types
CREATE CONSTRAINT your_entity_id IF NOT EXISTS 
  FOR (n:YourEntity) REQUIRE n.id IS UNIQUE;

// 2. Add indexes for common queries
CREATE INDEX your_entity_name IF NOT EXISTS 
  FOR (n:YourEntity) ON (n.name);

// 3. Add text indexes for search
CREATE FULLTEXT INDEX entity_search IF NOT EXISTS
  FOR (n:YourEntity) ON EACH [n.name, n.description];
```

### Step 2: Create Data Loader

**File: `scripts/load_your_data.py`**

```python
"""
Template for loading your domain data.
"""
from neo4j import GraphDatabase
import pandas as pd
import json

class YourDataLoader:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def load_from_csv(self, filepath):
        """Load data from CSV file."""
        df = pd.read_csv(filepath)
        
        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (n:YourEntity {id: $id})
                    SET n.name = $name,
                        n.property = $property
                """, **row.to_dict())
    
    def load_from_api(self, api_endpoint):
        """Load data from REST API."""
        import requests
        response = requests.get(api_endpoint)
        data = response.json()
        
        with self.driver.session() as session:
            for item in data:
                session.run("""
                    MERGE (n:YourEntity {id: $id})
                    SET n += $properties
                """, id=item['id'], properties=item)
    
    def load_from_database(self, db_connection_string):
        """Load from existing SQL database."""
        import sqlalchemy as sa
        engine = sa.create_engine(db_connection_string)
        
        query = "SELECT * FROM your_table"
        df = pd.read_sql(query, engine)
        
        self.load_from_csv(df)  # Reuse CSV loader
    
    def close(self):
        self.driver.close()

# Usage
if __name__ == "__main__":
    loader = YourDataLoader(
        "bolt://localhost:7687",
        "neo4j",
        "password123"
    )
    
    # Choose your data source
    loader.load_from_csv("data/your_data.csv")
    # OR
    # loader.load_from_api("https://api.yourcompany.com/data")
    # OR
    # loader.load_from_database("postgresql://user:pass@localhost/db")
    
    loader.close()
```

### Step 3: Update Configuration

**File: `.env`**
```bash
# Your company settings
APP_NAME=Your Company Knowledge API
ENVIRONMENT=production

# Neo4j
NEO4J_URI=bolt://your-neo4j-server:7687
NEO4J_USERNAME=your_username
NEO4J_PASSWORD=your_secure_password

# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-production-key
OPENAI_MODEL=gpt-4  # Use GPT-4 for better accuracy

# API Security
API_KEY_ENABLED=true
API_KEY=your-secret-api-key-here

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600
```

### Step 4: Add Domain-Specific Endpoints

**File: `src/api/routes/custom.py`**

```python
"""
Custom endpoints for your domain.
"""
from fastapi import APIRouter, HTTPException
from src.services.neo4j_service import neo4j_service

router = APIRouter(prefix="/custom", tags=["Custom"])

@router.get("/top-employees")
async def get_top_employees(limit: int = 10):
    """Get top employees by project count."""
    graph = neo4j_service.get_graph()
    
    result = graph.query("""
        MATCH (e:Employee)-[:WORKED_ON]->(p:Project)
        RETURN e.name as name, count(p) as project_count
        ORDER BY project_count DESC
        LIMIT $limit
    """, params={"limit": limit})
    
    return {"top_employees": result}

@router.get("/department-stats")
async def get_department_stats():
    """Get statistics by department."""
    graph = neo4j_service.get_graph()
    
    result = graph.query("""
        MATCH (e:Employee)-[:WORKS_IN]->(d:Department)
        RETURN d.name as department, 
               count(e) as employee_count
        ORDER BY employee_count DESC
    """)
    
    return {"departments": result}
```

Register in `src/main.py`:
```python
from src.api.routes import custom

app.include_router(custom.router, prefix=settings.api_prefix)
```

---

## 🚀 Deployment for Real Users

### Option 1: Cloud Deployment (AWS)

**1. Use AWS Elastic Beanstalk**
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 neo4j-api

# Create environment
eb create production-env

# Deploy
eb deploy
```

**2. Use Docker on AWS ECS/Fargate**
```bash
# Build image
docker build -f docker/Dockerfile -t neo4j-api:prod .

# Tag for ECR
docker tag neo4j-api:prod YOUR_AWS_ACCOUNT.dkr.ecr.region.amazonaws.com/neo4j-api:prod

# Push to ECR
docker push YOUR_AWS_ACCOUNT.dkr.ecr.region.amazonaws.com/neo4j-api:prod

# Deploy with ECS
aws ecs update-service --cluster your-cluster \
  --service neo4j-api --force-new-deployment
```

### Option 2: Cloud Deployment (Azure)

```bash
# Login to Azure
az login

# Create resource group
az group create --name neo4j-rg --location eastus

# Create container instance
az container create \
  --resource-group neo4j-rg \
  --name neo4j-api \
  --image yourdockerhub/neo4j-api:latest \
  --dns-name-label neo4j-api \
  --ports 8000
```

### Option 3: Kubernetes

**k8s/deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: neo4j-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: neo4j-api
  template:
    metadata:
      labels:
        app: neo4j-api
    spec:
      containers:
      - name: api
        image: neo4j-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: NEO4J_URI
          valueFrom:
            secretKeyRef:
              name: neo4j-secrets
              key: uri
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
---
apiVersion: v1
kind: Service
metadata:
  name: neo4j-api-service
spec:
  selector:
    app: neo4j-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl get services  # Get external IP
```

---

## 🔒 Production Security

### Add API Key Authentication

**File: `src/core/security.py`**
```python
"""API security middleware."""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from src.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key from header."""
    if not settings.api_key_enabled:
        return True
    
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return True
```

Use in endpoints:
```python
from fastapi import Depends
from src.core.security import verify_api_key

@router.post("/query", dependencies=[Depends(verify_api_key)])
async def process_query(request: QueryRequest):
    ...
```

### Add Rate Limiting

```bash
pip install slowapi
```

**Update `src/main.py`:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/query")
@limiter.limit("10/minute")
async def process_query(request: Request, query: QueryRequest):
    ...
```

---

## 📊 Monitoring & Analytics

### Add Prometheus Metrics

```bash
pip install prometheus-fastapi-instrumentator
```

**Update `src/main.py`:**
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(...)

# Add metrics endpoint
Instrumentator().instrument(app).expose(app)
```

Access metrics at: `http://localhost:8000/metrics`

### Add Logging to CloudWatch/DataDog

```python
import watchtower
import logging

logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler())
```

---

## 💰 Cost Optimization

### Use Caching to Reduce LLM Calls

**File: `src/services/cache_service.py`**
```python
"""Redis caching for query results."""
import redis
import json
from src.core.config import settings

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True
        )
    
    def get_cached_query(self, question: str):
        """Get cached query result."""
        key = f"query:{question}"
        cached = self.redis_client.get(key)
        return json.loads(cached) if cached else None
    
    def cache_query(self, question: str, result: dict, ttl: int = 3600):
        """Cache query result for 1 hour."""
        key = f"query:{question}"
        self.redis_client.setex(
            key,
            ttl,
            json.dumps(result)
        )

cache_service = CacheService()
```

Use in QA service:
```python
def query(self, question: str):
    # Check cache first
    cached = cache_service.get_cached_query(question)
    if cached:
        return cached
    
    # Process query
    result = self._process_query(question)
    
    # Cache result
    cache_service.cache_query(question, result)
    
    return result
```

---

## 📈 Scaling Strategies

1. **Horizontal Scaling**: Run multiple API instances behind load balancer
2. **Neo4j Clustering**: Use Neo4j Enterprise for read replicas
3. **Caching Layer**: Redis for frequent queries
4. **CDN**: CloudFlare for static assets
5. **Database Indexing**: Optimize Cypher queries with proper indexes

---

## 🎯 Next Steps

1. **Define your domain** - Choose use case (knowledge base, e-commerce, support)
2. **Design schema** - Model your entities and relationships
3. **Load real data** - Connect to your data sources
4. **Customize queries** - Add domain-specific endpoints
5. **Deploy** - Choose cloud provider and deploy
6. **Monitor** - Set up logging and metrics
7. **Iterate** - Improve based on user feedback

---

**Need help with a specific use case? Let me know!** 🚀
