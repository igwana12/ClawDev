"""
Main entry point for ClawDev framework.

This script provides a command-line interface to run the ClawDev framework
with different configurations and options.
"""

import argparse
import sys
import os
import json
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from clawdev.chain.chain import ChatChain
from clawdev.adapter.agent_adapter import AgentAdapter
from openclaw_acp import OpenClawAgent


class MockAgentAdapter:
    """Mock adapter for testing without real agent."""

    def send(self, message, role="default"):
        """Mock send method that returns a simple response."""
        print(f"MockAgentAdapter received message: {message[:100]}...")
        if "DemandAnalysis" in str(message) or "product modality" in str(message):
            response = "Based on the task, I recommend we create an Application.\n<INFO> Application"
            print(f"MockAgentAdapter response for demand analysis: {response}")
            return response
        elif "language" in str(message).lower() and (
            "choose" in str(message).lower() or "Choose" in str(message)
        ):
            response = "For this task, Python would be the best choice.\n<INFO> Python"
            print(f"MockAgentAdapter response for language choose: {response}")
            return response
        elif "According to the new user's task and some creative" in str(message):
            response = "For this task, Python would be the best choice.\n<INFO> Python"
            print(
                f"MockAgentAdapter response for language choose (fallback): {response}"
            )
            return response
        elif "Coding" in str(message) or "create a simple implementation" in str(
            message
        ):
            response = "Here's a simple implementation:\n\nmain.py\n```python\nprint('Hello, World!')\n```\n\n"
            print(f"MockAgentAdapter response for coding: {response}")
            return response
        elif "EnvironmentDoc" in str(message):
            response = "requirements.txt\n```\nrequests==2.25.1\nnumpy==1.21.0\n```"
            print(f"MockAgentAdapter response for environment doc: {response}")
            return response
        elif "Manual" in str(message):
            response = "manual.md\n```\n# Simple Calculator App\n\nThis is a simple calculator app.\n```"
            print(f"MockAgentAdapter response for manual: {response}")
            return response
        else:
            response = "Mock response to: " + str(message)[:50] + "..."
            print(f"MockAgentAdapter default response: {response}")
            return response


def main():
    """Main function to run the ClawDev framework."""
    parser = argparse.ArgumentParser(
        description="ClawDev - Multi-agent software development framework"
    )
    parser.add_argument("task", help="The development task to execute")
    parser.add_argument(
        "--project-name",
        "-p",
        default="clawdev_project",
        help="Name of the project directory",
    )
    parser.add_argument(
        "--config", "-c", default="default", help="Configuration to use"
    )
    parser.add_argument(
        "--no-agent",
        action="store_true",
        help="Run without connecting to a real agent (for testing)",
    )

    args = parser.parse_args()

    print("Starting ClawDev framework...")
    print(f"Task: {args.task}")
    print(f"Project name: {args.project_name}")
    print(f"Configuration: {args.config}")

    if args.no_agent:
        # Run with mock adapter for testing
        print("Running in test mode with mock adapter")
        adapter = MockAgentAdapter()
    else:
        # Run with real OpenClaw agents
        print("Connecting to OpenClaw agents...")
        try:
            # Map roles to agent names
            agent_configs = {
                "Chief Executive Officer": "chief_executive_officer",
                "Chief Product Officer": "chief_product_officer",
                "Chief Technology Officer": "chief_technology_officer",
                "Programmer": "programmer",
                "Code Reviewer": "code_reviewer",
                "Software Test Engineer": "software_test_engineer",
                "Chief Creative Officer": "chief_creative_officer",
                "Counselor": "counselor",
                "Chief Human Resource Officer": "chief_human_resource_officer",
            }
            adapter = AgentAdapter(agent_configs)
        except Exception as e:
            print(f"Error connecting to OpenClaw agents: {e}")
            print("Falling back to mock adapter for testing")
            adapter = MockAgentAdapter()

    # Create a ChatChain with the adapter
    chain = ChatChain(adapter, config_name=args.config)

    # Run the development chain
    try:
        chain.run(args.task, args.project_name)
        print(
            f"Development process completed! Project created in projects/{args.project_name}"
        )
    except Exception as e:
        print(f"Error during development process: {e}")
        return 1
    finally:
        # Clean up if we're using real agents
        if not args.no_agent and isinstance(adapter, AgentAdapter):
            try:
                adapter.reset()
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
