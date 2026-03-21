import asyncio
import os
import threading
from queue import Queue
from unittest.mock import Mock, patch

import pytest

from openclaw_acp.agent import OpenClawAgent


class TestOpenClawAgent:
    @patch.dict("os.environ", {"OPENCLAW_GATEWAY_TOKEN": "test_token"})
    def test_step_raises_when_not_started(self):
        agent = OpenClawAgent(auto_start=False)
        with pytest.raises(RuntimeError, match="请先调用 start()"):
            agent.step("test message")

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

    def test_step_returns_streaming_response(self):
        with patch.dict("os.environ", {"OPENCLAW_GATEWAY_TOKEN": "test_token"}):
            agent = OpenClawAgent(auto_start=False)
            agent._proc = Mock()
            agent._session_id = "test-session"
            agent._lock = threading.Lock()
            agent._recv_queue = Queue()

        def put_response():
            import time

            time.sleep(0.05)
            resp_q = agent._pending.get("mock-id")
            if resp_q:
                resp_q.put({"result": {"stopReason": None}})

        threading.Thread(target=put_response, daemon=True).start()

        with patch("openclaw_acp.agent.uuid.uuid4", return_value="mock-id"):
            result = agent.step("test", timeout=10)

        assert result == ""

    def test_step_returns_immediate_response(self):
        with patch.dict("os.environ", {"OPENCLAW_GATEWAY_TOKEN": "test_token"}):
            agent = OpenClawAgent(auto_start=False)
            agent._proc = Mock()
            agent._session_id = "test-session"
            agent._lock = threading.Lock()

        def put_response():
            import time

            time.sleep(0.05)
            resp_q = agent._pending.get("mock-id")
            if resp_q:
                resp_q.put(
                    {
                        "result": {
                            "stopReason": "stop",
                            "parts": [{"type": "text", "text": "Hello"}],
                        }
                    }
                )

        threading.Thread(target=put_response, daemon=True).start()

        with patch("openclaw_acp.agent.uuid.uuid4", return_value="mock-id"):
            result = agent.step("test", timeout=10)

        assert result == "Hello"

    def test_step_raises_on_error(self):
        with patch.dict("os.environ", {"OPENCLAW_GATEWAY_TOKEN": "test_token"}):
            agent = OpenClawAgent(auto_start=False)
            agent._proc = Mock()
            agent._session_id = "test-session"
            agent._lock = threading.Lock()

        def put_response():
            import time

            time.sleep(0.05)
            resp_q = agent._pending.get("mock-id")
            if resp_q:
                resp_q.put({"error": {"message": "test error"}})

        threading.Thread(target=put_response, daemon=True).start()

        with patch("openclaw_acp.agent.uuid.uuid4", return_value="mock-id"):
            with pytest.raises(RuntimeError, match="ACP error"):
                agent.step("test", timeout=10)

    def test_astep_returns_response(self):
        with patch.dict("os.environ", {"OPENCLAW_GATEWAY_TOKEN": "test_token"}):
            agent = OpenClawAgent(auto_start=False)
            agent._proc = Mock()
            agent._session_id = "test-session"
            agent._lock = threading.Lock()

        def put_response():
            import time

            time.sleep(0.05)
            resp_q = agent._pending.get("mock-id")
            if resp_q:
                resp_q.put(
                    {
                        "result": {
                            "stopReason": "stop",
                            "parts": [{"type": "text", "text": "Async Hello"}],
                        }
                    }
                )

        threading.Thread(target=put_response, daemon=True).start()

        async def run():
            with patch("openclaw_acp.agent.uuid.uuid4", return_value="mock-id"):
                return await agent.astep("test", timeout=10)

        result = asyncio.run(run())
        assert result == "Async Hello"

    def test_stream_yields_chunks(self):
        with patch.dict("os.environ", {"OPENCLAW_GATEWAY_TOKEN": "test_token"}):
            agent = OpenClawAgent(auto_start=False)
            agent._proc = Mock()
            agent._session_id = "test-session"
            agent._lock = threading.Lock()
            agent._recv_queue = Queue()

        def put_responses():
            import time

            time.sleep(0.05)
            resp_q = agent._pending.get("mock-id")
            if resp_q:
                resp_q.put({"result": {}})

            time.sleep(0.1)
            agent._recv_queue.put(
                {
                    "method": "session/update",
                    "params": {
                        "update": {
                            "sessionUpdate": "agent_message_chunk",
                            "content": {"type": "text", "text": "Hello "},
                        }
                    },
                }
            )

            time.sleep(0.1)
            agent._recv_queue.put(
                {
                    "method": "session/update",
                    "params": {
                        "update": {
                            "sessionUpdate": "agent_message_chunk",
                            "content": {"type": "text", "text": "World"},
                        },
                        "stopReason": "stop",
                    },
                }
            )

        threading.Thread(target=put_responses, daemon=True).start()

        async def run():
            chunks = []
            with patch("openclaw_acp.agent.uuid.uuid4", return_value="mock-id"):
                async for chunk in agent.stream("test", timeout=10):
                    chunks.append(chunk)
            return chunks

        result = asyncio.run(run())
        assert result == ["Hello ", "World"]

    def test_stream_raises_on_error(self):
        with patch.dict("os.environ", {"OPENCLAW_GATEWAY_TOKEN": "test_token"}):
            agent = OpenClawAgent(auto_start=False)
            agent._proc = Mock()
            agent._session_id = "test-session"
            agent._lock = threading.Lock()
            agent._recv_queue = Queue()

        def put_error():
            import time

            time.sleep(0.05)
            resp_q = agent._pending.get("mock-id")
            if resp_q:
                resp_q.put({"error": {"message": "test error"}})

        threading.Thread(target=put_error, daemon=True).start()

        async def run():
            with patch("openclaw_acp.agent.uuid.uuid4", return_value="mock-id"):
                async for chunk in agent.stream("test", timeout=10):
                    pass

        with pytest.raises(RuntimeError, match="ACP error"):
            asyncio.run(run())


class TestOpenClawAgentRequiresApiKey:
    @patch.dict(os.environ, {}, clear=True)
    def test_raises_without_token(self):
        with pytest.raises(ValueError, match="API key"):
            OpenClawAgent(auto_start=False)

    def test_accepts_token_in_env(self):
        with patch.dict(os.environ, {"OPENCLAW_GATEWAY_TOKEN": "test_token"}):
            agent = OpenClawAgent(auto_start=False)
            assert agent is not None
