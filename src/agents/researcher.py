"""
The Researcher Agent - Market Research & Competitive Analysis

Investigates the "Y" market in an "X for Y" business idea.
"""

import asyncio
import json
from typing import Dict, Any
from datetime import datetime

from src.agents.base import BaseAgent
from src.agents.prompts.researcher import RESEARCHER_SYSTEM_PROMPT
from src.llm.openrouter_client import get_llm_client
from src.tools.tavily import get_tavily_tool
from src.tools.base import ToolInput
from src.orchestration.state import MarketResearch, AgentInteraction
from src.observability.decorators import trace_agent
from src.observability.logger import get_logger

logger = get_logger(__name__)


class ResearcherAgent(BaseAgent):
    """
    The Researcher - Investigates market saturation and competition.

    Analyzes the "Y" market to assess saturation, competitors,
    opportunities, and barriers to entry.
    """

    def __init__(self):
        super().__init__(name="researcher")
        self.llm_client = get_llm_client()
        self.tavily_tool = get_tavily_tool()

    @trace_agent("researcher")
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute researcher agent logic.

        Args:
            state: Current analysis state

        Returns:
            Updated state with researcher findings
        """
        business_idea = state.get("business_idea") or {}
        y_market = business_idea.get("y_market", "Unknown market")
        iteration = state.get("loop_count", 0)

        # Check if this is a loop back (skeptic rejected previous iteration)
        skeptic_critique = state.get("skeptic_critique")
        is_loop_back = skeptic_critique is not None and iteration > 0

        logger.info(
            "researcher_started",
            market=y_market,
            iteration=iteration,
            is_loop_back=is_loop_back,
        )

        # Step 1: Search for market information
        # Adjust query based on skeptic feedback
        if is_loop_back:
            concerns = skeptic_critique.get("concerns", [])
            suggestions = skeptic_critique.get("suggestions", [])
            focus_areas = " ".join(concerns[:2] + suggestions[:2])
            market_query = f"{y_market} {focus_areas} market saturation barriers opportunities"
            logger.info("researcher_searching_focused", query=market_query, reason="addressing_skeptic_feedback")
        else:
            market_query = f"{y_market} market size competitors landscape trends"
            logger.info("researcher_searching", query=market_query)

        # Step 2: Define competitor search query
        competitor_query = f"{y_market} companies apps services startups competitors"

        # OPTIMIZATION: Execute both searches in parallel using asyncio.gather
        logger.info("researcher_parallel_search_started", market_query=market_query, competitor_query=competitor_query)

        market_search, competitor_search = await asyncio.gather(
            self.tavily_tool.execute(
                ToolInput(
                    tool_name="tavily_search",
                    parameters={
                        "query": market_query,
                        "max_results": 7 if is_loop_back else 5,
                        "search_depth": "advanced",
                    },
                )
            ),
            self.tavily_tool.execute(
                ToolInput(
                    tool_name="tavily_search",
                    parameters={
                        "query": competitor_query,
                        "max_results": 7 if is_loop_back else 5,
                        "search_depth": "advanced" if is_loop_back else "basic",
                    },
                )
            )
        )

        logger.info("researcher_parallel_search_completed")

        # Extract search context
        market_context = ""
        if market_search.success:
            results = market_search.result.get("results", [])
            # Use more results if looping back
            num_results = 5 if is_loop_back else 3
            market_context = "\n\n".join([
                f"**{r['title']}**\n{r['content']}"
                for r in results[:num_results]
            ])

        competitor_context = ""
        if competitor_search.success:
            results = competitor_search.result.get("results", [])
            # Use more results if looping back
            num_results = 5 if is_loop_back else 3
            competitor_context = "\n\n".join([
                f"**{r['title']}**\n{r['content']}"
                for r in results[:num_results]
            ])

        # Step 3: LLM analysis with skeptic feedback if available
        full_idea = business_idea.get('full_idea', f'Business idea targeting {y_market}')
        user_message = f"""Analyze the market: {y_market}

Business Idea Context: {full_idea}

Market Research:
{market_context}

Competitor Research:
{competitor_context}"""

        # Include skeptic feedback if this is a loop back
        if is_loop_back:
            user_message += f"""

⚠️ PREVIOUS ITERATION FEEDBACK - CRITICAL TO ADDRESS:

The Skeptic rejected the previous analysis for the following reasons:
Rejection Reason: {skeptic_critique.get('loop_back_reason', 'Quality concerns')}

Specific Concerns Identified:
{chr(10).join(f"- {concern}" for concern in skeptic_critique.get('concerns', []))}

Fatal Flaws Found:
{chr(10).join(f"- {flaw}" for flaw in skeptic_critique.get('fatal_flaws', [])) if skeptic_critique.get('fatal_flaws') else "None"}

Suggestions for Improvement:
{chr(10).join(f"- {suggestion}" for suggestion in skeptic_critique.get('suggestions', []))}

Iteration: {iteration + 1} of {state.get('max_loops', 3)}

