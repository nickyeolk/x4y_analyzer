"""
The Skeptic Agent - Critical Evaluation & Loop Decision

Critiques the business idea and decides whether to approve or loop back.
"""

import json
from typing import Dict, Any
from datetime import datetime

from src.agents.base import BaseAgent
from src.agents.prompts.skeptic import SKEPTIC_SYSTEM_PROMPT
from src.llm.openrouter_client import get_llm_client, OpenRouterClient
from src.tools.marketing_rag import get_rag_tool
from src.tools.base import ToolInput
from src.orchestration.state import Critique, AgentInteraction
from src.observability.decorators import trace_agent
from src.observability.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class SkepticAgent(BaseAgent):
    """
    The Skeptic - Critical thinker who validates analysis quality.

    Reviews brand analysis and market research to identify flaws,
    gaps, and weaknesses. Decides whether to approve or loop back
    for deeper investigation.
    """

    def __init__(self):
        super().__init__(name="skeptic")
        self.llm_client = get_llm_client()
        # OPTIMIZATION: Use faster/cheaper GPT-4o-mini for simple classification task
        self.classification_client = OpenRouterClient(
            api_key=settings.openrouter_api_key,
            model="openai/gpt-4o-mini"
        )
        self.rag_tool = get_rag_tool()

    @trace_agent("skeptic")
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute skeptic agent logic.

        Args:
            state: Current analysis state

        Returns:
            Updated state with critique and approval decision
        """
        business_idea = state["business_idea"]
        analyst_insights = state.get("analyst_insights", {})
        researcher_findings = state.get("researcher_findings", {})
        iteration = state.get("loop_count", 0)
        max_loops = state.get("max_loops", 3)

        logger.info(
            "skeptic_started",
            idea=business_idea["full_idea"],
            iteration=iteration,
            max_loops=max_loops,
        )

        # Step 1: Classify business model to query relevant frameworks
        # OPTIMIZATION: Use GPT-4o-mini for this simple classification task (saves ~2-3s)
        logger.info("skeptic_classifying_business_model", idea=business_idea["full_idea"], model="gpt-4o-mini")

        classification_response = await self.classification_client.generate(
            system="You are a business model expert. Classify startup ideas into business model types.",
            messages=[{
                "role": "user",
                "content": f"""Classify this business idea into ONE primary business model type: {business_idea['full_idea']}

Choose from:
- marketplace (two-sided platforms like Uber, Airbnb, Upwork)
- subscription (recurring revenue like Netflix, Spotify)
- saas (B2B software like Shopify, Salesforce, Slack)
- ecommerce (online retail like Amazon, Warby Parker)
- service (professional services, consulting)
- hardware (physical products, IoT)
- other

Respond with ONLY the business model type, nothing else."""
            }],
            max_tokens=50,
            temperature=0.3,
        )

        business_model_type = classification_response.content.strip().lower()
        logger.info("skeptic_business_model_classified", type=business_model_type, model="gpt-4o-mini")

        # Step 2: Build targeted RAG query based on business model type
        rag_query_map = {
            "marketplace": "marketplace startup cold start problem network effects unit economics two-sided platform supply demand liquidity",
            "subscription": "subscription business model churn retention pricing customer lifetime value cohort analysis",
            "saas": "B2B SaaS sales cycle enterprise adoption switching costs product-led growth customer success",
            "ecommerce": "ecommerce unit economics customer acquisition cost retention repeat purchase inventory",
            "service": "service business scalability pricing delivery model professional services margins",
            "hardware": "hardware product manufacturing supply chain distribution retail margins",
            "other": "startup market analysis quality criteria competitive analysis evaluation framework",
        }

        # Get specific query or fallback to generic
        rag_query = rag_query_map.get(business_model_type, rag_query_map["other"])
        logger.info("skeptic_consulting_rag", query=rag_query, business_model=business_model_type)

        rag_result = await self.rag_tool.execute(
            ToolInput(
                tool_name="marketing_rag",
                parameters={
                    "query": rag_query,
                    "k": 3,
                    "score_threshold": 0.3,  # Lower threshold to be more inclusive
                },
            )
        )

        # Extract RAG context
        rag_context = ""
        if rag_result.success:
            documents = rag_result.result.get("documents", [])
            if documents:
                rag_context = "\n\n".join([
                    f"**Marketing Framework {d['rank']}** (relevance: {d['relevance_score']:.2f})\n{d['content']}"
                    for d in documents[:3]
                ])
            else:
                rag_context = "No relevant marketing frameworks found."
        else:
            rag_context = "RAG lookup failed - proceeding without framework consultation."

        # Step 2: Prepare critique context
        user_message = f"""Review this business idea critically:

Business Idea: {business_idea['full_idea']}

