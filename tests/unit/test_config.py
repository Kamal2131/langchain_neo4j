"""Test configuration module."""

from src.core.config import settings


def test_settings_load():
    """Test settings load successfully."""
    assert settings.app_name is not None
    assert settings.neo4j_uri is not None


def test_llm_config():
    """Test LLM configuration."""
    config = settings.get_llm_config()
    assert "provider" in config
    assert "model" in config
    assert config["provider"] in ["openai", "groq"]
