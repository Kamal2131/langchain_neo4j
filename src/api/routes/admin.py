"""
Admin endpoints for system management.
"""

from fastapi import APIRouter, HTTPException, status

from src.core.logging import get_logger
from src.services.qa_service import get_qa_service

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/refresh-schema",
    status_code=status.HTTP_200_OK,
    summary="Refresh graph schema",
    description="Force a refresh of the Neo4j graph schema and invalidate the QAService cache.",
)
async def refresh_schema() -> dict:
    """
    Refresh the graph schema.
    """
    try:
        logger.info("Admin request: Refreshing schema")
        qa_service = get_qa_service()
        qa_service.refresh_schema()
        return {"status": "success", "message": "Schema refreshed and chain cache invalidated"}
    except Exception as e:
        logger.error(f"Failed to refresh schema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