ANALYST'S BRAND DNA ANALYSIS:
{json.dumps(analyst_insights, indent=2)}

RESEARCHER'S MARKET FINDINGS:
{json.dumps(researcher_findings, indent=2)}

MARKETING FRAMEWORKS & PITFALLS:
{rag_context}

CONTEXT:
- Current iteration: {iteration + 1}
- Maximum iterations allowed: {max_loops}
- This is {'the final' if iteration >= max_loops - 1 else 'NOT the final'} opportunity to loop back

INSTRUCTIONS:
Critically evaluate the analysis quality. Look for:
1. Superficial or incomplete analysis
2. Missing competitive threats
3. Unclear market saturation assessment
4. Weak differentiation
5. Fatal flaws that weren't investigated

Decide: APPROVE (proceed to strategy) or REJECT (loop back for deeper analysis)?

If rejecting and iteration < {max_loops - 1}, specify what needs deeper investigation.
If iteration >= {max_loops - 1}, you MUST approve (even if weak) to prevent infinite loops.
"""

        llm_response = await self.llm_client.generate(
            system=SKEPTIC_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=1500,
            temperature=0.6,  # Slightly lower for more consistent decisions
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

            # Force approval if max loops reached
            approved = analysis.get("approved", False)
            if iteration >= max_loops - 1:
                logger.info(
                    "skeptic_max_loops_reached",
                    iteration=iteration,
                    max_loops=max_loops,
                    forcing_approval=True,
                )
                approved = True
                if not analysis.get("approved"):
                    analysis["concerns"].append("Max iterations reached - forcing approval")

            # Create Critique object
            critique = Critique(
                approved=approved,
                concerns=analysis.get("concerns", []),
                fatal_flaws=analysis.get("fatal_flaws", []),
                suggestions=analysis.get("suggestions", []),
                loop_back_reason=analysis.get("loop_back_reason") if not approved else None,
                confidence=analysis.get("confidence", 0.7),
                reasoning=analysis.get("reasoning", ""),
            )

            # Log decision
            self.log_decision(
                decision="approved" if critique.approved else "rejected_loop_back",
                reasoning=critique.reasoning,
                confidence=critique.confidence,
            )

            # Record interaction
            interaction = AgentInteraction(
                agent_name="skeptic",
                timestamp=datetime.utcnow(),
                action="critical_review",
                reasoning=critique.reasoning,
                tool_calls=[
                    {"tool": "llm_classification", "business_model": business_model_type},
                    {"tool": "marketing_rag", "query": rag_query}
                ],
                result=f"{'APPROVED' if critique.approved else 'REJECTED'} - {critique.loop_back_reason or 'Proceed to strategy'}",
                iteration=iteration,
            )

            # Update state
            if "agent_interactions" not in state:
                state["agent_interactions"] = []
            state["agent_interactions"].append(interaction.__dict__)

            state["skeptic_critique"] = {
                "approved": critique.approved,
                "concerns": critique.concerns,
                "fatal_flaws": critique.fatal_flaws,
                "suggestions": critique.suggestions,
                "loop_back_reason": critique.loop_back_reason,
                "confidence": critique.confidence,
                "reasoning": critique.reasoning,
            }

            # Set approval flag for routing
            state["skeptic_approved"] = critique.approved

            # Update metadata
            if "metadata" not in state:
                state["metadata"] = {}
            if "token_usage" not in state["metadata"]:
                state["metadata"]["token_usage"] = {}
            state["metadata"]["token_usage"]["skeptic"] = {
                "classification_prompt_tokens": classification_response.prompt_tokens,
                "classification_completion_tokens": classification_response.completion_tokens,
                "critique_prompt_tokens": llm_response.prompt_tokens,
                "critique_completion_tokens": llm_response.completion_tokens,
                "total_tokens": (
                    classification_response.total_tokens + llm_response.total_tokens
                ),
            }

            logger.info(
                "skeptic_completed",
                approved=critique.approved,
                confidence=critique.confidence,
                iteration=iteration,
                loop_back_reason=critique.loop_back_reason,
            )

            return state

        except json.JSONDecodeError as e:
            logger.error(
                "skeptic_parse_error",
                error=str(e),
                response=llm_response.content[:500],
            )
            # Fallback: approve to prevent getting stuck
            logger.warning(
                "skeptic_fallback_approval",
                reason="JSON parse error",
            )
            state["skeptic_critique"] = {
                "approved": True,  # Approve on error to prevent infinite loops
                "concerns": ["Failed to parse skeptic response"],
                "fatal_flaws": [],
                "suggestions": [],
                "loop_back_reason": None,
                "confidence": 0.5,
                "reasoning": "Error parsing response - proceeding by default",
            }
            state["skeptic_approved"] = True
            return state
