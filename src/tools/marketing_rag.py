"""
RAG tool for marketing frameworks and knowledge base.

Provides semantic search over marketing pitfalls, frameworks, and best practices.
"""

from typing import Dict, Any, List, Optional
import os
from pathlib import Path

from config.settings import settings
from src.tools.base import BaseTool, ToolInput, ToolOutput
from src.observability.decorators import trace_tool
from src.observability.logger import get_logger

logger = get_logger(__name__)


class MarketingRAGTool(BaseTool):
    """
    RAG tool for marketing frameworks and knowledge.

    Uses FAISS vector store for semantic search over marketing documents.
    """

    def __init__(self, vector_store_path: Optional[str] = None):
        """
        Initialize RAG tool.

        Args:
            vector_store_path: Path to FAISS vector store
        """
        super().__init__(
            name="marketing_rag",
            description="Semantic search over marketing frameworks, pitfalls, and best practices knowledge base using RAG."
        )
        self.vector_store_path = vector_store_path or settings.rag_vector_store_path
        self.vectorstore = None
        self.embeddings = None

        self._load_vectorstore()

    def _load_vectorstore(self):
        """Initialize or load vector store."""
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_openai import OpenAIEmbeddings

            vector_store_file = Path(self.vector_store_path)

            # Debug: Check what files exist
            logger.info(
                "rag_load_attempt",
                vector_store_path=str(self.vector_store_path),
                path_exists=vector_store_file.exists(),
                path_is_dir=vector_store_file.is_dir() if vector_store_file.exists() else False,
                parent_exists=vector_store_file.parent.exists(),
            )

            # List files in vector store directory if it exists
            if vector_store_file.exists() and vector_store_file.is_dir():
                files = list(vector_store_file.glob("*"))
                logger.info(
                    "rag_vectorstore_files",
                    path=str(self.vector_store_path),
                    files=[f.name for f in files],
                    file_count=len(files),
                )

            # Initialize embeddings
            logger.info("rag_initializing_embeddings", api_base="https://openrouter.ai/api/v1")
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.openrouter_api_key,
                openai_api_base="https://openrouter.ai/api/v1",
            )
            logger.info("rag_embeddings_initialized")

            if vector_store_file.exists():
                # Load existing vector store
                logger.info("rag_loading_faiss", path=str(self.vector_store_path))
                self.vectorstore = FAISS.load_local(
                    self.vector_store_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True,  # We trust our own vector store
                )
                logger.info(
                    "rag_vectorstore_loaded",
                    path=self.vector_store_path,
                    success=True,
                )
            else:
                logger.warning(
                    "rag_vectorstore_not_found",
                    path=self.vector_store_path,
                    message="Vector store not found, will need to be created",
                )
                self.vectorstore = None

        except Exception as e:
            logger.error(
                "rag_initialization_failed",
                error=str(e),
                error_type=type(e).__name__,
                vector_store_path=str(self.vector_store_path),
                traceback=True,
            )
            self.vectorstore = None

    async def _execute(self, input: ToolInput) -> Dict[str, Any]:
        """
        Execute RAG search.

        Args:
            input: Tool input with parameters:
                - query: Search query
                - k: Number of results to return (default: 3)
                - score_threshold: Minimum relevance score (default: 0.5)

        Returns:
            Dict with retrieved documents
        """
        # Retry loading vector store if it wasn't available during initialization
        if not self.vectorstore:
            logger.warning(
                "rag_retry_load_needed",
                message="Vector store not loaded during init, attempting to reload",
                vector_store_path=self.vector_store_path,
            )
            self._load_vectorstore()

            if self.vectorstore:
                logger.info(
                    "rag_retry_load_success",
                    message="Vector store successfully loaded on retry",
                )
            else:
                logger.error(
                    "rag_retry_load_failed",
                    message="Vector store still not available after retry",
                    vector_store_path=self.vector_store_path,
                )

        if not self.vectorstore:
            error_msg = f"Vector store not initialized at path: {self.vector_store_path}. Please ensure vector store is built and path is correct."
            logger.error("rag_execute_failed", error=error_msg)
            raise RuntimeError(error_msg)

        query = input.parameters.get("query")
        if not query:
            raise ValueError("Query parameter is required")

        k = input.parameters.get("k", 3)
        score_threshold = input.parameters.get("score_threshold", 0.5)

        logger.info(
            "rag_search_started",
            query=query,
            k=k,
            score_threshold=score_threshold,
        )

        # Perform similarity search with scores
        docs_and_scores = self.vectorstore.similarity_search_with_score(
            query,
            k=k,
        )

        # Log raw scores for debugging
        if docs_and_scores:
            logger.info(
                "rag_similarity_scores",
                query=query[:100],
                scores=[float(score) for _, score in docs_and_scores],
                min_score=float(min(score for _, score in docs_and_scores)),
                max_score=float(max(score for _, score in docs_and_scores)),
            )

        # Filter by score threshold
        # Note: FAISS with L2 distance returns lower scores for better matches
        # For cosine similarity, higher scores are better
        # We're using a permissive threshold since we want relevant frameworks
        filtered_docs = [
            (doc, score) for doc, score in docs_and_scores
            if score >= score_threshold
        ]

        # Format results
        results = []
        for idx, (doc, score) in enumerate(filtered_docs, 1):
            results.append({
                "rank": idx,
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": float(score),
            })

        logger.info(
            "rag_search_completed",
            query=query,
            results_count=len(results),
            total_candidates=len(docs_and_scores),
        )

        return {
            "query": query,
            "documents": results,
            "results_count": len(results),
            "metadata": {
                "k": k,
                "score_threshold": score_threshold,
            }
        }


def get_rag_tool() -> MarketingRAGTool:
    """
    Get configured RAG tool instance.

    Returns:
        MarketingRAGTool instance
    """
    return MarketingRAGTool()
