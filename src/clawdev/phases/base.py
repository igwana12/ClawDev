"""
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

    def __init__(self, phase_config: Dict[str, Any]):
        """
        Initialize phase with configuration.

        Args:
            phase_config: Configuration dictionary for this phase
        """
        self.phase_config = phase_config
        self.phase_name = phase_config.get("phase", self.__class__.__name__)
        self.assistant_role = phase_config.get("assistant_role_name", "")
        self.user_role = phase_config.get("user_role_name", "")
        self.max_dialog_turns = phase_config.get("max_dialog_turns", 5)
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
        matches = re.finditer(result_pattern, response, re.DOTALL)
        for match in matches:
            result_content = match.group(1)
            start_pos = match.start()
            end_pos = match.end()
            before_result = response[:start_pos]
            after_result = response[end_pos:]
            if self._is_inside_quotes(before_result, after_result):
                continue
            return True
        return False

    def _is_inside_quotes(self, before: str, after: str) -> bool:
        """Check if a string segment is enclosed in quotes."""
        last_single_quote = before.rfind("'")
        last_double_quote = before.rfind('"')
        if last_single_quote == -1 and last_double_quote == -1:
            return False
        last_quote_pos = max(last_single_quote, last_double_quote)
        last_quote_char = "'" if last_single_quote > last_double_quote else '"'
        quote_count_before = before.count(last_quote_char)
        quote_count_after = after.count(last_quote_char)
        if quote_count_before % 2 == 1 and quote_count_after > 0:
            return True
        return False

    def _format_prompt(self, prompt_template: str, env: ChatEnv) -> str:
        """Format prompt template with environment data."""
        try:
            return prompt_template.format(
                task=env.task_prompt,
                modality=env.modality,
                language=env.language,
                ideas=env.ideas,
                codes=env.get_codes(),
                requirements=env.requirements,
                comments=env.review_comments,
                test_reports=env.test_reports,
                error_summary=env.error_summary,
                images=env.images,
                unimplemented_file=env.unimplemented_file,
                description=env.description,
                gui=env.gui,
                assistant_role=self.assistant_role,
                user_role=self.user_role,
            )
        except KeyError as e:
            print(f"KeyError in _format_prompt: {e}")
            raise

    def update_env(self, env: ChatEnv, response: str) -> None:
        """Update environment based on agent response."""
        print(f"update_env: response={response}")
        result_pattern = r"<result>\s*(.+?)\s*</result>"
        matches = list(re.finditer(result_pattern, response, re.DOTALL))
        result_content = None
        for match in matches:
            content = match.group(1).strip()
            start_pos = match.start()
            end_pos = match.end()
            before_result = response[:start_pos]
            after_result = response[end_pos:]
            if not self._is_inside_quotes(before_result, after_result):
                result_content = content
                break
        if result_content:
            print(f"update_env: result_content={result_content}")

            if self.phase_name == "DemandAnalysis":
                env.modality = result_content
            elif self.phase_name == "LanguageChoose":
                env.language = result_content
            elif self.phase_name == "Coding":
                env.description = result_content
            elif self.phase_name == "CodeComplete":
                env.unimplemented_file = result_content
            elif self.phase_name == "CodeReviewComment":
                env.comments = result_content
            elif self.phase_name == "TestErrorSummary":
                env.error_summary = result_content
            elif self.phase_name == "EnvironmentDoc":
                env.docs = result_content
            elif self.phase_name == "Manual":
                env.manual = result_content
            elif self.phase_name == "ArtDesign":
                env.images = result_content
            elif self.phase_name == "ArtIntegration":
                env.art_integration_result = result_content
