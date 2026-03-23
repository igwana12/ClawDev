"""
Agent adapter for ClawDev framework.

Provides a unified interface for communicating with AI agents through OpenClaw ACP.
"""

import logging
from typing import Dict, Any, Optional
from openclaw_acp import OpenClawAgent

logger = logging.getLogger(__name__)


class AgentAdapter:
    """Adapter that wraps OpenClawAgent for use in ClawDev framework."""

    def __init__(self, agent_configs: Dict[str, str]):
        """
        Initialize adapter with OpenClaw agent configurations.

        Args:
            agent_configs: Dictionary mapping role names to agent names
                           e.g., {"Chief Executive Officer": "chief_executive_officer"}
        """
        self.agent_configs = agent_configs
        self.agents: Dict[str, OpenClawAgent] = {}

    def send(self, message: str, role: str = "default") -> str:
        """
        Send message to agent and get response.

        Args:
            message: Message to send to agent
            role: Role name to determine which agent to use

        Returns:
            Agent's response
        """
        agent_name = self.agent_configs.get(role, "chief_executive_officer")
        logger.debug(
            "[AgentAdapter] send() role=%s agent=%s message=%r",
            role,
            agent_name,
            message[:100],
        )

        if agent_name not in self.agents:
            logger.debug("[AgentAdapter] Creating new agent: %s", agent_name)
            self.agents[agent_name] = OpenClawAgent(agent=agent_name)

        logger.debug("[AgentAdapter] Calling agent.step()")
        response = self.agents[agent_name].step(message)
        logger.debug("[AgentAdapter] agent.step() returned %d chars", len(response))
        return response

    def reset(self) -> None:
        """Reset all agents."""
        for agent in self.agents.values():
            try:
                agent.stop()
            except:
                pass
        self.agents.clear()
