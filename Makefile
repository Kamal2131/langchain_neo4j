.PHONY: help install install-dev run-api run-cli docker-up docker-down test lint format clean

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt

run-api:  ## Run FastAPI server
	python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

run-cli:  ## Run CLI interface
	python -m src.cli

docker-up:  ## Start Docker containers
	docker-compose up -d

docker-down:  ## Stop Docker containers
	docker-compose down

docker-logs:  ## View Docker logs
	docker-compose logs -f

load-data:  ## Load data into Neo4j
	python scripts/load_data.py

run-worker:  ## Run Celery worker for background jobs
	celery -A src.celery_worker worker --loglevel=info --pool=solo

run-flower:  ## Run Flower (Celery monitoring UI)
	celery -A src.celery_worker flower --port=5555

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:  ## Run linting
	ruff check src/ tests/
	mypy src/

format:  ## Format code
	black src/ tests/
	isort src/ tests/

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache

setup:  ## Initial project setup
	@echo "Setting up project..."
	docker-compose up -d
	@echo "Waiting for Neo4j to start..."
	@timeout /t 10 /nobreak
	cp .env.example .env
	@echo "Please edit .env and add your API keys"
	@echo "Then run: make load-data"
