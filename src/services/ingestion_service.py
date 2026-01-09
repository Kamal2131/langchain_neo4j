"""
Service for ingesting unstructured data (PDFs) into the Neo4j graph.
Uses LLM to extract nodes and relationships with specialized handling for different document types.
"""

import os
import uuid
from typing import List, Optional, Dict
from datetime import datetime

from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from src.core.config import settings
from src.core.logging import get_logger
from src.services.neo4j_service import neo4j_service

logger = get_logger(__name__)

# Specialized extraction prompts
DOCUMENT_CLASSIFICATION_PROMPT = """
Analyze the following document excerpt and classify it into ONE of these categories:
- "contract": Legal agreements, service agreements, NDAs, SOWs
- "policy": Company policies, procedural documents, guidelines
- "general": Any other document type

Document excerpt:
{text}

Respond with ONLY the category name (contract, policy, or general).
"""

CONTRACT_EXTRACTION_PROMPT = """
Extract the following information from this contract document:

{text}

Return a JSON object with these fields:
- title: Contract title/name
- client_name: Name of the client/customer (if mentioned)
- contract_type: Type of contract (e.g., "Service Agreement", "NDA", "SOW")
- start_date: Start date in YYYY-MM-DD format (if mentioned)
- end_date: End date in YYYY-MM-DD format (if mentioned)
- value: Contract value as a number (if mentioned)
- key_terms: Brief summary of key terms (2-3 sentences)
- signatories: List of people who signed (employee names if mentioned)

If any field is not found, use null. Ensure valid JSON format.
"""

POLICY_EXTRACTION_PROMPT = """
Extract the following information from this policy document:

{text}

Return a JSON object with these fields:
- title: Policy title/name
- policy_type: Type (e.g., "HR", "IT", "Compliance", "Financial")
- departments: List of department names this policy applies to
- effective_date: Effective date in YYYY-MM-DD format (if mentioned)
- key_rules: List of 3-5 main rules or points from the policy

If any field is not found, use null or empty list. Ensure valid JSON format.
"""


