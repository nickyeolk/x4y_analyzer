"""
Routing evaluation tests.

Tests the accuracy of the triage agent's routing decisions across all ticket categories.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestration.graph import process_ticket
from src.observability.context import set_correlation_id
from tests.evaluation.metrics.routing_accuracy import RoutingAccuracyMetric


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


async def test_billing_routing():
    """Test routing accuracy for billing tickets."""
    print("\n" + "="*60)
    print("  Testing Billing Ticket Routing")
    print("="*60)

    test_cases = await load_test_cases("billing_cases.json")
    actual_results = []

    for test_case in test_cases:
        print(f"Processing {test_case['test_id']}...", end=" ")
        state = await run_ticket_through_workflow(test_case)
        actual_results.append(state)
        print("✓")

    metric = RoutingAccuracyMetric(threshold=0.9)
    results = metric.evaluate(test_cases, actual_results)

    print(metric.get_summary(results))

    return results


async def test_technical_routing():
    """Test routing accuracy for technical tickets."""
    print("\n" + "="*60)
    print("  Testing Technical Ticket Routing")
    print("="*60)

    test_cases = await load_test_cases("technical_cases.json")
    actual_results = []

    for test_case in test_cases:
        print(f"Processing {test_case['test_id']}...", end=" ")
        state = await run_ticket_through_workflow(test_case)
        actual_results.append(state)
        print("✓")

    metric = RoutingAccuracyMetric(threshold=0.9)
    results = metric.evaluate(test_cases, actual_results)

    print(metric.get_summary(results))

    return results


async def test_account_routing():
    """Test routing accuracy for account tickets."""
    print("\n" + "="*60)
    print("  Testing Account Ticket Routing")
    print("="*60)

    test_cases = await load_test_cases("account_cases.json")
    actual_results = []

    for test_case in test_cases:
        print(f"Processing {test_case['test_id']}...", end=" ")
        state = await run_ticket_through_workflow(test_case)
        actual_results.append(state)
        print("✓")

    metric = RoutingAccuracyMetric(threshold=0.9)
    results = metric.evaluate(test_cases, actual_results)

    print(metric.get_summary(results))

    return results


async def test_edge_case_routing():
    """Test routing accuracy for edge case tickets."""
    print("\n" + "="*60)
    print("  Testing Edge Case Ticket Routing")
    print("="*60)

    test_cases = await load_test_cases("edge_cases.json")
    actual_results = []

    for test_case in test_cases:
        print(f"Processing {test_case['test_id']}...", end=" ")
        state = await run_ticket_through_workflow(test_case)
        actual_results.append(state)
        print("✓")

    # Lower threshold for edge cases (70%) since they're ambiguous
    metric = RoutingAccuracyMetric(threshold=0.7)
    results = metric.evaluate(test_cases, actual_results)

    print(metric.get_summary(results))

    return results


async def test_overall_routing():
    """Test routing accuracy across all ticket categories."""
    print("\n" + "="*60)
    print("  Testing Overall Routing Accuracy")
    print("="*60)

    all_test_cases = []
    all_actual_results = []

    # Load all datasets
    for dataset_file in ["billing_cases.json", "technical_cases.json", "account_cases.json", "edge_cases.json"]:
        test_cases = await load_test_cases(dataset_file)
        all_test_cases.extend(test_cases)

        for test_case in test_cases:
            state = await run_ticket_through_workflow(test_case)
            all_actual_results.append(state)

    metric = RoutingAccuracyMetric(threshold=0.85)
    results = metric.evaluate(all_test_cases, all_actual_results)

    print(metric.get_summary(results))

    return results


async def main():
    """Run all routing evaluation tests."""
    print("\n" + "="*60)
    print("  ROUTING EVALUATION TEST SUITE")
    print("="*60)

    try:
        # Run category-specific tests
        billing_results = await test_billing_routing()
        technical_results = await test_technical_routing()
        account_results = await test_account_routing()
        edge_results = await test_edge_case_routing()

        # Summary
        print("\n" + "="*60)
        print("  ROUTING EVALUATION SUMMARY")
        print("="*60)
        print(f"\nBilling Routing: {billing_results['accuracy']:.1%} ({'✅ PASSED' if billing_results['passed'] else '❌ FAILED'})")
        print(f"Technical Routing: {technical_results['accuracy']:.1%} ({'✅ PASSED' if technical_results['passed'] else '❌ FAILED'})")
        print(f"Account Routing: {account_results['accuracy']:.1%} ({'✅ PASSED' if account_results['passed'] else '❌ FAILED'})")
        print(f"Edge Case Routing: {edge_results['accuracy']:.1%} ({'✅ PASSED' if edge_results['passed'] else '❌ FAILED'})")

        all_passed = all([
            billing_results['passed'],
            technical_results['passed'],
            account_results['passed'],
            edge_results['passed']
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
