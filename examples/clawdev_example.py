"""
Example usage of ClawDev package.

Demonstrates how to use the ClawDev framework to automate software development.
"""

import os
import sys

# Add src to path so we can import clawdev
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from openclaw_acp import OpenClawAgent
from clawdev import ChatChain, AgentAdapter


def main():
    """Main function to run the ClawDev example."""
    # Create an OpenClaw agent
    agent = OpenClawAgent(agent="programmer-a")

    # Create an adapter for the agent
    adapter = AgentAdapter(agent)

    # Create a ChatChain with the adapter
    chain = ChatChain(adapter, config_name="default")

    # Define a task
    task = "Create a simple Python script that calculates the Fibonacci sequence up to n numbers and prints the result."

    # Run the development chain
    print("Starting ClawDev development process...")
    chain.run(task, project_name="fibonacci_calculator")
    print("Development process completed!")

    # Clean up
    agent.stop()


if __name__ == "__main__":
    main()
