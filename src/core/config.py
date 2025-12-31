"""
Enhanced configuration management with Pydantic Settings.
Provides type-safe configuration with validation.
"""

from typing import List, Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application
    app_name: str = "Neo4j LangChain API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # Neo4j Configuration
    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", alias="NEO4J_USERNAME")
    neo4j_password: str = Field(default="password123", alias="NEO4J_PASSWORD")
    
    # Neo4j Connection Pool Settings
    neo4j_max_pool_size: int = Field(default=50, alias="NEO4J_MAX_POOL_SIZE")
    neo4j_connection_timeout: int = Field(default=30, alias="NEO4J_CONNECTION_TIMEOUT")
    neo4j_max_connection_lifetime: int = Field(default=3600, alias="NEO4J_MAX_CONNECTION_LIFETIME")
    
    # Query Optimization Settings
    query_timeout: int = Field(default=30, alias="QUERY_TIMEOUT", description="Query timeout in seconds")
    query_max_results: int = Field(default=1000, alias="QUERY_MAX_RESULTS", description="Maximum query result limit")

    # LLM Provider Configuration
    llm_provider: Literal["openai", "groq"] = Field(default="openai", alias="LLM_PROVIDER")

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", alias="OPENAI_MODEL")

    # Groq Configuration
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="mixtral-8x7b-32768", alias="GROQ_MODEL")

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    # CORS
    cors_origins: List[str] = Field(
        default=["*"], description="Allowed CORS origins"
    )

    # Rate Limiting (optional)
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "text"] = "text"

    # Redis Configuration
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    
    # Celery Configuration
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0", 
        alias="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0", 
        alias="CELERY_RESULT_BACKEND"
    )
    celery_task_timeout: int = Field(
        default=300, 
        alias="CELERY_TASK_TIMEOUT",
        description="Celery task timeout in seconds"
    )

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls: type["Settings"], v: str) -> str:
        """Validate LLM provider."""
        return v

    @field_validator("openai_api_key", "groq_api_key")
    @classmethod
    def validate_api_keys(cls, v: Optional[str], info) -> Optional[str]:
        """Validate API keys are provided based on provider."""
        return v

    def validate_llm_config(self) -> None:
        """Validate LLM configuration based on provider."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        if self.llm_provider == "groq" and not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required when using Groq provider")

    def get_llm_config(self) -> dict:
        """Get LLM configuration based on provider."""
        if self.llm_provider == "openai":
            return {
                "provider": "openai",
                "api_key": self.openai_api_key,
                "model": self.openai_model,
            }
        elif self.llm_provider == "groq":
            return {"provider": "groq", "api_key": self.groq_api_key, "model": self.groq_model}
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")


# Global settings instance
settings = Settings()

# Validate on import
settings.validate_llm_config()
