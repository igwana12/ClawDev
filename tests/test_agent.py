import os
import pytest
from unittest.mock import Mock, patch

from openclaw_acp.agent import OpenClawAgent


class TestOpenClawAgent:
    @patch.dict("os.environ", {"OPENCLAW_GATEWAY_TOKEN": "test_token"})
    def test_step_raises_when_not_started(self):
        agent = OpenClawAgent(auto_start=False)
        with pytest.raises(RuntimeError, match="请先调用 start()"):
            agent.step("test message")

    @patch.dict("os.environ", {"OPENCLAW_GATEWAY_TOKEN": "test_token"})
    def test_call_forwards_to_step(self):
        agent = OpenClawAgent(auto_start=False)
        agent.step = Mock(return_value="response")
        result = agent("test message")
        agent.step.assert_called_once_with("test message", 120)
        assert result == "response"

    @patch.dict("os.environ", {"OPENCLAW_GATEWAY_TOKEN": "test_token"})
    def test_context_manager(self):
        with patch.object(OpenClawAgent, "start") as mock_start:
            with OpenClawAgent(auto_start=False):
                mock_start.assert_called_once()

    @patch.dict("os.environ", {"OPENCLAW_GATEWAY_TOKEN": "test_token"})
    def test_stop(self):
        agent = OpenClawAgent(auto_start=False)
        agent._started = True
        proc_mock = Mock()
        agent._proc = proc_mock
        agent.stop()
        proc_mock.terminate.assert_called_once()
        proc_mock.wait.assert_called_once()
        assert agent._started is False
        assert agent._proc is None


class TestOpenClawAgentRequiresApiKey:
    def test_raises_without_token(self):
        with pytest.raises(ValueError, match="API key"):
            OpenClawAgent(auto_start=False)

    def test_accepts_token_in_env(self):
        with patch.dict(os.environ, {"OPENCLAW_GATEWAY_TOKEN": "test_token"}):
            agent = OpenClawAgent(auto_start=False)
            assert agent is not None
