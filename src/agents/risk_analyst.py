"""
The Risk Analyst Agent - Risk Assessment & Threat Identification

Identifies competitive threats, market risks, execution challenges, and fatal flaws.
"""

import json
from typing import Dict, Any
from datetime import datetime

from src.agents.base import BaseAgent
from src.agents.prompts.risk_analyst import RISK_ANALYST_SYSTEM_PROMPT
from src.llm.openrouter_client import get_llm_client, OpenRouterClient
from src.tools.marketing_rag import get_rag_tool
from src.tools.base import ToolInput
from src.orchestration.state import AgentInteraction
from src.observability.decorators import trace_agent
from src.observability.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class RiskAnalystAgent(BaseAgent):
    """
    The Risk Analyst - Identifies threats, risks, and potential failure modes.

    Provides critical analysis of competitive threats, market risks,
    execution challenges, and financial concerns to inform strategy.
    """

    def __init__(self):
        super().__init__(name="risk_analyst")
        self.llm_client = get_llm_client()
        # OPTIMIZATION: Use faster/cheaper GPT-4o-mini for simple classification task
        self.classification_client = OpenRouterClient(
            api_key=settings.openrouter_api_key,
            model="openai/gpt-4o-mini"
        )
        self.rag_tool = get_rag_tool()

    @trace_agent("risk_analyst")
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute risk analyst logic.

        Args:
            state: Current analysis state

        Returns:
            Updated state with risk analysis
        """
        business_idea = state.get("business_idea") or {}
        analyst_insights = state.get("analyst_insights") or {}
        researcher_findings = state.get("researcher_findings") or {}

        full_idea = business_idea.get("full_idea", "Unknown business idea")

        logger.info(
            "risk_analyst_started",
            idea=full_idea,
        )

        # Step 1: Classify business model to query relevant risk frameworks
        # OPTIMIZATION: Use GPT-4o-mini for this simple classification task (saves ~2-3s)
        logger.info("risk_analyst_classifying_business_model", idea=full_idea, model="gpt-4o-mini")

        classification_response = await self.classification_client.generate(
            system="You are a business model expert. Classify startup ideas into business model types.",
            messages=[{
                "role": "user",
                "content": f"""Classify this business idea into ONE primary business model type: {full_idea}

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
        logger.info("risk_analyst_business_model_classified", type=business_model_type, model="gpt-4o-mini")

        # Step 2: Build targeted RAG query for risks based on business model type
        rag_query_map = {
            "marketplace": "marketplace startup risks cold start problem chicken-egg dilemma network effects failure competitive threats regulatory barriers",
            "subscription": "subscription business risks churn rate customer retention pricing pressure competitive threats SaaS failures",
            "saas": "B2B SaaS risks enterprise sales cycle switching costs implementation challenges support burden security compliance",
            "ecommerce": "ecommerce risks inventory management supply chain logistics competitive pricing customer acquisition cost",
            "service": "service business risks scalability constraints quality consistency hiring challenges pricing pressure",
            "hardware": "hardware product risks manufacturing supply chain capital intensive distribution retail margins",
            "other": "startup failure reasons competitive threats market risks execution challenges financial risks",
        }

        # Get specific query or fallback to generic
        rag_query = rag_query_map.get(business_model_type, rag_query_map["other"])
        logger.info("risk_analyst_consulting_rag", query=rag_query, business_model=business_model_type)

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

        # Step 3: Prepare risk analysis context
        user_message = f"""Analyze the risks and threats for this business idea:

Business Idea: {full_idea}

ANALYST'S BRAND DNA ANALYSIS:
{json.dumps(analyst_insights, indent=2)}

RESEARCHER'S MARKET FINDINGS:
{json.dumps(researcher_findings, indent=2)}

RISK FRAMEWORKS & PITFALLS:
{rag_context}

INSTRUCTIONS:
Identify and analyze:
1. Competitive threats - Who will fight back? What advantages do incumbents have?
2. Market risks - Saturation, regulatory barriers, timing issues
3. Execution challenges - What's hard? What commonly fails?
4. Financial risks - Unit economics, CAC vs LTV, burn rate concerns
5. Fatal flaws - Deal-breakers that could make this unviable

Provide a balanced, realistic assessment of what could go wrong.
"""

        llm_response = await self.llm_client.generate(
            system=RISK_ANALYST_SYSTEM_PROMPT,
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

            # Log risk analysis
            self.log_decision(
                decision="risk_analysis_complete",
                reasoning=analysis.get("summary", ""),
                confidence=analysis.get("confidence", 0.7),
            )

            # Record interaction
            interaction = AgentInteraction(
                agent_name="risk_analyst",
                timestamp=datetime.utcnow(),
                action="risk_analysis",
                reasoning=analysis.get("summary", ""),
                tool_calls=[
                    {"tool": "llm_classification", "business_model": business_model_type},
                    {"tool": "marketing_rag", "query": rag_query}
                ],
                result=f"Risk Level: {analysis.get('overall_risk_level', 'unknown')} - {len(analysis.get('competitive_threats', []))} threats, {len(analysis.get('fatal_flaws', []))} fatal flaws identified",
                iteration=0,
            )

            # Update state
            if "agent_interactions" not in state:
                state["agent_interactions"] = []
            state["agent_interactions"].append(interaction.__dict__)

            # Store risk analysis
            state["risk_analysis"] = {
                "competitive_threats": analysis.get("competitive_threats", []),
                "market_risks": analysis.get("market_risks", []),
                "execution_challenges": analysis.get("execution_challenges", []),
                "financial_risks": analysis.get("financial_risks", []),
                "fatal_flaws": analysis.get("fatal_flaws", []),
                "overall_risk_level": analysis.get("overall_risk_level", "medium"),
                "summary": analysis.get("summary", ""),
                "confidence": analysis.get("confidence", 0.7),
            }

            # Update metadata
            if "metadata" not in state:
                state["metadata"] = {}
            if "token_usage" not in state["metadata"]:
                state["metadata"]["token_usage"] = {}
            state["metadata"]["token_usage"]["risk_analyst"] = {
                "classification_prompt_tokens": classification_response.prompt_tokens,
                "classification_completion_tokens": classification_response.completion_tokens,
                "analysis_prompt_tokens": llm_response.prompt_tokens,
                "analysis_completion_tokens": llm_response.completion_tokens,
                "total_tokens": (
                    classification_response.total_tokens + llm_response.total_tokens
                ),
            }

            logger.info(
                "risk_analyst_completed",
                risk_level=analysis.get("overall_risk_level"),
                confidence=analysis.get("confidence"),
                threats_count=len(analysis.get("competitive_threats", [])),
                fatal_flaws_count=len(analysis.get("fatal_flaws", [])),
            )

            return state

        except json.JSONDecodeError as e:
            logger.error(
                "risk_analyst_parse_error",
                error=str(e),
                response=llm_response.content[:500],
            )
            # Fallback: create minimal risk analysis
            state["risk_analysis"] = {
                "competitive_threats": [],
                "market_risks": [],
                "execution_challenges": [],
                "financial_risks": [],
                "fatal_flaws": [],
                "overall_risk_level": "unknown",
                "summary": "Failed to parse risk analysis response",
                "confidence": 0.5,
            }
            return state


    async def execute_focused(self, state: Dict[str, Any], focus_query: str) -> Dict[str, Any]:
        """
        Execute focused risk analysis based on Strategist's specific query.

        Args:
            state: Current analysis state
            focus_query: Specific question or area to investigate

        Returns:
            Focused risk analysis results
        """
        business_idea = state.get("business_idea") or {}

        logger.info(
            "risk_analyst_focused_analysis_started",
            query=focus_query[:100] if focus_query else "",
        )

        # Use existing risk context
        existing_analysis = state.get("risk_analysis", {})
        full_idea = business_idea.get("full_idea", "Unknown business idea")

        # Focused search for specific risk area
        search_query = f"{full_idea} {focus_query} risks challenges threats"
        logger.info("risk_analyst_focused_search", query=search_query)

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
        user_message = f"""Focused Risk Analysis Request: {focus_query}

Business Idea: {full_idea}

EXISTING RISK ANALYSIS:
{json.dumps(existing_analysis, indent=2)}

ADDITIONAL WEB RESEARCH:
{search_context}

Provide detailed, focused risk analysis addressing the specific query above.
Return JSON with:
{{
  "query": "{focus_query}",
  "risks": ["risk1", "risk2", ...],
  "insights": "detailed analysis",
  "severity": "high|medium|low",
  "confidence": 0.0-1.0
}}
"""

        llm_response = await self.llm_client.generate(
            system=RISK_ANALYST_SYSTEM_PROMPT,
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
                "risk_analyst_focused_analysis_completed",
                confidence=result.get("confidence", 0.7),
            )

            return {
                "type": "focused_risk_analysis",
                "agent": "risk_analyst",
                "query": focus_query,
                "risks": result.get("risks", []),
                "insights": result.get("insights", ""),
                "severity": result.get("severity", "medium"),
                "confidence": result.get("confidence", 0.7),
            }

        except json.JSONDecodeError as e:
            logger.error(
                "risk_analyst_focused_parse_error",
                error=str(e),
                response=llm_response.content[:300],
            )
            return {
                "type": "focused_risk_analysis",
                "agent": "risk_analyst",
                "query": focus_query,
                "risks": [],
                "insights": llm_response.content[:500],
                "severity": "unknown",
                "confidence": 0.5,
            }


def get_risk_analyst() -> RiskAnalystAgent:
    """Get or create RiskAnalyst agent instance."""
    return RiskAnalystAgent()

