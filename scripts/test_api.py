#!/usr/bin/env python3
"""
Test script for the Startup Analyzer API.

This script tests both the synchronous and streaming endpoints.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
import json
from datetime import datetime


async def test_health_endpoint(base_url: str = "http://localhost:8000"):
    """Test the health endpoint."""
    print("\n" + "=" * 80)
    print("Testing Health Endpoint")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False


async def test_root_endpoint(base_url: str = "http://localhost:8000"):
    """Test the root endpoint."""
    print("\n" + "=" * 80)
    print("Testing Root Endpoint")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False


async def test_synchronous_analysis(
    base_url: str = "http://localhost:8000",
    x_brand: str = "Uber",
    y_market: str = "Dog Walkers",
):
    """Test the synchronous analysis endpoint."""
    print("\n" + "=" * 80)
    print("Testing Synchronous Analysis Endpoint")
    print("=" * 80)

    request_data = {
        "x_brand": x_brand,
        "y_market": y_market,
        "description": "On-demand dog walking service with real-time GPS tracking",
    }

    print(f"\nRequest:")
    print(json.dumps(request_data, indent=2))

    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            print("\nSending request (this may take 30-60 seconds)...")
            response = await client.post(
                f"{base_url}/api/analyze",
                json=request_data,
            )

            print(f"\nStatus: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print("\n" + "-" * 80)
                print("Analysis Result:")
                print("-" * 80)
                print(f"Analysis ID: {result.get('analysis_id')}")
                print(f"Correlation ID: {result.get('correlation_id')}")
                print(f"Status: {result.get('status')}")
                print(f"Loop Count: {result.get('loop_count')}")
                print(f"Skeptic Approved: {result.get('skeptic_approved')}")

                # Display agent results
                if result.get('analyst_insights'):
                    print("\n" + "-" * 40)
                    print("Analyst Insights:")
                    print(f"  Brand: {result['analyst_insights']['brand_name']}")
                    print(f"  Confidence: {result['analyst_insights']['confidence']}")
                    print(f"  Strengths: {', '.join(result['analyst_insights']['core_strengths'][:3])}")

                if result.get('researcher_findings'):
                    print("\n" + "-" * 40)
                    print("Market Research:")
                    print(f"  Market: {result['researcher_findings']['market_name']}")
                    print(f"  Saturation: {result['researcher_findings']['saturation_level']}")
                    print(f"  Competitors: {result['researcher_findings']['competitor_count']}")

                if result.get('skeptic_critique'):
                    print("\n" + "-" * 40)
                    print("Skeptic Critique:")
                    print(f"  Approved: {result['skeptic_critique']['approved']}")
                    print(f"  Concerns: {len(result['skeptic_critique']['concerns'])}")
                    if result['skeptic_critique'].get('loop_back_reason'):
                        print(f"  Loop Reason: {result['skeptic_critique']['loop_back_reason']}")

                if result.get('strategist_plan'):
                    print("\n" + "-" * 40)
                    print("GTM Strategy:")
                    print(f"  Viability Score: {result['strategist_plan']['viability_score']}/10")
                    print(f"  Target Audience: {result['strategist_plan']['target_audience'][:100]}...")
                    print(f"  Value Prop: {result['strategist_plan']['value_proposition'][:100]}...")

                # Display metadata
                if result.get('metadata'):
                    print("\n" + "-" * 40)
                    print("Metadata:")
                    print(f"  Duration: {result['metadata']['total_duration_seconds']:.2f}s")
                    print(f"  Cost: ${result['metadata']['cost_usd']:.4f}")
                    if result['metadata'].get('token_usage'):
                        tokens = result['metadata']['token_usage']
                        print(f"  Tokens: {tokens.get('total_tokens', 0):,}")

                # Save result
                output_file = "test_api_result.json"
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"\n✅ Full result saved to {output_file}")

                return True
            else:
                print(f"Error Response: {response.text}")
                return False

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False


async def test_streaming_analysis(
    base_url: str = "http://localhost:8000",
    x_brand: str = "Netflix",
    y_market: str = "Fitness Classes",
):
    """Test the streaming analysis endpoint."""
    print("\n" + "=" * 80)
    print("Testing Streaming Analysis Endpoint (SSE)")
    print("=" * 80)

    request_data = {
        "x_brand": x_brand,
        "y_market": y_market,
        "description": "Subscription-based on-demand fitness classes",
    }

    print(f"\nRequest:")
    print(json.dumps(request_data, indent=2))

    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            print("\nConnecting to SSE stream...")
            async with client.stream(
                "POST",
                f"{base_url}/api/analyze/stream",
                json=request_data,
            ) as response:
                print(f"Status: {response.status_code}")

                if response.status_code != 200:
                    print(f"Error: {await response.aread()}")
                    return False

                print("\nReceiving events:\n")
                event_count = 0
                final_result = None

                async for line in response.aiter_lines():
                    if line.startswith("event:"):
                        event_type = line[6:].strip()
                        print(f"📡 {event_type}")
                        event_count += 1
                    elif line.startswith("data:"):
                        data = line[5:].strip()
                        try:
                            event_data = json.loads(data)

                            # Display relevant info based on event type
                            if event_data.get("agent"):
                                print(f"   Agent: {event_data['agent']} - {event_data.get('status', 'unknown')}")
                            elif event_data.get("iteration"):
                                print(f"   Loop Iteration: {event_data['iteration']}")
                                print(f"   Reason: {event_data.get('reason', 'N/A')}")
                            elif event_data.get("analysis_id"):
                                if "viability_score" in event_data:
                                    print(f"   Viability: {event_data.get('viability_score')}/10")
                                    print(f"   Duration: {event_data.get('duration_seconds', 0):.2f}s")
                                    print(f"   Cost: ${event_data.get('cost_usd', 0):.4f}")

                            # Save final result
                            if "status" in event_data and "analyst_insights" in event_data:
                                final_result = event_data
                        except json.JSONDecodeError:
                            pass

                print(f"\n✅ Received {event_count} events")

                if final_result:
                    output_file = "test_api_stream_result.json"
                    with open(output_file, "w") as f:
                        json.dump(final_result, f, indent=2, default=str)
                    print(f"✅ Final result saved to {output_file}")

                return True

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run all API tests."""
    print("\n" + "=" * 80)
    print("STARTUP ANALYZER API TEST SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now().isoformat()}")

    base_url = "http://localhost:8000"

    # Test 1: Health check
    health_ok = await test_health_endpoint(base_url)

    # Test 2: Root endpoint
    root_ok = await test_root_endpoint(base_url)

    # Test 3: Synchronous analysis
    sync_ok = await test_synchronous_analysis(
        base_url,
        x_brand="Uber",
        y_market="Dog Walkers",
    )

    # Test 4: Streaming analysis
    stream_ok = await test_streaming_analysis(
        base_url,
        x_brand="Netflix",
        y_market="Fitness Classes",
    )

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Health Endpoint:      {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Root Endpoint:        {'✅ PASS' if root_ok else '❌ FAIL'}")
    print(f"Synchronous Analysis: {'✅ PASS' if sync_ok else '❌ FAIL'}")
    print(f"Streaming Analysis:   {'✅ PASS' if stream_ok else '❌ FAIL'}")
    print("=" * 80)

    all_passed = all([health_ok, root_ok, sync_ok, stream_ok])

    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
