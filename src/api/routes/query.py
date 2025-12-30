"""
Query endpoints for natural language processing.
"""

from fastapi import APIRouter, HTTPException, status
from src.api.schemas import QueryRequest, QueryResponse, ErrorResponse
from src.services.neo4j_service import neo4j_service
from src.services.qa_service import QAService, SAMPLE_QUESTIONS
from src.core.exceptions import QueryExecutionError, LLMProviderError
from src.core.logging import get_logger

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
        500: {"model": ErrorResponse, "description": "Query execution failed"}
    }
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
        result = qa_service.query(
            question=request.question,
            include_cypher=request.include_cypher
        )
        
        return QueryResponse(**result)
        
    except (QueryExecutionError, LLMProviderError) as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "details": getattr(e, 'details', {})}
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error"}
        )


@router.get(
    "/examples",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    summary="Get sample questions",
    description="Get a list of sample questions to try"
)
async def get_sample_questions() -> list[str]:
    """
    Get sample questions for testing.
    
    Returns:
        List of sample questions
    """
    return SAMPLE_QUESTIONS
