"""
Verification script to test all 4 agents are properly implemented.

This script doesn't actually call the LLM/tools (which require API keys),
but verifies that all agents can be imported and instantiated correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def verify_agents():
    """Verify all agents can be imported and instantiated."""

    print("=" * 60)
    print("AGENT VERIFICATION SCRIPT")
    print("=" * 60)
    print()

    agents_status = []

    # Test 1: Import BaseAgent
    print("✓ Importing BaseAgent...")
    try:
        from src.agents.base import BaseAgent
        agents_status.append(("BaseAgent", "✅ Import successful"))
    except Exception as e:
        agents_status.append(("BaseAgent", f"❌ Import failed: {e}"))
        print(f"  ❌ Failed: {e}")
        return False

    # Test 2: Import all 4 agents
    agents_to_test = [
        ("AnalystAgent", "src.agents.analyst", "AnalystAgent"),
        ("ResearcherAgent", "src.agents.researcher", "ResearcherAgent"),
        ("SkepticAgent", "src.agents.skeptic", "SkepticAgent"),
        ("StrategistAgent", "src.agents.strategist", "StrategistAgent"),
    ]

    print("\n" + "=" * 60)
    print("IMPORTING AGENTS")
    print("=" * 60)

    all_passed = True
    agent_classes = {}

    for agent_name, module_path, class_name in agents_to_test:
        print(f"\n{agent_name}:")
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            agent_classes[agent_name] = agent_class
            print(f"  ✅ Import successful")
            print(f"  ✅ Class found: {agent_class.__name__}")
            agents_status.append((agent_name, "✅ Import successful"))
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            agents_status.append((agent_name, f"❌ Import failed: {e}"))
            all_passed = False

    # Test 3: Instantiate agents (without API keys)
    print("\n" + "=" * 60)
    print("INSTANTIATING AGENTS")
    print("=" * 60)

    for agent_name, agent_class in agent_classes.items():
        print(f"\n{agent_name}:")
        try:
            # Note: This will fail if API keys are required, but at least
            # we can verify the class structure
            agent = agent_class()
            print(f"  ✅ Instantiation successful")
            print(f"  ✅ Agent name: {agent.name}")
            print(f"  ✅ Has execute method: {hasattr(agent, 'execute')}")
            agents_status.append((f"{agent_name} instantiation", "✅ Successful"))
        except Exception as e:
            # Expected if API keys not set - that's okay
            if "API key" in str(e) or "not set" in str(e):
                print(f"  ⚠️  Instantiation requires API keys (expected): {e}")
                agents_status.append((f"{agent_name} instantiation", "⚠️  Needs API keys"))
            else:
                print(f"  ❌ Failed: {e}")
                agents_status.append((f"{agent_name} instantiation", f"❌ Failed: {e}"))
                all_passed = False

    # Test 4: Verify prompts
    print("\n" + "=" * 60)
    print("VERIFYING PROMPTS")
    print("=" * 60)

    prompts_to_test = [
        ("Analyst Prompt", "src.agents.prompts.analyst", "ANALYST_SYSTEM_PROMPT"),
        ("Researcher Prompt", "src.agents.prompts.researcher", "RESEARCHER_SYSTEM_PROMPT"),
        ("Skeptic Prompt", "src.agents.prompts.skeptic", "SKEPTIC_SYSTEM_PROMPT"),
        ("Strategist Prompt", "src.agents.prompts.strategist", "STRATEGIST_SYSTEM_PROMPT"),
    ]

    for prompt_name, module_path, prompt_var in prompts_to_test:
        print(f"\n{prompt_name}:")
        try:
            module = __import__(module_path, fromlist=[prompt_var])
            prompt = getattr(module, prompt_var)
            print(f"  ✅ Prompt loaded")
            print(f"  ✅ Length: {len(prompt)} characters")
            print(f"  ✅ Preview: {prompt[:100]}...")
            agents_status.append((prompt_name, "✅ Loaded"))
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            agents_status.append((prompt_name, f"❌ Failed: {e}"))
            all_passed = False

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print()

    for item, status in agents_status:
        print(f"{item:.<50} {status}")

    print()
    if all_passed:
        print("✅ ALL AGENTS VERIFIED SUCCESSFULLY!")
        print()
        print("Next steps:")
        print("1. Set up .env file with API keys (OPENROUTER_API_KEY, TAVILY_API_KEY)")
        print("2. Create RAG knowledge base in data/knowledge_base/")
        print("3. Run: python scripts/build_vector_store.py")
        print("4. Implement LangGraph workflow in src/orchestration/graph.py")
        return True
    else:
        print("❌ VERIFICATION FAILED - See errors above")
        return False


if __name__ == "__main__":
    success = verify_agents()
    sys.exit(0 if success else 1)
