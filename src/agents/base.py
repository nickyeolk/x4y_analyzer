"""
Base agent class with observability hooks.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.observability.logger import get_logger
from src.observability.decorators import trace_agent


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    All agents should inherit from this class and implement the execute method.
    Provides built-in observability through logging and tracing.
    """

    def __init__(self, name: str):
        """
        Initialize base agent.

        Args:
            name: Agent name for logging and tracing
        """
        self.name = name
        self.logger = get_logger(f"agent.{name}")

    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent logic.

        Args:
            state: Current agent state

        Returns:
            Updated state after agent execution

        This method must be implemented by subclasses.
        """
        pass

    def log_decision(
        self,
        decision: str,
        reasoning: Optional[str] = None,
        confidence: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """
        Log an agent decision with context.

        Args:
            decision: The decision made
            reasoning: Optional reasoning for the decision
            confidence: Optional confidence score (0-1)
            **kwargs: Additional context
        """
        self.logger.info(
            "agent_decision",
            agent=self.name,
            decision=decision,
            reasoning=reasoning,
            confidence=confidence,
            **kwargs,
        )

    def log_error(self, error: str, **kwargs: Any) -> None:
        """
        Log an agent error with context.

        Args:
            error: Error message
            **kwargs: Additional context
        """
        self.logger.error(
            "agent_error",
            agent=self.name,
            error=error,
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
