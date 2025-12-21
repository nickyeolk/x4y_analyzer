"""
Performance benchmark tests.

Measures end-to-end latency, token usage, and cost metrics.
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Any
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestration.graph import process_ticket
from src.observability.context import set_correlation_id


async def load_test_cases(dataset_file: str) -> list:
    """Load test cases from dataset file."""
    dataset_path = Path(__file__).parent / "datasets" / dataset_file
    with open(dataset_path, "r") as f:
        return json.load(f)


async def run_ticket_with_timing(test_case: dict) -> Dict[str, Any]:
    """Run a single test case and measure timing."""
    set_correlation_id(f"BENCH-{test_case['test_id']}")

    start_time = time.time()

    state = await process_ticket(
        ticket_id=f"T-{test_case['test_id']}",
        correlation_id=f"BENCH-{test_case['test_id']}",
        customer_id=test_case["customer_id"],
        subject=test_case["subject"],
        body=test_case["input"],
        email=test_case.get("email", "test@example.com"),
    )

    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000

    return {
        "test_id": test_case["test_id"],
        "category": dataset_file_to_category(test_case.get("source_dataset", "")),
        "duration_ms": duration_ms,
        "token_usage": state.get("metadata", {}).get("token_usage", {}),
        "agent_latencies": state.get("metadata", {}).get("latency_ms", {}),
        "num_interactions": len(state.get("agent_interactions", [])),
        "num_tool_calls": sum(
            len(i.get("tool_calls", [])) for i in state.get("agent_interactions", [])
        ),
    }


def dataset_file_to_category(filename: str) -> str:
    """Extract category from dataset filename."""
    if "billing" in filename:
        return "billing"
    elif "technical" in filename:
        return "technical"
    elif "account" in filename:
        return "account"
    elif "edge" in filename:
        return "edge_case"
    return "unknown"


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """Calculate statistical measures."""
    if not values:
        return {"min": 0, "max": 0, "mean": 0, "median": 0, "p50": 0, "p95": 0, "p99": 0}

    sorted_values = sorted(values)
    n = len(sorted_values)

    return {
        "min": sorted_values[0],
        "max": sorted_values[-1],
        "mean": statistics.mean(sorted_values),
        "median": statistics.median(sorted_values),
        "p50": sorted_values[int(n * 0.50)],
        "p95": sorted_values[int(n * 0.95)] if n >= 20 else sorted_values[-1],
        "p99": sorted_values[int(n * 0.99)] if n >= 100 else sorted_values[-1],
    }


async def benchmark_category(dataset_file: str) -> Dict[str, Any]:
    """Benchmark a specific category of tickets."""
    category = dataset_file_to_category(dataset_file)
    print(f"\nBenchmarking {category.upper()} tickets...")

    test_cases = await load_test_cases(dataset_file)

    # Add source dataset to each test case
    for tc in test_cases:
        tc["source_dataset"] = dataset_file

    results = []
    for test_case in test_cases:
        print(f"  Processing {test_case['test_id']}...", end=" ")
        result = await run_ticket_with_timing(test_case)
        results.append(result)
        print(f"{result['duration_ms']:.0f}ms")

    # Calculate statistics
    durations = [r["duration_ms"] for r in results]
    stats = calculate_statistics(durations)

    # Calculate token usage
    total_prompt_tokens = 0
    total_completion_tokens = 0

    for result in results:
        for agent, usage in result["token_usage"].items():
            total_prompt_tokens += usage.get("prompt", 0)
            total_completion_tokens += usage.get("completion", 0)

    avg_prompt_tokens = total_prompt_tokens / len(results) if results else 0
    avg_completion_tokens = total_completion_tokens / len(results) if results else 0

    # Calculate cost (based on mock pricing: $3/MTok input, $15/MTok output)
    total_cost = (total_prompt_tokens / 1_000_000 * 3) + (total_completion_tokens / 1_000_000 * 15)
    avg_cost = total_cost / len(results) if results else 0

    return {
        "category": category,
        "num_tests": len(results),
        "latency_stats": stats,
        "avg_prompt_tokens": avg_prompt_tokens,
        "avg_completion_tokens": avg_completion_tokens,
        "total_cost": total_cost,
        "avg_cost_per_ticket": avg_cost,
        "results": results,
    }


def print_benchmark_summary(benchmark_results: List[Dict[str, Any]]):
    """Print a formatted summary of benchmark results."""
    print("\n" + "="*60)
    print("  PERFORMANCE BENCHMARK SUMMARY")
    print("="*60)

    for result in benchmark_results:
        print(f"\n{result['category'].upper()} ({result['num_tests']} tickets):")
        print(f"  Latency:")
        print(f"    Mean:   {result['latency_stats']['mean']:.0f}ms")
        print(f"    Median: {result['latency_stats']['median']:.0f}ms")
        print(f"    P95:    {result['latency_stats']['p95']:.0f}ms")
        print(f"    P99:    {result['latency_stats']['p99']:.0f}ms")
        print(f"  Token Usage:")
        print(f"    Avg Prompt:     {result['avg_prompt_tokens']:.0f}")
        print(f"    Avg Completion: {result['avg_completion_tokens']:.0f}")
        print(f"  Cost:")
        print(f"    Total:       ${result['total_cost']:.4f}")
        print(f"    Per Ticket:  ${result['avg_cost_per_ticket']:.4f}")

    # Overall statistics
    all_durations = []
    total_tickets = 0
    total_cost = 0

    for result in benchmark_results:
        all_durations.extend([r["duration_ms"] for r in result["results"]])
        total_tickets += result["num_tests"]
        total_cost += result["total_cost"]

    overall_stats = calculate_statistics(all_durations)

    print(f"\nOVERALL ({total_tickets} tickets):")
    print(f"  Latency:")
    print(f"    Mean:   {overall_stats['mean']:.0f}ms")
    print(f"    Median: {overall_stats['median']:.0f}ms")
    print(f"    P95:    {overall_stats['p95']:.0f}ms")
    print(f"    P99:    {overall_stats['p99']:.0f}ms")
    print(f"  Total Cost: ${total_cost:.4f}")
    print(f"  Avg Cost Per Ticket: ${total_cost/total_tickets:.4f}")

    # Performance targets
    print(f"\n  Performance Targets:")
    p95_threshold = 3000  # 3 seconds
    p95_passed = overall_stats['p95'] < p95_threshold
    print(f"    P95 < {p95_threshold}ms: {'✅ PASSED' if p95_passed else '❌ FAILED'} (actual: {overall_stats['p95']:.0f}ms)")

    cost_threshold = 0.01  # $0.01 per ticket
    cost_passed = (total_cost / total_tickets) < cost_threshold
    print(f"    Avg Cost < ${cost_threshold}: {'✅ PASSED' if cost_passed else '❌ FAILED'} (actual: ${total_cost/total_tickets:.4f})")

    print("="*60 + "\n")

    return p95_passed and cost_passed


async def main():
    """Run performance benchmarks."""
    print("\n" + "="*60)
    print("  PERFORMANCE BENCHMARK SUITE")
    print("="*60)

    try:
        # Benchmark each category
        benchmark_results = []

        for dataset_file in ["billing_cases.json", "technical_cases.json", "account_cases.json"]:
            result = await benchmark_category(dataset_file)
            benchmark_results.append(result)

        # Print summary and check if targets met
        all_passed = print_benchmark_summary(benchmark_results)

        print(f"{'✅ ALL PERFORMANCE TARGETS MET!' if all_passed else '⚠️  SOME TARGETS NOT MET'}\n")

        return 0 if all_passed else 1

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
