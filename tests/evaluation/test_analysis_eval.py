#!/usr/bin/env python3
"""
Evaluation Test Script for Startup Analyzer.

This script runs the complete analysis workflow on test datasets
and evaluates the quality of the results using custom metrics.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestration.graph import analyze_startup
from tests.evaluation.metrics import (
    evaluate_gtm_quality,
    evaluate_skeptic_accuracy,
)


class EvaluationRunner:
    """Run evaluation tests on startup ideas."""

    def __init__(self, dataset_path: str):
        """
        Initialize evaluation runner.

        Args:
            dataset_path: Path to test dataset JSON file
        """
        self.dataset_path = dataset_path
        self.results = []

    def load_test_cases(self) -> List[Dict[str, Any]]:
        """
        Load test cases from dataset.

        Returns:
            List of test cases
        """
        with open(self.dataset_path, 'r') as f:
            data = json.load(f)
        return data['test_cases']

    async def run_analysis(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run analysis for a single test case.

        Args:
            test_case: Test case dictionary

        Returns:
            Analysis result
        """
        print(f"\n{'='*80}")
        print(f"Running: {test_case['id']}")
        print(f"Idea: {test_case['x_brand']} for {test_case['y_market']}")
        print(f"{'='*80}")

        try:
            result = await analyze_startup(
                analysis_id=f"EVAL-{test_case['id']}",
                correlation_id=f"CID-{test_case['id']}",
                x_brand=test_case['x_brand'],
                y_market=test_case['y_market'],
                description=test_case.get('description'),
            )
            return result
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            return None

    def evaluate_result(
        self,
        result: Dict[str, Any],
        test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate analysis result.

        Args:
            result: Analysis result
            test_case: Original test case

        Returns:
            Evaluation scores
        """
        if not result:
            return {
                'gtm_quality': None,
                'skeptic_accuracy': None,
                'error': 'Analysis failed'
            }

        # Evaluate GTM quality
        gtm_score = evaluate_gtm_quality(result)

        # Evaluate Skeptic accuracy
        skeptic_score = evaluate_skeptic_accuracy(result, test_case)

        # Check viability score range
        viability = result.get('strategist_plan', {}).get('viability_score', 0)
        expected_range = test_case.get('expected_viability_range', [0, 10])
        viability_in_range = expected_range[0] <= viability <= expected_range[1]

        return {
            'gtm_quality': {
                'overall': gtm_score.overall_score,
                'completeness': gtm_score.completeness_score,
                'specificity': gtm_score.specificity_score,
                'actionability': gtm_score.actionability_score,
            },
            'skeptic_accuracy': {
                'overall': skeptic_score.overall_score,
                'concern_relevance': skeptic_score.concern_relevance_score,
                'concern_coverage': skeptic_score.concern_coverage_score,
                'approval_accuracy': skeptic_score.approval_accuracy_score,
                'expected_concerns_found': skeptic_score.expected_concerns_found,
                'total_expected_concerns': skeptic_score.total_expected_concerns,
            },
            'viability_score': viability,
            'expected_viability_range': expected_range,
            'viability_in_range': viability_in_range,
            'loop_count': result.get('loop_count', 0),
            'duration_seconds': result.get('metadata', {}).get('total_duration_seconds', 0),
            'cost_usd': result.get('metadata', {}).get('cost_usd', 0),
        }

    async def run_evaluation(
        self,
        test_cases: List[Dict[str, Any]] = None,
        max_cases: int = None
    ) -> Dict[str, Any]:
        """
        Run evaluation on test cases.

        Args:
            test_cases: Specific test cases to run (or None for all)
            max_cases: Maximum number of cases to run

        Returns:
            Evaluation results summary
        """
        if test_cases is None:
            test_cases = self.load_test_cases()

        if max_cases:
            test_cases = test_cases[:max_cases]

        results = []
        start_time = datetime.now()

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] Processing: {test_case['id']}")

            # Run analysis
            result = await self.run_analysis(test_case)

            # Evaluate result
            evaluation = self.evaluate_result(result, test_case)

            # Store result
            test_result = {
                'test_case_id': test_case['id'],
                'x_brand': test_case['x_brand'],
                'y_market': test_case['y_market'],
                'category': test_case.get('category'),
                'evaluation': evaluation,
                'timestamp': datetime.now().isoformat(),
            }
            results.append(test_result)

            # Print summary
            if evaluation.get('gtm_quality'):
                gtm = evaluation['gtm_quality']
                print(f"  GTM Quality: {gtm['overall']:.2f} "
                      f"(Completeness: {gtm['completeness']:.2f}, "
                      f"Specificity: {gtm['specificity']:.2f})")

            if evaluation.get('skeptic_accuracy'):
                skeptic = evaluation['skeptic_accuracy']
                print(f"  Skeptic Accuracy: {skeptic['overall']:.2f} "
                      f"(Relevance: {skeptic['concern_relevance']:.2f}, "
                      f"Coverage: {skeptic['concern_coverage']:.2f})")

            if evaluation.get('viability_score'):
                print(f"  Viability: {evaluation['viability_score']:.1f}/10 "
                      f"(Expected: {evaluation['expected_viability_range'][0]}-"
                      f"{evaluation['expected_viability_range'][1]}) "
                      f"{'✓' if evaluation['viability_in_range'] else '✗'}")

            print(f"  Duration: {evaluation.get('duration_seconds', 0):.1f}s "
                  f"Cost: ${evaluation.get('cost_usd', 0):.4f}")

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        # Calculate aggregate metrics
        aggregate = self.calculate_aggregate_metrics(results)

        summary = {
            'total_cases': len(results),
            'total_duration_seconds': total_duration,
            'aggregate_metrics': aggregate,
            'results': results,
            'timestamp': end_time.isoformat(),
        }

        return summary

    def calculate_aggregate_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate aggregate metrics across all results.

        Args:
            results: List of test results

        Returns:
            Aggregate metrics
        """
        gtm_scores = []
        skeptic_scores = []
        viability_in_range_count = 0
        total_duration = 0
        total_cost = 0
        loop_counts = []

        for result in results:
            eval_data = result['evaluation']

            if eval_data.get('gtm_quality'):
                gtm_scores.append(eval_data['gtm_quality']['overall'])

            if eval_data.get('skeptic_accuracy'):
                skeptic_scores.append(eval_data['skeptic_accuracy']['overall'])

            if eval_data.get('viability_in_range'):
                viability_in_range_count += 1

            total_duration += eval_data.get('duration_seconds', 0)
            total_cost += eval_data.get('cost_usd', 0)
            loop_counts.append(eval_data.get('loop_count', 0))

        avg_gtm = sum(gtm_scores) / len(gtm_scores) if gtm_scores else 0
        avg_skeptic = sum(skeptic_scores) / len(skeptic_scores) if skeptic_scores else 0
        viability_accuracy = viability_in_range_count / len(results) if results else 0
        avg_duration = total_duration / len(results) if results else 0
        avg_cost = total_cost / len(results) if results else 0
        avg_loops = sum(loop_counts) / len(loop_counts) if loop_counts else 0

        return {
            'average_gtm_quality': avg_gtm,
            'average_skeptic_accuracy': avg_skeptic,
            'viability_accuracy': viability_accuracy,
            'average_duration_seconds': avg_duration,
            'average_cost_usd': avg_cost,
            'average_loop_count': avg_loops,
            'total_cost_usd': total_cost,
        }

    def print_summary(self, summary: Dict[str, Any]):
        """
        Print evaluation summary.

        Args:
            summary: Evaluation summary
        """
        print("\n" + "="*80)
        print("EVALUATION SUMMARY")
        print("="*80)

        metrics = summary['aggregate_metrics']

        print(f"\nTest Cases: {summary['total_cases']}")
        print(f"Total Duration: {summary['total_duration_seconds']:.1f}s "
              f"({summary['total_duration_seconds']/60:.1f}m)")
        print(f"Total Cost: ${metrics['total_cost_usd']:.4f}")

        print(f"\nAverage Metrics:")
        print(f"  GTM Quality:        {metrics['average_gtm_quality']:.2f}/1.0 "
              f"({metrics['average_gtm_quality']*100:.0f}%)")
        print(f"  Skeptic Accuracy:   {metrics['average_skeptic_accuracy']:.2f}/1.0 "
              f"({metrics['average_skeptic_accuracy']*100:.0f}%)")
        print(f"  Viability Accuracy: {metrics['viability_accuracy']:.2f} "
              f"({metrics['viability_accuracy']*100:.0f}% in range)")
        print(f"  Duration per Case:  {metrics['average_duration_seconds']:.1f}s")
        print(f"  Cost per Case:      ${metrics['average_cost_usd']:.4f}")
        print(f"  Average Loops:      {metrics['average_loops']:.2f}")

        # Pass/fail thresholds
        print(f"\nQuality Thresholds:")
        gtm_pass = metrics['average_gtm_quality'] >= 0.70
        skeptic_pass = metrics['average_skeptic_accuracy'] >= 0.60
        viability_pass = metrics['viability_accuracy'] >= 0.70

        print(f"  GTM Quality ≥ 0.70:        {'✓ PASS' if gtm_pass else '✗ FAIL'}")
        print(f"  Skeptic Accuracy ≥ 0.60:   {'✓ PASS' if skeptic_pass else '✗ FAIL'}")
        print(f"  Viability Accuracy ≥ 0.70: {'✓ PASS' if viability_pass else '✗ FAIL'}")

        overall_pass = gtm_pass and skeptic_pass and viability_pass
        print(f"\nOverall: {'✓ PASS' if overall_pass else '✗ FAIL'}")

        print("="*80)

    def save_results(self, summary: Dict[str, Any], output_path: str):
        """
        Save evaluation results to file.

        Args:
            summary: Evaluation summary
            output_path: Output file path
        """
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\n✅ Results saved to: {output_path}")


async def main():
    """Run evaluation tests."""
    # Get dataset path
    script_dir = Path(__file__).parent
    dataset_path = script_dir / "datasets" / "startup_ideas.json"

    if not dataset_path.exists():
        print(f"❌ Dataset not found: {dataset_path}")
        return 1

    # Initialize runner
    runner = EvaluationRunner(str(dataset_path))

    # Run evaluation
    # For quick testing, you can limit to first N cases:
    # summary = await runner.run_evaluation(max_cases=3)

    # For full evaluation:
    print("Starting evaluation...")
    print("Note: This will take several minutes (30-60s per test case)")
    print("\nRunning on full dataset (15 test cases)")

    summary = await runner.run_evaluation()

    # Print summary
    runner.print_summary(summary)

    # Save results
    output_path = script_dir / f"eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    runner.save_results(summary, str(output_path))

    # Return exit code based on pass/fail
    metrics = summary['aggregate_metrics']
    gtm_pass = metrics['average_gtm_quality'] >= 0.70
    skeptic_pass = metrics['average_skeptic_accuracy'] >= 0.60
    viability_pass = metrics['viability_accuracy'] >= 0.70

    return 0 if (gtm_pass and skeptic_pass and viability_pass) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
