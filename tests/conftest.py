"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from src.core.config import settings
from src.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_query():
    """Sample query for testing."""
    return "Which projects use Python?"


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return settings
