import os
import shutil
import tempfile
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form

from src.core.logging import get_logger
from src.services.qa_service import get_qa_service
from src.services.ingestion_service import ingestion_service

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/ingest",
    status_code=status.HTTP_200_OK,
    summary="Ingest PDF document (General)",
    description="Upload a PDF file to extract entities and add them to the graph. Document type will be auto-detected.",
)
async def ingest_document(
    file: UploadFile = File(...),
    doc_type: Optional[str] = Form(None)
) -> dict:
    """
    Ingest a PDF document with optional type hint.
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
        
        # Process with metadata
        metadata = {
            "filename": file.filename,
            "doc_type": doc_type
        }
        result = await ingestion_service.process_pdf(temp_path, metadata=metadata)
        
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
    "/ingest/contract",
    status_code=status.HTTP_200_OK,
    summary="Ingest Contract",
    description="Upload a contract PDF and link it to a client.",
)
async def ingest_contract(
    file: UploadFile = File(...),
    client_name: str = Form(...),
    contract_type: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
) -> dict:
    """
    Ingest a contract and automatically link to client.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
        
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
            
        logger.info(f"Processing contract: {file.filename} (Client: {client_name})")
        
        metadata = {
            "filename": file.filename,
            "doc_type": "contract",
            "client_name": client_name,
            "contract_type": contract_type or "General",
            "start_date": start_date
        }
        
        result = await ingestion_service.process_pdf(temp_path, metadata=metadata)
        return result
        
    except Exception as e:
        logger.error(f"Contract ingestion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
    finally:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


@router.post(
    "/ingest/policy",
    status_code=status.HTTP_200_OK,
    summary="Ingest Policy",
    description="Upload a policy PDF and link it to departments.",
)
async def ingest_policy(
    file: UploadFile = File(...),
    policy_type: str = Form(...),
    departments: str = Form(...),  # Comma-separated list
) -> dict:
    """
    Ingest a policy and automatically link to departments.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
        
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
            
        # Parse departments
        dept_list = [d.strip() for d in departments.split(',') if d.strip()]
        
        logger.info(f"Processing policy: {file.filename} (Type: {policy_type}, Depts: {dept_list})")
        
        metadata = {
            "filename": file.filename,
            "doc_type": "policy",
            "policy_type": policy_type,
            "departments": dept_list
        }
        
        result = await ingestion_service.process_pdf(temp_path, metadata=metadata)
        return result
        
    except Exception as e:
        logger.error(f"Policy ingestion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
    finally:
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
