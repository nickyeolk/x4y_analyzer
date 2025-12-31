"""
Node wrapper functions for LangGraph workflow.

Each node corresponds to an agent execution step.
"""

import asyncio
import json
from typing import Dict, Any
from datetime import datetime

from src.agents.analyst import AnalystAgent
from src.agents.researcher import ResearcherAgent
from src.agents.skeptic import SkepticAgent
from src.agents.risk_analyst import RiskAnalystAgent
from src.agents.strategist import StrategistAgent
from src.observability.logger import get_logger
from src.observability.tracer import trace_span

logger = get_logger(__name__)


# Initialize agents (singleton pattern)
_analyst = None
_researcher = None
_skeptic = None
_risk_analyst = None
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


def get_risk_analyst() -> RiskAnalystAgent:
    """Get or create Risk Analyst agent instance."""
    global _risk_analyst
    if _risk_analyst is None:
        _risk_analyst = RiskAnalystAgent()
    return _risk_analyst


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
    Run Analyst, Researcher, and Risk Analyst in parallel.

    These three agents provide complementary perspectives:
    - Analyst: Brand strengths and competitive advantages
    - Researcher: Market opportunities and competitive landscape
    - Risk Analyst: Threats, risks, and potential failure modes

    Args:
        state: Current workflow state

    Returns:
        Updated state with all three analyses
    """
    with trace_span("node.parallel_research"):
        logger.info(
            "node_executing",
            node="parallel_research",
            message="Running Analyst, Researcher, and Risk Analyst concurrently",
        )

        # Get agent instances
        analyst = get_analyst()
        researcher = get_researcher()
        risk_analyst = get_risk_analyst()

        # Run all three agents in parallel
        analyst_state, researcher_state, risk_state = await asyncio.gather(
            analyst.execute(state.copy()),
            researcher.execute(state.copy()),
            risk_analyst.execute(state.copy())
        )

        # Merge results back into the original state
        state["analyst_insights"] = analyst_state.get("analyst_insights")
        state["researcher_findings"] = researcher_state.get("researcher_findings")
        state["risk_analysis"] = risk_state.get("risk_analysis")

        # Merge agent interactions
        if "agent_interactions" not in state:
            state["agent_interactions"] = []
        state["agent_interactions"].extend(analyst_state.get("agent_interactions", []))
        state["agent_interactions"].extend(researcher_state.get("agent_interactions", []))
        state["agent_interactions"].extend(risk_state.get("agent_interactions", []))

        # Merge metadata (token usage)
        if "metadata" not in state:
            state["metadata"] = {}
        if "token_usage" not in state["metadata"]:
            state["metadata"]["token_usage"] = {}

        # Copy token usage from all three agents
        analyst_tokens = analyst_state.get("metadata", {}).get("token_usage", {}).get("analyst", {})
        researcher_tokens = researcher_state.get("metadata", {}).get("token_usage", {}).get("researcher", {})
        risk_tokens = risk_state.get("metadata", {}).get("token_usage", {}).get("risk_analyst", {})

        if analyst_tokens:
            state["metadata"]["token_usage"]["analyst"] = analyst_tokens
        if researcher_tokens:
            state["metadata"]["token_usage"]["researcher"] = researcher_tokens
        if risk_tokens:
            state["metadata"]["token_usage"]["risk_analyst"] = risk_tokens

        logger.info(
            "node_completed",
            node="parallel_research",
            has_analyst_insights=state.get("analyst_insights") is not None,
            has_researcher_findings=state.get("researcher_findings") is not None,
            has_risk_analysis=state.get("risk_analysis") is not None,
        )

        return state


async def strategist_coordination_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strategist coordination with dynamic research requests.

    The Strategist reviews all research and decides whether to:
    1. Request targeted follow-up research from specific agents
    2. Proceed to synthesis and create the final GTM plan

    Args:
        state: Current workflow state

    Returns:
        Updated state with coordination decision
    """
    from src.agents.strategist_tools import STRATEGIST_COORDINATION_SYSTEM_PROMPT

    iteration = state.get("coordination_iteration", 0)
    max_iterations = state.get("max_coordination_iterations", 3)

    logger.info(
        "strategist_coordination_started",
        iteration=iteration,
        max_iterations=max_iterations,
    )

    # Force synthesis if max iterations reached
    if iteration >= max_iterations:
        logger.warning("strategist_max_iterations_reached", forcing_synthesis=True)
        state["ready_for_synthesis"] = True
        return state

    with trace_span("node.strategist_coordination", {"iteration": iteration}):
        business_idea = state["business_idea"]
        analyst_insights = state.get("analyst_insights", {})
        researcher_findings = state.get("researcher_findings", {})
        risk_analysis = state.get("risk_analysis", {})

        # Get follow-up research if it exists
        follow_up_research = state.get("follow_up_research", [])

        # Prepare context for Strategist
        user_message = f"""Business Idea: {business_idea['full_idea']}

CURRENT RESEARCH:

Analyst Insights:
{json.dumps(analyst_insights, indent=2)}

Researcher Findings:
{json.dumps(researcher_findings, indent=2)}

Risk Analysis:
{json.dumps(risk_analysis, indent=2)}"""

        if follow_up_research:
            user_message += f"""

FOLLOW-UP RESEARCH (from previous iterations):
{json.dumps(follow_up_research, indent=2)}"""

        user_message += f"""

Coordination Iteration: {iteration + 1} of {max_iterations}

Review the research above and decide:

**Option 1**: If you identify specific gaps that need deeper investigation, respond with:
{{
  "decision": "request_research",
  "requests": [
    {{"agent": "analyst", "query": "specific question"}},
    {{"agent": "researcher", "query": "specific question"}},
    {{"agent": "risk_analyst", "query": "specific question"}}
  ],
  "reasoning": "why this research is needed"
}}

**Option 2**: If you have sufficient information to create a comprehensive GTM plan, respond with:
{{
  "decision": "create_plan",
  "reasoning": "why the current research is sufficient"
}}

Be thoughtful. Only request follow-up if genuinely needed.
"""

        strategist = get_strategist()
        llm_response = await strategist.llm_client.generate(
            system=STRATEGIST_COORDINATION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=1000,
            temperature=0.7,
        )

        # Parse response
        try:
            content = llm_response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            decision = json.loads(content.strip())

            logger.info(
                "strategist_decision_parsed",
                decision_type=decision.get("decision"),
                reasoning=decision.get("reasoning", "")[:100],
            )

            if decision.get("decision") == "create_plan":
                # Ready for synthesis
                state["ready_for_synthesis"] = True
                logger.info("strategist_ready_for_synthesis", reasoning=decision.get("reasoning"))
            else:
                # Request follow-up research
                requests = decision.get("requests", [])
                if requests:
                    logger.info("strategist_requesting_follow_up", num_requests=len(requests))

                    # Execute follow-up research
                    analyst = get_analyst()
                    researcher = get_researcher()
                    risk_analyst = get_risk_analyst()

                    for request in requests:
                        agent_name = request.get("agent")
                        query = request.get("query")

                        if not query:
                            continue

                        logger.info("strategist_executing_follow_up", agent=agent_name, query=query[:100])

                        try:
                            if agent_name == "analyst":
                                result = await analyst.execute_focused(state, query)
                            elif agent_name == "researcher":
                                result = await researcher.execute_focused(state, query)
                            elif agent_name == "risk_analyst":
                                result = await risk_analyst.execute_focused(state, query)
                            else:
                                logger.warning("strategist_unknown_agent", agent=agent_name)
                                continue

                            # Append to follow-up research
                            if "follow_up_research" not in state:
                                state["follow_up_research"] = []
                            state["follow_up_research"].append(result)

                            logger.info("strategist_follow_up_completed", agent=agent_name)

                        except Exception as e:
                            logger.error("strategist_follow_up_failed", agent=agent_name, error=str(e))

                    # Increment iteration
                    state["coordination_iteration"] = iteration + 1
                else:
                    # No requests, proceed to synthesis
                    state["ready_for_synthesis"] = True

        except json.JSONDecodeError as e:
            logger.error("strategist_coordination_parse_error", error=str(e), response=llm_response.content[:300])
            # Fallback: proceed to synthesis
            state["ready_for_synthesis"] = True

        return state


async def strategist_synthesis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strategist synthesis - creates final GTM plan from all research.

    This is the final node that synthesizes all insights into a comprehensive
    go-to-market strategy.

    Args:
        state: Current workflow state

    Returns:
        Updated state with final GTM plan
    """
    logger.info("strategist_synthesis_started")

    with trace_span("node.strategist_synthesis"):
        # Use the existing strategist node's logic
        strategist = get_strategist()
        state = await strategist.execute(state)

        logger.info(
            "strategist_synthesis_completed",
            has_plan=state.get("strategist_plan") is not None,
            viability_score=state.get("strategist_plan", {}).get("viability_score"),
        )

        return state
