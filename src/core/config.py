"""
Enhanced configuration management with Pydantic Settings.
Provides type-safe configuration with validation.
"""

from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
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
    cors_origins: list[str] = ["*"]
    
    # Rate Limiting (optional)
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "text"] = "text"
    
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
                "model": self.openai_model
            }
        elif self.llm_provider == "groq":
            return {
                "provider": "groq",
                "api_key": self.groq_api_key,
                "model": self.groq_model
            }
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")


# Global settings instance
settings = Settings()

# Validate on import
settings.validate_llm_config()
