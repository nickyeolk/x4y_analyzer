"""
Test script for the complete LangGraph workflow.

This script tests the full analysis workflow with a sample business idea.

Usage:
    python scripts/test_workflow.py

Requirements:
    - .env file with API keys (OPENROUTER_API_KEY, TAVILY_API_KEY)
    - RAG vector store built (python scripts/build_vector_store.py)
"""

import sys
import asyncio
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def test_workflow():
    """Test the complete workflow with a sample business idea."""
    print("=" * 70)
    print("STARTUP ANALYZER - WORKFLOW TEST")
    print("=" * 70)
    print()

    # Test case: "Uber for Dog Walkers"
    test_case = {
        "x_brand": "Uber",
        "y_market": "Dog Walkers",
        "description": "On-demand dog walking service with real-time tracking",
    }

    print(f"Test Case: {test_case['x_brand']} for {test_case['y_market']}")
    print(f"Description: {test_case['description']}")
    print()
    print("=" * 70)
    print()

    try:
        # Import workflow
        from src.orchestration.graph import analyze_startup
        import uuid

        # Generate IDs
        analysis_id = f"TEST-{uuid.uuid4().hex[:8]}"
        correlation_id = f"CID-{uuid.uuid4().hex[:8]}"

        print(f"Analysis ID: {analysis_id}")
        print(f"Correlation ID: {correlation_id}")
        print()

        # Execute workflow
        print("🚀 Starting analysis workflow...")
        print()

        result = await analyze_startup(
            analysis_id=analysis_id,
            correlation_id=correlation_id,
            x_brand=test_case["x_brand"],
            y_market=test_case["y_market"],
            description=test_case["description"],
        )

        # Display results
        print()
        print("=" * 70)
        print("ANALYSIS RESULTS")
        print("=" * 70)
        print()

        # Status
        print(f"Status: {result.get('status')}")
        print(f"Loop Count: {result.get('loop_count', 0)}")
        print(f"Skeptic Approved: {result.get('skeptic_approved', False)}")
        print()

        # Analyst Insights
        print("─" * 70)
        print("1. ANALYST - Brand DNA")
        print("─" * 70)
        analyst = result.get("analyst_insights", {})
        if analyst:
            print(f"Brand: {analyst.get('brand_name')}")
            print(f"Confidence: {analyst.get('confidence', 0):.2f}")
            print(f"Summary: {analyst.get('summary', 'N/A')}")
            print(f"Core Strengths: {', '.join(analyst.get('core_strengths', [])[:3])}")
        print()

        # Researcher Findings
        print("─" * 70)
        print("2. RESEARCHER - Market Analysis")
        print("─" * 70)
        researcher = result.get("researcher_findings", {})
        if researcher:
            print(f"Market: {researcher.get('market_name')}")
            print(f"Saturation: {researcher.get('saturation_level', 'unknown').upper()}")
            print(f"Competitors: {researcher.get('competitor_count', 0)}")
            print(f"Summary: {researcher.get('summary', 'N/A')}")
        print()

        # Skeptic Critique
        print("─" * 70)
        print("3. SKEPTIC - Critical Evaluation")
        print("─" * 70)
        skeptic = result.get("skeptic_critique", {})
        if skeptic:
            print(f"Approved: {'✅ YES' if skeptic.get('approved') else '❌ NO'}")
            print(f"Confidence: {skeptic.get('confidence', 0):.2f}")
            if not skeptic.get('approved'):
                print(f"Loop Back Reason: {skeptic.get('loop_back_reason', 'N/A')}")
            concerns = skeptic.get('concerns', [])
            if concerns:
                print(f"Concerns: {len(concerns)}")
                for i, concern in enumerate(concerns[:3], 1):
                    print(f"  {i}. {concern}")
        print()

        # Strategist Plan
        print("─" * 70)
        print("4. STRATEGIST - GTM Plan")
        print("─" * 70)
        strategist = result.get("strategist_plan", {})
        if strategist:
            print(f"Viability Score: {strategist.get('viability_score', 0):.2f}")
            print(f"Target Audience: {strategist.get('target_audience', 'N/A')}")
            print(f"Value Proposition: {strategist.get('value_proposition', 'N/A')[:100]}...")
            print()
            hooks = strategist.get('marketing_hooks', [])
            if hooks:
                print("Marketing Hooks:")
                for i, hook in enumerate(hooks, 1):
                    print(f"  {i}. {hook}")
            print()
            print(f"Summary: {strategist.get('summary', 'N/A')}")
        print()

        # Metadata
        print("─" * 70)
        print("METADATA")
        print("─" * 70)
        metadata = result.get("metadata", {})
        token_usage = metadata.get("token_usage", {})
        total_prompt = sum(t.get("prompt_tokens", 0) for t in token_usage.values())
        total_completion = sum(t.get("completion_tokens", 0) for t in token_usage.values())
        total_tokens = total_prompt + total_completion
        cost = metadata.get("cost_usd", 0)
        duration = metadata.get("total_duration_seconds", 0)

        print(f"Duration: {duration:.2f} seconds")
        print(f"Total Tokens: {total_tokens:,} ({total_prompt:,} prompt + {total_completion:,} completion)")
        print(f"Estimated Cost: ${cost:.4f}")
        print(f"Iterations: {result.get('loop_count', 0) + 1}")
        print()

        # Agent breakdown
        print("Token Usage by Agent:")
        for agent, usage in token_usage.items():
            agent_total = usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
            print(f"  - {agent}: {agent_total:,} tokens")
        print()

        # Save result
        output_file = project_root / "test_workflow_result.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Full result saved to: {output_file}")
        print()

        print("=" * 70)
        print("✅ WORKFLOW TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()

        return True

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ WORKFLOW TEST FAILED")
        print("=" * 70)
        print()
        print(f"Error: {str(e)}")
        print(f"Error Type: {type(e).__name__}")
        print()

        import traceback
        print("Traceback:")
        traceback.print_exc()
        print()

        return False


if __name__ == "__main__":
    print()
    print("NOTE: This test requires:")
    print("  1. .env file with OPENROUTER_API_KEY and TAVILY_API_KEY")
    print("  2. RAG vector store built (run: python scripts/build_vector_store.py)")
    print()

    success = asyncio.run(test_workflow())
    sys.exit(0 if success else 1)
