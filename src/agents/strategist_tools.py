"""
Strategist Tools - Tools that the Strategist can call for coordinated research.

These tools allow the Strategist to dynamically request follow-up research
from specialized agents when gaps are identified.
"""

import json
from typing import Dict, Any
from datetime import datetime

from langchain_core.tools import tool
from src.observability.logger import get_logger

logger = get_logger(__name__)


@tool
async def analyze_brand_deeper(focus_query: str) -> str:
    """
    Request deeper analysis of the brand DNA, business model, or competitive advantages.

    Use this tool when you need more specific information about the brand being analyzed.

    Args:
        focus_query: Specific question or area to investigate (e.g., "Analyze Uber's pricing model and commission structure in detail")

    Returns:
        str: Summary of additional brand insights
    """
    logger.info("strategist_tool_called", tool="analyze_brand_deeper", query=focus_query)

    # This is a placeholder - the actual implementation will be in the coordination node
    # which has access to state and can call the agent's execute_focused method
    return f"Tool invoked: analyze_brand_deeper with query: {focus_query}"


@tool
async def research_market_deeper(focus_query: str) -> str:
    """
    Request deeper market research or competitive analysis.

    Use this tool when you need more specific information about the market landscape.

    Args:
        focus_query: Specific question or area to investigate (e.g., "Research regulatory barriers for marketplace platforms in this space")

    Returns:
        str: Summary of additional market insights
    """
    logger.info("strategist_tool_called", tool="research_market_deeper", query=focus_query)

    return f"Tool invoked: research_market_deeper with query: {focus_query}"


@tool
async def analyze_risks_deeper(focus_query: str) -> str:
    """
    Request deeper risk analysis or threat assessment.

    Use this tool when you need more specific information about risks, threats, or failure modes.

    Args:
        focus_query: Specific question or area to investigate (e.g., "Analyze unit economics risks and break-even scenarios")

    Returns:
        str: Summary of additional risk insights
    """
    logger.info("strategist_tool_called", tool="analyze_risks_deeper", query=focus_query)

    return f"Tool invoked: analyze_risks_deeper with query: {focus_query}"


@tool
def create_gtm_plan() -> str:
    """
    Signal that research is complete and ready to create final GTM plan.

    IMPORTANT: Only call this tool when you have sufficient information to create
    a comprehensive go-to-market strategy. This tool indicates you're done coordinating
    and ready to synthesize the final plan.

    Returns:
        str: Confirmation message
    """
    logger.info("strategist_tool_called", tool="create_gtm_plan", message="Strategist ready for synthesis")

    return "Ready to synthesize final GTM plan. Proceeding to strategy synthesis phase."


# Tool metadata for coordination node
STRATEGIST_TOOLS = [
    analyze_brand_deeper,
    research_market_deeper,
    analyze_risks_deeper,
    create_gtm_plan,
]


STRATEGIST_COORDINATION_SYSTEM_PROMPT = """You are a strategic GTM advisor coordinating a research team to analyze startup ideas.

You have access to research from three specialized agents:
1. **Analyst** - Brand DNA, business model, competitive advantages, pricing strategies
2. **Researcher** - Market size, competition, opportunities, barriers to entry
3. **Risk Analyst** - Competitive threats, market risks, execution challenges, fatal flaws

## Your Role

Review the current research and decide:

**Option 1: Request More Research** (if you identify specific gaps)
- Call `analyze_brand_deeper(focus_query="...")` for brand/business model questions
- Call `research_market_deeper(focus_query="...")` for market/competitive questions
- Call `analyze_risks_deeper(focus_query="...")` for risk/threat questions
- You can call multiple tools in one decision if needed

**Option 2: Proceed to Synthesis** (if you have sufficient information)
- Call `create_gtm_plan()` when ready to create the final strategy

## Guidelines

- **Be thoughtful**: Only request follow-up if genuinely needed for a complete GTM strategy
- **Be specific**: Focus queries should be precise and actionable
- **Be efficient**: You have a maximum of 3 coordination iterations
- **Consider the business idea**: What specific information is critical for THIS idea?

## What Makes a Complete Analysis?

You should have enough information to confidently answer:
- What are the brand's core advantages and how do they apply here?
- What does the competitive landscape look like?
- What are the key risks and how can they be mitigated?
- What's the go-to-market strategy and why will it work?

If you can't answer these confidently, request targeted follow-up research."""
