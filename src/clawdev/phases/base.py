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

Base phase classes for ClawDev framework.

Defines the abstract interface and common functionality for all development phases.
- Phase: Abstract base class defining the interface
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import Dict, Any
from ..env.env import ChatEnv

logger = logging.getLogger(__name__)


class Phase(ABC):
    """Base class for all development phases."""

    def __init__(self, phase_config: Dict[str, Any], phase_name: str = None):
        """
        Initialize phase with configuration.

        Args:
            phase_config: Configuration dictionary for this phase
            phase_name: Optional phase name (if not in config)
        """
        self.phase_config = phase_config
        self.phase_name = phase_name or phase_config.get(
            "phase", self.__class__.__name__
        )
        self.assistant_role = phase_config.get("assistant_role_name", "")
        self.user_role = phase_config.get("user_role_name", "")
        self.max_dialog_turns = phase_config.get("max_dialog_turns", 5)
        self.notification_mode = phase_config.get("notification_mode", False)

        if self.notification_mode:
            self.max_dialog_turns = 1

        self.dialog_turn = 0
        self.phase_env: Dict[str, Any] = {}

    @abstractmethod
    def execute(self, env: ChatEnv, agent_adapter) -> ChatEnv:
        """
        Execute this phase.

        Args:
            env: Current development environment
            agent_adapter: Adapter for communicating with AI agents

        Returns:
            Updated environment after phase execution
        """
        pass

    def render_prompt(self, env: ChatEnv) -> str:
        """Render prompt for backward compatibility. Returns initiator prompt."""
        return self.render_initiator_prompt(env)

    def render_initiator_prompt(self, env: ChatEnv) -> str:
        """Render the instruction for initiating the dialog."""
        initiator_prompt = self.phase_config.get("initiator_prompt", [])
        prompt_template = "\n".join(initiator_prompt)

        context = self.phase_config.get("context", "")
        context = self._format_prompt(context, env)

        if "{context}" in prompt_template:
            return prompt_template.format(
                phase_name=self.phase_name,
                context=context,
                the_other_role=self.assistant_role,
                assistant_role=self.assistant_role,
                user_role=self.user_role,
            )
        else:
            prompt_template = self._format_prompt(prompt_template, env)
            return prompt_template.format(
                phase_name=self.phase_name,
                context=context,
                the_other_role=self.assistant_role,
                assistant_role=self.assistant_role,
                user_role=self.user_role,
            )

    def render_dialog_prompt(self, the_other_role: str, content: str) -> str:
        """Render the dialog prompt with the other role's message."""
        prompt_template = self.phase_config.get(
            "dialog_prompt",
            "{the_other_role} said: {content}",
        )
        return prompt_template.format(the_other_role=the_other_role, content=content)

    def _should_end_dialog(self, response: str) -> bool:
        """Check if the dialog should end."""
        result_pattern = r"<result>\s*(.+?)\s*</result>"
        matches = re.finditer(result_pattern, response, re.DOTALL | re.IGNORECASE)
        for match in matches:
            start_pos = match.start()
            if self._is_inside_quotes(response, start_pos):
                continue
            return True
        return False

    def _is_inside_quotes(self, text: str, pos: int) -> bool:
        """Check if position is inside any type of quotes (single, double, backtick).

        Only checks characters immediately surrounding the position.
        """
        if pos == 0:
            return False

        prev_char = text[pos - 1]
        prev_prev_char = text[pos - 2] if pos >= 2 else ""

        if prev_char == '"' or prev_prev_char == '"':
            return True
        if prev_char == "'" or prev_prev_char == "'":
            return True
        if prev_char == "`" or prev_prev_char == "`":
            return True

        return False

    def _format_prompt(self, prompt_template: str, env: ChatEnv) -> str:
        """Format prompt template with environment data."""
        return prompt_template.format(
            task=env.task_prompt,
            modality=env.modality,
            language=env.language,
            assistant_role=self.assistant_role,
            user_role=self.user_role,
        )

    def update_env(self, env: ChatEnv, response: str) -> None:
        """Update environment based on agent response."""
        print(f"update_env: response={response}")
        result_pattern = r"<result>\s*(.+?)\s*</result>"
        matches = list(re.finditer(result_pattern, response, re.DOTALL | re.IGNORECASE))
        result_content = None
        for match in matches:
            content = match.group(1).strip()
            start_pos = match.start()
            if not self._is_inside_quotes(response, start_pos):
                result_content = content
                break
        if result_content:
            print(f"update_env: result_content={result_content}")

            if self.phase_name == "DemandAnalysis":
                env.modality = result_content
            elif self.phase_name == "LanguageChoose":
                env.language = result_content
