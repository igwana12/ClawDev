"""
Code Review Phase for ClawDev framework.

Reviews and improves code quality through automated feedback.
"""

from typing import Dict, Any
from ..phases.base import Phase
from ..env.env import ChatEnv


class CodeReviewCommentPhase(Phase):
    """Phase for generating code review comments."""

    def __init__(self, phase_config: Dict[str, Any]):
        """
        Initialize code review comment phase.

        Args:
            phase_config: Configuration for this phase
        """
        super().__init__(phase_config)

    def execute(self, env: ChatEnv, agent_adapter) -> ChatEnv:
        """
        Execute code review comment phase.

        Args:
            env: Current development environment
            agent_adapter: Adapter for communicating with AI agents

        Returns:
            Updated environment with review comments
        """
        # Render prompt for this phase
        prompt = self.render_prompt(env)

        # Send prompt to agent and get response
        response = agent_adapter.send(prompt)

        # Store review comments in environment
        env.review_comments = response

        return env


class CodeReviewModificationPhase(Phase):
    """Phase for modifying code based on review comments."""

    def __init__(self, phase_config: Dict[str, Any]):
        """
        Initialize code review modification phase.

        Args:
            phase_config: Configuration for this phase
        """
        super().__init__(phase_config)

    def execute(self, env: ChatEnv, agent_adapter) -> ChatEnv:
        """
        Execute code review modification phase.

        Args:
            env: Current development environment
            agent_adapter: Adapter for communicating with AI agents

        Returns:
            Updated environment with modified code
        """
        # Render prompt for this phase
        prompt = self.render_prompt(env)

        # Send prompt to agent and get response
        response = agent_adapter.send(prompt)

        # Parse modified code from response and update environment
        # This would involve extracting code blocks from the response
        # For now, we'll just store the raw response
        env.codes = {"raw_response": response}

        return env
