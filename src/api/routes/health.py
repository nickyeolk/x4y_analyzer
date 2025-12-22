"""
Health check endpoints.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
from pathlib import Path

from src.api.models.responses import HealthResponse
from config.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        Health status and application info
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/readiness", response_model=HealthResponse)
async def readiness_check() -> HealthResponse:
    """
    Readiness check endpoint for Kubernetes/load balancers.

    Returns:
        Readiness status
    """
    # In a real app, check dependencies (DB, LLM API, etc.)
    return HealthResponse(
        status="ready",
        version="0.1.0",
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/debug/rag")
async def rag_debug():
    """
    Debug endpoint to check RAG vector store status.

    Returns:
        RAG configuration and vector store status
    """
    vector_store_path = Path(settings.rag_vector_store_path)
    kb_path = Path(settings.rag_knowledge_base_path)

    # Check vector store
    vs_status = {
        "path": str(vector_store_path),
        "exists": vector_store_path.exists(),
        "is_directory": vector_store_path.is_dir() if vector_store_path.exists() else False,
        "files": [],
    }

    if vector_store_path.exists() and vector_store_path.is_dir():
        vs_status["files"] = [f.name for f in vector_store_path.glob("*")]

    # Check knowledge base
    kb_status = {
        "path": str(kb_path),
        "exists": kb_path.exists(),
        "is_directory": kb_path.is_dir() if kb_path.exists() else False,
        "txt_files": [],
    }

    if kb_path.exists() and kb_path.is_dir():
        kb_status["txt_files"] = [f.name for f in kb_path.glob("*.txt")]

    # Try to load RAG tool and check status
    rag_tool_status = {"initialized": False, "error": None}
    try:
        from src.tools.marketing_rag import get_rag_tool
        rag_tool = get_rag_tool()
        rag_tool_status["initialized"] = rag_tool.vectorstore is not None
        rag_tool_status["has_embeddings"] = rag_tool.embeddings is not None
    except Exception as e:
        rag_tool_status["error"] = str(e)

    return {
        "rag_config": {
            "vector_store_path": settings.rag_vector_store_path,
            "knowledge_base_path": settings.rag_knowledge_base_path,
            "chunk_size": settings.rag_chunk_size,
            "chunk_overlap": settings.rag_chunk_overlap,
        },
        "vector_store": vs_status,
        "knowledge_base": kb_status,
        "rag_tool": rag_tool_status,
    }
