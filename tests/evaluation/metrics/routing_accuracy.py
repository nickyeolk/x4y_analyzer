"""
Routing Accuracy Metric.

Evaluates whether the triage agent routes tickets to the correct specialist agent.
"""

from typing import Dict, Any, List, Optional


class RoutingAccuracyMetric:
    """
    Custom metric for evaluating routing accuracy.

    Compares the predicted agent assignment against the expected agent.
    Calculates accuracy, precision, recall for each agent category.
    """

    def __init__(self, threshold: float = 0.9):
        """
        Initialize metric.

        Args:
            threshold: Minimum accuracy threshold for passing (default: 0.9 = 90%)
        """
        self.threshold = threshold
        self.name = "Routing Accuracy"
        self.results: List[Dict[str, Any]] = []

    def evaluate(
        self,
        test_cases: List[Dict[str, Any]],
        actual_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate routing accuracy across multiple test cases.

        Args:
            test_cases: List of test cases with expected_routing
            actual_results: List of actual state results from workflow

        Returns:
            Evaluation results with accuracy, precision, recall, per-agent metrics
        """
        self.results = []
        correct = 0
        total = len(test_cases)

        # Per-agent tracking
        agent_stats: Dict[str, Dict[str, int]] = {}

        for test_case, actual in zip(test_cases, actual_results):
            expected_agent = test_case["expected_routing"]["assigned_agent"]
            actual_agent = actual.get("routing", {}).get("assigned_agent", "unknown")

            is_correct = expected_agent == actual_agent

            if is_correct:
                correct += 1

            # Track per-agent stats
            if expected_agent not in agent_stats:
                agent_stats[expected_agent] = {
                    "true_positive": 0,
                    "false_positive": 0,
                    "false_negative": 0,
                }

            if actual_agent not in agent_stats:
                agent_stats[actual_agent] = {
                    "true_positive": 0,
                    "false_positive": 0,
                    "false_negative": 0,
                }

            if is_correct:
                agent_stats[expected_agent]["true_positive"] += 1
            else:
                agent_stats[expected_agent]["false_negative"] += 1
                agent_stats[actual_agent]["false_positive"] += 1

            self.results.append({
                "test_id": test_case.get("test_id", "unknown"),
                "expected": expected_agent,
                "actual": actual_agent,
                "correct": is_correct,
                "confidence": actual.get("routing", {}).get("confidence_score", 0.0),
            })

        # Calculate overall metrics
        accuracy = correct / total if total > 0 else 0.0

        # Calculate per-agent precision and recall
        agent_metrics = {}
        for agent, stats in agent_stats.items():
            tp = stats["true_positive"]
            fp = stats["false_positive"]
            fn = stats["false_negative"]

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            agent_metrics[agent] = {
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "true_positive": tp,
                "false_positive": fp,
                "false_negative": fn,
            }

        return {
            "metric_name": self.name,
            "accuracy": accuracy,
            "correct": correct,
            "total": total,
            "threshold": self.threshold,
            "passed": accuracy >= self.threshold,
            "agent_metrics": agent_metrics,
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
            f"\nOverall Accuracy: {results['accuracy']:.1%} ({results['correct']}/{results['total']})",
            f"Threshold: {results['threshold']:.1%}",
            f"Status: {'✅ PASSED' if results['passed'] else '❌ FAILED'}",
            f"\nPer-Agent Metrics:",
        ]

        for agent, metrics in results["agent_metrics"].items():
            summary.append(f"\n  {agent}:")
            summary.append(f"    Precision: {metrics['precision']:.1%}")
            summary.append(f"    Recall: {metrics['recall']:.1%}")
            summary.append(f"    F1 Score: {metrics['f1_score']:.3f}")
            summary.append(f"    TP: {metrics['true_positive']}, FP: {metrics['false_positive']}, FN: {metrics['false_negative']}")

        # Show failures
        failures = [r for r in results["details"] if not r["correct"]]
        if failures:
            summary.append(f"\n\nRouting Failures ({len(failures)}):")
            for failure in failures[:10]:  # Show first 10
                summary.append(f"  - {failure['test_id']}: Expected {failure['expected']}, got {failure['actual']} (conf: {failure['confidence']:.2f})")

        summary.append(f"\n{'='*60}\n")

        return "\n".join(summary)
