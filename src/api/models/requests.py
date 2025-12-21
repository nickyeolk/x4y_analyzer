"""Request models for the API."""

from typing import Optional
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Request to analyze a startup idea."""

    x_brand: str = Field(
        ...,
        description="The 'X' brand to analyze (e.g., 'Uber')",
        min_length=1,
        max_length=100,
        example="Uber",
    )
    y_market: str = Field(
        ...,
        description="The 'Y' market to target (e.g., 'Dog Walkers')",
        min_length=1,
        max_length=100,
        example="Dog Walkers",
    )
    description: Optional[str] = Field(
        None,
        description="Optional additional description of the idea",
        max_length=500,
        example="On-demand dog walking service with real-time GPS tracking",
    )

    class Config:
        schema_extra = {
            "example": {
                "x_brand": "Uber",
                "y_market": "Dog Walkers",
                "description": "On-demand dog walking service with real-time GPS tracking",
            }
        }


class AnalysisStatusRequest(BaseModel):
    """Request to get analysis status."""

    analysis_id: str = Field(
        ...,
        description="The analysis ID to query",
        example="A-abc12345",
    )
