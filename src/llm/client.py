"""
LLM client wrapper with observability and retry logic.

Note: This is a mock implementation since the Anthropic SDK requires
compilation in Termux. For production, replace with real Anthropic client.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from config.settings import settings
from src.llm.retry import retry_on_llm_error
from src.llm.token_counter import estimate_tokens, TokenUsageTracker
from src.observability.logger import get_logger
from src.observability.tracer import trace_span, add_span_attributes
from src.observability.metrics import record_llm_usage
from src.utils.errors import LLMError

logger = get_logger(__name__)


class LLMResponse:
    """LLM response wrapper."""

    def __init__(
        self,
        content: str,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
        stop_reason: str = "end_turn",
    ):
        self.content = content
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = prompt_tokens + completion_tokens
        self.model = model
        self.stop_reason = stop_reason

    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "usage": {
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "total_tokens": self.total_tokens,
            },
            "model": self.model,
            "stop_reason": self.stop_reason,
        }


class MockAnthropicClient:
    """
    Mock Anthropic client for development/testing.

    This simulates the Anthropic API with realistic responses.
    In production, replace with real anthropic.Anthropic() client.
    """

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        logger.info("mock_llm_initialized", model=model)

    async def generate(
        self,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> LLMResponse:
        """
        Generate a response (mocked).

        Args:
            system: System prompt
            messages: Conversation messages
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLM response
        """
        # Simulate API call delay
        await asyncio.sleep(0.1)

        # Get last user message
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break

        # Generate mock response based on content
        mock_response = self._generate_mock_response(user_message, system)

        # Estimate tokens
        prompt_text = system + " " + " ".join([m["content"] for m in messages])
        prompt_tokens = estimate_tokens(prompt_text)
        completion_tokens = estimate_tokens(mock_response)

        logger.info(
            "mock_llm_generated",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        return LLMResponse(
            content=mock_response,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model=self.model,
        )

    def _generate_mock_response(self, user_message: str, system: str) -> str:
        """Generate a mock response based on context."""
        user_lower = user_message.lower()

        # Triage agent responses
        if "triage" in system.lower():
            if any(word in user_lower for word in ["charge", "billing", "refund", "payment"]):
                return "ROUTE: billing_agent | URGENCY: medium | CONFIDENCE: 0.92 | REASONING: Customer mentions billing-related terms"
            elif any(word in user_lower for word in ["bug", "error", "crash", "not working"]):
                return "ROUTE: technical_agent | URGENCY: high | CONFIDENCE: 0.88 | REASONING: Technical issue reported"
            elif any(word in user_lower for word in ["password", "account", "login", "profile"]):
                return "ROUTE: account_agent | URGENCY: medium | CONFIDENCE: 0.85 | REASONING: Account management issue"
            else:
                return "ROUTE: escalation_agent | URGENCY: low | CONFIDENCE: 0.60 | REASONING: Unclear category"

        # Billing agent responses
        elif "billing" in system.lower():
            return self._generate_billing_response(user_message)

        # Technical agent responses
        elif "technical" in system.lower():
            return self._generate_technical_response(user_message)

        # Account agent responses
        elif "account" in system.lower():
            return self._generate_account_response(user_message)

        # Default response
        return "Thank you for contacting support. I'll help you with your request right away."

    def _generate_billing_response(self, user_message: str) -> str:
        """Generate context-aware billing response."""
        import re
        from datetime import datetime, timedelta

        # Parse payment history from context
        payment_pattern = r'- (\d{4}-\d{2}-\d{2}): \$(\d+\.\d{2}) \((\w+)\) - ([^\n]+)'
        payments = re.findall(payment_pattern, user_message)

        if payments:
            response_parts = ["I've reviewed your payment history and found the following charges:\n"]
            for date, amount, status, description in payments:
                response_parts.append(f"- {date}: ${amount} ({status}) - {description}")

            # Analyze for duplicate charges
            amounts = [float(amt) for _, amt, _, _ in payments]
            dates_str = [date for date, _, _, _ in payments]

            # Check for actual duplicates (same day or within a few days)
            is_duplicate = False
            if len(dates_str) >= 2:
                try:
                    date1 = datetime.strptime(dates_str[0], '%Y-%m-%d')
                    date2 = datetime.strptime(dates_str[1], '%Y-%m-%d')
                    days_apart = abs((date2 - date1).days)

                    # If same amount and within 7 days, likely a duplicate
                    if amounts[0] == amounts[1] and days_apart <= 7:
                        is_duplicate = True
                except ValueError:
                    pass

            if is_duplicate:
                response_parts.append(f"\n**ISSUE DETECTED**: I found duplicate charges of ${amounts[0]:.2f} on {dates_str[0]} and {dates_str[1]}, which are only {days_apart} days apart. This appears to be an error.")
                response_parts.append(f"\n**ACTION: PROCESS_REFUND** - I'm processing a refund of ${amounts[0]:.2f} for the duplicate charge. You should see the refund in 3-5 business days.")
            elif len(amounts) >= 2 and amounts[0] == amounts[1]:
                # Same amount but dates far apart (normal monthly billing)
                response_parts.append(f"\nI notice you have two charges of ${amounts[0]:.2f}. Looking at the dates ({dates_str[0]} and {dates_str[1]}), these appear to be your regular monthly subscription charges for consecutive months, which is **normal billing behavior**.")
                response_parts.append("\nNo refund is needed. However, if you'd like to cancel your subscription to avoid future charges, I can help with that.")
            else:
                response_parts.append("\nYour payment history shows regular billing activity. All charges appear to be legitimate. If you have specific concerns about any charge, please let me know.")

            return "\n".join(response_parts)
        else:
            return "I understand you're experiencing a billing issue. Let me check your payment history and help resolve this for you. I'll investigate and determine if a refund is warranted."

    def _generate_technical_response(self, user_message: str) -> str:
        """Generate context-aware technical response."""
        # Extract knowledge base articles if present
        import re
        kb_pattern = r'Article ID: (KB-\d+)[^\n]*\n\s*Title: ([^\n]+)'
        articles = re.findall(kb_pattern, user_message)

        if articles:
            response = "I've found relevant troubleshooting information for your issue:\n\n"
            for article_id, title in articles[:2]:  # Use top 2 articles
                response += f"Based on {article_id} ({title}), here are the steps to resolve this:\n"
                response += "1. Clear your browser cache and cookies\n"
                response += "2. Try accessing the service in an incognito window\n"
                response += "3. Check if your firewall is blocking the connection\n\n"
            response += "If these steps don't resolve the issue, I can escalate this to our engineering team for further investigation."
            return response
        else:
            return "I've identified the technical issue you're experiencing. Let me walk you through the troubleshooting steps to resolve this problem."

    def _generate_account_response(self, user_message: str) -> str:
        """Generate context-aware account management response."""
        import re

        user_lower = user_message.lower()

        # Parse account information from context
        name_match = re.search(r'Name: ([^\n]+)', user_message)
        email_match = re.search(r'Email: ([^\n]+)', user_message)
        tier_match = re.search(r'Tier: ([^\n]+)', user_message)
        status_match = re.search(r'Status: ([^\n]+)', user_message)

        customer_name = name_match.group(1) if name_match else "the customer"

        # Password reset scenario
        if "password" in user_lower and "reset" in user_lower:
            return f"I've verified your account information for {customer_name}. I'm sending a secure password reset link to your registered email address. Please check your inbox and follow the instructions to reset your password. The link will expire in 24 hours for security purposes."

        # Account access issues
        elif "access" in user_lower or "login" in user_lower or "sign in" in user_lower:
            if status_match and status_match.group(1).lower() == "active":
                return f"I've checked your account status - your account is active and in good standing. If you're having trouble logging in, I've sent a verification link to your email. Please also check that you're using the correct email address and that your browser cookies are enabled."
            else:
                return f"I've reviewed your account status. There may be an issue with your account access. I'm sending you detailed instructions via email to help restore access. If the issue persists, we may need to escalate this to our security team."

        # Profile/account information updates
        elif "update" in user_lower or "change" in user_lower or "profile" in user_lower:
            return f"I can help you update your account information. I've sent you a secure link to your email where you can modify your profile settings. For security reasons, some changes (like email address) may require additional verification."

        # General inquiry
        elif "question" in user_lower or "inquiry" in user_lower:
            tier_info = f" As a {tier_match.group(1)} customer, " if tier_match else " "
            return f"Thank you for reaching out!{tier_info}I'm here to help with any questions about your account or our service offerings. Could you provide more details about what you'd like to know? I can assist with account settings, subscription details, billing information, or general service questions."

        # Default account response
        else:
            return f"I've reviewed your account for {customer_name}. I'm here to assist with your account-related request. I've sent a confirmation email with next steps. If you need immediate assistance, please let me know the specific details of what you'd like to update or change."


class LLMClient:
    """
    LLM client with observability and retry logic.

    Wraps the Anthropic API (or mock) with automatic tracing,
    logging, metrics, and retry on transient failures.
    """

    def __init__(self):
        self.model = settings.llm_model
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature
        self.timeout = settings.llm_timeout_seconds

        # Initialize tracker
        self.usage_tracker = TokenUsageTracker()

        # Initialize client (mock or real)
        if settings.use_mock_llm:
            self.client = MockAnthropicClient(
                api_key=settings.anthropic_api_key,
                model=self.model,
            )
            logger.info("llm_client_initialized", mode="mock", model=self.model)
        else:
            # In production with real Anthropic SDK:
            # from anthropic import Anthropic
            # self.client = Anthropic(api_key=settings.anthropic_api_key)
            # For now, use mock
            self.client = MockAnthropicClient(
                api_key=settings.anthropic_api_key,
                model=self.model,
            )
            logger.warning(
                "llm_client_using_mock",
                reason="Anthropic SDK not available",
                model=self.model,
            )

    @retry_on_llm_error
    async def generate(
        self,
        system: str,
        user_message: str,
        agent_name: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            system: System prompt
            user_message: User message
            agent_name: Optional agent name for metrics
            **kwargs: Additional arguments

        Returns:
            LLM response

        Raises:
            LLMError: On API errors
        """
        with trace_span(
            "llm.generate",
            {"llm.model": self.model, "agent": agent_name or "unknown"},
        ):
            try:
                logger.info(
                    "llm_request_started",
                    model=self.model,
                    agent=agent_name,
                    system_length=len(system),
                    message_length=len(user_message),
                )

                # Build messages
                messages = [{"role": "user", "content": user_message}]

                # Call LLM
                response = await self.client.generate(
                    system=system,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )

                # Track usage
                usage = self.usage_tracker.track(
                    response.prompt_tokens,
                    response.completion_tokens,
                    self.model,
                )

                # Record metrics
                record_llm_usage(
                    model=self.model,
                    prompt_tokens=response.prompt_tokens,
                    completion_tokens=response.completion_tokens,
                    agent=agent_name,
                )

                # Add to span
                add_span_attributes(
                    llm_response_length=len(response.content),
                    llm_prompt_tokens=response.prompt_tokens,
                    llm_completion_tokens=response.completion_tokens,
                    llm_cost=usage["cost"],
                )

                logger.info(
                    "llm_request_completed",
                    model=self.model,
                    agent=agent_name,
                    prompt_tokens=response.prompt_tokens,
                    completion_tokens=response.completion_tokens,
                    cost=usage["cost"],
                )

                return response

            except Exception as e:
                logger.error(
                    "llm_request_failed",
                    model=self.model,
                    agent=agent_name,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise LLMError(f"LLM generation failed: {str(e)}") from e

    def get_usage_summary(self) -> Dict[str, float]:
        """
        Get summary of token usage and costs.

        Returns:
            Usage summary dictionary
        """
        return self.usage_tracker.get_summary()

    def reset_usage(self) -> None:
        """Reset usage tracking."""
        self.usage_tracker.reset()


# Global client instance
_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get the global LLM client instance.

    Returns:
        LLM client
    """
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
