"""
The Analyst Agent - Brand DNA Deconstruction

Analyzes the "X" brand in an "X for Y" business idea.
"""

import json
from typing import Dict, Any
from datetime import datetime

from src.agents.base import BaseAgent
from src.agents.prompts.analyst import ANALYST_SYSTEM_PROMPT
from src.llm.openrouter_client import get_llm_client
from src.tools.tavily import get_tavily_tool
from src.tools.base import ToolInput
from src.orchestration.state import BrandDNA, AgentInteraction
from src.observability.decorators import trace_agent
from src.observability.logger import get_logger

logger = get_logger(__name__)


class AnalystAgent(BaseAgent):
    """
    The Analyst - Deconstructs brand DNA.

    Analyzes the "X" brand to extract core strengths, business model,
    differentiators, and success factors.
    """

    def __init__(self):
        super().__init__(name="analyst")
        self.llm_client = get_llm_client()
        self.tavily_tool = get_tavily_tool()

    @trace_agent("analyst")
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute analyst agent logic.

        Args:
            state: Current analysis state

        Returns:
            Updated state with analyst insights
        """
        business_idea = state["business_idea"]
        x_brand = business_idea["x_brand"]
        iteration = state.get("loop_count", 0)

        # Check if this is a loop back (skeptic rejected previous iteration)
        skeptic_critique = state.get("skeptic_critique")
        is_loop_back = skeptic_critique is not None and iteration > 0

        logger.info(
            "analyst_started",
            brand=x_brand,
            iteration=iteration,
            is_loop_back=is_loop_back,
        )

        # Step 1: Search for brand information
        # Use more specific query if skeptic provided feedback
        if is_loop_back:
            # Extract concerns to focus search
            concerns = skeptic_critique.get("concerns", [])
            suggestions = skeptic_critique.get("suggestions", [])
            focus_areas = " ".join(concerns[:2] + suggestions[:2])  # Top 2 of each
            search_query = f"{x_brand} {focus_areas} business model competitive advantages"
            logger.info("analyst_searching_focused", query=search_query, reason="addressing_skeptic_feedback")
        else:
            search_query = f"{x_brand} company business model key features success factors"
            logger.info("analyst_searching", query=search_query)

        search_result = await self.tavily_tool.execute(
            ToolInput(
                tool_name="tavily_search",
                parameters={
                    "query": search_query,
                    "max_results": 7 if is_loop_back else 5,  # More results on loop back
                    "search_depth": "advanced",
                },
            )
        )

        # Extract search context
        search_context = ""
        if search_result.success:
            results = search_result.result.get("results", [])
            # Use more results if looping back
            num_results = 5 if is_loop_back else 3
            search_context = "\n\n".join([
                f"**{r['title']}**\n{r['content']}"
                for r in results[:num_results]
            ])

        # Step 2: LLM analysis with skeptic feedback if available
        user_message = f"""Analyze the brand: {x_brand}

Business Idea Context: {business_idea['full_idea']}

Web Search Results:
{search_context}"""

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

INSTRUCTION: Address ALL of the above concerns in your analysis. Be MORE specific, MORE detailed, and MORE thorough than the previous iteration. Focus especially on the areas flagged by the Skeptic."""

        user_message += "\n\nProvide a comprehensive brand DNA analysis."

        llm_response = await self.llm_client.generate(
            system=ANALYST_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=2000,
            temperature=0.7,
        )

        # Step 3: Parse response
        try:
            # Extract JSON from response
            content = llm_response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            analysis = json.loads(content.strip())

            # Create BrandDNA object
            brand_dna = BrandDNA(
                brand_name=analysis.get("brand_name", x_brand),
                core_strengths=analysis.get("core_strengths", []),
                business_model=analysis.get("business_model", ""),
                key_differentiators=analysis.get("key_differentiators", []),
                tech_stack=analysis.get("tech_stack", []),
                success_factors=analysis.get("success_factors", []),
                summary=analysis.get("summary", ""),
                confidence=analysis.get("confidence", 0.8),
            )

            # Log decision
            self.log_decision(
                decision="brand_analyzed",
                reasoning=brand_dna.summary,
                confidence=brand_dna.confidence,
            )

            # Record interaction
            interaction = AgentInteraction(
                agent_name="analyst",
                timestamp=datetime.utcnow(),
                action="brand_analysis",
                reasoning=brand_dna.summary,
                tool_calls=[
                    {"tool": "tavily_search", "query": search_query}
                ],
                result=brand_dna.summary,
                iteration=iteration,
            )

            # Update state
            if "agent_interactions" not in state:
                state["agent_interactions"] = []
            state["agent_interactions"].append(interaction.__dict__)

            state["analyst_insights"] = {
                "brand_name": brand_dna.brand_name,
                "core_strengths": brand_dna.core_strengths,
                "business_model": brand_dna.business_model,
                "key_differentiators": brand_dna.key_differentiators,
                "tech_stack": brand_dna.tech_stack,
                "success_factors": brand_dna.success_factors,
                "summary": brand_dna.summary,
                "confidence": brand_dna.confidence,
            }

            # Update metadata
            if "metadata" not in state:
                state["metadata"] = {}
            if "token_usage" not in state["metadata"]:
                state["metadata"]["token_usage"] = {}
            state["metadata"]["token_usage"]["analyst"] = {
                "prompt_tokens": llm_response.prompt_tokens,
                "completion_tokens": llm_response.completion_tokens,
                "total_tokens": llm_response.total_tokens,
            }

            logger.info(
                "analyst_completed",
                brand=x_brand,
                confidence=brand_dna.confidence,
                iteration=iteration,
            )

            return state

        except json.JSONDecodeError as e:
            logger.error(
                "analyst_parse_error",
                error=str(e),
                response=llm_response.content[:500],
            )
            # Fallback: create minimal analysis
            state["analyst_insights"] = {
                "brand_name": x_brand,
                "core_strengths": [],
                "business_model": llm_response.content,
                "key_differentiators": [],
                "tech_stack": [],
                "success_factors": [],
                "summary": llm_response.content[:200],
                "confidence": 0.5,
            }
            return state