INSTRUCTION: Address ALL of the above concerns in your analysis. Be MORE specific about competitive threats, MORE detailed about market saturation, and MORE thorough about barriers to entry. Focus especially on the areas flagged by the Skeptic."""

        user_message += "\n\nProvide a comprehensive market analysis including saturation assessment."

        llm_response = await self.llm_client.generate(
            system=RESEARCHER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=2000,
            temperature=0.7,
        )

        # Step 4: Parse response
        try:
            # Extract JSON from response
            content = llm_response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            analysis = json.loads(content.strip())

            # Create MarketResearch object
            market_research = MarketResearch(
                market_name=analysis.get("market_name", y_market),
                market_size=analysis.get("market_size"),
                competitor_count=analysis.get("competitor_count", 0),
                competitors=analysis.get("competitors", []),
                saturation_level=analysis.get("saturation_level", "unknown"),
                market_trends=analysis.get("market_trends", []),
                opportunities=analysis.get("opportunities", []),
                barriers=analysis.get("barriers", []),
                summary=analysis.get("summary", ""),
            )

            # Log decision
            self.log_decision(
                decision="market_researched",
                reasoning=market_research.summary,
                confidence=None,  # No confidence score for researcher
            )

            # Record interaction
            interaction = AgentInteraction(
                agent_name="researcher",
                timestamp=datetime.utcnow(),
                action="market_research",
                reasoning=market_research.summary,
                tool_calls=[
                    {"tool": "tavily_search", "query": market_query},
                    {"tool": "tavily_search", "query": competitor_query},
                ],
                result=f"Found {market_research.competitor_count} competitors, saturation: {market_research.saturation_level}",
                iteration=iteration,
            )

            # Update state
            if "agent_interactions" not in state:
                state["agent_interactions"] = []
            state["agent_interactions"].append(interaction.__dict__)

            state["researcher_findings"] = {
                "market_name": market_research.market_name,
                "market_size": market_research.market_size,
                "competitor_count": market_research.competitor_count,
                "competitors": market_research.competitors,
                "saturation_level": market_research.saturation_level,
                "market_trends": market_research.market_trends,
                "opportunities": market_research.opportunities,
                "barriers": market_research.barriers,
                "summary": market_research.summary,
            }

            # Update metadata
            if "metadata" not in state:
                state["metadata"] = {}
            if "token_usage" not in state["metadata"]:
                state["metadata"]["token_usage"] = {}
            state["metadata"]["token_usage"]["researcher"] = {
                "prompt_tokens": llm_response.prompt_tokens,
                "completion_tokens": llm_response.completion_tokens,
                "total_tokens": llm_response.total_tokens,
            }

            logger.info(
                "researcher_completed",
                market=y_market,
                saturation=market_research.saturation_level,
                competitors=market_research.competitor_count,
                iteration=iteration,
            )

            return state

        except json.JSONDecodeError as e:
            logger.error(
                "researcher_parse_error",
                error=str(e),
                response=llm_response.content[:500],
            )
            # Fallback: create minimal research
            state["researcher_findings"] = {
                "market_name": y_market,
                "market_size": None,
                "competitor_count": 0,
                "competitors": [],
                "saturation_level": "unknown",
                "market_trends": [],
                "opportunities": [],
                "barriers": [],
                "summary": llm_response.content[:200],
            }
            return state

    async def execute_focused(self, state: Dict[str, Any], focus_query: str) -> Dict[str, Any]:
        """
        Execute focused market research based on Strategist's specific query.

        Args:
            state: Current analysis state
            focus_query: Specific question or area to investigate

        Returns:
            Focused research results
        """
        business_idea = state.get("business_idea") or {}
        y_market = business_idea.get("y_market", "Unknown market")

        logger.info(
            "researcher_focused_analysis_started",
            market=y_market,
            query=focus_query[:100] if focus_query else "",
        )

        # Use existing market context
        existing_findings = state.get("researcher_findings", {})

        # Focused search
        search_query = f"{y_market} {focus_query}"
        logger.info("researcher_focused_search", query=search_query)

        search_result = await self.tavily_tool.execute(
            ToolInput(
                tool_name="tavily_search",
                parameters={
                    "query": search_query,
                    "max_results": 5,
                    "search_depth": "advanced",
                },
            )
        )

        # Extract search context
        search_context = ""
        if search_result.success:
            results = search_result.result.get("results", [])
            search_context = "\n\n".join([
                f"**{r['title']}**\n{r['content']}"
                for r in results[:3]
            ])

        # Focused LLM call
        full_idea = business_idea.get('full_idea', f'Business idea targeting {y_market}')
        user_message = f"""Focused Research Request: {focus_query}

Market: {y_market}
Business Idea: {full_idea}

EXISTING MARKET RESEARCH:
{json.dumps(existing_findings, indent=2)}

ADDITIONAL WEB RESEARCH:
{search_context}

Provide detailed, focused market research addressing the specific query above.
Return JSON with:
{{
  "query": "{focus_query}",
  "findings": ["finding1", "finding2", ...],
  "insights": "detailed analysis",
  "confidence": 0.0-1.0
}}
"""

        llm_response = await self.llm_client.generate(
            system=RESEARCHER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=1500,
            temperature=0.7,
        )

        # Parse response
        try:
            content = llm_response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())

            logger.info(
                "researcher_focused_analysis_completed",
                market=y_market,
                confidence=result.get("confidence", 0.7),
            )

            return {
                "type": "focused_research",
                "agent": "researcher",
                "query": focus_query,
                "findings": result.get("findings", []),
                "insights": result.get("insights", ""),
                "confidence": result.get("confidence", 0.7),
            }

        except json.JSONDecodeError as e:
            logger.error(
                "researcher_focused_parse_error",
                error=str(e),
                response=llm_response.content[:300],
            )
            return {
                "type": "focused_research",
                "agent": "researcher",
                "query": focus_query,
                "findings": [],
                "insights": llm_response.content[:500],
                "confidence": 0.5,
            }
