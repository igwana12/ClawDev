"""
Manual Generation Phase for ClawDev framework.

Generates user manuals and documentation.
"""

from typing import Dict, Any
from ..phases.base import Phase
from ..env.env import ChatEnv


class ManualPhase(Phase):
    """Phase for generating user manuals."""

    def __init__(self, phase_config: Dict[str, Any]):
        """
        Initialize manual generation phase.

        Args:
            phase_config: Configuration for this phase
        """
        super().__init__(phase_config)

    def execute(self, env: ChatEnv, agent_adapter) -> ChatEnv:
        """
        Execute manual generation phase.

        Args:
            env: Current development environment
            agent_adapter: Adapter for communicating with AI agents

        Returns:
            Updated environment with user manual
        """
        # Render prompt for this phase
        prompt = self.render_prompt(env)

        # Send prompt to agent and get response
        response = agent_adapter.send(prompt)

        # Store manual in environment
        env.manuals = response

        return env
