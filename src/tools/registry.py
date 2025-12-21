"""
Tool registry for managing and discovering available tools.
"""

from typing import Dict, List, Optional, Type
from src.tools.base import BaseTool
from src.tools.database import DatabaseTool, DatabaseQueryInput
from src.tools.payment import PaymentTool, RefundInput, PaymentQueryInput
from src.tools.email import EmailTool, EmailInput
from src.tools.knowledge_base import KnowledgeBaseTool, KnowledgeBaseInput
from src.observability.logger import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    """
    Registry for managing available tools.

    Provides tool discovery, registration, and execution.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._initialize_default_tools()

    def _initialize_default_tools(self) -> None:
        """Initialize default tools."""
        default_tools = [
            DatabaseTool(),
            PaymentTool(),
            EmailTool(),
            KnowledgeBaseTool(),
        ]

        for tool in default_tools:
            self.register(tool)

        logger.info("tool_registry_initialized", tool_count=len(self._tools))

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool.

        Args:
            tool: Tool instance to register
        """
        if tool.name in self._tools:
            logger.warning("tool_already_registered", tool_name=tool.name)
        else:
            self._tools[tool.name] = tool
            logger.info("tool_registered", tool_name=tool.name)

    def unregister(self, tool_name: str) -> bool:
        """
        Unregister a tool.

        Args:
            tool_name: Name of tool to unregister

        Returns:
            True if tool was unregistered, False if not found
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.info("tool_unregistered", tool_name=tool_name)
            return True
        return False

    def get(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, str]]:
        """
        Get list of all registered tools.

        Returns:
            List of tool metadata dictionaries
        """
        return [tool.to_dict() for tool in self._tools.values()]

    def get_tools_for_agent(self, agent_type: str) -> List[BaseTool]:
        """
        Get tools appropriate for a specific agent type.

        Args:
            agent_type: Type of agent (billing, technical, account, etc.)

        Returns:
            List of tools
        """
        # Map agent types to relevant tools
        agent_tool_mapping = {
            "billing": ["database_query", "payment_gateway", "email_sender"],
            "technical": ["database_query", "knowledge_base", "email_sender"],
            "account": ["database_query", "email_sender"],
            "escalation": ["database_query", "payment_gateway", "knowledge_base", "email_sender"],
            "triage": ["database_query"],  # Triage mainly needs customer context
        }

        tool_names = agent_tool_mapping.get(agent_type, [])
        tools = [self._tools[name] for name in tool_names if name in self._tools]

        return tools

    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self._tools)

    def __contains__(self, tool_name: str) -> bool:
        """Check if tool is registered."""
        return tool_name in self._tools


# Global registry instance
_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """
    Get the global tool registry instance.

    Returns:
        Tool registry
    """
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
