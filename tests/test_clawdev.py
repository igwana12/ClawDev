"""
Test script for ClawDev framework.

This script tests the basic functionality of the ClawDev framework
without actually connecting to an OpenClaw agent.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from clawdev.env.env import ChatEnv
from clawdev.phases.simple_phase import SimplePhase


class MockAgentAdapter:
    """Mock adapter for testing without real agent."""

    def send(self, message, role="default"):
        """Mock send method that returns a simple response."""
        if "DemandAnalysis" in str(message) or "product modality" in str(message):
            return "Based on the task, I recommend we create an Application.\n<result>Application</result>"
        elif "language" in str(message) and (
            "choose" in str(message).lower() or "Choose" in str(message)
        ):
            return "For this task, Python would be the best choice.\n<result>Python</result>"
        elif "Coding" in str(message) or "create a simple implementation" in str(
            message
        ):
            return "Here's a simple implementation:\n\nmain.py\n```python\nprint('Hello, World!')\n```\n\n"
        else:
            return "Mock response to: " + str(message)[:50] + "..."


def test_basic_functionality():
    """Test basic functionality of ClawDev framework."""
    print("Testing ClawDev framework...")

    adapter = MockAgentAdapter()

    env = ChatEnv("/tmp/test_project")
    env.task_prompt = "Create a simple calculator app"
    print(f"Initial environment: task_prompt={env.task_prompt}")

    print("Testing demand analysis phase...")
    demand_phase = SimplePhase(
        {
            "phase": "DemandAnalysis",
            "assistant_role_name": "Chief Product Officer",
            "user_role_name": "Chief Executive Officer",
            "initiator_prompt": [
                "You are {user_role}.",
                "What type of application should we create?",
                "Note that we must ONLY discuss the product modality and do not discuss anything else!",
            ],
            "dialog_prompt": "{the_other_role} said: {content}",
        }
    )

    print("Executing demand analysis phase...")
    env = demand_phase.execute(env, adapter)
    print(f"Demand analysis result: modality = {env.modality}")

    print("Testing language choose phase...")
    language_phase = SimplePhase(
        {
            "phase": "LanguageChoose",
            "assistant_role_name": "Chief Technology Officer",
            "user_role_name": "Chief Executive Officer",
            "initiator_prompt": [
                "You are {user_role}.",
                'Modality: "{modality}".',
                "We need to choose a programming language.",
                "Please respond with <result> followed by the language name.",
            ],
            "dialog_prompt": "{the_other_role} said: {content}",
        }
    )

    print("Executing language choose phase...")
    env = language_phase.execute(env, adapter)
    print(f"Language choose result: language = {env.language}")

    print("Testing coding phase...")
    coding_phase = SimplePhase(
        {
            "phase": "Coding",
            "assistant_role_name": "Programmer",
            "user_role_name": "Chief Technology Officer",
            "initiator_prompt": [
                "You are {user_role}.",
                'Modality: "{modality}".',
                'Programming Language: "{language}"',
                "Please create a simple implementation.",
            ],
            "dialog_prompt": "{the_other_role} said: {content}",
        }
    )

    print("Executing coding phase...")
    env = coding_phase.execute(env, adapter)
    print("Coding phase completed")
    print(f"Generated codes: {list(env.codes.keys())}")

    print("Test completed successfully!")


if __name__ == "__main__":
    test_basic_functionality()
