"""
ChatChain for ClawDev framework.

Orchestrates the complete software development process through configured phases.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from ..env.env import ChatEnv
from ..phases.base import Phase

logger = logging.getLogger(__name__)


class ChatChain:
    """Main orchestrator for the software development process."""

    def __init__(self, agent_adapter, config_name: str = "Default"):
        """
        Initialize chain with agent adapter and configuration.

        Args:
            agent_adapter: Adapter for communicating with AI agents (can be any object with a send method)
            config_name: Name of configuration to use
        """
        self.agent_adapter = agent_adapter
        self.config_name = config_name
        self.config_path = os.path.join("configs", config_name)

        # Load configuration files
        self.chain_config = self._load_config("ChatChainConfig.json")
        self.phase_config = self._load_config("PhaseConfig.json")
        self.role_config = self._load_config("RoleConfig.json")

        # Initialize environment
        self.env: Optional[ChatEnv] = None

    def _load_config(self, filename: str) -> Dict[str, Any]:
        """
        Load configuration file.

        Args:
            filename: Name of configuration file

        Returns:
            Configuration dictionary
        """
        config_file = os.path.join(self.config_path, filename)
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def pre_processing(self, task_prompt: str, project_name: str) -> None:
        """
        Perform pre-processing steps before chain execution.

        Args:
            task_prompt: User's task description
            project_name: Name for the project directory
        """
        # Create project directory
        project_dir = os.path.join("projects", project_name)
        os.makedirs(project_dir, exist_ok=True)

        # Initialize environment
        self.env = ChatEnv(project_dir)
        self.env.task_prompt = task_prompt

    def make_recruitment(self) -> None:
        """Register roles in the environment."""
        # In a full implementation, this would register roles with the environment
        # For now, we'll just ensure the environment exists
        if self.env is None:
            raise RuntimeError("Environment not initialized")

    def execute_chain(self) -> None:
        """Execute all phases in the chain."""
        if self.env is None:
            raise RuntimeError("Environment not initialized")

        # Execute each phase in the chain configuration
        for phase_item in self.chain_config["chain"]:
            self.execute_step(phase_item)

    def execute_step(self, phase_item: Dict[str, Any]) -> None:
        """
        Execute a single phase step.

        Args:
            phase_item: Configuration for the phase to execute
        """
        if self.env is None:
            raise RuntimeError("Environment not initialized")

        phase_type = phase_item["phaseType"]

        if phase_type == "SimplePhase":
            # Execute a simple phase
            phase_name = phase_item["phase"]
            phase_config = self.phase_config[phase_name]

            # Dynamically create and execute the appropriate phase class
            print(f"Executing phase: {phase_name}")

            # Import the appropriate phase class
            if phase_name == "DemandAnalysis":
                from ..phases.demand_analysis import DemandAnalysisPhase

                phase = DemandAnalysisPhase(phase_config)
            elif phase_name == "LanguageChoose":
                from ..phases.language_choose import LanguageChoosePhase

                phase = LanguageChoosePhase(phase_config)
            elif phase_name == "Coding":
                from ..phases.coding import CodingPhase

                phase = CodingPhase(phase_config)
            elif phase_name == "CodeComplete":
                from ..phases.coding import CodeCompletePhase

                phase = CodeCompletePhase(phase_config)
            elif phase_name == "CodeReviewComment":
                from ..phases.code_review import CodeReviewCommentPhase

                phase = CodeReviewCommentPhase(phase_config)
            elif phase_name == "CodeReviewModification":
                from ..phases.code_review import CodeReviewModificationPhase

                phase = CodeReviewModificationPhase(phase_config)
            elif phase_name == "TestErrorSummary":
                from ..phases.testing import TestErrorSummaryPhase

                phase = TestErrorSummaryPhase(phase_config)
            elif phase_name == "TestModification":
                from ..phases.testing import TestModificationPhase

                phase = TestModificationPhase(phase_config)
            elif phase_name == "EnvironmentDoc":
                from ..phases.environment_doc import EnvironmentDocPhase

                phase = EnvironmentDocPhase(phase_config)
            elif phase_name == "Manual":
                from ..phases.manual import ManualPhase

                phase = ManualPhase(phase_config)
            else:
                print(f"Unknown phase: {phase_name}")
                return

            # Execute the phase
            self.env = phase.execute(self.env, self.agent_adapter)

        elif phase_type == "ComposedPhase":
            # Execute a composed phase with multiple sub-phases
            cycle_num = phase_item["cycleNum"]
            composition = phase_item["Composition"]

            print(f"Executing composed phase with {cycle_num} cycles")

            # Execute sub-phases for the specified number of cycles
            for cycle in range(cycle_num):
                print(f"Cycle {cycle + 1}")
                for sub_phase_item in composition:
                    sub_phase_name = sub_phase_item["phase"]
                    print(f"  Executing sub-phase: {sub_phase_name}")

                    # Import the appropriate phase class
                    if sub_phase_name == "DemandAnalysis":
                        from ..phases.demand_analysis import DemandAnalysisPhase

                        phase = DemandAnalysisPhase(sub_phase_item)
                    elif sub_phase_name == "LanguageChoose":
                        from ..phases.language_choose import LanguageChoosePhase

                        phase = LanguageChoosePhase(sub_phase_item)
                    elif sub_phase_name == "Coding":
                        from ..phases.coding import CodingPhase

                        phase = CodingPhase(sub_phase_item)
                    elif sub_phase_name == "CodeComplete":
                        from ..phases.coding import CodeCompletePhase

                        phase = CodeCompletePhase(sub_phase_item)
                    elif sub_phase_name == "CodeReviewComment":
                        from ..phases.code_review import CodeReviewCommentPhase

                        phase = CodeReviewCommentPhase(sub_phase_item)
                    elif sub_phase_name == "CodeReviewModification":
                        from ..phases.code_review import CodeReviewModificationPhase

                        phase = CodeReviewModificationPhase(sub_phase_item)
                    elif sub_phase_name == "TestErrorSummary":
                        from ..phases.testing import TestErrorSummaryPhase

                        phase = TestErrorSummaryPhase(sub_phase_item)
                    elif sub_phase_name == "TestModification":
                        from ..phases.testing import TestModificationPhase

                        phase = TestModificationPhase(sub_phase_item)
                    elif sub_phase_name == "EnvironmentDoc":
                        from ..phases.environment_doc import EnvironmentDocPhase

                        phase = EnvironmentDocPhase(sub_phase_item)
                    elif sub_phase_name == "Manual":
                        from ..phases.manual import ManualPhase

                        phase = ManualPhase(sub_phase_item)
                    else:
                        print(f"Unknown sub-phase: {sub_phase_name}")
                        continue

                    # Execute the phase
                    self.env = phase.execute(self.env, self.agent_adapter)

    def post_processing(self) -> None:
        """Perform post-processing steps after chain execution."""
        if self.env is None:
            raise RuntimeError("Environment not initialized")

        # Write all generated files
        self.env.write_meta()
        self.env.write_codes()
        self.env.write_manual()
        self.env.write_requirements()

    def run(self, task_prompt: str, project_name: str) -> None:
        """
        Run the complete development chain.

        Args:
            task_prompt: User's task description
            project_name: Name for the project directory
        """
        self.pre_processing(task_prompt, project_name)
        self.make_recruitment()
        self.execute_chain()
        self.post_processing()
