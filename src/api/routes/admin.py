import os
import shutil
import tempfile
from fastapi import APIRouter, HTTPException, status, UploadFile, File

from src.core.logging import get_logger
from src.services.qa_service import get_qa_service
from src.services.ingestion_service import ingestion_service

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/ingest",
    status_code=status.HTTP_200_OK,
    summary="Ingest PDF document",
    description="Upload a PDF file to extract entities and add them to the graph.",
)
async def ingest_document(file: UploadFile = File(...)) -> dict:
    """
    Ingest a PDF document.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
        
    try:
        # Save upload to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
            
        logger.info(f"Saved upload to {temp_path}")
        
        # Process
        result = await ingestion_service.process_pdf(temp_path)
        
        return result
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
    finally:
        # Ensure cleanup just in case service didn't
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


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
