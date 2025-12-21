"""
Application configuration management using Pydantic Settings.
Loads configuration from environment variables with type validation.
"""

from typing import Literal
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    # Application
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Debug mode")

    # LLM Provider (OpenRouter)
    openrouter_api_key: str = Field(default="", description="OpenRouter API key")
    llm_model: str = Field(
        default="openai/gpt-4o",
        description="LLM model to use via OpenRouter",
    )
    llm_max_tokens: int = Field(default=4096, description="Maximum tokens for LLM")
    llm_temperature: float = Field(default=0.7, description="LLM temperature")
    llm_max_retries: int = Field(default=3, description="Maximum retries for LLM calls")
    llm_timeout_seconds: int = Field(default=60, description="LLM request timeout")

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(
        default=60,
        description="Rate limit for requests per minute",
    )
    rate_limit_tokens_per_minute: int = Field(
        default=100000,
        description="Rate limit for tokens per minute",
    )

    # Tools
    tavily_api_key: str = Field(default="", description="Tavily API key")

    # RAG
    rag_knowledge_base_path: str = Field(
        default="data/knowledge_base",
        description="Path to RAG knowledge base documents",
    )
    rag_vector_store_path: str = Field(
        default="data/vector_store",
        description="Path to FAISS vector store",
    )
    rag_chunk_size: int = Field(default=1000, description="Text chunk size for RAG")
    rag_chunk_overlap: int = Field(default=200, description="Chunk overlap for RAG")

    # Observability
    otel_enabled: bool = Field(default=True, description="Enable OpenTelemetry")
    otel_exporter: Literal["console", "jaeger", "otlp"] = Field(
        default="console",
        description="OpenTelemetry exporter type",
    )
    metrics_port: int = Field(default=9090, description="Prometheus metrics port")

    # LangSmith
    langsmith_api_key: str = Field(default="", description="LangSmith API key")
    langsmith_project: str = Field(
        default="startup-analyzer",
        description="LangSmith project name",
    )
    langchain_tracing_v2: bool = Field(
        default=True,
        description="Enable LangChain tracing v2",
    )
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com",
        description="LangSmith API endpoint",
    )

    # Mock Mode
    use_mock_tools: bool = Field(default=True, description="Use mock tools for testing")
    use_mock_llm: bool = Field(default=False, description="Use mock LLM responses")

    # Evaluation
    eval_dataset_path: str = Field(
        default="tests/evaluation/datasets",
        description="Path to evaluation datasets",
    )
    eval_run_on_ci: bool = Field(
        default=True,
        description="Run evaluation in CI",
    )
    eval_sample_size: int = Field(
        default=50,
        description="Sample size for CI evaluation",
    )

    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_reload: bool = Field(default=True, description="Auto-reload in development")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"

    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.app_env == "staging"


# Singleton instance
settings = Settings()
