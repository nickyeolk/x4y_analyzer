"""
Skeptic Agent Accuracy Metrics.

This module provides metrics for evaluating the quality and accuracy
of the Skeptic agent's critical evaluation.
"""

from typing import Dict, Any, List, Set
from dataclasses import dataclass


@dataclass
class SkepticAccuracyScore:
    """Skeptic evaluation accuracy score."""

    overall_score: float  # 0-1
    concern_relevance_score: float  # 0-1
    concern_coverage_score: float  # 0-1
    approval_accuracy_score: float  # 0-1

    # Metrics
    num_concerns: int
    num_fatal_flaws: int
    num_suggestions: int
    approved: bool
    confidence: float

    # Expected vs actual
    expected_concerns_found: int
    total_expected_concerns: int
    unexpected_concerns: int

    details: Dict[str, Any]


def calculate_concern_overlap(
    actual_concerns: List[str],
    expected_concerns: List[str]
) -> tuple[int, int]:
    """
    Calculate overlap between actual and expected concerns.

    Args:
        actual_concerns: Concerns identified by Skeptic
        expected_concerns: Expected concerns from test case

    Returns:
        Tuple of (matches, total_expected)
    """
    if not expected_concerns:
        return 0, 0

    # Normalize concerns to lowercase for comparison
    actual_normalized = [c.lower() for c in actual_concerns]
    expected_normalized = [c.lower() for c in expected_concerns]

    matches = 0
    for expected in expected_normalized:
        # Check if any actual concern contains the expected concern keywords
        keywords = expected.split()
        for actual in actual_normalized:
            # If at least half the keywords match, consider it a match
            matching_keywords = sum(1 for kw in keywords if kw in actual)
            if matching_keywords >= len(keywords) / 2:
                matches += 1
                break

    return matches, len(expected_concerns)


def evaluate_concern_relevance(
    critique: Dict[str, Any],
    test_case: Dict[str, Any]
) -> float:
    """
    Evaluate relevance of concerns identified by Skeptic.

    Checks if concerns match expected concerns from test case.

    Args:
        critique: Skeptic critique
        test_case: Test case with expected concerns

    Returns:
        Relevance score from 0-1
    """
    actual_concerns = critique.get('concerns', [])
    expected_concerns = test_case.get('expected_concerns', [])

    if not expected_concerns:
        # If no expected concerns, just check that concerns exist
        return 1.0 if len(actual_concerns) > 0 else 0.5

    matches, total = calculate_concern_overlap(actual_concerns, expected_concerns)

    if total == 0:
        return 0.5

    # Score based on percentage of expected concerns found
    return matches / total


def evaluate_concern_coverage(critique: Dict[str, Any]) -> float:
    """
    Evaluate coverage of concerns.

    Checks if Skeptic identified a reasonable number of concerns
    across different dimensions.

    Args:
        critique: Skeptic critique

    Returns:
        Coverage score from 0-1
    """
    concerns = critique.get('concerns', [])
    fatal_flaws = critique.get('fatal_flaws', [])
    suggestions = critique.get('suggestions', [])

    coverage_score = 0.0
    max_score = 4.0

    # Has multiple concerns (0-1)
    if len(concerns) >= 3:
        coverage_score += 1.0
    elif len(concerns) >= 2:
        coverage_score += 0.7
    elif len(concerns) >= 1:
        coverage_score += 0.4

    # Has suggestions (0-1)
    if len(suggestions) >= 3:
        coverage_score += 1.0
    elif len(suggestions) >= 2:
        coverage_score += 0.7
    elif len(suggestions) >= 1:
        coverage_score += 0.4

    # Appropriate number of fatal flaws (0-1)
    # Too many fatal flaws indicates over-pessimism
    if len(fatal_flaws) == 0:
        coverage_score += 0.7  # Most ideas shouldn't have fatal flaws
    elif len(fatal_flaws) <= 2:
        coverage_score += 1.0
    else:
        coverage_score += 0.3  # Too many fatal flaws

    # Has reasoning (0-1)
    reasoning = critique.get('reasoning', '')
    if len(reasoning) > 100:
        coverage_score += 1.0
    elif len(reasoning) > 50:
        coverage_score += 0.7
    elif len(reasoning) > 0:
        coverage_score += 0.4

    return coverage_score / max_score


