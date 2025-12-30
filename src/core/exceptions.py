"""Custom exceptions for the application."""

from typing import Any, Optional


class Neo4jLangChainException(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(Neo4jLangChainException):
    """Raised when configuration is invalid."""
    pass


class Neo4jConnectionError(Neo4jLangChainException):
    """Raised when Neo4j connection fails."""
    pass


class LLMProviderError(Neo4jLangChainException):
    """Raised when LLM provider encounters an error."""
    pass


class QueryValidationError(Neo4jLangChainException):
    """Raised when query validation fails."""
    pass


class QueryExecutionError(Neo4jLangChainException):
    """Raised when query execution fails."""
    pass


class SchemaError(Neo4jLangChainException):
    """Raised when schema operations fail."""
    pass
