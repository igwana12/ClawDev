"""
ChatChain for ClawDev framework.

Orchestrates the complete software development process through configured phases.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from ..env.env import ChatEnv

logger = logging.getLogger(__name__)


class ChatChain:
    """Main orchestrator for the software development process."""

    def __init__(self, agent_adapter, config_name: str = "Default"):
        """
        Initialize chain with agent adapter and configuration.

        Args:
            agent_adapter: Adapter for communicating with AI agents (can be any object with a send method)
            config_name: Name of configuration to use
        """
        self.agent_adapter = agent_adapter
        self.config_name = config_name
        self.config_path = os.path.join("configs", config_name)

        # Load configuration files
        self.chain_config = self._load_config("ChatChainConfig.json")
        self.phase_config = self._load_config("PhaseConfig.json")

        # Initialize environment
        self.env: Optional[ChatEnv] = None

    def _load_config(self, filename: str) -> Dict[str, Any]:
        """
        Load configuration file.

        Args:
            filename: Name of configuration file

        Returns:
            Configuration dictionary
        """
        config_file = os.path.join(self.config_path, filename)
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def pre_processing(self, task_prompt: str, project_name: str) -> None:
        """
        Perform pre-processing steps before chain execution.

        Args:
            task_prompt: User's task description
            project_name: Name for the project directory
        """
        # Initialize environment
        self.env = ChatEnv(project_name)
        self.env.task_prompt = task_prompt

    def make_recruitment(self) -> None:
        """Register roles in the environment and set up agent contexts."""
        if self.env is None:
            raise RuntimeError("Environment not initialized")

        session_context_template = self.chain_config.get("session_context_template")
        all_roles = list(self.agent_adapter.agent_configs.keys())

        if session_context_template and self.env.task_prompt:
            context_lines = session_context_template
            if isinstance(context_lines, list):
                context_lines = "\n".join(context_lines)
            for role in all_roles:
                colleagues = [r for r in all_roles if r != role]
                colleagues_str = (
                    ", ".join(colleagues[:-1]) + ", and " + colleagues[-1]
                    if len(colleagues) > 1
                    else colleagues[0]
                )
                session_context = context_lines.format(
                    task=self.env.task_prompt,
                    role_name=role,
                    colleagues_list=colleagues_str,
                )
                self.agent_adapter.set_session_context(role, session_context)

        for role in all_roles:
            self.agent_adapter.get_agent(role)

    def execute_chain(self) -> None:
        """Execute all phases in the chain."""
        if self.env is None:
            raise RuntimeError("Environment not initialized")

        # Execute each phase in the chain configuration
        for phase_item in self.chain_config["chain"]:
            self.execute_step(phase_item)

    def execute_step(self, phase_item: Dict[str, Any]) -> None:
        """
        Execute a single phase step.

        Args:
            phase_item: Configuration for the phase to execute
        """
        if self.env is None:
            raise RuntimeError("Environment not initialized")

        phase_type = phase_item["phaseType"]

        if phase_type == "SimplePhase":
            phase_name = phase_item["phase"]
            phase_config = self.phase_config[phase_name]

            print(f"Executing phase: {phase_name}")

            from ..phases.simple_phase import SimplePhase

            phase = SimplePhase(phase_config, phase_name=phase_name)

            self.env = phase.execute(self.env, self.agent_adapter)

        elif phase_type == "ComposedPhase":
            phase_name = phase_item["phase"]

            print(f"Executing composed phase: {phase_name}")

            from ..phases.composed_phase import ComposedPhase

            phase = ComposedPhase(phase_item, config_phase=self.phase_config)

            self.env = phase.execute(self.env, self.agent_adapter)

    def post_processing(self) -> None:
        """Perform post-processing steps after chain execution."""
        pass

    def run(self, task_prompt: str, project_name: str) -> None:
        """
        Run the complete development chain.

        Args:
            task_prompt: User's task description
            project_name: Name for the project directory
        """
        self.pre_processing(task_prompt, project_name)
        self.make_recruitment()
        self.execute_chain()
        self.post_processing()
