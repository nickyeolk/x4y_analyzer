"""
Edge routing logic for LangGraph workflow.

Defines conditional routing between nodes.
"""

from typing import Dict, Any, Literal

from src.observability.logger import get_logger

logger = get_logger(__name__)


def route_after_skeptic(state: Dict[str, Any]) -> Literal["analyst", "strategist"]:
    """
    Route after skeptic node - decides whether to loop or continue.

    This is the critical routing function that enables cyclic workflows.

    Args:
        state: Current workflow state

    Returns:
        Next node name: "analyst" (loop back) or "strategist" (continue)
    """
    critique = state.get("skeptic_critique", {})
    approved = critique.get("approved", False)
    loop_count = state.get("loop_count", 0)
    max_loops = state.get("max_loops", 3)

    logger.info(
        "routing_decision",
        approved=approved,
        loop_count=loop_count,
        max_loops=max_loops,
    )

    # Decision logic
    if approved:
        # Skeptic approved - proceed to strategy
        logger.info(
            "routing_to_strategist",
            reason="skeptic_approved",
        )
        return "strategist"
    elif loop_count >= max_loops - 1:
        # Max loops reached - force proceed (shouldn't happen as skeptic should approve)
        logger.warning(
            "routing_to_strategist_forced",
            reason="max_loops_reached",
            loop_count=loop_count,
        )
        return "strategist"
    else:
        # Not approved and loops remaining - loop back to analyst
        loop_back_reason = critique.get("loop_back_reason", "Unknown reason")
        logger.info(
            "routing_to_analyst",
            reason="skeptic_rejected",
            loop_back_reason=loop_back_reason,
            new_iteration=loop_count + 1,
        )
        return "analyst"


def route_after_coordination(state: Dict[str, Any]) -> Literal["coordination", "synthesis"]:
    """
    Route after strategist coordination node - decides whether to loop or synthesize.

    This enables dynamic research coordination where the Strategist can request
    targeted follow-up research from specific agents before creating the final plan.

    Args:
        state: Current workflow state

    Returns:
        Next node name: "coordination" (loop back for more research) or "synthesis" (create final plan)
    """
    ready_for_synthesis = state.get("ready_for_synthesis", False)
    coordination_iteration = state.get("coordination_iteration", 0)
    max_iterations = state.get("max_coordination_iterations", 3)

    logger.info(
        "routing_decision_coordination",
        ready_for_synthesis=ready_for_synthesis,
        coordination_iteration=coordination_iteration,
        max_iterations=max_iterations,
    )

    # Decision logic
    if ready_for_synthesis:
        # Strategist has sufficient research - proceed to synthesis
        logger.info(
            "routing_to_synthesis",
            reason="strategist_ready",
            coordination_iteration=coordination_iteration,
        )
        return "synthesis"
    elif coordination_iteration >= max_iterations:
        # Max iterations reached - force synthesis
        logger.warning(
            "routing_to_synthesis_forced",
            reason="max_coordination_iterations_reached",
            coordination_iteration=coordination_iteration,
        )
        return "synthesis"
    else:
        # Need more research - loop back to coordination
        logger.info(
            "routing_to_coordination",
            reason="follow_up_research_requested",
            new_iteration=coordination_iteration + 1,
        )
        return "coordination"


def should_continue(state: Dict[str, Any]) -> bool:
    """
    Helper function to check if workflow should continue.

    Args:
        state: Current workflow state

    Returns:
        True if workflow should continue, False otherwise
    """
    status = state.get("status", "pending")
    return status not in ["completed", "failed"]