def evaluate_approval_accuracy(
    critique: Dict[str, Any],
    test_case: Dict[str, Any],
    viability_score: float
) -> float:
    """
    Evaluate accuracy of approval decision.

    Checks if approval aligns with expected viability.

    Args:
        critique: Skeptic critique
        test_case: Test case with expected viability range
        viability_score: Final viability score from strategist

    Returns:
        Approval accuracy score from 0-1
    """
    approved = critique.get('approved', False)
    expected_range = test_case.get('expected_viability_range', [0, 10])

    # Expected viability midpoint
    expected_viability = (expected_range[0] + expected_range[1]) / 2

    # Check if approval decision makes sense
    # High viability (>6.5) should generally be approved
    # Low viability (<4.5) should generally not be approved
    # Medium viability (4.5-6.5) can go either way

    if expected_viability >= 6.5:
        # Should be approved
        return 1.0 if approved else 0.3
    elif expected_viability <= 4.5:
        # Should not be approved
        return 1.0 if not approved else 0.3
    else:
        # Medium viability - either decision is reasonable
        # Give partial credit based on confidence
        confidence = critique.get('confidence', 0.5)
        if approved and viability_score >= 5.0:
            return 0.8 + (confidence * 0.2)
        elif not approved and viability_score < 5.0:
            return 0.8 + (confidence * 0.2)
        else:
            return 0.6


def evaluate_skeptic_accuracy(
    result: Dict[str, Any],
    test_case: Dict[str, Any]
) -> SkepticAccuracyScore:
    """
    Evaluate overall Skeptic accuracy.

    Args:
        result: Complete analysis result with skeptic_critique
        test_case: Test case with expected values

    Returns:
        SkepticAccuracyScore with detailed metrics
    """
    critique = result.get('skeptic_critique', {})
    viability_score = result.get('strategist_plan', {}).get('viability_score', 0)

    # Calculate component scores
    concern_relevance = evaluate_concern_relevance(critique, test_case)
    concern_coverage = evaluate_concern_coverage(critique)
    approval_accuracy = evaluate_approval_accuracy(critique, test_case, viability_score)

    # Calculate overall score (weighted average)
    overall = (
        concern_relevance * 0.40 +
        concern_coverage * 0.35 +
        approval_accuracy * 0.25
    )

    # Metrics
    concerns = critique.get('concerns', [])
    fatal_flaws = critique.get('fatal_flaws', [])
    suggestions = critique.get('suggestions', [])
    approved = critique.get('approved', False)
    confidence = critique.get('confidence', 0.0)

    # Expected vs actual
    expected_concerns = test_case.get('expected_concerns', [])
    matches, total = calculate_concern_overlap(concerns, expected_concerns)
    unexpected = len(concerns) - matches

    return SkepticAccuracyScore(
        overall_score=overall,
        concern_relevance_score=concern_relevance,
        concern_coverage_score=concern_coverage,
        approval_accuracy_score=approval_accuracy,
        num_concerns=len(concerns),
        num_fatal_flaws=len(fatal_flaws),
        num_suggestions=len(suggestions),
        approved=approved,
        confidence=confidence,
        expected_concerns_found=matches,
        total_expected_concerns=total,
        unexpected_concerns=unexpected,
        details={
            'concerns': concerns,
            'fatal_flaws': fatal_flaws,
            'suggestions': suggestions,
            'reasoning': critique.get('reasoning', ''),
            'expected_concerns': expected_concerns,
            'viability_score': viability_score,
        }
    )
