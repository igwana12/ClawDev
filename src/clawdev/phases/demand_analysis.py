"""
Demand Analysis Phase for ClawDev framework.

Determines the software product modality based on user requirements.
"""

from typing import Dict, Any
from ..phases.base import Phase
from ..env.env import ChatEnv


class DemandAnalysisPhase(Phase):
    """Phase for analyzing user requirements and determining product modality."""

    def __init__(self, phase_config: Dict[str, Any]):
        """
        Initialize demand analysis phase.

        Args:
            phase_config: Configuration for this phase
        """
        super().__init__(phase_config)

    def execute(self, env: ChatEnv, agent_adapter) -> ChatEnv:
        """
        Execute demand analysis phase.

        Args:
            env: Current development environment
            agent_adapter: Adapter for communicating with AI agents

        Returns:
            Updated environment with determined modality
        """
        # Render prompt for this phase
        prompt = self.render_prompt(env)
        print(f"DemandAnalysisPhase: Rendered prompt: {prompt[:100]}...")

        # Send prompt to agent and get response
        response = agent_adapter.send(prompt, role=self.assistant_role)
        print(f"DemandAnalysisPhase: Received response: {response[:100]}...")

        # Update environment with agent response
        print("DemandAnalysisPhase: Updating environment...")
        print(f"DemandAnalysisPhase: self.phase_name = {self.phase_name}")
        self.update_env(env, response)
        print(f"DemandAnalysisPhase: Updated environment modality: {env.modality}")

        return env
