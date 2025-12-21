"""
FastAPI application initialization and configuration.
"""

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


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
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
