"""
Test script for ClawDev framework.

This script tests the basic functionality of the ClawDev framework
without actually connecting to an OpenClaw agent.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from clawdev.env.env import ChatEnv
from clawdev.phases.demand_analysis import DemandAnalysisPhase
from clawdev.phases.language_choose import LanguageChoosePhase
from clawdev.phases.coding import CodingPhase


class MockAgentAdapter:
    """Mock adapter for testing without real agent."""

    def send(self, message, role="default"):
        """Mock send method that returns a simple response."""
        if "DemandAnalysis" in str(message) or "product modality" in str(message):
            return "Based on the task, I recommend we create an Application.\n<INFO> Application"
        elif "language" in str(message) and (
            "choose" in str(message).lower() or "Choose" in str(message)
        ):
            return "For this task, Python would be the best choice.\n<INFO> Python"
        elif "Coding" in str(message) or "create a simple implementation" in str(
            message
        ):
            return "Here's a simple implementation:\n\nmain.py\n```python\nprint('Hello, World!')\n```\n\n"
        else:
            return "Mock response to: " + str(message)[:50] + "..."


def test_basic_functionality():
    """Test basic functionality of ClawDev framework."""
    print("Testing ClawDev framework...")

    # Create a mock adapter
    adapter = MockAgentAdapter()

    # Create environment
    env = ChatEnv("/tmp/test_project")
    env.task_prompt = "Create a simple calculator app"
    print(f"Initial environment: task_prompt={env.task_prompt}")

    # Test demand analysis phase
    print("Testing demand analysis phase...")
    demand_phase = DemandAnalysisPhase(
        {
            "phase": "DemandAnalysis",
            "assistant_role_name": "Chief Product Officer",
            "user_role_name": "Chief Executive Officer",
            "phase_prompt": [
                'Task: "{task}".',
                "What type of application should we create?",
                "Note that we must ONLY discuss the product modality and do not discuss anything else!",
            ],
        }
    )

    print("Executing demand analysis phase...")
    env = demand_phase.execute(env, adapter)
    print(f"Demand analysis result: modality = {env.modality}")

    # Test language choose phase
    print("Testing language choose phase...")
    language_phase = LanguageChoosePhase(
        {
            "phase": "LanguageChoose",
            "assistant_role_name": "Chief Technology Officer",
            "user_role_name": "Chief Executive Officer",
            "phase_prompt": [
                'Task: "{task}".',
                'Modality: "{modality}".',
                "We need to choose a programming language.",
                "Please respond with <INFO> followed by the language name.",
            ],
        }
    )

    print("Executing language choose phase...")
    env = language_phase.execute(env, adapter)
    print(f"Language choose result: language = {env.language}")

    # Test coding phase
    print("Testing coding phase...")
    coding_phase = CodingPhase(
        {
            "phase": "Coding",
            "assistant_role_name": "Programmer",
            "user_role_name": "Chief Technology Officer",
            "phase_prompt": [
                'Task: "{task}".',
                'Modality: "{modality}".',
                'Programming Language: "{language}"',
                "Please create a simple implementation.",
            ],
        }
    )

    print("Executing coding phase...")
    env = coding_phase.execute(env, adapter)
    print("Coding phase completed")
    print(f"Generated codes: {list(env.codes.keys())}")

    print("Test completed successfully!")


if __name__ == "__main__":
    test_basic_functionality()
