"""
Integration test for ClawDev full workflow.

This test simulates the execution of the default ClawDev workflow and verifies
that each phase sends the correct prompt to the correct agent.
"""

import sys
import os
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from clawdev.chain.chain import ChatChain
from clawdev.adapter.agent_adapter import AgentAdapter
from clawdev.env.env import ChatEnv


class WorkflowRecorder:
    """Record the complete workflow execution."""

    def __init__(self, agent_configs):
        self.agent_configs = agent_configs
        self.steps = []
        self.adapter = None

    def create_adapter(self):
        """Create adapter that records calls."""
        adapter = AgentAdapter(self.agent_configs)
        self.adapter = adapter

        # Wrap send method to record calls
        def recorded_send(message, role="default"):
            agent_name = adapter.agent_configs.get(role, "chief_executive_officer")
            self.steps.append(
                {
                    "role": role,
                    "agent_name": agent_name,
                    "message_preview": message[:200] if message else "",
                    "message_length": len(message),
                }
            )
            # Return mock response based on role
            return self._mock_response(role)

        adapter.send = recorded_send

        return adapter

    def _mock_response(self, role):
        """Return mock response based on role."""
        responses = {
            "Chief Product Officer": "Based on the task, I recommend we create an Application.\n<INFO> Application",
            "Chief Technology Officer": "For this task, Python would be the best choice.\n<INFO> Python",
            "Programmer": "Here is the code:\n\nmain.py\n```python\nprint('Hello')\n```\n<INFO> Code complete",
            "Code Reviewer": "Code looks good, no issues found.\n<INFO> Finished",
            "Software Test Engineer": "All tests passed.\n<INFO> No errors",
            "Chief Creative Officer": "Design approved.\n<INFO> Approved",
        }
        return responses.get(role, f"Mock response for {role}")


def load_chain_config():
    """Load chain configuration."""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "configs", "default", "ChatChainConfig.json"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_phase_config():
    """Load phase configuration."""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "configs", "default", "PhaseConfig.json"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def agent_configs():
    """Agent configuration mapping."""
    return {
        "Chief Executive Officer": "chief_executive_officer",
        "Chief Product Officer": "chief_product_officer",
        "Chief Technology Officer": "chief_technology_officer",
        "Programmer": "programmer",
        "Code Reviewer": "code_reviewer",
        "Software Test Engineer": "software_test_engineer",
        "Chief Creative Officer": "chief_creative_officer",
        "Counselor": "counselor",
        "Chief Human Resource Officer": "chief_human_resource_officer",
    }


@pytest.fixture
def chain_config():
    """Load chain config."""
    return load_chain_config()


@pytest.fixture
def phase_config():
    """Load phase config."""
    return load_phase_config()


class TestClawDevWorkflow:
    """Test the complete ClawDev workflow."""

    def test_full_workflow_execution_order(
        self, agent_configs, chain_config, phase_config
    ):
        """
        Test that the workflow executes phases in the correct order
        and routes to correct agents.
        """
        recorder = WorkflowRecorder(agent_configs)
        adapter = recorder.create_adapter()

        # Create chain
        chain = ChatChain(adapter, config_name="default")

        # Run pre-processing
        task = "Create a simple calculator app"
        chain.pre_processing(task, "test_project")
        chain.make_recruitment()

        # Execute phases (simplified - just call execute_step for each)
        for phase_item in chain_config["chain"]:
            phase_type = phase_item.get("phaseType")

            if phase_type == "SimplePhase":
                # Execute via chain
                chain.execute_step(phase_item)

            elif phase_type == "ComposedPhase":
                cycle_num = phase_item.get("cycleNum", 1)
                composition = phase_item.get("Composition", [])

                for cycle in range(cycle_num):
                    for sub_phase_item in composition:
                        # Execute via chain
                        chain.execute_step(sub_phase_item)

        # Verify the execution
        print("\n" + "=" * 60)
        print("Workflow Execution Summary")
        print("=" * 60)
        print(f"Total steps executed: {len(recorder.steps)}")
        print("\nExecution sequence:")

        for i, step in enumerate(recorder.steps):
            print(f"  {i + 1}. {step['role']} -> {step['agent_name']}")

        # Verify first few steps match expected
        assert len(recorder.steps) > 0, "Workflow should execute at least one step"

        # First step should be DemandAnalysis -> CEO (user_role initiates dialog)
        first_step = recorder.steps[0]
        assert first_step["role"] == "Chief Executive Officer", (
            f"First step should be CEO (initiator), got {first_step['role']}"
        )
        assert first_step["agent_name"] == "chief_executive_officer"

        print("\n" + "=" * 60)
        print("✓ Workflow executes correctly")
        print("=" * 60)


