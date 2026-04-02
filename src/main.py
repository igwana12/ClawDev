"""
Copyright 2024 HDAnzz

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Main entry point for ClawDev framework.

This script provides a command-line interface to run the ClawDev framework
with different configurations and options.
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

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


def setup_logging(verbose: bool = False) -> None:
    """Configure logging to console and file."""
    log_level = logging.DEBUG if verbose else logging.INFO

    # Create logs directory
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Log file path: logs/YYYY-MM-DD.log
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

    # Use a named logger to avoid affecting third-party libraries
    clawdev_logger = logging.getLogger("clawdev")
    clawdev_logger.setLevel(logging.DEBUG)

    # Guard against duplicate handlers
    if clawdev_logger.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    clawdev_logger.addHandler(console_handler)

    # File handler - always DEBUG, append mode
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    clawdev_logger.addHandler(file_handler)


logger = logging.getLogger(__name__)


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
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    setup_logging(verbose=args.verbose)

    logger.info("Starting ClawDev framework...")
    logger.info("Task: %s", args.task)
    logger.info("Project name: %s", args.project_name)
    logger.info("Configuration: %s", args.config)

    load_dotenv()

    # Run with real OpenClaw agents
    print("Connecting to OpenClaw agents...")
    adapter = AgentAdapter(DEFAULT_AGENT_CONFIGS)

    # Create a ChatChain with the adapter
    chain = ChatChain(adapter, config_name=args.config)

    # Run the development chain
    try:
        chain.run(args.task, args.project_name)
        logger.info("Development process completed!")
    except Exception as e:
        logger.error("Error during development process: %s", e)
        return 1
    finally:
        try:
            adapter.reset()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
