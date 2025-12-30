"""
Health check and monitoring endpoints.
"""

from fastapi import APIRouter, status
from src.api.schemas import HealthResponse, SchemaResponse
from src.services.neo4j_service import neo4j_service
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the API and Neo4j are healthy"
)
async def health_check() -> HealthResponse:
    """
    Perform health check on API and Neo4j connection.
    
    Returns:
        HealthResponse with status and connection information
    """
    neo4j_healthy = neo4j_service.health_check()
    
    health_status = "healthy" if neo4j_healthy else "degraded"
    
    return HealthResponse(
        status=health_status,
        neo4j_connected=neo4j_healthy,
        details={
            "environment": settings.environment,
            "version": settings.app_version,
            "llm_provider": settings.llm_provider
        }
    )


@router.get(
    "/schema",
    response_model=SchemaResponse,
    status_code=status.HTTP_200_OK,
    summary="Get graph schema",
    description="Get information about the Neo4j graph schema"
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
