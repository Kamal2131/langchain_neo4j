"""
Celery worker entry point.

Run with:
    celery -A src.celery_worker worker --loglevel=info
"""

from src.services.celery_service import celery_app
from src.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Import tasks to register them
from src.services.celery_service import process_query_task  # noqa: F401

logger.info("Celery worker initialized")

# Export celery app for worker
__all__ = ["celery_app"]
