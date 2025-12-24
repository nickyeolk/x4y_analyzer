"""
Analysis API routes with SSE streaming support.

Provides endpoints for analyzing startup ideas with real-time progress updates.
"""

import asyncio
import json
import uuid
from typing import AsyncGenerator, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from src.api.models.requests import AnalysisRequest
from src.api.models.responses import (
    AnalysisResponse,
    BrandDNAResponse,
    MarketResearchResponse,
    CritiqueResponse,
    GTMPlanResponse,
    AnalysisMetadataResponse,
    StreamEvent,
    ErrorResponse,
)
from src.orchestration.graph import analyze_startup
from src.observability.logger import get_logger
from src.observability.context import get_correlation_id

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["analysis"])


def generate_analysis_id() -> str:
    """Generate a unique analysis ID."""
    return f"A-{uuid.uuid4().hex[:8]}"


async def stream_analysis_events(
    analysis_id: str,
    correlation_id: str,
    x_brand: str,
    y_market: str,
    description: str = None,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Stream analysis events via SSE.

    This generator yields events as the analysis progresses through
    each agent in the workflow.

    Args:
        analysis_id: Analysis identifier
        correlation_id: Correlation ID for tracing
        x_brand: The "X" brand
        y_market: The "Y" market
        description: Optional description

    Yields:
        SSE events with analysis progress
    """
    try:
        # Send start event
        yield {
            "event": "analysis_started",
            "data": json.dumps({
                "analysis_id": analysis_id,
                "correlation_id": correlation_id,
                "business_idea": f"{x_brand} for {y_market}",
                "timestamp": datetime.utcnow().isoformat(),
            })
        }

        # Note: For true real-time streaming, we'd need to modify the workflow
        # to yield events during execution. For now, we'll execute and then
        # send the complete result. In a future iteration, you can add
        # callback handlers to LangGraph for true streaming.

        # Execute analysis
        logger.info(
            "api_analysis_started",
            analysis_id=analysis_id,
            x_brand=x_brand,
            y_market=y_market,
        )

        # Send agent events (simulated for now)
        agents = ["analyst", "researcher", "skeptic"]
        for agent in agents:
            yield {
                "event": "agent_started",
                "data": json.dumps({
                    "agent": agent,
                    "status": "running",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            }
            await asyncio.sleep(0.1)  # Small delay for UX

        # Execute the workflow with keepalive
        # Create a task for the workflow execution
        workflow_task = asyncio.create_task(
            analyze_startup(
                analysis_id=analysis_id,
                correlation_id=correlation_id,
                x_brand=x_brand,
                y_market=y_market,
                description=description,
            )
        )

        # Send keepalive pings while workflow is running to prevent timeout
        keepalive_counter = 0
        max_wait_seconds = 600  # 10 minute timeout

        while not workflow_task.done():
            await asyncio.sleep(10)  # Ping every 10 seconds
            if not workflow_task.done():
                keepalive_counter += 1
                elapsed = keepalive_counter * 10

                # Check timeout
                if elapsed >= max_wait_seconds:
                    workflow_task.cancel()
                    logger.error(
                        "api_analysis_timeout",
                        analysis_id=analysis_id,
                        elapsed_seconds=elapsed,
                    )
                    raise asyncio.TimeoutError(f"Analysis exceeded {max_wait_seconds} seconds")

                yield {
                    "event": "keepalive",
                    "data": json.dumps({
                        "message": "Analysis in progress",
                        "elapsed_seconds": elapsed,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                }

                logger.debug(
                    "api_keepalive_sent",
                    analysis_id=analysis_id,
                    elapsed_seconds=elapsed,
                )

        # Get the result
        result = await workflow_task

        logger.info(
            "api_workflow_completed",
            analysis_id=analysis_id,
            elapsed_seconds=keepalive_counter * 10,
        )

        # Send agent completion events
        for agent in agents:
            yield {
                "event": "agent_completed",
                "data": json.dumps({
                    "agent": agent,
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            }

        # Check if loop occurred
        if result.get("loop_count", 0) > 0:
            yield {
                "event": "loop_triggered",
                "data": json.dumps({
                    "iteration": result["loop_count"],
                    "reason": result.get("skeptic_critique", {}).get("loop_back_reason", "Quality improvement needed"),
                    "timestamp": datetime.utcnow().isoformat(),
                })
            }

        # Strategist
        yield {
            "event": "agent_started",
            "data": json.dumps({
                "agent": "strategist",
                "status": "running",
                "timestamp": datetime.utcnow().isoformat(),
            })
        }

        yield {
            "event": "agent_completed",
            "data": json.dumps({
                "agent": "strategist",
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
            })
        }

        # Send completion event with full result
        yield {
            "event": "analysis_completed",
            "data": json.dumps({
                "analysis_id": analysis_id,
                "status": result.get("status"),
                "viability_score": result.get("strategist_plan", {}).get("viability_score"),
                "loop_count": result.get("loop_count", 0),
                "duration_seconds": result.get("metadata", {}).get("total_duration_seconds"),
                "cost_usd": result.get("metadata", {}).get("cost_usd"),
                "timestamp": datetime.utcnow().isoformat(),
            })
        }

        # Send final result
        logger.info(
            "api_sending_final_result",
            analysis_id=analysis_id,
            status=result.get("status"),
            has_strategist_plan=bool(result.get("strategist_plan")),
        )

        yield {
            "event": "result",
            "data": json.dumps(result, default=str)
        }

        logger.info(
            "api_result_event_yielded",
            analysis_id=analysis_id,
            message="Result event sent, stream should close after this",
        )

        logger.info(
            "api_analysis_completed",
            analysis_id=analysis_id,
            status=result.get("status"),
            viability_score=result.get("strategist_plan", {}).get("viability_score"),
        )

        # Generator function ends here, stream should close

    except Exception as e:
        logger.error(
            "api_analysis_failed",
            analysis_id=analysis_id,
            error=str(e),
            error_type=type(e).__name__,
        )

        # Send error event
        yield {
            "event": "error",
            "data": json.dumps({
                "analysis_id": analysis_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat(),
            })
        }

        logger.info(
            "api_error_event_sent",
            analysis_id=analysis_id,
            message="Error event sent, stream will close",
        )


@router.post("/analyze/stream")
async def analyze_stream(request: AnalysisRequest) -> EventSourceResponse:
    """
    Analyze a startup idea with SSE streaming.

    This endpoint streams events as the analysis progresses through each agent.

    Args:
        request: Analysis request with x_brand and y_market

    Returns:
        SSE stream with real-time progress updates
    """
    analysis_id = generate_analysis_id()
    correlation_id = f"CID-{uuid.uuid4().hex[:8]}"

    logger.info(
        "api_analyze_stream_request",
        analysis_id=analysis_id,
        correlation_id=correlation_id,
        x_brand=request.x_brand,
        y_market=request.y_market,
    )

    return EventSourceResponse(
        stream_analysis_events(
            analysis_id=analysis_id,
            correlation_id=correlation_id,
            x_brand=request.x_brand,
            y_market=request.y_market,
            description=request.description,
        )
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyze a startup idea (non-streaming).

    This endpoint executes the complete analysis and returns the final result.

    Args:
        request: Analysis request with x_brand and y_market

    Returns:
        Complete analysis result

    Raises:
        HTTPException: If analysis fails
    """
    analysis_id = generate_analysis_id()
    correlation_id = f"CID-{uuid.uuid4().hex[:8]}"

    logger.info(
        "api_analyze_request",
        analysis_id=analysis_id,
        correlation_id=correlation_id,
        x_brand=request.x_brand,
        y_market=request.y_market,
    )

    try:
        # Execute analysis
        result = await analyze_startup(
            analysis_id=analysis_id,
            correlation_id=correlation_id,
            x_brand=request.x_brand,
            y_market=request.y_market,
            description=request.description,
        )

        # Convert to response model
        response = AnalysisResponse(
            analysis_id=result["analysis_id"],
            correlation_id=result["correlation_id"],
            status=result["status"],
            business_idea=result["business_idea"],
            analyst_insights=BrandDNAResponse(**result["analyst_insights"]) if result.get("analyst_insights") else None,
            researcher_findings=MarketResearchResponse(**result["researcher_findings"]) if result.get("researcher_findings") else None,
            skeptic_critique=CritiqueResponse(**result["skeptic_critique"]) if result.get("skeptic_critique") else None,
            strategist_plan=GTMPlanResponse(**result["strategist_plan"]) if result.get("strategist_plan") else None,
            metadata=AnalysisMetadataResponse(**result.get("metadata", {})),
            loop_count=result.get("loop_count", 0),
            skeptic_approved=result.get("skeptic_approved", False),
            final_recommendation=result.get("final_recommendation", ""),
            requires_human_review=result.get("requires_human_review", False),
            # TODO: Add LangSmith URL generation
            trace_url=None,
            langsmith_url=None,
        )

        logger.info(
            "api_analyze_success",
            analysis_id=analysis_id,
            status=response.status,
            viability_score=response.strategist_plan.viability_score if response.strategist_plan else None,
        )

        return response

    except Exception as e:
        logger.error(
            "api_analyze_error",
            analysis_id=analysis_id,
            error=str(e),
            error_type=type(e).__name__,
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "error_type": type(e).__name__,
                "analysis_id": analysis_id,
                "correlation_id": correlation_id,
            },
        )


@router.get("/analyze/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str) -> AnalysisResponse:
    """
    Get analysis result by ID.

    Note: This requires implementing a storage layer (database or cache).
    For now, this returns a 501 Not Implemented.

    Args:
        analysis_id: The analysis ID

    Returns:
        Analysis result

    Raises:
        HTTPException: Not implemented yet
    """
    logger.info("api_get_analysis_request", analysis_id=analysis_id)

    # TODO: Implement storage layer
    raise HTTPException(
        status_code=501,
        detail={
            "error": "Analysis storage not implemented yet",
            "message": "Use the /analyze endpoint for synchronous analysis or /analyze/stream for streaming",
        },
    )
