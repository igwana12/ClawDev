"""
Testing Phase for ClawDev framework.

Tests and fixes code based on error reports.
"""

from typing import Dict, Any
from ..phases.base import Phase
from ..env.env import ChatEnv


class TestErrorSummaryPhase(Phase):
    """Phase for summarizing test errors."""

    def __init__(self, phase_config: Dict[str, Any]):
        """
        Initialize test error summary phase.

        Args:
            phase_config: Configuration for this phase
        """
        super().__init__(phase_config)

    def execute(self, env: ChatEnv, agent_adapter) -> ChatEnv:
        """
        Execute test error summary phase.

        Args:
            env: Current development environment
            agent_adapter: Adapter for communicating with AI agents

        Returns:
            Updated environment with error summary
        """
        # Render prompt for this phase
        prompt = self.render_prompt(env)

        # Send prompt to agent and get response
        response = agent_adapter.send(prompt, role=self.assistant_role)

        # Store error summary in environment
        env.error_summary = response

        return env


class TestModificationPhase(Phase):
    """Phase for modifying code based on test errors."""

    def __init__(self, phase_config: Dict[str, Any]):
        """
        Initialize test modification phase.

        Args:
            phase_config: Configuration for this phase
        """
        super().__init__(phase_config)

    def execute(self, env: ChatEnv, agent_adapter) -> ChatEnv:
        """
        Execute test modification phase.

        Args:
            env: Current development environment
            agent_adapter: Adapter for communicating with AI agents

        Returns:
            Updated environment with fixed code
        """
        # Render prompt for this phase
        prompt = self.render_prompt(env)

        # Send prompt to agent and get response
        response = agent_adapter.send(prompt, role=self.assistant_role)

        # Parse fixed code from response and update environment
        # This would involve extracting code blocks from the response
        # For now, we'll just store the raw response
        env.codes = {"raw_response": response}

        return env
