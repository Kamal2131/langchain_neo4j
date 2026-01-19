"""
Agent Tools for Agentic RAG System.

Defines tools the agent can use:
- graph_search: Query Neo4j with natural language
- vector_search: Semantic search in Qdrant
- entity_lookup: Find specific entities
"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_core.documents import Document

from src.core.logging import get_logger
from src.services.neo4j_service import neo4j_service
from src.services.qdrant_service import qdrant_service

logger = get_logger(__name__)


@tool
def graph_search(query: str) -> str:
    """
    Search the knowledge graph for structured data about entities.
    
    Use this tool for:
    - Finding employees, projects, departments
    - Counting entities
    - Finding relationships (who works in, who manages)
    - Listing entities by properties
    
    Args:
        query: Natural language question about graph entities
        
    Returns:
        String with structured data from the graph
    """
    logger.info(f"[TOOL] graph_search: {query}")
    
    try:
        graph = neo4j_service.get_graph()
        
        # Simple entity queries based on keywords
        query_lower = query.lower()
        
        if "employee" in query_lower or "who" in query_lower:
            result = graph.query("""
                MATCH (e:Employee)
                OPTIONAL MATCH (e)-[:WORKS_IN]->(d:Department)
                RETURN e.name as name, e.title as title, d.name as department
                LIMIT 10
            """)
            if result:
                return "Employees:\n" + "\n".join([
                    f"- {r['name']} ({r['title']}) - {r['department']}"
                    for r in result
                ])
                
        elif "project" in query_lower:
            result = graph.query("""
                MATCH (p:Project)
                OPTIONAL MATCH (e:Employee)-[:LEADS]->(p)
                RETURN p.name as name, p.status as status, e.name as leader
                LIMIT 10
            """)
            if result:
                return "Projects:\n" + "\n".join([
                    f"- {r['name']} (status: {r['status']}, lead: {r['leader']})"
                    for r in result
                ])
                
        elif "department" in query_lower:
            result = graph.query("""
                MATCH (d:Department)
                OPTIONAL MATCH (e:Employee)-[:WORKS_IN]->(d)
                RETURN d.name as name, count(e) as employee_count
                ORDER BY employee_count DESC
            """)
            if result:
                return "Departments:\n" + "\n".join([
                    f"- {r['name']} ({r['employee_count']} employees)"
                    for r in result
                ])
        
        # Generic query attempt
        result = graph.query("""
            MATCH (n)
            RETURN labels(n)[0] as type, count(*) as count
        """)
        return f"Graph contains: " + ", ".join([
            f"{r['count']} {r['type']} nodes" for r in result
        ])
        
    except Exception as e:
        logger.error(f"Graph search failed: {e}")
        return f"Graph search failed: {str(e)}"


@tool
def vector_search(query: str) -> str:
    """
    Search documents for semantic/contextual information.
    
    Use this tool for:
    - Finding information in contracts, policies
    - Summarizing document content
    - Finding context about topics
    - Semantic similarity search
    
    Args:
        query: Natural language query for semantic search
        
    Returns:
        String with relevant document excerpts
    """
    logger.info(f"[TOOL] vector_search: {query}")
    
    try:
        docs = qdrant_service.similarity_search(query, k=3)
        
        if not docs:
            return "No relevant documents found."
        
        results = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            doc_type = doc.metadata.get("doc_type", "general")
            excerpt = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
            results.append(f"[{i}] ({doc_type} - {source})\n{excerpt}")
        
        return "Relevant documents:\n\n" + "\n\n".join(results)
        
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return f"Vector search failed: {str(e)}"


@tool
def entity_lookup(entity_type: str, entity_name: str) -> str:
    """
    Look up a specific entity by name.
    
    Use this tool for:
    - Finding details about a specific person
    - Looking up a specific project
    - Getting information about a named entity
    
    Args:
        entity_type: Type of entity (Employee, Project, Department, Client)
        entity_name: Name of the entity to look up
        
    Returns:
        String with entity details
    """
    logger.info(f"[TOOL] entity_lookup: {entity_type} - {entity_name}")
    
    try:
        graph = neo4j_service.get_graph()
        
        # Sanitize entity type
        valid_types = ["Employee", "Project", "Department", "Client", "Contract", "Policy"]
        entity_type = entity_type.title()
        if entity_type not in valid_types:
            entity_type = "Employee"  # Default
        
        result = graph.query(f"""
            MATCH (n:{entity_type})
            WHERE toLower(n.name) CONTAINS toLower($name)
            RETURN n
            LIMIT 1
        """, {"name": entity_name})
        
        if result:
            node = result[0]["n"]
            details = "\n".join([f"  {k}: {v}" for k, v in node.items() if v])
            return f"Found {entity_type}:\n{details}"
        else:
            return f"No {entity_type} found matching '{entity_name}'"
            
    except Exception as e:
        logger.error(f"Entity lookup failed: {e}")
        return f"Entity lookup failed: {str(e)}"


@tool  
def get_relationships(entity_name: str) -> str:
    """
    Get all relationships for an entity.
    
    Use this tool for:
    - Finding who reports to whom
    - Discovering project team members
    - Understanding entity connections
    
    Args:
        entity_name: Name of the entity
        
    Returns:
        String describing entity relationships
    """
    logger.info(f"[TOOL] get_relationships: {entity_name}")
    
    try:
        graph = neo4j_service.get_graph()
        
        result = graph.query("""
            MATCH (n)-[r]-(m)
            WHERE toLower(n.name) CONTAINS toLower($name)
            RETURN n.name as source, type(r) as relationship, m.name as target, labels(m)[0] as target_type
            LIMIT 20
        """, {"name": entity_name})
        
        if result:
            relationships = []
            for r in result:
                relationships.append(f"  {r['source']} --[{r['relationship']}]--> {r['target']} ({r['target_type']})")
            return f"Relationships for '{entity_name}':\n" + "\n".join(relationships)
        else:
            return f"No relationships found for '{entity_name}'"
            
    except Exception as e:
        logger.error(f"Get relationships failed: {e}")
        return f"Relationship lookup failed: {str(e)}"


# Export all tools
ALL_TOOLS = [graph_search, vector_search, entity_lookup, get_relationships]
