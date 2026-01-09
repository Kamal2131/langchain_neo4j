"""
Service for ingesting unstructured data (PDFs) into the Neo4j graph.
Uses LLM to extract nodes and relationships.
"""

import os
from typing import List, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from src.core.config import settings
from src.core.logging import get_logger
from src.services.neo4j_service import neo4j_service

logger = get_logger(__name__)


class IngestionService:
    """Service for processing and ingesting documents."""

    def __init__(self):
        self.graph = neo4j_service.get_graph()
        self.llm = self._get_llm()
        self.transformer = None

    def _get_llm(self):
        """Get LLM instance for extraction."""
        llm_config = settings.get_llm_config()
        # Note: Extraction works best with capable models like GPT-4 or good open models
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

    async def process_pdf(self, file_path: str) -> dict:
        """
        Process a PDF file and ingest it into the graph.
        
        Args:
            file_path: Path to the PDF file.
            
        Returns:
            dict: Statistics about the ingestion.
        """
        try:
            logger.info(f"Starting ingestion for file: {file_path}")
            
            # 1. Extract Text
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            logger.info(f"Extracted {len(documents)} pages from PDF")
            
            # 2. Extract Graph Elements (Nodes/Relationships)
            # We combine all pages into one document for context, or process page by page
            # Processing page by page is safer for context limits
            
            total_nodes = 0
            total_relationships = 0
            
            logger.info("Extracting graph data using LLM...")
            
            if not self.transformer:
                try:
                    self.transformer = LLMGraphTransformer(llm=self.llm)
                except NotImplementedError as e:
                    # Fallback or error if LLM provider doesn't support structured output
                    logger.error(f"LLM graph transformation failed to initialize: {e}")
                    raise NotImplementedError(
                        "The configured LLM provider does not support structured output required for graph extraction. "
                        "Please use OpenAI or a supported model."
                    ) from e

            graph_documents = self.transformer.convert_to_graph_documents(documents)
            
            # 3. Write to Neo4j
            logger.info("Writing to Neo4j...")
            self.graph.add_graph_documents(graph_documents)
            
            # Calculate stats
            for doc in graph_documents:
                total_nodes += len(doc.nodes)
                total_relationships += len(doc.relationships)
                
            logger.info(f"Ingestion complete. Added {total_nodes} nodes and {total_relationships} relationships.")
            
            # Cleanup - typically managed by the caller (temp file), but good to be safe
            if os.path.exists(file_path):
                os.remove(file_path)
                
            return {
                "status": "success",
                "nodes_created": total_nodes,
                "relationships_created": total_relationships,
                "pages_processed": len(documents)
            }
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            raise e

# Global instance
ingestion_service = IngestionService()
