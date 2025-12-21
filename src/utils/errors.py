"""
Custom exception hierarchy for AgentLand.
"""


class AgentLandError(Exception):
    """Base exception for all AgentLand errors."""

    pass


class LLMError(AgentLandError):
    """Errors related to LLM API calls."""

    pass


class LLMRateLimitError(LLMError):
    """LLM rate limit exceeded."""

    pass


class LLMTimeoutError(LLMError):
    """LLM request timed out."""

    pass


class ToolError(AgentLandError):
    """Errors related to tool execution."""

    pass


class ToolNotFoundError(ToolError):
    """Requested tool not found in registry."""

    pass


class ToolExecutionError(ToolError):
    """Tool execution failed."""

    pass


class RoutingError(AgentLandError):
    """Errors related to agent routing."""

    pass


class StateError(AgentLandError):
    """Errors related to state management."""

    pass


class ValidationError(AgentLandError):
    """Errors related to input validation."""

    pass
