"""
Base tool class with observability and tracing.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from src.observability.logger import get_logger
from src.observability.decorators import trace_tool


class ToolInput(BaseModel):
    """Base model for tool inputs."""

    pass


class ToolOutput(BaseModel):
    """Base model for tool outputs."""

    success: bool = Field(..., description="Whether the tool execution succeeded")
    result: Any = Field(..., description="Tool execution result")
    error: Optional[str] = Field(None, description="Error message if failed")


class BaseTool(ABC):
    """
    Abstract base class for all tools.

    All tools should inherit from this class and implement the _execute method.
    Provides built-in observability through automatic tracing and logging.
    """

    def __init__(self, name: str, description: str):
        """
        Initialize base tool.

        Args:
            name: Tool name for logging and tracing
            description: Tool description for agent understanding
        """
        self.name = name
        self.description = description
        self.logger = get_logger(f"tool.{name}")

    @abstractmethod
    async def _execute(self, input_data: ToolInput) -> Any:
        """
        Execute the tool logic.

        Args:
            input_data: Tool input data

        Returns:
            Tool execution result

        This method must be implemented by subclasses.
        """
        pass

    @trace_tool("base_tool")
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        """
        Execute the tool with observability.

        This method wraps _execute with automatic tracing and error handling.

        Args:
            input_data: Tool input data

        Returns:
            Tool output with success status
        """
        try:
            self.logger.info(
                "tool_executing",
                tool=self.name,
                input=str(input_data.dict())[:200],  # Truncate for logging
            )

            result = await self._execute(input_data)

            self.logger.info(
                "tool_success",
                tool=self.name,
            )

            return ToolOutput(success=True, result=result, error=None)

        except Exception as e:
            self.logger.error(
                "tool_failed",
                tool=self.name,
                error=str(e),
                error_type=type(e).__name__,
            )

            return ToolOutput(success=False, result=None, error=str(e))

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tool to dictionary representation.

        Returns:
            Tool metadata as dict
        """
        return {
            "name": self.name,
            "description": self.description,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
