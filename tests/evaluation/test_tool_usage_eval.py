"""
Tool usage evaluation tests.

Tests whether agents call the correct tools for different scenarios.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestration.graph import process_ticket
from src.observability.context import set_correlation_id
from tests.evaluation.metrics.tool_usage_metric import ToolUsageMetric


async def load_test_cases(dataset_file: str) -> list:
    """Load test cases from dataset file."""
    dataset_path = Path(__file__).parent / "datasets" / dataset_file
    with open(dataset_path, "r") as f:
        return json.load(f)


async def run_ticket_through_workflow(test_case: dict) -> dict:
    """Run a single test case through the workflow."""
    set_correlation_id(f"EVAL-{test_case['test_id']}")

    state = await process_ticket(
        ticket_id=f"T-{test_case['test_id']}",
        correlation_id=f"EVAL-{test_case['test_id']}",
        customer_id=test_case["customer_id"],
        subject=test_case["subject"],
        body=test_case["input"],
        email=test_case.get("email", "test@example.com"),
    )

    return state


async def test_billing_tool_usage():
    """Test tool usage for billing tickets."""
    print("\n" + "="*60)
    print("  Testing Billing Ticket Tool Usage")
    print("="*60)

    test_cases = await load_test_cases("billing_cases.json")
    actual_results = []

    for test_case in test_cases:
        print(f"Processing {test_case['test_id']}...", end=" ")
        state = await run_ticket_through_workflow(test_case)
        actual_results.append(state)
        print("✓")

    metric = ToolUsageMetric(threshold=0.80)  # 80% for tool usage
    results = metric.evaluate(test_cases, actual_results)

    print(metric.get_summary(results))

    return results


async def test_technical_tool_usage():
    """Test tool usage for technical tickets."""
    print("\n" + "="*60)
    print("  Testing Technical Ticket Tool Usage")
    print("="*60)

    test_cases = await load_test_cases("technical_cases.json")
    actual_results = []

    for test_case in test_cases:
        print(f"Processing {test_case['test_id']}...", end=" ")
        state = await run_ticket_through_workflow(test_case)
        actual_results.append(state)
        print("✓")

    metric = ToolUsageMetric(threshold=0.80)
    results = metric.evaluate(test_cases, actual_results)

    print(metric.get_summary(results))

    return results


async def test_account_tool_usage():
    """Test tool usage for account tickets."""
    print("\n" + "="*60)
    print("  Testing Account Ticket Tool Usage")
    print("="*60)

    test_cases = await load_test_cases("account_cases.json")
    actual_results = []

    for test_case in test_cases:
        print(f"Processing {test_case['test_id']}...", end=" ")
        state = await run_ticket_through_workflow(test_case)
        actual_results.append(state)
        print("✓")

    metric = ToolUsageMetric(threshold=0.80)
    results = metric.evaluate(test_cases, actual_results)

    print(metric.get_summary(results))

    return results


async def test_overall_tool_usage():
    """Test tool usage across all ticket categories."""
    print("\n" + "="*60)
    print("  Testing Overall Tool Usage Correctness")
    print("="*60)

    all_test_cases = []
    all_actual_results = []

    # Load all datasets (exclude edge_cases as they don't all have expected_tools)
    for dataset_file in ["billing_cases.json", "technical_cases.json", "account_cases.json"]:
        test_cases = await load_test_cases(dataset_file)
        all_test_cases.extend(test_cases)

        for test_case in test_cases:
            state = await run_ticket_through_workflow(test_case)
            all_actual_results.append(state)

    metric = ToolUsageMetric(threshold=0.80)
    results = metric.evaluate(all_test_cases, all_actual_results)

    print(metric.get_summary(results))

    return results


async def main():
    """Run all tool usage evaluation tests."""
    print("\n" + "="*60)
    print("  TOOL USAGE EVALUATION TEST SUITE")
    print("="*60)

    try:
        # Run category-specific tests
        billing_results = await test_billing_tool_usage()
        technical_results = await test_technical_tool_usage()
        account_results = await test_account_tool_usage()

        # Summary
        print("\n" + "="*60)
        print("  TOOL USAGE EVALUATION SUMMARY")
        print("="*60)
        print(f"\nBilling Tool Usage: {billing_results['correctness']:.1%} ({'✅ PASSED' if billing_results['passed'] else '❌ FAILED'})")
        print(f"  Avg F1 Score: {billing_results['avg_f1_score']:.3f}")
        print(f"\nTechnical Tool Usage: {technical_results['correctness']:.1%} ({'✅ PASSED' if technical_results['passed'] else '❌ FAILED'})")
        print(f"  Avg F1 Score: {technical_results['avg_f1_score']:.3f}")
        print(f"\nAccount Tool Usage: {account_results['correctness']:.1%} ({'✅ PASSED' if account_results['passed'] else '❌ FAILED'})")
        print(f"  Avg F1 Score: {account_results['avg_f1_score']:.3f}")

        all_passed = all([
            billing_results['passed'],
            technical_results['passed'],
            account_results['passed']
        ])

        print(f"\n{'✅ ALL TESTS PASSED!' if all_passed else '❌ SOME TESTS FAILED'}")
        print("="*60 + "\n")

        return 0 if all_passed else 1

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
