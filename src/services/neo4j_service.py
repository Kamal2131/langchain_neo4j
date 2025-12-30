"""
Neo4j database service with connection management and schema operations.
"""

from typing import Any, Dict, Optional

from langchain_community.graphs import Neo4jGraph

from src.core.config import settings
from src.core.exceptions import Neo4jConnectionError, SchemaError
from src.core.logging import get_logger

logger = get_logger(__name__)


class Neo4jService:
    """Service for Neo4j database operations."""

    def __init__(self) -> None:
        self._graph: Optional[Neo4jGraph] = None

    def connect(self) -> Neo4jGraph:
        """
        Create and return a Neo4jGraph instance.

        Returns:
            Neo4jGraph: Connected Neo4j graph instance

        Raises:
            Neo4jConnectionError: If connection fails
        """
        if self._graph is not None:
            return self._graph

        try:
            self._graph = Neo4jGraph(
                url=settings.neo4j_uri,
                username=settings.neo4j_username,
                password=settings.neo4j_password,
            )

            # Test connection
            self._graph.query("RETURN 1 as test")

            logger.info(f"Connected to Neo4j at {settings.neo4j_uri}")
            return self._graph

        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise Neo4jConnectionError(f"Failed to connect to Neo4j: {e}", details={"uri": settings.neo4j_uri}) from e

    def get_graph(self) -> Neo4jGraph:
        """Get or create graph instance."""
        if self._graph is None:
            return self.connect()
        return self._graph

    def verify_schema(self) -> Dict[str, Any]:
        """
        Verify database schema and return statistics.

        Returns:
            dict: Schema statistics with node and relationship counts

        Raises:
            SchemaError: If schema verification fails
        """
        try:
            graph = self.get_graph()

            # Count nodes by type
            node_counts = graph.query(
                """
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY label
            """
            )

            # Count relationships by type
            rel_counts = graph.query(
                """
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY type
            """
            )

            stats = {
                "nodes": {item["label"]: item["count"] for item in node_counts if item["label"]},
                "relationships": {item["type"]: item["count"] for item in rel_counts},
            }

            total_nodes = sum(stats["nodes"].values()) if stats["nodes"] else 0
            total_rels = sum(stats["relationships"].values()) if stats["relationships"] else 0

            stats["total_nodes"] = total_nodes
            stats["total_relationships"] = total_rels

            logger.info(f"Schema verified: {total_nodes} nodes, {total_rels} relationships")
            return stats

        except Exception as e:
            logger.error(f"Schema verification failed: {e}")
            raise SchemaError(f"Failed to verify schema: {e}") from e

    def health_check(self) -> bool:
        """
        Check if Neo4j connection is healthy.

        Returns:
            bool: True if connection is healthy
        """
        try:
            graph = self.get_graph()
            graph.query("RETURN 1")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def close(self) -> None:
        """Close the Neo4j connection."""
        if self._graph is not None:
            # Neo4jGraph doesn't have explicit close in LangChain
            self._graph = None
            logger.info("Neo4j connection closed")


# Global service instance
neo4j_service = Neo4jService()
