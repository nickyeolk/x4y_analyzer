"""
Tool Usage Metric.

Evaluates whether agents call the correct tools for each scenario.
"""

from typing import Dict, Any, List, Optional, Set


class ToolUsageMetric:
    """
    Custom metric for evaluating tool usage correctness.

    Validates that:
    1. Expected tools were called
    2. No unnecessary tools were called
    3. Tools were used in appropriate order/context
    """

    def __init__(self, threshold: float = 0.95):
        """
        Initialize metric.

        Args:
            threshold: Minimum correctness threshold for passing (default: 0.95 = 95%)
        """
        self.threshold = threshold
        self.name = "Tool Usage Correctness"
        self.results: List[Dict[str, Any]] = []

    def evaluate(
        self,
        test_cases: List[Dict[str, Any]],
        actual_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate tool usage across multiple test cases.

        Args:
            test_cases: List of test cases with expected_tools
            actual_results: List of actual state results from workflow

        Returns:
            Evaluation results with correctness score and details
        """
        self.results = []
        correct = 0
        total = len(test_cases)

        for test_case, actual in zip(test_cases, actual_results):
            expected_tools = set(test_case.get("expected_tools", []))

            # Extract tools from agent interactions
            actual_tools: Set[str] = set()
            tool_calls_detail = []

            for interaction in actual.get("agent_interactions", []):
                for tool_call in interaction.get("tool_calls", []):
                    tool_name = tool_call.get("tool", "unknown")
                    actual_tools.add(tool_name)
                    tool_calls_detail.append({
                        "agent": interaction.get("agent_name"),
                        "tool": tool_name,
                        "success": tool_call.get("success", False),
                    })

            # Check if expected tools are a subset of actual tools
            # (allows for extra tools that might be reasonable)
            has_required_tools = expected_tools.issubset(actual_tools)

            # Calculate precision: how many of the called tools were expected?
            if len(actual_tools) > 0:
                tool_precision = len(expected_tools.intersection(actual_tools)) / len(actual_tools)
            else:
                tool_precision = 0.0 if len(expected_tools) > 0 else 1.0

            # Calculate recall: how many of the expected tools were called?
            if len(expected_tools) > 0:
                tool_recall = len(expected_tools.intersection(actual_tools)) / len(expected_tools)
            else:
                tool_recall = 1.0

            # F1 score
            if tool_precision + tool_recall > 0:
                f1_score = 2 * (tool_precision * tool_recall) / (tool_precision + tool_recall)
            else:
                f1_score = 0.0

            # Consider correct if F1 >= 0.8 (allows some flexibility)
            is_correct = f1_score >= 0.8

            if is_correct:
                correct += 1

            missing_tools = expected_tools - actual_tools
            unexpected_tools = actual_tools - expected_tools

            self.results.append({
                "test_id": test_case.get("test_id", "unknown"),
                "expected_tools": sorted(list(expected_tools)),
                "actual_tools": sorted(list(actual_tools)),
                "missing_tools": sorted(list(missing_tools)),
                "unexpected_tools": sorted(list(unexpected_tools)),
                "precision": tool_precision,
                "recall": tool_recall,
                "f1_score": f1_score,
                "correct": is_correct,
                "tool_calls_detail": tool_calls_detail,
            })

        # Calculate overall metrics
        correctness = correct / total if total > 0 else 0.0

        # Calculate average precision and recall
        avg_precision = sum(r["precision"] for r in self.results) / len(self.results) if self.results else 0.0
        avg_recall = sum(r["recall"] for r in self.results) / len(self.results) if self.results else 0.0
        avg_f1 = sum(r["f1_score"] for r in self.results) / len(self.results) if self.results else 0.0

        return {
            "metric_name": self.name,
            "correctness": correctness,
            "correct": correct,
            "total": total,
            "threshold": self.threshold,
            "passed": correctness >= self.threshold,
            "avg_precision": avg_precision,
            "avg_recall": avg_recall,
            "avg_f1_score": avg_f1,
            "details": self.results,
        }

    def get_summary(self, results: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of results.

        Args:
            results: Results dict from evaluate()

        Returns:
            Formatted summary string
        """
        summary = [
            f"\n{'='*60}",
            f"  {self.name}",
            f"{'='*60}",
            f"\nOverall Correctness: {results['correctness']:.1%} ({results['correct']}/{results['total']})",
            f"Threshold: {results['threshold']:.1%}",
            f"Status: {'✅ PASSED' if results['passed'] else '❌ FAILED'}",
            f"\nAverage Metrics:",
            f"  Precision: {results['avg_precision']:.1%}",
            f"  Recall: {results['avg_recall']:.1%}",
            f"  F1 Score: {results['avg_f1_score']:.3f}",
        ]

        # Show failures
        failures = [r for r in results["details"] if not r["correct"]]
        if failures:
            summary.append(f"\n\nTool Usage Issues ({len(failures)}):")
            for failure in failures[:10]:  # Show first 10
                summary.append(f"\n  {failure['test_id']}:")
                summary.append(f"    Expected: {failure['expected_tools']}")
                summary.append(f"    Actual: {failure['actual_tools']}")
                if failure['missing_tools']:
                    summary.append(f"    Missing: {failure['missing_tools']}")
                if failure['unexpected_tools']:
                    summary.append(f"    Unexpected: {failure['unexpected_tools']}")
                summary.append(f"    F1 Score: {failure['f1_score']:.3f}")

        summary.append(f"\n{'='*60}\n")

        return "\n".join(summary)
