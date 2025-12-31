"""
LangGraph workflow definition for startup analysis.

Implements a directed cyclic graph (DCG) with loop support.
"""

import time
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from src.orchestration.state import create_initial_state
from src.orchestration.nodes import (
    analyst_node,
    researcher_node,
    strategist_node,
    parallel_analysis_node,
    strategist_coordination_node,
    strategist_synthesis_node,
)
from src.orchestration.edges import route_after_coordination
from src.observability.logger import get_logger
from src.observability.tracer import trace_span
from src.observability.metrics import record_ticket_processed

logger = get_logger(__name__)


def create_analysis_graph():
    """
    Create the LangGraph workflow for startup analysis.

    Workflow (OPTIMIZED with Dynamic Research Coordination):
    1. Parallel Analysis → Analyst, Researcher, and Risk Analyst run concurrently (SAVES 15-20s)
    2. Strategist Coordination → reviews all research, decides:
       - If gaps identified: requests targeted follow-up research, loops back (up to max_coordination_iterations)
       - If sufficient: proceeds to synthesis
    3. Strategist Synthesis → creates final GTM plan

    Returns:
        Compiled StateGraph
    """
    logger.info("creating_analysis_graph", optimization="parallel_execution_with_dynamic_coordination")

    # Create state graph
    workflow = StateGraph(dict)

    # Add nodes
    # OPTIMIZATION: Use parallel_analysis_node (Analyst + Researcher + Risk Analyst run concurrently)
    workflow.add_node("parallel_analysis", parallel_analysis_node)
    workflow.add_node("strategist_coordination", strategist_coordination_node)
    workflow.add_node("strategist_synthesis", strategist_synthesis_node)

    # Define edges
    # Start with parallel analysis (3 agents run concurrently)
    workflow.set_entry_point("parallel_analysis")
    workflow.add_edge("parallel_analysis", "strategist_coordination")

    # Conditional edge after coordination (COORDINATION LOOP LOGIC)
    workflow.add_conditional_edges(
        "strategist_coordination",
        route_after_coordination,
        {
            "coordination": "strategist_coordination",  # Loop back for more research
            "synthesis": "strategist_synthesis",        # Proceed to final synthesis
        },
    )

    # End after synthesis
    workflow.add_edge("strategist_synthesis", END)

    logger.info("analysis_graph_created", optimization="parallel_execution_with_dynamic_coordination")

    return workflow.compile()


class AnalysisWorkflow:
    """
    Workflow orchestrator for startup analysis.

    Manages the complete analysis lifecycle with observability.
    """

    def __init__(self):
        """Initialize the workflow."""
        self.graph = create_analysis_graph()
        logger.info("analysis_workflow_initialized")

    async def execute(
        self,
        analysis_id: str,
        correlation_id: str,
        x_brand: str,
        y_market: str,
        description: str = None,
    ) -> Dict[str, Any]:
        """
        Execute the complete startup analysis workflow.

        Args:
            analysis_id: Unique analysis identifier
            correlation_id: Correlation ID for tracing
            x_brand: The "X" brand (e.g., "Uber")
            y_market: The "Y" market (e.g., "Dog Walkers")
            description: Optional additional description

        Returns:
            Final state with complete analysis
        """
        with trace_span(
            "workflow.execute",
            {
                "analysis_id": analysis_id,
                "correlation_id": correlation_id,
                "business_idea": f"{x_brand} for {y_market}",
            },
        ):
            start_time = time.time()

            logger.info(
                "workflow_started",
                analysis_id=analysis_id,
                correlation_id=correlation_id,
                x_brand=x_brand,
                y_market=y_market,
            )

            try:
                # Create initial state
                state = create_initial_state(
                    analysis_id=analysis_id,
                    correlation_id=correlation_id,
                    x_brand=x_brand,
                    y_market=y_market,
                    description=description,
                )

                # Set status
                state["status"] = "analyzing"

                # Execute workflow
                # Set recursion_limit to handle max_loops with safety margin
                logger.info("workflow_invoking_graph")
                final_state = await self.graph.ainvoke(
                    state,
                    config={"recursion_limit": 50}
                )

                # Calculate total duration
                duration = time.time() - start_time
                if "metadata" not in final_state:
                    final_state["metadata"] = {}
                final_state["metadata"]["total_duration_seconds"] = duration

                # Record metrics
                routing = final_state.get("routing", {})
                record_ticket_processed(
                    category=routing.get("assigned_agent", "unknown"),
                    urgency=routing.get("urgency", "medium"),
                    duration=duration,
                )

                logger.info(
                    "workflow_completed",
                    analysis_id=analysis_id,
                    status=final_state.get("status"),
                    duration_seconds=duration,
                    coordination_iterations=final_state.get("coordination_iteration", 0),
                    follow_up_research_count=len(final_state.get("follow_up_research", [])),
                    viability_score=final_state.get("strategist_plan", {}).get("viability_score"),
                )

                return final_state

            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    "workflow_failed",
                    analysis_id=analysis_id,
                    error=str(e),
                    error_type=type(e).__name__,
                    duration_seconds=duration,
                )

                # Return error state
                error_state = state if 'state' in locals() else {}
                if "metadata" not in error_state:
                    error_state["metadata"] = {}
                error_state["metadata"]["total_duration_seconds"] = duration
                error_state["metadata"]["error_count"] = error_state.get("metadata", {}).get("error_count", 0) + 1

                error_state["status"] = "failed"
                error_state["final_recommendation"] = f"Analysis failed: {str(e)}"
                error_state["requires_human_review"] = True

                raise


# Global workflow instance
_workflow: AnalysisWorkflow = None


def get_workflow() -> AnalysisWorkflow:
    """
    Get the global workflow instance.

    Returns:
        AnalysisWorkflow instance
    """
    global _workflow
    if _workflow is None:
        _workflow = AnalysisWorkflow()
    return _workflow


async def analyze_startup(
    analysis_id: str,
    correlation_id: str,
    x_brand: str,
    y_market: str,
    description: str = None,
) -> Dict[str, Any]:
    """
    Convenience function to analyze a startup idea.

    This is the main entry point for analysis.

    Args:
        analysis_id: Unique analysis identifier
        correlation_id: Correlation ID for tracing
        x_brand: The "X" brand
        y_market: The "Y" market
        description: Optional description

    Returns:
        Final analysis state
    """
    workflow = get_workflow()
    return await workflow.execute(
        analysis_id=analysis_id,
        correlation_id=correlation_id,
        x_brand=x_brand,
        y_market=y_market,
        description=description,
    )
