"""
Token counting utilities for cost estimation.
"""

from typing import Dict


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for a text string.

    This is a rough approximation. For production, use proper tokenizer.
    Rule of thumb: ~4 characters per token for English text.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    # Simple estimation: 4 characters per token
    return max(1, len(text) // 4)


def calculate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: str = "claude-sonnet-4-5-20250929",
) -> float:
    """
    Calculate estimated API cost in dollars.

    Pricing (as of Dec 2024):
    - Claude Sonnet 4.5: $3/MTok input, $15/MTok output

    Args:
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        model: Model identifier

    Returns:
        Estimated cost in dollars
    """
    # Pricing per million tokens
    pricing = {
        "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
        "claude-sonnet-3-5": {"input": 3.0, "output": 15.0},
        "claude-opus-4": {"input": 15.0, "output": 75.0},
    }

    # Get pricing for model or use default
    model_pricing = pricing.get(model, pricing["claude-sonnet-4-5-20250929"])

    # Calculate cost
    input_cost = (prompt_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * model_pricing["output"]

    return input_cost + output_cost


class TokenUsageTracker:
    """Track token usage and costs across LLM calls."""

    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        self.calls = 0

    def track(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "claude-sonnet-4-5-20250929",
    ) -> Dict[str, float]:
        """
        Track a single LLM call.

        Args:
            prompt_tokens: Prompt tokens used
            completion_tokens: Completion tokens used
            model: Model identifier

        Returns:
            Dictionary with usage stats
        """
        cost = calculate_cost(prompt_tokens, completion_tokens, model)

        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_cost += cost
        self.calls += 1

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost": cost,
        }

    def get_summary(self) -> Dict[str, float]:
        """
        Get summary of all tracked usage.

        Returns:
            Dictionary with total usage stats
        """
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "total_cost": self.total_cost,
            "total_calls": self.calls,
            "avg_tokens_per_call": (
                (self.total_prompt_tokens + self.total_completion_tokens) / self.calls
                if self.calls > 0
                else 0
            ),
        }

    def reset(self) -> None:
        """Reset all tracked usage."""
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        self.calls = 0
