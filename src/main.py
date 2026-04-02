"""
Main entry point for ClawDev framework.

This script provides a command-line interface to run the ClawDev framework
with different configurations and options.
"""

import argparse
import logging
import sys

from clawdev.chain.chain import ChatChain
from clawdev.adapter.agent_adapter import AgentAdapter

DEFAULT_AGENT_CONFIGS = {
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

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MockAgentAdapter:
    """Mock adapter for testing without real agent."""

    agent_configs = DEFAULT_AGENT_CONFIGS

    def set_session_context(self, role: str, context: str) -> None:
        """Mock method - does nothing."""
        pass

    def send(self, message, role="default"):
        """Mock send method that returns a simple response."""
        print(f"MockAgentAdapter received message: {message[:100]}...")
        if "DemandAnalysis" in str(message) or "product modality" in str(message):
            response = "Based on the task, I recommend we create an Application.\n<result>Application</result>"
            print(f"MockAgentAdapter response for demand analysis: {response}")
            return response
        elif "language" in str(message).lower() and (
            "choose" in str(message).lower() or "Choose" in str(message)
        ):
            response = "For this task, Python would be the best choice.\n<result>Python</result>"
            print(f"MockAgentAdapter response for language choose: {response}")
            return response
        elif "CodingInit" in str(message):
            response = "I've created the repository and added Programmer as a collaborator.\n<result>Done</result>"
            print(f"MockAgentAdapter response for CodingInit: {response}")
            return response
        elif "CodingImprove" in str(message) or "Coding" in str(message):
            response = "I've created the initial code and submitted a PR.\n<result>Done</result>"
            print(f"MockAgentAdapter response for coding: {response}")
            return response
        elif "CodeReviewInit" in str(message):
            response = "I've verified access to the repository and I'm ready to review.\n<result>Done</result>"
            print(f"MockAgentAdapter response for CodeReviewInit: {response}")
            return response
        elif "CodeReviewModification" in str(message):
            response = "The code looks good, all checks passed.\n<result>Done</result>"
            print(f"MockAgentAdapter response for CodeReviewModification: {response}")
            return response
        elif "TestErrorSummary" in str(message):
            response = "All tests passed.\n<result>Done</result>"
            print(f"MockAgentAdapter response for TestErrorSummary: {response}")
            return response
        elif "TestModification" in str(message):
            response = "Tests are now passing.\n<result>Done</result>"
            print(f"MockAgentAdapter response for TestModification: {response}")
            return response
        elif "EnvironmentDoc" in str(message):
            response = "requirements.txt\n```\nrequests==2.25.1\nnumpy==1.21.0\n```\n<result>Done</result>"
            print(f"MockAgentAdapter response for environment doc: {response}")
            return response
        else:
            response = "Mock response.\n<result>Done</result>"
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
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

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
            adapter = AgentAdapter(DEFAULT_AGENT_CONFIGS)
        except Exception as e:
            print(f"Error connecting to OpenClaw agents: {e}")
            print("Falling back to mock adapter for testing")
            adapter = MockAgentAdapter()

    # Create a ChatChain with the adapter
    chain = ChatChain(adapter, config_name=args.config)

    # Run the development chain
    try:
        chain.run(args.task, args.project_name)
        print(f"Development process completed!")
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
