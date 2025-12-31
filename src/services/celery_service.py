"""
Celery configuration and task definitions for background job processing.
"""

from celery import Celery
from typing import Dict, Any

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# Create Celery app
celery_app = Celery(
    "neo4j_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.celery_task_timeout,
    task_soft_time_limit=settings.celery_task_timeout - 10,
    result_expires=3600,  # Results expire after 1 hour
)


@celery_app.task(bind=True, name="tasks.process_query")
def process_query_task(self, question: str, include_cypher: bool = False) -> Dict[str, Any]:
    """
    Background task for processing natural language queries.
    
    Args:
        self: Celery task instance
        question: Natural language question
        include_cypher: Whether to include Cypher query in response
        
    Returns:
        dict: Query result with answer and metadata
    """
    try:
        # Import here to avoid circular dependencies
        from src.services.neo4j_service import neo4j_service
        from src.services.qa_service import QAService
        
        logger.info(f"Processing async query: {question} (task_id: {self.request.id})")
        
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Connecting to database..."})
        
        # Get Neo4j graph
        graph = neo4j_service.get_graph()
        
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Processing query..."})
        
        # Create QA service and process query
        qa_service = QAService(graph)
        result = qa_service.query(question=question, include_cypher=include_cypher)
        
        logger.info(f"Async query completed successfully (task_id: {self.request.id})")
        return result
        
    except Exception as e:
        logger.error(f"Async query failed (task_id: {self.request.id}): {e}")
        # Update task state to failure
        self.update_state(
            state="FAILURE",
            meta={
                "status": "Query failed",
                "error": str(e)
            }
        )
        raise


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a Celery task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        dict: Task status information
    """
    task = celery_app.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task.state,
    }
    
    if task.state == "PENDING":
        response["message"] = "Task is waiting to be processed"
    elif task.state == "PROGRESS":
        response["message"] = task.info.get("status", "Processing...")
    elif task.state == "SUCCESS":
        response["message"] = "Task completed successfully"
        response["ready"] = True
    elif task.state == "FAILURE":
        response["message"] = "Task failed"
        response["error"] = str(task.info)
        response["ready"] = True
    else:
        response["message"] = f"Task state: {task.state}"
    
    return response


def get_task_result(task_id: str) -> Dict[str, Any]:
    """
    Get the result of a completed Celery task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        dict: Task result or error
        
    Raises:
        Exception: If task failed or not ready
    """
    task = celery_app.AsyncResult(task_id)
    
    if not task.ready():
        return {
            "error": "Task not completed yet",
            "status": task.state
        }
    
    if task.successful():
        return task.result
    else:
        return {
            "error": "Task failed",
            "details": str(task.info)
        }
