#!/usr/bin/env python3
"""
Comprehensive evaluation runner.

Runs all evaluation tests and generates a summary report.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.evaluation.test_routing_eval import (
    test_billing_routing,
    test_technical_routing,
    test_account_routing,
    test_edge_case_routing,
)
from tests.evaluation.test_tool_usage_eval import (
    test_billing_tool_usage,
    test_technical_tool_usage,
    test_account_tool_usage,
)
from tests.evaluation.test_benchmark import benchmark_category, dataset_file_to_category, calculate_statistics


async def run_all_evaluations():
    """Run all evaluation tests and generate comprehensive report."""
    print("\n" + "="*60)
    print("  COMPREHENSIVE EVALUATION SUITE")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)

    results = {
        "timestamp": datetime.now().isoformat(),
        "routing": {},
        "tool_usage": {},
        "performance": {},
        "summary": {},
    }

    # ===== ROUTING EVALUATION =====
    print("\n" + "#"*60)
    print("#  PART 1: ROUTING ACCURACY EVALUATION")
    print("#"*60)

    try:
        billing_routing = await test_billing_routing()
        technical_routing = await test_technical_routing()
        account_routing = await test_account_routing()
        edge_routing = await test_edge_case_routing()

        results["routing"] = {
            "billing": {
                "accuracy": billing_routing["accuracy"],
                "passed": billing_routing["passed"],
                "correct": billing_routing["correct"],
                "total": billing_routing["total"],
            },
            "technical": {
                "accuracy": technical_routing["accuracy"],
                "passed": technical_routing["passed"],
                "correct": technical_routing["correct"],
                "total": technical_routing["total"],
            },
            "account": {
                "accuracy": account_routing["accuracy"],
                "passed": account_routing["passed"],
                "correct": account_routing["correct"],
                "total": account_routing["total"],
            },
            "edge_cases": {
                "accuracy": edge_routing["accuracy"],
                "passed": edge_routing["passed"],
                "correct": edge_routing["correct"],
                "total": edge_routing["total"],
            },
        }

        routing_passed = all([
            billing_routing["passed"],
            technical_routing["passed"],
            account_routing["passed"],
            edge_routing["passed"],
        ])
        results["summary"]["routing_passed"] = routing_passed

    except Exception as e:
        print(f"❌ Routing evaluation failed: {e}")
        results["summary"]["routing_passed"] = False

    # ===== TOOL USAGE EVALUATION =====
    print("\n" + "#"*60)
    print("#  PART 2: TOOL USAGE CORRECTNESS EVALUATION")
    print("#"*60)

    try:
        billing_tools = await test_billing_tool_usage()
        technical_tools = await test_technical_tool_usage()
        account_tools = await test_account_tool_usage()

        results["tool_usage"] = {
            "billing": {
                "correctness": billing_tools["correctness"],
                "passed": billing_tools["passed"],
                "avg_f1_score": billing_tools["avg_f1_score"],
            },
            "technical": {
                "correctness": technical_tools["correctness"],
                "passed": technical_tools["passed"],
                "avg_f1_score": technical_tools["avg_f1_score"],
            },
            "account": {
                "correctness": account_tools["correctness"],
                "passed": account_tools["passed"],
                "avg_f1_score": account_tools["avg_f1_score"],
            },
        }

        tool_usage_passed = all([
            billing_tools["passed"],
            technical_tools["passed"],
            account_tools["passed"],
        ])
        results["summary"]["tool_usage_passed"] = tool_usage_passed

    except Exception as e:
        print(f"❌ Tool usage evaluation failed: {e}")
        results["summary"]["tool_usage_passed"] = False

    # ===== PERFORMANCE BENCHMARKS =====
    print("\n" + "#"*60)
    print("#  PART 3: PERFORMANCE BENCHMARKS")
    print("#"*60)

    try:
        benchmark_results = []

        for dataset_file in ["billing_cases.json", "technical_cases.json", "account_cases.json"]:
            result = await benchmark_category(dataset_file)
            benchmark_results.append(result)

        # Calculate overall performance
        all_durations = []
        total_tickets = 0
        total_cost = 0

        for result in benchmark_results:
            all_durations.extend([r["duration_ms"] for r in result["results"]])
            total_tickets += result["num_tests"]
            total_cost += result["total_cost"]

        overall_stats = calculate_statistics(all_durations)

        results["performance"] = {
            "total_tickets": total_tickets,
            "latency_ms": {
                "mean": overall_stats["mean"],
                "median": overall_stats["median"],
                "p95": overall_stats["p95"],
                "p99": overall_stats["p99"],
            },
            "total_cost": total_cost,
            "avg_cost_per_ticket": total_cost / total_tickets if total_tickets > 0 else 0,
        }

        # Check performance targets
        p95_passed = overall_stats["p95"] < 3000  # 3 seconds
        cost_passed = (total_cost / total_tickets) < 0.01 if total_tickets > 0 else False  # $0.01

        results["summary"]["performance_passed"] = p95_passed and cost_passed

    except Exception as e:
        print(f"❌ Performance benchmarks failed: {e}")
        results["summary"]["performance_passed"] = False

    # ===== FINAL SUMMARY =====
    print("\n" + "="*60)
    print("  EVALUATION SUMMARY")
    print("="*60)

    print(f"\nRouting Accuracy:")
    for category, data in results["routing"].items():
        status = "✅ PASSED" if data["passed"] else "❌ FAILED"
        print(f"  {category.capitalize()}: {data['accuracy']:.1%} ({data['correct']}/{data['total']}) {status}")

    print(f"\nTool Usage Correctness:")
    for category, data in results["tool_usage"].items():
        status = "✅ PASSED" if data["passed"] else "❌ FAILED"
        print(f"  {category.capitalize()}: {data['correctness']:.1%} (F1: {data['avg_f1_score']:.3f}) {status}")

    print(f"\nPerformance:")
    perf = results["performance"]
    print(f"  Total Tickets: {perf['total_tickets']}")
    print(f"  Latency P95: {perf['latency_ms']['p95']:.0f}ms {'✅' if perf['latency_ms']['p95'] < 3000 else '❌'}")
    print(f"  Latency P99: {perf['latency_ms']['p99']:.0f}ms")
    print(f"  Avg Cost: ${perf['avg_cost_per_ticket']:.4f} {'✅' if perf['avg_cost_per_ticket'] < 0.01 else '❌'}")

    # Overall result
    all_passed = all([
        results["summary"].get("routing_passed", False),
        results["summary"].get("tool_usage_passed", False),
        results["summary"].get("performance_passed", False),
    ])

    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL EVALUATIONS PASSED!")
    else:
        print("❌ SOME EVALUATIONS FAILED")
    print("="*60 + "\n")

    # Save results to file
    report_dir = Path(__file__).parent.parent / "evaluation_reports"
    report_dir.mkdir(exist_ok=True)

    report_file = report_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Report saved to: {report_file}")

    return 0 if all_passed else 1


async def main():
    """Main entry point."""
    try:
        exit_code = await run_all_evaluations()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
