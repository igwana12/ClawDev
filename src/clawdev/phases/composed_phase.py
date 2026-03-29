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

Composed Phase for ClawDev framework.

Executes multiple phases in a loop with configurable cycle limits.
Provides hooks for sub-classes to customize behavior.
"""

import logging
from typing import Dict, Any, List
from .base import Phase
from .simple_phase import SimplePhase

logger = logging.getLogger(__name__)


class ComposedPhase(Phase):
    """Phase that executes multiple sub-phases in a loop."""

    def __init__(
        self, phase_config: Dict[str, Any], config_phase: Dict[str, Any] = None
    ):
        """
        Initialize ComposedPhase with configuration.

        Args:
            phase_config: Configuration for this composed phase
            config_phase: Configuration for all phases (from PhaseConfig.json)
        """
        super().__init__(phase_config)
        self.cycle_num = phase_config.get("cycleNum", 1)
        self.composition: List[Dict[str, Any]] = phase_config.get("composition", [])

        self.config_phase = config_phase or {}
        self.phase_env: Dict[str, Any] = {"cycle_num": self.cycle_num}

        self.sub_phases: Dict[str, Phase] = {}
        self._init_sub_phases()

    def _init_sub_phases(self) -> None:
        """Initialize all SimplePhase instances in this ComposedPhase."""
        for phase_item in self.composition:
            if phase_item.get("phaseType") == "SimplePhase":
                phase_name = phase_item["phase"]
                if phase_name in self.config_phase:
                    phase_config = self.config_phase[phase_name]
                    self.sub_phases[phase_name] = SimplePhase(phase_config)

    def update_phase_env(self, env) -> None:
        """
        Update phase environment from global environment.
        Override in subclass for custom behavior.
        """
        pass

    def update_chat_env(self, env) -> None:
        """
        Update global environment using the conclusion.
        Override in subclass for custom behavior.
        """
        pass

    def break_cycle(self, phase_env: Dict[str, Any]) -> bool:
        """
        Check if should break early from the loop.
        Override in subclass for custom conditions.
        """
        return False

    def execute(self, env, agent_adapter):
        """
        Execute this composed phase by cycling through sub-phases.

        Args:
            env: Current development environment
            agent_adapter: Adapter for communicating with AI agents

        Returns:
            Updated environment after all cycles complete
        """
        logger.info(
            "[ComposedPhase] execute() phase=%s, cycles=%d",
            self.phase_name,
            self.cycle_num,
        )

        self.update_phase_env(env)

        for cycle_index in range(1, self.cycle_num + 1):
            logger.info("[ComposedPhase] cycle %d/%d", cycle_index, self.cycle_num)
            self.phase_env["cycle_index"] = cycle_index

            for phase_item in self.composition:
                if phase_item.get("phaseType") != "SimplePhase":
                    continue

                phase_name = phase_item["phase"]
                logger.info("[ComposedPhase] executing sub-phase: %s", phase_name)

                if phase_name in self.sub_phases:
                    sub_phase = self.sub_phases[phase_name]
                    sub_phase.phase_env = self.phase_env

                    self.update_phase_env(env)
                    if self.break_cycle(self.phase_env):
                        logger.info("[ComposedPhase] break_cycle true, returning")
                        return env

                    env = sub_phase.execute(env, agent_adapter)

                    if self.break_cycle(self.phase_env):
                        logger.info(
                            "[ComposedPhase] break_cycle true after sub-phase, returning"
                        )
                        return env
                else:
                    logger.warning("Phase '%s' not found in config", phase_name)

        self.update_chat_env(env)
        return env
