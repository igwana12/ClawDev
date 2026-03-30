"""
SimplePhase for ClawDev framework.

Single dialog phase execution between two agents.
"""

import logging
from .base import Phase
from ..env.env import ChatEnv

logger = logging.getLogger(__name__)


class SimplePhase(Phase):
    """Single dialog phase execution."""

    def execute(self, env, agent_adapter) -> ChatEnv:
        """
        Execute this phase as a dialog between two agents.

        The user_role agent initiates the conversation, and assistant_role responds.
        If assistant_role is empty, this becomes a notification phase (single-agent mode).

        Args:
            env: Current development environment
            agent_adapter: Adapter for communicating with AI agents

        Returns:
            Updated environment after dialog execution
        """
        logger.debug("[SimplePhase] execute() phase=%s", self.phase_name)

        if self.notification_mode or not self.assistant_role:
            return self._execute_notification(env, agent_adapter)

        return self._execute_dialog(env, agent_adapter)

    def _execute_notification(self, env, agent_adapter) -> ChatEnv:
        """Execute as a notification phase (single-agent mode)."""
        logger.debug("[SimplePhase] notification mode for phase=%s", self.phase_name)
        self.dialog_turn = 0

        initiator_prompt = self.render_initiator_prompt(env)
        response = agent_adapter.send(initiator_prompt, role=self.user_role)

        self.update_env(env, response)
        return env

    def _execute_dialog(self, env, agent_adapter) -> ChatEnv:
        """Execute as a dialog between two agents."""
        self.dialog_turn = 0

        initiator_prompt = self.render_initiator_prompt(env)
        logger.debug(
            "[SimplePhase] initiator_prompt() returned %d chars", len(initiator_prompt)
        )

        response = agent_adapter.send(initiator_prompt, role=self.user_role)
        logger.debug(
            "[SimplePhase] initiator_response returned %d chars", len(response)
        )

        if self._should_end_dialog(response):
            self.update_env(env, response)
            return env

        self.dialog_turn += 1
        other_role = self.user_role
        dialog_prompt = self.render_dialog_prompt(other_role, response)
        response = agent_adapter.send(dialog_prompt, role=self.assistant_role)
        logger.debug(
            "[SimplePhase] responder_response returned %d chars", len(response)
        )

        if self._should_end_dialog(response):
            self.update_env(env, response)
            return env

        self.dialog_turn += 1

        while self.dialog_turn < self.max_dialog_turns:
            other_role = self.assistant_role
            dialog_prompt = self.render_dialog_prompt(other_role, response)
            response = agent_adapter.send(dialog_prompt, role=self.user_role)
            logger.debug(
                "[SimplePhase] continuation response returned %d chars", len(response)
            )

            if self._should_end_dialog(response):
                break

            self.dialog_turn += 1
            other_role = self.user_role
            dialog_prompt = self.render_dialog_prompt(other_role, response)
            response = agent_adapter.send(dialog_prompt, role=self.assistant_role)
            logger.debug(
                "[SimplePhase] continuation response returned %d chars", len(response)
            )

            if self._should_end_dialog(response):
                break

            self.dialog_turn += 1

        self.update_env(env, response)
        return env
