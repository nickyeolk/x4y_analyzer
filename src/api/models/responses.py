"""Response models for the API."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class BrandDNAResponse(BaseModel):
    """Brand DNA analysis response."""

    brand_name: str
    core_strengths: List[str] = Field(default_factory=list)
    business_model: str = ""
    key_differentiators: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    success_factors: List[str] = Field(default_factory=list)
    summary: str = ""
    confidence: float = 0.0


class MarketResearchResponse(BaseModel):
    """Market research response."""

    market_name: str
    market_size: Optional[str] = None
    competitor_count: int = 0
    competitors: List[str] = Field(default_factory=list)
    saturation_level: str = "unknown"
    market_trends: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    barriers: List[str] = Field(default_factory=list)
    summary: str = ""


class CritiqueResponse(BaseModel):
    """Skeptic critique response."""

    approved: bool = False
    concerns: List[str] = Field(default_factory=list)
    fatal_flaws: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    loop_back_reason: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""


class GTMPlanResponse(BaseModel):
    """GTM plan response."""

    target_audience: str = ""
    value_proposition: str = ""
    pricing_strategy: str = ""
    distribution_channels: List[str] = Field(default_factory=list)
    marketing_hooks: List[str] = Field(default_factory=list)
    competitive_advantages: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)
    timeline: str = ""
    viability_score: float = 0.0
    summary: str = ""


class AnalysisMetadataResponse(BaseModel):
    """Analysis metadata response."""

    token_usage: Dict[str, Any] = Field(default_factory=dict)
    total_duration_seconds: float = 0.0
    cost_usd: float = 0.0
    loop_count: int = 0


class AnalysisResponse(BaseModel):
    """Complete analysis response."""

    analysis_id: str
    correlation_id: str
    status: str = "pending"
    business_idea: Dict[str, str]

    # Agent results
    analyst_insights: Optional[BrandDNAResponse] = None
    researcher_findings: Optional[MarketResearchResponse] = None
    skeptic_critique: Optional[CritiqueResponse] = None
    strategist_plan: Optional[GTMPlanResponse] = None

    # Metadata
    metadata: AnalysisMetadataResponse
    loop_count: int = 0
    skeptic_approved: bool = False

    # Final output
    final_recommendation: str = ""
    requires_human_review: bool = False

    # Observability
    trace_url: Optional[str] = None
    langsmith_url: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "analysis_id": "A-abc12345",
                "correlation_id": "CID-def67890",
                "status": "completed",
                "business_idea": {
                    "x_brand": "Uber",
                    "y_market": "Dog Walkers",
                    "full_idea": "Uber for Dog Walkers",
                },
                "loop_count": 1,
                "skeptic_approved": True,
                "metadata": {
                    "total_duration_seconds": 18.5,
                    "cost_usd": 0.023,
                    "loop_count": 1,
                },
            }
        }


class StreamEvent(BaseModel):
    """SSE stream event."""

    event: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "event": "agent_started",
                "data": {"agent": "analyst", "status": "running"},
                "timestamp": "2025-12-20T19:30:45.123Z",
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type")
    correlation_id: Optional[str] = None
    analysis_id: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "error": "Analysis failed: Invalid API key",
                "error_type": "AuthenticationError",
                "correlation_id": "CID-abc123",
            }
        }
