"""
Base phase class for ClawDev framework.

Defines the abstract interface and common functionality for all development phases.
"""

from abc import ABC, abstractmethod
import re
from typing import Dict, Any, List
from ..env.env import ChatEnv


class Phase(ABC):
    """Abstract base class for all development phases."""

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
        self.phase_prompt = phase_config.get("phase_prompt", [])

    def execute(self, env: ChatEnv, agent_adapter) -> ChatEnv:
        """
        Execute this phase of the development process.

        Args:
            env: Current development environment
            agent_adapter: Adapter for communicating with AI agents

        Returns:
            Updated environment after phase execution
        """
        # Render prompt for this phase
        prompt = self.render_prompt(env)

        # Send prompt to agent and get response
        # Pass the role information to the adapter
        if hasattr(self, "assistant_role") and self.assistant_role:
            response = agent_adapter.send(prompt, role=self.assistant_role)
        else:
            response = agent_adapter.send(prompt)

        # Update environment with agent response
        self.update_env(env, response)

        return env

    def render_prompt(self, env: ChatEnv) -> str:
        """
        Render the prompt for this phase based on environment state.

        Args:
            env: Current development environment

        Returns:
            Formatted prompt string
        """
        # Join all prompt lines and format with environment data
        prompt_template = "\n".join(self.phase_prompt)

        # Replace placeholders with actual values from environment
        try:
            prompt = prompt_template.format(
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
                gui=env.gui,  # This would be set based on config
                assistant_role=self.assistant_role,
                user_role=self.user_role,
            )
        except KeyError as e:
            print(f"KeyError in render_prompt: {e}")
            print(
                f"Available keys in template: {set(re.findall(r'\{(\w+)\}', prompt_template))}"
            )
            print(
                f"Environment state: task_prompt={env.task_prompt}, modality={env.modality}, language={env.language}"
            )
            raise

        return prompt

    def update_env(self, env: ChatEnv, response: str) -> None:
        """
        Update environment based on agent response.

        Args:
            env: Environment to update
            response: Agent response to parse
        """
        # Default implementation - can be overridden by subclasses
        # Look for <INFO> markers in response
        print(f"update_env: response={response}")
        if "<INFO>" in response:
            info_start = response.find("<INFO>") + 6  # Length of "<INFO>"
            info_end = response.find("\n", info_start)
            if info_end == -1:
                info_end = len(response)

            info_content = response[info_start:info_end].strip()
            print(f"update_env: info_content={info_content}")

            # Update environment based on phase type
            if (
                self.phase_name == "DemandAnalysis"
                or self.phase_name == "DemandAnalysisPhase"
            ):
                print(f"update_env: Setting env.modality to {info_content}")
                env.modality = info_content
                print(f"update_env: env.modality is now {env.modality}")
            elif (
                self.phase_name == "LanguageChoose"
                or self.phase_name == "LanguageChoosePhase"
            ):
                print(f"update_env: Setting env.language to {info_content}")
                env.language = info_content
                print(f"update_env: env.language is now {env.language}")
            # Other phase-specific updates would go here
