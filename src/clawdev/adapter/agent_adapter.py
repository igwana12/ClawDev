"""
Agent adapter for ClawDev framework.

Provides a unified interface for communicating with AI agents through OpenClaw ACP.
"""

import logging
from typing import Dict
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
        self._session_contexts: Dict[str, str] = {}

    def set_session_context(self, role: str, context: str) -> None:
        """
        Set session context for an agent role.

        Args:
            role: Role name
            context: Context message to send after agent initialization
        """
        self._session_contexts[role] = context

    def get_agent(self, role: str) -> OpenClawAgent:
        """
        Get or create an agent for the specified role.

        Args:
            role: Role name to determine which agent to use

        Returns:
            OpenClawAgent instance
        """
        agent_name = self.agent_configs.get(role, "default")
        if agent_name not in self.agents:
            logger.debug("[AgentAdapter] Creating new agent: %s", agent_name)
            session_context = self._session_contexts.get(role)
            self.agents[agent_name] = OpenClawAgent(
                agent=agent_name,
                session_context=session_context,
            )
        return self.agents[agent_name]

    def send(self, message: str, role: str = "default") -> str:
        """
        Send message to agent and get response.

        Args:
            message: Message to send to agent
            role: Role name to determine which agent to use

        Returns:
            Agent's response
        """
        logger.debug(
            "[AgentAdapter] send() role=%s message=%r",
            role,
            message[:100] if message else "",
        )

        agent = self.get_agent(role)
        logger.debug("[AgentAdapter] Calling agent.step()")
        response = agent.step(message)
        logger.debug("[AgentAdapter] agent.step() returned %d chars", len(response))

        return response

    def reset(self) -> None:
        """Reset all agents."""
        for agent in self.agents.values():
            try:
                agent.stop()
            except Exception:
                pass
        self.agents.clear()
