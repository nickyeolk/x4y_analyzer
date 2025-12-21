"""
Tavily search tool for AI-optimized web search.

Provides access to Tavily's search API for gathering information about brands and markets.
"""

from typing import Dict, Any, List, Optional
import httpx

from config.settings import settings
from src.tools.base import BaseTool, ToolInput, ToolOutput
from src.observability.decorators import trace_tool
from src.observability.logger import get_logger

logger = get_logger(__name__)


class TavilySearchTool(BaseTool):
    """
    Tavily AI-optimized search tool.

    Provides high-quality search results optimized for LLM consumption.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily tool.

        Args:
            api_key: Tavily API key (defaults to settings)
        """
        super().__init__(
            name="tavily_search",
            description="Search the web using Tavily AI-optimized search for high-quality, LLM-ready results about brands, markets, and business information."
        )
        self.api_key = api_key or settings.tavily_api_key
        self.base_url = "https://api.tavily.com"
        self.client = httpx.AsyncClient(timeout=30.0)

        if not self.api_key:
            logger.warning("tavily_api_key_not_set",
                          message="Tavily API key not configured, tool will fail")

    async def _execute(self, input: ToolInput) -> Dict[str, Any]:
        """
        Execute Tavily search.

        Args:
            input: Tool input with parameters:
                - query: Search query
                - max_results: Maximum results to return (default: 5)
                - search_depth: "basic" or "advanced" (default: "basic")
                - include_domains: List of domains to include
                - exclude_domains: List of domains to exclude

        Returns:
            Dict with search results
        """
        query = input.parameters.get("query")
        if not query:
            raise ValueError("Query parameter is required")

        max_results = input.parameters.get("max_results", 5)
        search_depth = input.parameters.get("search_depth", "basic")
        include_domains = input.parameters.get("include_domains", [])
        exclude_domains = input.parameters.get("exclude_domains", [])

        logger.info(
            "tavily_search_started",
            query=query,
            max_results=max_results,
            search_depth=search_depth,
        )

        # Call Tavily API
        response = await self._search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
        )

        results = response.get("results", [])

        # Format results for LLM consumption
        formatted_results = []
        for idx, result in enumerate(results, 1):
            formatted_results.append({
                "rank": idx,
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
            })

        # Extract answer if available (Tavily sometimes provides direct answers)
        answer = response.get("answer", None)

        logger.info(
            "tavily_search_completed",
            query=query,
            results_count=len(results),
            has_answer=answer is not None,
        )

        return {
            "query": query,
            "results": formatted_results,
            "answer": answer,
            "results_count": len(results),
            "metadata": {
                "search_depth": search_depth,
                "max_results": max_results,
            }
        }

    async def _search(
        self,
        query: str,
        max_results: int,
        search_depth: str,
        include_domains: List[str],
        exclude_domains: List[str],
    ) -> Dict[str, Any]:
        """
        Make request to Tavily API.

        Args:
            query: Search query
            max_results: Max results
            search_depth: Search depth
            include_domains: Domains to include
            exclude_domains: Domains to exclude

        Returns:
            API response
        """
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": True,  # Request direct answer when possible
        }

        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains

        response = await self.client.post(
            f"{self.base_url}/search",
            json=payload,
        )

        if response.status_code != 200:
            error_text = response.text
            raise Exception(f"Tavily API error: {response.status_code} - {error_text}")

        return response.json()

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


def get_tavily_tool() -> TavilySearchTool:
    """
    Get configured Tavily tool instance.

    Returns:
        TavilySearchTool instance
    """
    return TavilySearchTool()
