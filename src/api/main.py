"""
FastAPI application initialization and configuration.
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from config.settings import settings
from config.logging_config import configure_logging
from config.observability import configure_observability

from src.api.routes import health, metrics, analysis
from src.api.middleware.correlation_id import CorrelationIdMiddleware
from src.api.middleware.error_handler import error_handler_middleware

from src.observability.logger import get_logger

# Configure observability before creating the app
configure_logging()
configure_observability()

logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Startup Analyzer",
    description="AI-powered startup idea analyzer with multi-agent workflow and real-time streaming",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, configure specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add correlation ID middleware
app.add_middleware(CorrelationIdMiddleware)

# Add error handler middleware
app.middleware("http")(error_handler_middleware)

# Instrument with OpenTelemetry
if settings.otel_enabled:
    FastAPIInstrumentor.instrument_app(app)

# Include routers
app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(analysis.router)


async def ensure_vector_store():
    """Ensure vector store exists, build if necessary."""
    vector_store_path = Path(settings.rag_vector_store_path)

    # Check if vector store already exists
    if vector_store_path.exists():
        logger.info(
            "vector_store_found",
            path=str(vector_store_path),
            message="Vector store already exists, skipping build"
        )
        return

    # Vector store doesn't exist - need to build it
    kb_path = Path(settings.rag_knowledge_base_path)

    if not kb_path.exists() or not any(kb_path.glob("*.txt")):
        logger.warning(
            "vector_store_build_skipped",
            reason="no_knowledge_base",
            kb_path=str(kb_path),
            message="Knowledge base directory empty or missing, RAG will not be available"
        )
        return

    try:
        logger.info(
            "vector_store_building",
            kb_path=str(kb_path),
            vector_store_path=str(vector_store_path),
            message="Building vector store from knowledge base..."
        )

        # Import here to avoid startup overhead when vector store exists
        from langchain_community.document_loaders import DirectoryLoader, TextLoader
        from langchain_community.vectorstores import FAISS
        from langchain_openai import OpenAIEmbeddings
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        # Load documents
        loader = DirectoryLoader(
            str(kb_path),
            glob="**/*.txt",
            loader_cls=TextLoader,
        )
        documents = loader.load()

        if not documents:
            logger.warning(
                "vector_store_build_skipped",
                reason="no_documents",
                message="No documents found in knowledge base"
            )
            return

        logger.info("vector_store_documents_loaded", count=len(documents))

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.rag_chunk_size,
            chunk_overlap=settings.rag_chunk_overlap,
            length_function=len,
        )
        splits = text_splitter.split_documents(documents)
        logger.info("vector_store_chunks_created", count=len(splits))

        # Initialize embeddings
        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
        )

        # Create vector store
        vectorstore = FAISS.from_documents(splits, embeddings)

        # Save vector store
        vector_store_path.parent.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(vector_store_path))

        logger.info(
            "vector_store_built",
            documents=len(documents),
            chunks=len(splits),
            path=str(vector_store_path),
            message="Vector store built successfully"
        )

    except Exception as e:
        logger.error(
            "vector_store_build_failed",
            error=str(e),
            error_type=type(e).__name__,
            message="Failed to build vector store, RAG will not be available"
        )


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    # Build vector store if it doesn't exist
    await ensure_vector_store()

    logger.info(
        "application_started",
        environment=settings.app_env,
        version="1.0.0",
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("application_shutdown")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Startup Analyzer",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "description": "AI-powered startup idea analyzer",
    }