class IngestionService:
    """Service for processing and ingesting documents with type-aware extraction."""

    def __init__(self):
        self.graph = neo4j_service.get_graph()
        self.llm = self._get_llm()
        self.transformer = None

    def _get_llm(self):
        """Get LLM instance for extraction."""
        llm_config = settings.get_llm_config()
        if llm_config["provider"] == "openai":
            return ChatOpenAI(
                api_key=llm_config["api_key"], 
                model=llm_config["model"], 
                temperature=0
            )
        elif llm_config["provider"] == "groq":
            return ChatGroq(
                api_key=llm_config["api_key"], 
                model_name=llm_config["model"], 
                temperature=0
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_config['provider']}")

    async def _classify_document(self, documents: List[Document]) -> str:
        """Classify document type using LLM."""
        # Take first 2000 characters for classification
        sample_text = " ".join([d.page_content for d in documents])[:2000]
        
        prompt = DOCUMENT_CLASSIFICATION_PROMPT.format(text=sample_text)
        response = self.llm.invoke(prompt)
        doc_type = response.content.strip().lower()
        
        logger.info(f"Document classified as: {doc_type}")
        return doc_type

    async def _process_contract(self, documents: List[Document], metadata: Dict) -> dict:
        """Extract Contract node and link to Client."""
        logger.info("Processing as contract document...")
        
        # Combine all pages
        full_text = "\n\n".join([d.page_content for d in documents])
        
        # Extract contract information
        extraction_prompt = CONTRACT_EXTRACTION_PROMPT.format(text=full_text[:4000])
        response = self.llm.invoke(extraction_prompt)
        
        try:
            import json
            contract_data = json.loads(response.content)
        except:
            logger.warning("Failed to parse contract extraction JSON, using defaults")
            contract_data = {
                "title": metadata.get("filename", "Untitled Contract"),
                "client_name": metadata.get("client_name"),
                "contract_type": metadata.get("contract_type", "General"),
                "key_terms": "Failed to extract terms"
            }
        
        # Generate unique ID
        contract_id = str(uuid.uuid4())
        
        # Create Contract node
        contract_query = """
        CREATE (c:Contract {
            id: $id,
            title: $title,
            type: $type,
            start_date: date($start_date),
            end_date: date($end_date),
            value: $value,
            status: $status,
            terms: $terms,
            text: $text,
            created_at: datetime()
        })
        RETURN c
        """
        
        self.graph.query(contract_query, {
            "id": contract_id,
            "title": contract_data.get("title", "Untitled"),
            "type": contract_data.get("contract_type", "General"),
            "start_date": contract_data.get("start_date", "2024-01-01"),
            "end_date": contract_data.get("end_date", "2025-01-01"),
            "value": contract_data.get("value", 0.0),
            "status": "active",
            "terms": contract_data.get("key_terms", ""),
            "text": full_text[:1000]  # Store excerpt
        })
        
        # Link to Client if specified
        client_name = contract_data.get("client_name") or metadata.get("client_name")
        if client_name:
            link_query = """
            MATCH (c:Contract {id: $contract_id})
            MATCH (cl:Client)
            WHERE toLower(cl.name) CONTAINS toLower($client_name)
            MERGE (c)-[:FOR_CLIENT]->(cl)
            RETURN cl.name as linked_client
            """
            result = self.graph.query(link_query, {
                "contract_id": contract_id,
                "client_name": client_name
            })
            
            if result:
                logger.info(f"✅ Linked contract to client: {result[0]['linked_client']}")
            else:
                logger.warning(f"⚠️  Client '{client_name}' not found in graph")
        
        return {
            "status": "success",
            "document_type": "contract",
            "contract_id": contract_id,
            "title": contract_data.get("title"),
            "linked_client": client_name
        }

    async def _process_policy(self, documents: List[Document], metadata: Dict) -> dict:
        """Extract Policy node and link to Departments."""
        logger.info("Processing as policy document...")
        
        full_text = "\n\n".join([d.page_content for d in documents])
        
        # Extract policy information
        extraction_prompt = POLICY_EXTRACTION_PROMPT.format(text=full_text[:4000])
        response = self.llm.invoke(extraction_prompt)
        
        try:
            import json
            policy_data = json.loads(response.content)
        except:
            logger.warning("Failed to parse policy extraction JSON, using defaults")
            policy_data = {
                "title": metadata.get("filename", "Untitled Policy"),
                "policy_type": metadata.get("policy_type", "General"),
                "departments": metadata.get("departments", [])
            }
        
        policy_id = str(uuid.uuid4())
        
        # Create Policy node
        policy_query = """
        CREATE (p:Policy {
            id: $id,
            title: $title,
            type: $type,
            effective_date: date($effective_date),
            version: '1.0',
            status: 'active',
            text: $text,
            created_at: datetime()
        })
        RETURN p
        """
        
        self.graph.query(policy_query, {
            "id": policy_id,
            "title": policy_data.get("title", "Untitled"),
            "type": policy_data.get("policy_type", "General"),
            "effective_date": policy_data.get("effective_date", "2024-01-01"),
            "text": full_text[:1000]
        })
        
        # Link to Departments
        departments = policy_data.get("departments", []) or metadata.get("departments", [])
        linked_depts = []
        
        for dept_name in departments:
            link_query = """
            MATCH (p:Policy {id: $policy_id})
            MATCH (d:Department)
            WHERE toLower(d.name) CONTAINS toLower($dept_name)
            MERGE (p)-[:APPLIES_TO]->(d)
            RETURN d.name as linked_dept
            """
            result = self.graph.query(link_query, {
                "policy_id": policy_id,
                "dept_name": dept_name
            })
            
            if result:
                linked_depts.append(result[0]['linked_dept'])
                logger.info(f"✅ Linked policy to department: {result[0]['linked_dept']}")
            else:
                logger.warning(f"⚠️  Department '{dept_name}' not found in graph")
        
        return {
            "status": "success",
            "document_type": "policy",
            "policy_id": policy_id,
            "title": policy_data.get("title"),
            "linked_departments": linked_depts
        }

    async def _process_general_document(self, documents: List[Document], metadata: Dict) -> dict:
        """Process general document using existing LLMGraphTransformer."""
        logger.info("Processing as general document...")
        
        # Use existing generic extraction
        if not self.transformer:
            try:
                self.transformer = LLMGraphTransformer(llm=self.llm)
            except NotImplementedError as e:
                logger.error(f"LLM graph transformation failed to initialize: {e}")
                raise NotImplementedError(
                    "The configured LLM provider does not support structured output required for graph extraction. "
                    "Please use OpenAI or a supported model."
                ) from e

        graph_documents = self.transformer.convert_to_graph_documents(documents)
        
        # Write to Neo4j
        self.graph.add_graph_documents(graph_documents)
        
        total_nodes = sum(len(doc.nodes) for doc in graph_documents)
        total_relationships = sum(len(doc.relationships) for doc in graph_documents)
        
        return {
            "status": "success",
            "document_type": "general",
            "nodes_created": total_nodes,
            "relationships_created": total_relationships,
            "pages_processed": len(documents)
        }

    async def process_pdf(self, file_path: str, metadata: Dict = None) -> dict:
        """
        Enhanced PDF processing with document type awareness.
        
        Args:
            file_path: Path to PDF
            metadata: Optional metadata (doc_type, client_name, departments, etc.)
        
        Returns:
            dict: Processing results with document-specific information
        """
        metadata = metadata or {}
        
        try:
            logger.info(f"Starting ingestion for file: {file_path}")
            
            # 1. Extract Text
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            logger.info(f"Extracted {len(documents)} pages from PDF")
            
            # 2. Classify document type
            doc_type = metadata.get("doc_type") or await self._classify_document(documents)
            
            # 3. Route to specialized processor
            if doc_type == "contract":
                result = await self._process_contract(documents, metadata)
            elif doc_type == "policy":
                result = await self._process_policy(documents, metadata)
            else:
                result = await self._process_general_document(documents, metadata)
            
            logger.info(f"✅ Ingestion complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            raise e


# Global instance
ingestion_service = IngestionService()

