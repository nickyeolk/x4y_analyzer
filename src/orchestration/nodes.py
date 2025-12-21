"""
Node wrapper functions for LangGraph workflow.

Each node corresponds to an agent execution step.
"""

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
