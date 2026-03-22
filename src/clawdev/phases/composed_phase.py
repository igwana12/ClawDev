"""
Composed Phase for ClawDev framework.

Executes multiple phases in a loop with configurable cycle limits.
"""

from typing import Dict, Any, List
from ..phases.base import Phase
from ..env.env import ChatEnv


class ComposedPhase(Phase):
    """Phase that executes multiple sub-phases in a loop."""

    def __init__(self, phase_config: Dict[str, Any]):
        """
        Initialize composed phase.

        Args:
            phase_config: Configuration for this phase including sub-phases
        """
        super().__init__(phase_config)
        self.cycle_num = phase_config.get("cycleNum", 1)
        self.composition = phase_config.get("Composition", [])

    def execute(self, env: ChatEnv, agent_adapter) -> ChatEnv:
        """
        Execute composed phase by running sub-phases in cycles.

        Args:
            env: Current development environment
            agent_adapter: Adapter for communicating with AI agents

        Returns:
            Updated environment after all cycles
        """
        # Execute sub-phases for the specified number of cycles
        for cycle in range(self.cycle_num):
            print(f"Executing cycle {cycle + 1} of {self.cycle_num}")

            # Execute each sub-phase in the composition
            for sub_phase_config in self.composition:
                sub_phase_name = sub_phase_config["phase"]
                print(f"  Executing sub-phase: {sub_phase_name}")

                # In a full implementation, this would dynamically create and execute the sub-phase
                # For now, we'll just print the sub-phase name

        return env
