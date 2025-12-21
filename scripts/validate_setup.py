#!/usr/bin/env python3
"""
Setup validation script.

Validates that all components are properly configured and functional.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def validate_imports():
    """Validate all critical imports work."""
    print("🔍 Validating imports...")

    try:
        # Config
        from config.settings import Settings
        from config.logging_config import configure_logging
        from config.observability import configure_observability

        # API
        from src.api.main import app

        # Agents
        from src.agents.triage_agent import TriageAgent
        from src.agents.billing_agent import BillingAgent
        from src.agents.technical_agent import TechnicalAgent
        from src.agents.account_agent import AccountAgent
        from src.agents.escalation_agent import EscalationAgent

        # Orchestration
        from src.orchestration.graph import process_ticket

        # Tools
        from src.tools.database import DatabaseTool
        from src.tools.payment import PaymentTool
        from src.tools.email import EmailTool
        from src.tools.knowledge_base import KnowledgeBaseTool

        # LLM
        from src.llm.client import get_llm_client

        # Observability
        from src.observability.logger import get_logger
        from src.observability.metrics import record_ticket_processed

        # Evaluation
        from tests.evaluation.metrics.routing_accuracy import RoutingAccuracyMetric
        from tests.evaluation.metrics.tool_usage_metric import ToolUsageMetric

        print("  ✅ All imports successful")
        return True

    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


def validate_configuration():
    """Validate configuration is properly set up."""
    print("\n🔍 Validating configuration...")

    try:
        from config.settings import Settings

        settings = Settings()
        print(f"  Configuration loaded successfully")
        print(f"  ✅ Configuration valid")
        return True

    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False


def validate_agents():
    """Validate agents can be instantiated."""
    print("\n🔍 Validating agents...")

    try:
        from src.agents.triage_agent import TriageAgent
        from src.agents.billing_agent import BillingAgent
        from src.agents.technical_agent import TechnicalAgent
        from src.agents.account_agent import AccountAgent
        from src.agents.escalation_agent import EscalationAgent

        agents = {
            "Triage": TriageAgent(),
            "Billing": BillingAgent(),
            "Technical": TechnicalAgent(),
            "Account": AccountAgent(),
            "Escalation": EscalationAgent(),
        }

        for name, agent in agents.items():
            print(f"  ✅ {name} agent instantiated")

        print("  ✅ All agents valid")
        return True

    except Exception as e:
        print(f"  ❌ Agent error: {e}")
        return False


def validate_tools():
    """Validate tools can be instantiated."""
    print("\n🔍 Validating tools...")

    try:
        from src.tools.registry import get_tool_registry

        registry = get_tool_registry()
        tools = registry._tools  # Access internal dict

        print(f"  Found {len(tools)} tools:")
        for name in tools.keys():
            print(f"    ✅ {name}")

        print("  ✅ All tools valid")
        return True

    except Exception as e:
        print(f"  ❌ Tool error: {e}")
        return False


def validate_datasets():
    """Validate evaluation datasets exist."""
    print("\n🔍 Validating evaluation datasets...")

    datasets = [
        "tests/evaluation/datasets/billing_cases.json",
        "tests/evaluation/datasets/technical_cases.json",
        "tests/evaluation/datasets/account_cases.json",
        "tests/evaluation/datasets/edge_cases.json",
    ]

    all_exist = True
    for dataset in datasets:
        path = Path(__file__).parent.parent / dataset
        if path.exists():
            print(f"  ✅ {dataset}")
        else:
            print(f"  ❌ {dataset} not found")
            all_exist = False

    if all_exist:
        print("  ✅ All datasets present")
    return all_exist


def validate_documentation():
    """Validate documentation files exist."""
    print("\n🔍 Validating documentation...")

    docs = [
        "README.md",
        "docs/architecture.md",
        "docs/observability_guide.md",
        "docs/evaluation_guide.md",
    ]

    all_exist = True
    for doc in docs:
        path = Path(__file__).parent.parent / doc
        if path.exists():
            print(f"  ✅ {doc}")
        else:
            print(f"  ❌ {doc} not found")
            all_exist = False

    if all_exist:
        print("  ✅ All documentation present")
    return all_exist


def main():
    """Run all validations."""
    print("="*60)
    print("  AGENTLAND SETUP VALIDATION")
    print("="*60)

    results = {
        "imports": validate_imports(),
        "configuration": validate_configuration(),
        "agents": validate_agents(),
        "tools": validate_tools(),
        "datasets": validate_datasets(),
        "documentation": validate_documentation(),
    }

    print("\n" + "="*60)
    print("  VALIDATION SUMMARY")
    print("="*60)

    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name.capitalize()}: {status}")

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("  ✅ ALL VALIDATIONS PASSED")
        print("  System is ready for use!")
    else:
        print("  ❌ SOME VALIDATIONS FAILED")
        print("  Please fix errors above")
    print("="*60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
