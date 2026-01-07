"""
Pydantic schemas for request/response validation.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for natural language queries."""

    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language question to query the graph",
        examples=["Which projects use Python?"],
    )
    include_cypher: bool = Field(
        default=False, description="Whether to include generated Cypher query in response"
    )


class QueryResponse(BaseModel):
    """Response model for query results."""

    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Answer to the question")
    cypher_query: Optional[str] = Field(None, description="Generated Cypher query")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Query metadata")


class SchemaResponse(BaseModel):
    """Response model for schema information."""

    nodes: Dict[str, int] = Field(..., description="Node counts by type")
    relationships: Dict[str, int] = Field(..., description="Relationship counts by type")
    total_nodes: int = Field(..., description="Total number of nodes")
    total_relationships: int = Field(..., description="Total number of relationships")


class HealthResponse(BaseModel):
    """Response model for health checks."""

    status: str = Field(..., description="Health status")
    neo4j_connected: bool = Field(..., description="Neo4j connection status")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional health details")


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")


class AsyncQueryResponse(BaseModel):
    """Response model for async query submission."""
    
    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(default="PENDING", description="Task status")
    message: str = Field(default="Query submitted for background processing", description="Status message")


class TaskStatusResponse(BaseModel):
    """Response model for task status check."""
    
    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status (PENDING, PROGRESS, SUCCESS, FAILURE)")
    message: str = Field(..., description="Status message")
    ready: Optional[bool] = Field(None, description="Whether task is complete")
    error: Optional[str] = Field(None, description="Error message if failed")


class TaskResultResponse(BaseModel):
    """Response model for task result retrieval."""
    
    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status")
    result: Optional[QueryResponse] = Field(None, description="Query result if successful")
    error: Optional[str] = Field(None, description="Error details if failed")

