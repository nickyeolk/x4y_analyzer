"""
Prometheus metrics registry for agent monitoring.
"""

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from typing import Optional

# Create a custom registry for our metrics
registry = CollectorRegistry()

# Agent metrics
agent_invocation_count = Counter(
    "agent_invocation_count",
    "Number of agent invocations",
    ["agent", "status"],
    registry=registry,
)

agent_decision_latency = Histogram(
    "agent_decision_latency_seconds",
    "Time taken for agent to make a decision",
    ["agent"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
    registry=registry,
)

agent_routing_confidence = Gauge(
    "agent_routing_confidence",
    "Confidence score for agent routing decision",
    ["agent"],
    registry=registry,
)

agent_error_count = Counter(
    "agent_error_count",
    "Number of agent errors",
    ["agent", "error_type"],
    registry=registry,
)

# Tool metrics
tool_call_count = Counter(
    "tool_call_count",
    "Number of tool calls",
    ["tool", "status"],
    registry=registry,
)

tool_call_duration = Histogram(
    "tool_call_duration_seconds",
    "Time taken for tool execution",
    ["tool"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0],
    registry=registry,
)

tool_error_count = Counter(
    "tool_error_count",
    "Number of tool errors",
    ["tool", "error_type"],
    registry=registry,
)

# LLM metrics
llm_tokens_used = Counter(
    "llm_tokens_used",
    "Number of tokens used",
    ["model", "type"],
    registry=registry,
)

llm_api_cost = Counter(
    "llm_api_cost_dollars",
    "Estimated API cost in dollars",
    ["agent"],
    registry=registry,
)

# Business metrics
tickets_processed_total = Counter(
    "tickets_processed_total",
    "Total tickets processed",
    ["category", "urgency"],
    registry=registry,
)

ticket_resolution_time = Histogram(
    "ticket_resolution_time_seconds",
    "Time to resolve tickets",
    ["category"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0],
    registry=registry,
)

escalation_rate = Gauge(
    "escalation_rate",
    "Rate of ticket escalations",
    ["from_agent"],
    registry=registry,
)


def record_agent_invocation(agent: str, success: bool) -> None:
    """Record an agent invocation."""
    status = "success" if success else "failure"
    agent_invocation_count.labels(agent=agent, status=status).inc()


def record_agent_error(agent: str, error_type: str) -> None:
    """Record an agent error."""
    agent_error_count.labels(agent=agent, error_type=error_type).inc()


def record_tool_call(tool: str, success: bool, duration: float) -> None:
    """Record a tool call."""
    status = "success" if success else "failure"
    tool_call_count.labels(tool=tool, status=status).inc()
    tool_call_duration.labels(tool=tool).observe(duration)


def record_tool_error(tool: str, error_type: str) -> None:
    """Record a tool error."""
    tool_error_count.labels(tool=tool, error_type=error_type).inc()


def record_llm_usage(model: str, prompt_tokens: int, completion_tokens: int, agent: Optional[str] = None) -> None:
    """Record LLM token usage and estimate cost."""
    llm_tokens_used.labels(model=model, type="prompt").inc(prompt_tokens)
    llm_tokens_used.labels(model=model, type="completion").inc(completion_tokens)

    # Rough cost estimation (adjust based on actual pricing)
    # Claude Sonnet 4.5: ~$3/MTok input, ~$15/MTok output
    cost = (prompt_tokens / 1_000_000 * 3.0) + (completion_tokens / 1_000_000 * 15.0)

    if agent:
        llm_api_cost.labels(agent=agent).inc(cost)


def record_ticket_processed(category: str, urgency: str, duration: float) -> None:
    """Record a processed ticket."""
    tickets_processed_total.labels(category=category, urgency=urgency).inc()
    ticket_resolution_time.labels(category=category).observe(duration)
