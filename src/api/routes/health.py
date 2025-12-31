"""
Health check and monitoring endpoints.
"""

from fastapi import APIRouter, status

from src.api.schemas import HealthResponse, SchemaResponse
from src.core.config import settings
from src.core.logging import get_logger
from src.services.neo4j_service import neo4j_service

try:
    from src.services.celery_service import celery_app
except ImportError:
    celery_app = None

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the API and Neo4j are healthy",
)
async def health_check() -> HealthResponse:
    """
    Perform health check on API and Neo4j connection.

    Returns:
        HealthResponse with status and connection information
    """
    neo4j_healthy = neo4j_service.health_check()
    
    # Check Redis connection
    redis_healthy = False
    try:
        import redis
        r = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            socket_connect_timeout=2
        )
        r.ping()
        redis_healthy = True
        r.close()
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
    
    # Check Celery workers
    celery_healthy = False
    active_workers = 0
    try:
        if celery_app:
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            if stats:
                active_workers = len(stats)
                celery_healthy = True
    except Exception as e:
        logger.warning(f"Celery health check failed: {e}")

    # Overall health status
    health_status = "healthy" if (neo4j_healthy and redis_healthy) else "degraded"
    if not neo4j_healthy:
        health_status = "unhealthy"

    return HealthResponse(
        status=health_status,
        neo4j_connected=neo4j_healthy,
        details={
            "environment": settings.environment,
            "version": settings.app_version,
            "llm_provider": settings.llm_provider,
            "redis_connected": redis_healthy,
            "celery_workers": active_workers,
            "celery_healthy": celery_healthy,
        },
    )


@router.get(
    "/schema",
    response_model=SchemaResponse,
    status_code=status.HTTP_200_OK,
    summary="Get graph schema",
    description="Get information about the Neo4j graph schema",
)
async def get_schema() -> SchemaResponse:
    """
    Get Neo4j graph schema information.

    Returns:
        SchemaResponse with node and relationship counts
    """
    try:
        schema = neo4j_service.verify_schema()
        return SchemaResponse(**schema)
    except Exception as e:
        logger.error(f"Failed to get schema: {e}")
        raise
