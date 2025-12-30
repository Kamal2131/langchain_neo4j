# Neo4j + LangChain Production API

<div align="center">

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.15-008CC1.svg)](https://neo4j.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1-00A67E.svg)](https://www.langchain.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Query your Neo4j graph database using natural language powered by LangChain and LLMs**

[Features](#-features) •
[Quick Start](#-quick-start) •
[API Docs](#-api-documentation) •
[Examples](#-usage-examples) •
[Development](#-development)

</div>

---

## 🎯 Overview

A production-ready REST API that enables natural language querying of Neo4j graph databases. Built with FastAPI, LangChain, and supporting multiple LLM providers (OpenAI, Groq).

**Ask questions like:**
- "Which projects use Python and who worked on them?"
- "What technologies does Alice work with?"
- "Show me all active projects"

**Get structured answers** with automatically generated Cypher queries.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Natural Language** | Ask questions in plain English, no Cypher knowledge required |
| 🚀 **REST API** | Production-ready FastAPI with auto-generated OpenAPI docs |
| 🔒 **Type Safe** | Pydantic validation for all inputs and outputs |
| 📊 **Multiple LLMs** | Support for OpenAI GPT and Groq Mixtral |
| 🐳 **Docker Ready** | Multi-stage Dockerfile for optimized deployment |
| ✅ **Tested** | Comprehensive test suite with pytest |
| 📝 **Documented** | Interactive Swagger UI and ReDoc |
| 🎨 **Clean Architecture** | Modular design with services, routes, and schemas |

## 🏗️ Architecture

```
┌──────────────┐
│    Client    │
│  (HTTP/CLI)  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│         FastAPI Application          │
│  ┌────────────┐  ┌───────────────┐  │
│  │  Routes    │  │   Schemas     │  │
│  │  (API)     │  │  (Pydantic)   │  │
│  └─────┬──────┘  └───────────────┘  │
└────────┼─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│         Service Layer                │
│  ┌────────────┐  ┌───────────────┐  │
│  │  Neo4j     │  │  QA Service   │  │
│  │  Service   │  │  (LangChain)  │  │
│  └─────┬──────┘  └───────┬───────┘  │
└────────┼──────────────────┼──────────┘
         │                  │
         ▼                  ▼
    ┌────────┐        ┌─────────┐
    │ Neo4j  │        │   LLM   │
    │  DB    │        │ Provider│
    └────────┘        └─────────┘
```

## 📋 Prerequisites

- **Python 3.8+**
- **Docker & Docker Compose**
- **API Key**: OpenAI or Groq

## 🚀 Quick Start

### 1. Clone & Start Neo4j

```bash
cd c:\Users\91629\Desktop\SoftCoders\neo4j
docker-compose up -d
```

Neo4j will be available at:
- **Browser UI**: http://localhost:7474
- **Bolt**: bolt://localhost:7687
- **Credentials**: `neo4j` / `password123`

### 2. Install Dependencies

```bash
# Install with dev dependencies
pip install -r requirements-dev.txt
```

### 3. Configure Environment

```bash
# Copy template
copy .env.example .env

# Edit .env and add your API key
# For OpenAI:
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# OR for Groq:
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-key-here
```

### 4. Load Sample Data

```bash
python scripts\load_data.py
```

This loads a sample knowledge graph:
- **5 People** (developers, engineers)
- **5 Projects** (software projects)
- **10 Technologies** (languages, frameworks)
- **27 Relationships** (WORKED_ON, USES)

### 5. Start the API

```bash
# Start API server
python -m uvicorn src.main:app --reload

# Server runs at: http://localhost:8000
```

### 6. Explore the API

Open your browser to:
- **📖 Interactive Docs**: http://localhost:8000/api/v1/docs
- **📚 ReDoc**: http://localhost:8000/api/v1/redoc

## 📖 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 🔍 Query Natural Language

**POST** `/query`

Submit a natural language question to query the graph.

**Request:**
```json
{
  "question": "Which projects use Python and who worked on them?",
  "include_cypher": true
}
```

**Response:**
```json
{
  "question": "Which projects use Python and who worked on them?",
  "answer": "The following projects use Python:\n1. AI Chatbot - worked on by Alice Johnson and Bob Smith\n2. Analytics Dashboard - worked on by Charlie Davis\n3. REST API Service - worked on by Charlie Davis\n4. Recommendation Engine - worked on by Bob Smith and Diana Martinez",
  "cypher_query": "MATCH (p:Person)-[:WORKED_ON]->(pr:Project)-[:USES]->(t:Technology {name: 'Python'}) RETURN pr.name, collect(p.name)",
  "metadata": {
    "provider": "openai",
    "model": "gpt-3.5-turbo"
  }
}
```

#### 📝 Get Sample Questions

**GET** `/query/examples`

Returns a list of sample questions to try.

**Response:**
```json
[
  "Which projects use Python and who worked on them?",
  "What technologies does Alice Johnson work with?",
  "Show me all active projects",
  "Who worked on the AI Chatbot project?",
  "What programming languages are used across all projects?"
]
```

#### 💚 Health Check

**GET** `/health`

Check API and database health.

**Response:**
```json
{
  "status": "healthy",
  "neo4j_connected": true,
  "details": {
    "environment": "development",
    "version": "1.0.0",
    "llm_provider": "openai"
  }
}
```

#### 📊 Graph Schema

**GET** `/health/schema`

Get information about the graph structure.

**Response:**
```json
{
  "nodes": {
    "Person": 5,
    "Project": 5,
    "Technology": 10
  },
  "relationships": {
    "WORKED_ON": 10,
    "USES": 17
  },
  "total_nodes": 20,
  "total_relationships": 27
}
```

## 💻 Usage Examples

### Using cURL

```bash
# Query the graph
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who worked on the AI Chatbot project?",
    "include_cypher": false
  }'

# Get sample questions
curl "http://localhost:8000/api/v1/query/examples"

# Health check
curl "http://localhost:8000/api/v1/health"
```

### Using Python

```python
import requests

# Initialize API client
API_URL = "http://localhost:8000/api/v1"

# Query the graph
response = requests.post(
    f"{API_URL}/query",
    json={
        "question": "What technologies does Bob Smith use?",
        "include_cypher": True
    }
)

result = response.json()
print(f"Question: {result['question']}")
print(f"Answer: {result['answer']}")
if result.get('cypher_query'):
    print(f"Cypher: {result['cypher_query']}")
```

### Using the CLI

The original CLI interface is still available:

```bash
# Start interactive CLI
python -m src.cli

# Test connection
python -m src.cli --test
```

**CLI Commands:**
- `help` - Show sample questions
- `info` - Display database schema
- `debug` - Toggle Cypher query display
- `quit` - Exit

## 🛠️ Development

### Project Structure

```
neo4j-langchain-api/
├── src/
│   ├── api/                    # API layer
│   │   ├── routes/
│   │   │   ├── health.py       # Health & schema endpoints
│   │   │   └── query.py        # Query endpoints
│   │   └── schemas.py          # Pydantic models
│   ├── core/                   # Core components
│   │   ├── config.py           # Settings (Pydantic)
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── logging.py          # Logging setup
│   ├── services/               # Business logic
│   │   ├── neo4j_service.py    # Neo4j operations
│   │   └── qa_service.py       # Query processing
│   ├── main.py                 # FastAPI app
│   └── cli.py                  # CLI interface
├── tests/                      # Test suite
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── scripts/                    # Utility scripts
│   └── load_data.py
├── data/                       # Cypher files
│   ├── schema.cypher
│   └── sample_data.cypher
├── docker/                     # Docker configs
│   └── Dockerfile
├── pyproject.toml              # Project config
├── Makefile                    # Dev commands
└── README.md
```

### Using Makefile

```bash
make help          # Show all commands
make install-dev   # Install dependencies
make run-api       # Start API server
make run-cli       # Start CLI
make docker-up     # Start Neo4j
make load-data     # Load sample data
make test          # Run tests
make test-cov      # Run with coverage
make lint          # Check code quality
make format        # Format code
make clean         # Clean artifacts
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/integration/test_api.py -v

# Run and generate HTML report
pytest --cov=src --cov-report=html && start htmlcov/index.html
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint
ruff check src/ tests/
mypy src/

# All at once
make format && make lint
```

## ⚙️ Configuration

Configuration is managed via environment variables in `.env`:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` | Yes |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` | Yes |
| `NEO4J_PASSWORD` | Neo4j password | `password123` | Yes |
| `LLM_PROVIDER` | LLM provider (`openai`/`groq`) | `openai` | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | If using OpenAI |
| `GROQ_API_KEY` | Groq API key | - | If using Groq |
| `OPENAI_MODEL` | OpenAI model name | `gpt-3.5-turbo` | No |
| `GROQ_MODEL` | Groq model name | `mixtral-8x7b-32768` | No |
| `API_PORT` | API server port | `8000` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `ENVIRONMENT` | Environment | `development` | No |

## 🐳 Docker Deployment

### Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Build

```bash
# Build production image
docker build -f docker/Dockerfile -t neo4j-langchain-api:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name neo4j-api \
  neo4j-langchain-api:latest
```

## 📊 Sample Knowledge Graph

The demo includes a **Project-Technology-Person** graph:

**People:**
- Alice Johnson (Full Stack Developer)
- Bob Smith (Data Scientist)  
- Charlie Davis (Backend Developer)
- Diana Martinez (ML Engineer)
- Eve Wilson (Frontend Developer)

**Projects:**
- AI Chatbot (Active)
- Analytics Dashboard (Active)
- REST API Service (Completed)
- Recommendation Engine (Active)
- E-commerce Platform (Planning)

**Technologies:**
- Languages: Python, JavaScript
- Frameworks: React, Django, FastAPI
- ML: TensorFlow
- Databases: PostgreSQL, Neo4j
- DevOps: Docker, Kubernetes

## 🎓 Example Queries

Try these questions in the API or CLI:

1. **"Which projects use Python and who worked on them?"**
2. **"What technologies does Alice Johnson work with?"**
3. **"Show me all active projects"**
4. **"Who worked on the AI Chatbot project?"**
5. **"What programming languages are used across all projects?"**
6. **"Which person has worked on the most projects?"**
7. **"What projects use React?"**
8. **"List all machine learning projects"**

## 🔧 Troubleshooting

### Issue: Neo4j Connection Failed

**Solution:**
```bash
# Check if Neo4j is running
docker-compose ps

# View Neo4j logs
docker-compose logs neo4j

# Restart Neo4j
docker-compose restart neo4j
```

### Issue: API Key Error

**Solution:**
- Verify `.env` file exists
- Check API key is correctly set
- Ensure `LLM_PROVIDER` matches your key

### Issue: No Data Found

**Solution:**
```bash
# Reload data
python scripts\load_data.py

# Verify in Neo4j Browser
# http://localhost:7474
# Run: MATCH (n) RETURN count(n)
```

## 📝 API Response Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `422` | Validation Error (invalid input) |
| `500` | Server Error (connection/query failed) |

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Before submitting:**
- Run tests: `make test`
- Format code: `make format`
- Check linting: `make lint`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [LangChain](https://www.langchain.com/) - LLM application framework
- [Neo4j](https://neo4j.com/) - Graph database platform
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation

## 📧 Support

For issues and questions:
- 🐛 [GitHub Issues](https://github.com/yourusername/neo4j-langchain-api/issues)
- 📖 [Documentation](docs/)
- 💬 [Discussions](https://github.com/yourusername/neo4j-langchain-api/discussions)

---

<div align="center">

**Built with ❤️ using FastAPI, LangChain, and Neo4j**

⭐ Star this repo if you find it helpful!

</div>
