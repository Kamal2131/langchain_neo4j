# CHANGELOG

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-12-30

### Added - Production Upgrade

#### Core Architecture
- ✅ Modular `src/` directory structure
- ✅ Pydantic Settings for configuration with validation
- ✅ Custom exception handling system
- ✅ Structured logging with environment-specific formats
- ✅ Type hints throughout codebase

#### API Layer (NEW)
- ✅ FastAPI REST API application
- ✅ POST `/api/v1/query` - Natural language query endpoint
- ✅ GET `/api/v1/query/examples` - Sample questions endpoint
- ✅ GET `/api/v1/health` - Health check endpoint
- ✅ GET `/api/v1/health/schema` - Graph schema endpoint
- ✅ Auto-generated OpenAPI/Swagger documentation
- ✅ CORS middleware configuration
- ✅ Pydantic request/response validation

#### Services
- ✅ `Neo4jService` - Connection management and schema verification
- ✅ `QAService` - Natural language query processing
- ✅ Singleton pattern for service instances
- ✅ Health check functionality

#### Developer Experience
- ✅ `pyproject.toml` for modern Python packaging
- ✅ `Makefile` with common development commands
- ✅ `requirements-dev.txt` with testing and linting tools
- ✅ Enhanced CLI interface (`src/cli.py`)
- ✅ Multi-stage production `Dockerfile`

#### Testing
- ✅ Pytest configuration with fixtures
- ✅ Integration tests for API endpoints
- ✅ Test coverage setup
- ✅ FastAPI TestClient integration

#### Documentation
- ✅ Production-level README
- ✅ API endpoint documentation
- ✅ Production upgrade plan
- ✅ CHANGELOG

### Changed
- 🔄 Moved `config.py` to `src/core/config.py` with Pydantic Settings
- 🔄 Reorganized data files to `data/` directory
- 🔄 Moved scripts to `scripts/` directory
- 🔄 Enhanced error handling with custom exceptions

### Maintained (Backward Compatible)
- ✅ Original demo functionality preserved in CLI
- ✅ Same environment variable configuration
- ✅ Compatible with existing `.env` files
- ✅ Same Neo4j schema and data

## [0.1.0] - Initial Demo

### Added
- Basic CLI demo application
- Neo4j Docker Compose setup
- LangChain integration
- Sample knowledge graph
- Basic documentation
