"""
Query endpoints for natural language processing.
"""

from typing import List

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import (
    ErrorResponse, 
    QueryRequest, 
    QueryResponse,
    AsyncQueryResponse,
    TaskStatusResponse,
    TaskResultResponse,
)
from src.core.exceptions import LLMProviderError, QueryExecutionError, QueryValidationError
from src.core.logging import get_logger
from src.services.neo4j_service import neo4j_service
from src.services.qa_service import SAMPLE_QUESTIONS, QAService
from src.services.celery_service import (
    process_query_task,
    get_task_status as get_celery_task_status,
    get_task_result as get_celery_task_result,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/query", tags=["Query"])


@router.post(
    "",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Process natural language query",
    description="Submit a natural language question to query the Neo4j graph database",
    responses={
        200: {"description": "Query executed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid query"},
        500: {"model": ErrorResponse, "description": "Query execution failed"},
    },
)
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    Process a natural language query against the graph database.

    Args:
        request: QueryRequest with question and options

    Returns:
        QueryResponse with answer and optional Cypher query

    Raises:
        HTTPException: If query processing fails
    """
    try:
        # Get Neo4j graph
        graph = neo4j_service.get_graph()

        # Create QA service
        qa_service = QAService(graph)

        # Process query
        result = qa_service.query(question=request.question, include_cypher=request.include_cypher)

        return QueryResponse(**result)

    except (QueryValidationError, QueryExecutionError, LLMProviderError) as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "details": getattr(e, "details", {})},
        ) from e
    except Exception as e:
        logger.error(f"Failed to process query: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/examples",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    summary="Get sample questions",
    description="Get a list of sample questions to try",
)
async def get_sample_questions() -> List[str]:
    """
    Get sample questions for testing.

    Returns:
        List of sample questions
    """
    return SAMPLE_QUESTIONS


@router.post(
    "/async",
    response_model=AsyncQueryResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit async query for background processing",
    description="Submit a query that will be processed in the background via Celery",
)
async def submit_async_query(request: QueryRequest) -> AsyncQueryResponse:
    """
    Submit a query for background processing.
    
    This endpoint immediately returns a task_id that can be used to check
    the status and retrieve results later.
    
    Args:
        request: QueryRequest with question and options
        
    Returns:
        AsyncQueryResponse with task_id
    """
    try:
        # Submit task to Celery
        task = process_query_task.delay(
            question=request.question,
            include_cypher=request.include_cypher
        )
        
        logger.info(f"Async query submitted: task_id={task.id}")
        
        return AsyncQueryResponse(
            task_id=task.id,
            status="PENDING",
            message="Query submitted for background processing"
        )
        
    except Exception as e:
        logger.error(f"Failed to submit async query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@router.get(
    "/status/{task_id}",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Check async query status",
    description="Check the status of a background query task",
)
async def check_task_status(task_id: str) -> TaskStatusResponse:
    """
    Get the status of an async query task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        TaskStatusResponse with current status
    """
    try:
        status_info = get_celery_task_status(task_id)
        return TaskStatusResponse(**status_info)
        
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@router.get(
    "/result/{task_id}",
    response_model=TaskResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Get async query result",
    description="Retrieve the result of a completed background query task",
)
async def retrieve_task_result(task_id: str) -> TaskResultResponse:
    """
    Get the result of a completed async query task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        TaskResultResponse with query result or error
    """
    try:
        result = get_celery_task_result(task_id)
        
        # Check if result has error
        if "error" in result:
            return TaskResultResponse(
                task_id=task_id,
                status="FAILURE",
                error=result["error"]
            )
        
        # Successful result
        return TaskResultResponse(
            task_id=task_id,
            status="SUCCESS",
            result=QueryResponse(**result)
        )
        
    except Exception as e:
        logger.error(f"Failed to get task result: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
