"""
Node wrapper functions for LangGraph workflow.

Each node corresponds to an agent execution step.
"""

import asyncio
from typing import Dict, Any

from src.agents.analyst import AnalystAgent
from src.agents.researcher import ResearcherAgent
from src.agents.skeptic import SkepticAgent
from src.agents.strategist import StrategistAgent
from src.observability.logger import get_logger
from src.observability.tracer import trace_span

logger = get_logger(__name__)


# Initialize agents (singleton pattern)
_analyst = None
_researcher = None
_skeptic = None
_strategist = None


def get_analyst() -> AnalystAgent:
    """Get or create Analyst agent instance."""
    global _analyst
    if _analyst is None:
        _analyst = AnalystAgent()
    return _analyst


def get_researcher() -> ResearcherAgent:
    """Get or create Researcher agent instance."""
    global _researcher
    if _researcher is None:
        _researcher = ResearcherAgent()
    return _researcher


def get_skeptic() -> SkepticAgent:
    """Get or create Skeptic agent instance."""
    global _skeptic
    if _skeptic is None:
        _skeptic = SkepticAgent()
    return _skeptic


def get_strategist() -> StrategistAgent:
    """Get or create Strategist agent instance."""
    global _strategist
    if _strategist is None:
        _strategist = StrategistAgent()
    return _strategist


async def analyst_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyst node - analyzes brand DNA.

    Args:
        state: Current workflow state

    Returns:
        Updated state with analyst insights
    """
    # Increment loop count if this is a re-entry (skeptic rejected previous iteration)
    if state.get("skeptic_critique") is not None:
        state["loop_count"] = state.get("loop_count", 0) + 1
        logger.info(
            "analyst_loop_back",
            loop_count=state["loop_count"],
            reason=state.get("skeptic_critique", {}).get("loop_back_reason"),
        )

    with trace_span("node.analyst", {"iteration": state.get("loop_count", 0)}):
        logger.info(
            "node_executing",
            node="analyst",
            iteration=state.get("loop_count", 0),
        )

        analyst = get_analyst()
        state = await analyst.execute(state)

        logger.info(
            "node_completed",
            node="analyst",
            has_insights=state.get("analyst_insights") is not None,
        )

        return state


async def researcher_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Researcher node - investigates market.

    Args:
        state: Current workflow state

    Returns:
        Updated state with researcher findings
    """
    with trace_span("node.researcher", {"iteration": state.get("loop_count", 0)}):
        logger.info(
            "node_executing",
            node="researcher",
            iteration=state.get("loop_count", 0),
        )

        researcher = get_researcher()
        state = await researcher.execute(state)

        logger.info(
            "node_completed",
            node="researcher",
            has_findings=state.get("researcher_findings") is not None,
        )

        return state


async def skeptic_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Skeptic node - critical evaluation and loop decision.

    Args:
        state: Current workflow state

    Returns:
        Updated state with critique and approval decision
    """
    with trace_span("node.skeptic", {"iteration": state.get("loop_count", 0)}):
        logger.info(
            "node_executing",
            node="skeptic",
            iteration=state.get("loop_count", 0),
        )

        skeptic = get_skeptic()
        state = await skeptic.execute(state)

        approved = state.get("skeptic_approved", False)
        logger.info(
            "node_completed",
            node="skeptic",
            approved=approved,
            will_loop=not approved and state.get("loop_count", 0) < state.get("max_loops", 3) - 1,
        )

        return state


async def strategist_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strategist node - GTM strategy synthesis.

    Args:
        state: Current workflow state

    Returns:
        Updated state with GTM plan
    """
    with trace_span("node.strategist", {"iteration": state.get("loop_count", 0)}):
        logger.info(
            "node_executing",
            node="strategist",
            iteration=state.get("loop_count", 0),
        )

        strategist = get_strategist()
        state = await strategist.execute(state)

        logger.info(
            "node_completed",
            node="strategist",
            has_plan=state.get("strategist_plan") is not None,
            viability_score=state.get("strategist_plan", {}).get("viability_score"),
        )

        return state


async def parallel_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    OPTIMIZATION: Run Analyst and Researcher in parallel.

    Since these agents don't depend on each other's outputs, they can
    execute concurrently to save 15-20 seconds per iteration.

    Args:
        state: Current workflow state

    Returns:
        Updated state with both analyst insights and researcher findings
    """
    iteration = state.get("loop_count", 0)

    # Increment loop count if this is a re-entry (skeptic rejected previous iteration)
    if state.get("skeptic_critique") is not None:
        state["loop_count"] = state.get("loop_count", 0) + 1
        iteration = state["loop_count"]
        logger.info(
            "parallel_analysis_loop_back",
            loop_count=iteration,
            reason=state.get("skeptic_critique", {}).get("loop_back_reason"),
        )

    with trace_span("node.parallel_analysis", {"iteration": iteration}):
        logger.info(
            "node_executing",
            node="parallel_analysis",
            iteration=iteration,
            message="Running Analyst and Researcher concurrently",
        )

        # Get agent instances
        analyst = get_analyst()
        researcher = get_researcher()

        # OPTIMIZATION: Run both agents in parallel
        # Each agent gets a copy of the state and updates it independently
        analyst_state, researcher_state = await asyncio.gather(
            analyst.execute(state.copy()),
            researcher.execute(state.copy())
        )

        # Merge results back into the original state
        # The agents update different keys, so no conflicts
        state["analyst_insights"] = analyst_state.get("analyst_insights")
        state["researcher_findings"] = researcher_state.get("researcher_findings")

        # Merge agent interactions
        if "agent_interactions" not in state:
            state["agent_interactions"] = []
        state["agent_interactions"].extend(analyst_state.get("agent_interactions", []))
        state["agent_interactions"].extend(researcher_state.get("agent_interactions", []))

        # Merge metadata (token usage)
        if "metadata" not in state:
            state["metadata"] = {}
        if "token_usage" not in state["metadata"]:
            state["metadata"]["token_usage"] = {}

        # Copy token usage from both agents
        analyst_tokens = analyst_state.get("metadata", {}).get("token_usage", {}).get("analyst", {})
        researcher_tokens = researcher_state.get("metadata", {}).get("token_usage", {}).get("researcher", {})

        if analyst_tokens:
            state["metadata"]["token_usage"]["analyst"] = analyst_tokens
        if researcher_tokens:
            state["metadata"]["token_usage"]["researcher"] = researcher_tokens

        logger.info(
            "node_completed",
            node="parallel_analysis",
            has_analyst_insights=state.get("analyst_insights") is not None,
            has_researcher_findings=state.get("researcher_findings") is not None,
            iteration=iteration,
        )

        return state
