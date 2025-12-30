"""Logging configuration for the application."""

import logging
import sys
from typing import Any

from src.core.config import settings


def setup_logging() -> None:
    """Configure logging for the application."""
    
    log_level = getattr(logging, settings.log_level)
    
    # Create logger
    logger = logging.getLogger("neo4j_langchain")
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    if settings.log_format == "json":
        # For production, use JSON formatter (requires structlog)
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
        )
    else:
        # For development, use readable format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Set propagate to False to avoid duplicate logs
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"neo4j_langchain.{name}")
