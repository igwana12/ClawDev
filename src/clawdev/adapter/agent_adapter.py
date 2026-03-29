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

Agent adapter for ClawDev framework.

Provides a unified interface for communicating with AI agents through OpenClaw ACP.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
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

    def _create_agent(self, role: str) -> None:
        """
        Create and start an agent for the specified role.
        Thread-safe agent creation.
        """
        agent_name = self.agent_configs.get(role, "default")
        if agent_name not in self.agents:
            logger.debug(
                "[AgentAdapter] Creating agent: %s (role: %s)", agent_name, role
            )
            session_context = self._session_contexts.get(role)
            agent = OpenClawAgent(
                agent=agent_name,
                session_context=session_context,
            )
            self.agents[agent_name] = agent

    def pre_init_agents(self, max_workers: int = 8) -> None:
        """
        Pre-initialize all agents in parallel.

        Args:
            max_workers: Maximum number of parallel initializations
        """
        roles = list(self.agent_configs.keys())
        logger.info("[AgentAdapter] Pre-initializing %d agents...", len(roles))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._create_agent, role): role for role in roles
            }
            for future in as_completed(futures):
                role = futures[future]
                try:
                    future.result()
                    logger.debug("[AgentAdapter] Agent ready: %s", role)
                except Exception as e:
                    logger.error(
                        "[AgentAdapter] Failed to initialize agent %s: %s", role, e
                    )

        logger.info("[AgentAdapter] All agents pre-initialized")

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
        response = agent.step(message, timeout=3600)
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