class TestPhaseSequence:
    """Test individual phase execution sequence."""

    def test_demand_analysis_sends_to_ceo(self, agent_configs, phase_config):
        """Test that DemandAnalysis phase sends to CEO (user_role initiates)."""
        recorder = WorkflowRecorder(agent_configs)
        adapter = recorder.create_adapter()

        from clawdev.phases.demand_analysis import DemandAnalysisPhase

        # Create phase
        phase = DemandAnalysisPhase(phase_config["DemandAnalysis"])

        # Create env
        env = ChatEnv("/tmp/test")
        env.task_prompt = "Create a calculator"

        # Execute
        env = phase.execute(env, adapter)

        # Verify first message goes to CEO (user_role, the initiator)
        assert len(recorder.steps) >= 1
        first_step = recorder.steps[0]
        assert first_step["role"] == "Chief Executive Officer"
        assert first_step["agent_name"] == "chief_executive_officer"

    def test_language_choose_sends_to_ceo(self, agent_configs, phase_config):
        """Test that LanguageChoose phase sends to CEO (user_role initiates)."""
        recorder = WorkflowRecorder(agent_configs)
        adapter = recorder.create_adapter()

        from clawdev.phases.language_choose import LanguageChoosePhase

        phase = LanguageChoosePhase(phase_config["LanguageChoose"])

        env = ChatEnv("/tmp/test")
        env.task_prompt = "Create a calculator"
        env.modality = "Application"

        env = phase.execute(env, adapter)

        assert len(recorder.steps) >= 1
        first_step = recorder.steps[0]
        assert first_step["role"] == "Chief Executive Officer"
        assert first_step["agent_name"] == "chief_executive_officer"

    def test_coding_sends_to_cto(self, agent_configs, phase_config):
        """Test that Coding phase sends to CTO (user_role initiates)."""
        recorder = WorkflowRecorder(agent_configs)
        adapter = recorder.create_adapter()

        from clawdev.phases.coding import CodingPhase

        phase = CodingPhase(phase_config["Coding"])

        env = ChatEnv("/tmp/test")
        env.task_prompt = "Create a calculator"
        env.modality = "Application"
        env.language = "Python"
        env.description = "Simple calculator"

        env = phase.execute(env, adapter)

        assert len(recorder.steps) >= 1
        first_step = recorder.steps[0]
        assert first_step["role"] == "Chief Technology Officer"
        assert first_step["agent_name"] == "chief_technology_officer"


class TestMessageContent:
    """Test that messages contain expected content."""

    def test_demand_analysis_prompt_contains_task(self, agent_configs, phase_config):
        """Test that DemandAnalysis prompt contains task information."""
        from clawdev.phases.demand_analysis import DemandAnalysisPhase

        adapter = AgentAdapter(agent_configs)

        # Override send to capture message
        captured_message = []

        def capture_send(message, role="default"):
            captured_message.append(message)
            return "Test response"

        adapter.send = capture_send

        phase = DemandAnalysisPhase(phase_config["DemandAnalysis"])

        env = ChatEnv("/tmp/test")
        env.task_prompt = "Create a calculator app"

        phase.execute(env, adapter)

        assert len(captured_message) >= 1
        first_message = captured_message[0]

        # Verify prompt contains task
        assert (
            "Create a calculator app" in first_message
            or "calculator" in first_message.lower()
        ), "Prompt should contain task information"

    def test_coding_prompt_contains_language(self, agent_configs, phase_config):
        """Test that Coding prompt contains language information."""
        from clawdev.phases.coding import CodingPhase

        adapter = AgentAdapter(agent_configs)

        captured_message = []

        def capture_send(message, role="default"):
            captured_message.append(message)
            return "Test response"

        adapter.send = capture_send

        phase = CodingPhase(phase_config["Coding"])

        env = ChatEnv("/tmp/test")
        env.task_prompt = "Create a calculator"
        env.modality = "Application"
        env.language = "Python"
        env.description = "Calculator app"

        phase.execute(env, adapter)

        assert len(captured_message) >= 1
        first_message = captured_message[0]

        # Verify prompt contains language
        assert "Python" in first_message, "Prompt should contain language information"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
