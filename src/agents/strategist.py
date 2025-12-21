"""
The Strategist Agent - GTM Strategy Synthesis

Creates comprehensive go-to-market plan from all gathered insights.
"""

import json
from typing import Dict, Any
from datetime import datetime

from src.agents.base import BaseAgent
from src.agents.prompts.strategist import STRATEGIST_SYSTEM_PROMPT
from src.llm.openrouter_client import get_llm_client
from src.orchestration.state import GTMPlan, AgentInteraction
from src.observability.decorators import trace_agent
from src.observability.logger import get_logger

logger = get_logger(__name__)


class StrategistAgent(BaseAgent):
    """
    The Strategist - GTM expert who synthesizes insights into action.

    Creates a comprehensive go-to-market plan including target audience,
    value proposition, pricing, channels, marketing hooks, and viability
    assessment.
    """

    def __init__(self):
        super().__init__(name="strategist")
        self.llm_client = get_llm_client()

    @trace_agent
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute strategist agent logic.

        Args:
            state: Current analysis state

        Returns:
            Updated state with GTM plan
        """
        business_idea = state["business_idea"]
        analyst_insights = state.get("analyst_insights", {})
        researcher_findings = state.get("researcher_findings", {})
        skeptic_critique = state.get("skeptic_critique", {})
        iteration = state.get("loop_count", 0)

        logger.info(
            "strategist_started",
            idea=business_idea["full_idea"],
            iteration=iteration,
        )

        # Step 1: Synthesize all insights
        user_message = f"""Create a comprehensive GTM strategy for this business idea:

Business Idea: {business_idea['full_idea']}
{f"Description: {business_idea.get('description')}" if business_idea.get('description') else ""}

BRAND DNA (from Analyst):
{json.dumps(analyst_insights, indent=2)}

MARKET RESEARCH (from Researcher):
{json.dumps(researcher_findings, indent=2)}

SKEPTIC'S FEEDBACK:
{json.dumps(skeptic_critique, indent=2)}

INSTRUCTIONS:
Create an actionable, realistic GTM plan that:
1. Targets a specific, well-defined audience
2. Articulates clear value proposition
3. Recommends evidence-based pricing strategy
4. Identifies viable distribution channels
5. Creates 3 LinkedIn-worthy marketing hooks
6. Highlights genuine competitive advantages
7. Acknowledges key risks honestly
8. Defines measurable success metrics
9. Provides realistic timeline
10. Assigns overall viability score (0.0-1.0)

Consider:
- Market saturation level: {researcher_findings.get('saturation_level', 'unknown')}
- Competitor count: {researcher_findings.get('competitor_count', 0)}
- Skeptic concerns: {', '.join(skeptic_critique.get('concerns', [])[:3])}

Be realistic about viability. Don't oversell if market is saturated.
"""

        llm_response = await self.llm_client.generate(
            system=STRATEGIST_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=2500,
            temperature=0.7,
        )

        # Step 2: Parse response
        try:
            # Extract JSON from response
            content = llm_response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            analysis = json.loads(content.strip())

            # Create GTMPlan object
            gtm_plan = GTMPlan(
                target_audience=analysis.get("target_audience", ""),
                value_proposition=analysis.get("value_proposition", ""),
                pricing_strategy=analysis.get("pricing_strategy", ""),
                distribution_channels=analysis.get("distribution_channels", []),
                marketing_hooks=analysis.get("marketing_hooks", []),
                competitive_advantages=analysis.get("competitive_advantages", []),
                key_risks=analysis.get("key_risks", []),
                success_metrics=analysis.get("success_metrics", []),
                timeline=analysis.get("timeline", ""),
                viability_score=analysis.get("viability_score", 0.5),
                summary=analysis.get("summary", ""),
            )

            # Log decision
            self.log_decision(
                decision="gtm_plan_created",
                reasoning=gtm_plan.summary,
                confidence=gtm_plan.viability_score,
            )

            # Record interaction
            interaction = AgentInteraction(
                agent_name="strategist",
                timestamp=datetime.utcnow(),
                action="gtm_synthesis",
                reasoning=gtm_plan.summary,
                tool_calls=[],  # No external tools for strategist
                result=f"Viability score: {gtm_plan.viability_score:.2f}",
                iteration=iteration,
            )

            # Update state
            if "agent_interactions" not in state:
                state["agent_interactions"] = []
            state["agent_interactions"].append(interaction.__dict__)

            state["strategist_plan"] = {
                "target_audience": gtm_plan.target_audience,
                "value_proposition": gtm_plan.value_proposition,
                "pricing_strategy": gtm_plan.pricing_strategy,
                "distribution_channels": gtm_plan.distribution_channels,
                "marketing_hooks": gtm_plan.marketing_hooks,
                "competitive_advantages": gtm_plan.competitive_advantages,
                "key_risks": gtm_plan.key_risks,
                "success_metrics": gtm_plan.success_metrics,
                "timeline": gtm_plan.timeline,
                "viability_score": gtm_plan.viability_score,
                "summary": gtm_plan.summary,
            }

            # Set final status
            state["status"] = "completed"
            state["final_recommendation"] = gtm_plan.summary

            # Determine if human review needed (low viability)
            if gtm_plan.viability_score < 0.4:
                state["requires_human_review"] = True
                logger.warning(
                    "low_viability_score",
                    score=gtm_plan.viability_score,
                    human_review_recommended=True,
                )

            # Update metadata
            if "metadata" not in state:
                state["metadata"] = {}
            if "token_usage" not in state["metadata"]:
                state["metadata"]["token_usage"] = {}
            state["metadata"]["token_usage"]["strategist"] = {
                "prompt_tokens": llm_response.prompt_tokens,
                "completion_tokens": llm_response.completion_tokens,
                "total_tokens": llm_response.total_tokens,
            }

            # Calculate total cost (approximate)
            total_prompt_tokens = sum(
                usage.get("prompt_tokens", 0)
                for usage in state["metadata"]["token_usage"].values()
            )
            total_completion_tokens = sum(
                usage.get("completion_tokens", 0)
                for usage in state["metadata"]["token_usage"].values()
            )

            # GPT-4o pricing: ~$2.50/MTok input, ~$10/MTok output (approximate)
            cost_usd = (total_prompt_tokens / 1_000_000 * 2.5) + (total_completion_tokens / 1_000_000 * 10.0)
            state["metadata"]["cost_usd"] = cost_usd

            logger.info(
                "strategist_completed",
                viability_score=gtm_plan.viability_score,
                iteration=iteration,
                total_cost_usd=cost_usd,
                total_tokens=total_prompt_tokens + total_completion_tokens,
            )

            return state

        except json.JSONDecodeError as e:
            logger.error(
                "strategist_parse_error",
                error=str(e),
                response=llm_response.content[:500],
            )
            # Fallback: create minimal plan from raw text
            state["strategist_plan"] = {
                "target_audience": "Unknown - see summary",
                "value_proposition": "Unknown - see summary",
                "pricing_strategy": "Unknown - see summary",
                "distribution_channels": [],
                "marketing_hooks": [],
                "competitive_advantages": [],
                "key_risks": ["Unable to parse structured plan"],
                "success_metrics": [],
                "timeline": "Unknown",
                "viability_score": 0.5,
                "summary": llm_response.content[:500],
            }
            state["status"] = "completed"
            state["final_recommendation"] = llm_response.content[:200]
            return state
