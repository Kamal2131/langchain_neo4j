"""
Async Neo4j database service with connection pooling and optimization.
"""

from typing import Any, Dict, List, Optional

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import ServiceUnavailable, SessionExpired

from src.core.config import settings
from src.core.exceptions import Neo4jConnectionError, SchemaError
from src.core.logging import get_logger

logger = get_logger(__name__)


class AsyncNeo4jService:
    """Async service for Neo4j database operations with connection pooling."""

    def __init__(self) -> None:
        self._driver: Optional[AsyncDriver] = None

    async def connect(self) -> AsyncDriver:
        """
        Create and return an async Neo4j driver with connection pooling.

        Returns:
            AsyncDriver: Connected Neo4j async driver

        Raises:
            Neo4jConnectionError: If connection fails
        """
        if self._driver is not None:
            return self._driver

        try:
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password),
                max_connection_pool_size=settings.neo4j_max_pool_size,
                connection_timeout=settings.neo4j_connection_timeout,
                max_connection_lifetime=settings.neo4j_max_connection_lifetime,
            )

            # Test connection
            async with self._driver.session() as session:
                await session.run("RETURN 1 as test")

            logger.info(
                f"Connected to Neo4j at {settings.neo4j_uri} "
                f"(pool size: {settings.neo4j_max_pool_size})"
            )
            return self._driver

        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise Neo4jConnectionError(
                f"Failed to connect to Neo4j: {e}", 
                details={"uri": settings.neo4j_uri}
            ) from e

    async def get_driver(self) -> AsyncDriver:
        """Get or create driver instance."""
        if self._driver is None:
            return await self.connect()
        return self._driver

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query with timeout and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters
            timeout: Query timeout in seconds (uses default if not specified)

        Returns:
            List of result records as dictionaries

        Raises:
            Exception: If query execution fails
        """
        driver = await self.get_driver()
        timeout_seconds = timeout or settings.query_timeout
        
        async with driver.session() as session:
            result = await session.run(
                query, 
                parameters or {},
                timeout=timeout_seconds
            )
            records = await result.data()
            
            # Limit results if needed
            if len(records) > settings.query_max_results:
                logger.warning(
                    f"Query returned {len(records)} results, "
                    f"limiting to {settings.query_max_results}"
                )
                records = records[:settings.query_max_results]
            
            return records

    async def verify_schema(self) -> Dict[str, Any]:
        """
        Verify database schema and return statistics.

        Returns:
            dict: Schema statistics with node and relationship counts

        Raises:
            SchemaError: If schema verification fails
        """
        try:
            # Count nodes by type
            node_counts = await self.execute_query(
                """
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY label
                """
            )

            # Count relationships by type
            rel_counts = await self.execute_query(
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

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if Neo4j connection is healthy and return pool stats.

        Returns:
            dict: Health status with connection pool statistics
        """
        try:
            driver = await self.get_driver()
            
            # Test query
            async with driver.session() as session:
                await session.run("RETURN 1")
            
            # Note: Neo4j async driver doesn't expose pool stats directly
            # This is a placeholder for basic health info
            return {
                "healthy": True,
                "pool_config": {
                    "max_size": settings.neo4j_max_pool_size,
                    "connection_timeout": settings.neo4j_connection_timeout,
                    "max_lifetime": settings.neo4j_max_connection_lifetime,
                }
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }

    async def close(self) -> None:
        """Close the Neo4j driver and all connections in the pool."""
        if self._driver is not None:
            await self._driver.close()
            self._driver = None
            logger.info("Neo4j connection pool closed")


# Global async service instance
async_neo4j_service = AsyncNeo4jService()
