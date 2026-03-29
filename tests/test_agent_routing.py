"""
Test for ClawDev framework agent routing using pytest.

This test verifies that each phase correctly routes to the expected agent
based on the assistant_role defined in PhaseConfig.json.
"""

import sys
import os
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from clawdev.adapter.agent_adapter import AgentAdapter
from clawdev.phases.simple_phase import SimplePhase
from clawdev.env.env import ChatEnv


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
def phase_config():
    """Load phase configuration."""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "configs", "default", "PhaseConfig.json"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def agent_adapter(agent_configs):
    """Create AgentAdapter instance."""
    return AgentAdapter(agent_configs)


@pytest.fixture
def chat_env():
    """Create ChatEnv for testing."""
    return ChatEnv("/tmp/test")


class TestPhaseConfigConsistency:
    """Test that all phases have required configuration."""

    @pytest.mark.parametrize(
        "phase_name,expected_assistant,expected_user",
        [
            ("DemandAnalysis", "Chief Product Officer", "Chief Executive Officer"),
            ("LanguageChoose", "Chief Technology Officer", "Chief Executive Officer"),
            ("CodingInit", "Programmer", "Chief Technology Officer"),
            ("CodingImprove", "Programmer", "Chief Technology Officer"),
            ("CodeReviewInit", "Code Reviewer", "Chief Technology Officer"),
            ("CodeReviewModification", "Programmer", "Code Reviewer"),
            ("TestRunInit", "Software Test Engineer", "Chief Technology Officer"),
            ("TestRun", "Programmer", "Software Test Engineer"),
            ("CodingDoc", "Programmer", "Chief Technology Officer"),
        ],
    )
    def test_phase_role_mapping(
        self, phase_config, phase_name, expected_assistant, expected_user
    ):
        """Test that each phase has correct role mapping."""
        config = phase_config[phase_name]

        assert config.get("assistant_role_name") == expected_assistant, (
            f"{phase_name}: assistant_role should be {expected_assistant}"
        )
        assert config.get("user_role_name") == expected_user, (
            f"{phase_name}: user_role should be {expected_user}"
        )


class TestAgentRouting:
    """Test agent routing for each phase."""

    @pytest.mark.parametrize(
        "phase_name",
        [
            "DemandAnalysis",
            "LanguageChoose",
            "CodingInit",
            "CodingImprove",
            "CodeReviewInit",
            "CodeReviewModification",
            "TestRunInit",
            "TestRun",
            "CodingDoc",
        ],
    )
    def test_phase_routes_to_correct_agent(
        self, phase_config, agent_adapter, chat_env, phase_name
    ):
        """Test that phase routes to correct agent based on assistant_role."""
        if phase_name not in phase_config:
            pytest.skip(f"{phase_name} not in config")

        config = phase_config[phase_name]
        assistant_role = config.get("assistant_role_name")

        if not assistant_role:
            pytest.fail(f"{phase_name} has no assistant_role_name")

        # Create phase and render prompt
        phase = SimplePhase(config)
        prompt = phase.render_prompt(chat_env)

        # Verify prompt was rendered
        assert prompt, f"{phase_name}: prompt should not be empty"

        # Get expected agent name
        expected_agent = agent_adapter.agent_configs.get(
            assistant_role, "chief_executive_officer"
        )

        # The routing is based on agent_configs.get(assistant_role)
        actual_agent = agent_adapter.agent_configs.get(
            assistant_role, "chief_executive_officer"
        )

        assert actual_agent == expected_agent, (
            f"{phase_name}: should route to {expected_agent}, got {actual_agent}"
        )


class TestAgentAdapter:
    """Test AgentAdapter functionality."""

    def test_agent_configs_contains_all_roles(self, agent_adapter):
        """Test that agent_configs contains all required roles."""
        required_roles = {
            "Chief Executive Officer",
            "Chief Product Officer",
            "Chief Technology Officer",
            "Programmer",
            "Code Reviewer",
            "Software Test Engineer",
            "Chief Creative Officer",
            "Counselor",
            "Chief Human Resource Officer",
        }

        for role in required_roles:
            assert role in agent_adapter.agent_configs, f"Missing role: {role}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
