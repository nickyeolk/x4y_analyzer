"""
The Researcher Agent - Market Research & Competitive Analysis

Investigates the "Y" market in an "X for Y" business idea.
"""

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
        business_idea = state["business_idea"]
        y_market = business_idea["y_market"]
        iteration = state.get("loop_count", 0)

        logger.info(
            "researcher_started",
            market=y_market,
            iteration=iteration,
        )

        # Step 1: Search for market information
        market_query = f"{y_market} market size competitors landscape trends"
        logger.info("researcher_searching", query=market_query)

        market_search = await self.tavily_tool.execute(
            ToolInput(
                tool_name="tavily_search",
                parameters={
                    "query": market_query,
                    "max_results": 5,
                    "search_depth": "advanced",
                },
            )
        )

        # Step 2: Search for competitors
        competitor_query = f"{y_market} companies apps services startups"
        competitor_search = await self.tavily_tool.execute(
            ToolInput(
                tool_name="tavily_search",
                parameters={
                    "query": competitor_query,
                    "max_results": 5,
                    "search_depth": "basic",
                },
            )
        )

        # Extract search context
        market_context = ""
        if market_search.success:
            results = market_search.result.get("results", [])
            market_context = "\n\n".join([
                f"**{r['title']}**\n{r['content']}"
                for r in results[:3]
            ])

        competitor_context = ""
        if competitor_search.success:
            results = competitor_search.result.get("results", [])
            competitor_context = "\n\n".join([
                f"**{r['title']}**\n{r['content']}"
                for r in results[:3]
            ])

        # Step 3: LLM analysis
        user_message = f"""Analyze the market: {y_market}

Business Idea Context: {business_idea['full_idea']}

Market Research:
{market_context}

Competitor Research:
{competitor_context}

Provide a comprehensive market analysis including saturation assessment."""

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
