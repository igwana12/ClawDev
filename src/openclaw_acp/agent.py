import asyncio
import json
import os
import subprocess
import threading
import uuid
from queue import Queue, Empty
from typing import AsyncGenerator, Callable, Optional

from .utils import require_api_key


class OpenClawAgent:
    """
    简化使用的 OpenClaw Agent 包装类。

    用法:
        agent = OpenClawAgent()
        response = agent("你的消息")
        # 或
        response = agent.step("你的消息")

    异步用法:
        response = await agent.async_step("你的消息")

    流式用法:
        async for chunk in agent.stream("你的消息"):
            print(chunk, end="")
    """

    @require_api_key("OPENCLAW_GATEWAY_TOKEN")
    def __init__(
        self,
        gateway_url: str = None,
        agent: str = "main",
        cwd: str = "/",
        auto_start: bool = True,
    ):
        self.gateway_url = gateway_url or os.getenv(
            "OPENCLAW_GATEWAY_URL", "ws://127.0.0.1:18789"
        )
        self.agent = agent
        self.cwd = cwd

        self._proc = None
        self._recv_queue = Queue()
        self._pending: dict[str, Queue] = {}
        self._session_id = None
        self._lock = threading.Lock()
        self._started = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

        if auto_start:
            self.start()

    def start(self):
        if self._started:
            return

        cmd = [
            "openclaw",
            "acp",
            "--url",
            self.gateway_url,
            "--session",
            f"agent:{self.agent}:main",
        ]

        env = {
            **os.environ,
            "OPENCLAW_HIDE_BANNER": "1",
            "OPENCLAW_SUPPRESS_NOTES": "1",
            "NODE_TLS_REJECT_UNAUTHORIZED": "0",
        }

        self._proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
        )

        self._thread = threading.Thread(target=self._read_stdout, daemon=True)
        self._thread.start()
        threading.Thread(target=self._read_stderr, daemon=True).start()

        self._initialize()
        self._session_id = self._new_session()
        self._started = True

    def stop(self):
        if not self._started:
            return
        if self._proc:
            try:
                self._proc.stdin.close()
            except Exception:
                pass
            self._proc.terminate()
            self._proc.wait()
            self._proc = None
        self._session_id = None
        self._started = False

    def __call__(self, message: str, timeout: int = 120) -> str:
        return self.step(message, timeout)

    def step(self, message: str, timeout: int = 120) -> str:
        if not self._proc or not self._session_id:
            raise RuntimeError("请先调用 start()")

        req_id = str(uuid.uuid4())
        resp_q: Queue = Queue()

        with self._lock:
            self._pending[req_id] = resp_q

        self._write(
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "method": "session/prompt",
                "params": {
                    "sessionId": self._session_id,
                    "prompt": [{"type": "text", "text": message}],
                },
            }
        )

        try:
            resp = resp_q.get(timeout=timeout)
        except Empty:
            raise TimeoutError(f"等待 session/prompt 响应超时（{timeout}s）")

        if "error" in resp:
            raise RuntimeError(f"[ACP error] {resp['error']}")

        result = resp.get("result", {})
        if result.get("stopReason"):
            if result.get("parts"):
                collected = [
                    p.get("text", "")
                    for p in result["parts"]
                    if p.get("type") == "text"
                ]
                return "".join(collected).strip()
            return result.get("text", "")

        collected = []
        while True:
            try:
                msg = self._recv_queue.get(timeout=timeout)
            except Empty:
                raise TimeoutError(f"等待智能体回复超时（{timeout}s）")

            method = msg.get("method")
            if method == "session/update":
                params = msg.get("params", {})
                for part in params.get("parts", []):
                    if part.get("type") == "text":
                        collected.append(part.get("text", ""))
                if params.get("stopReason"):
                    break
            elif method == "session/error":
                raise RuntimeError(f"[session error] {msg.get('params')}")

        return "".join(collected).strip()

    async def async_step(self, message: str, timeout: int = 120) -> str:
        if self._loop is None:
            self._loop = asyncio.get_event_loop()
        return await asyncio.wait_for(
            self._loop.run_in_executor(None, self.step, message, timeout),
            timeout=timeout,
        )

    async def stream(
        self,
        message: str,
        timeout: int = 120,
        on_chunk: Optional[Callable[[str], None]] = None,
    ) -> AsyncGenerator[str, None]:
        if not self._proc or not self._session_id:
            raise RuntimeError("请先调用 start()")

        if self._loop is None:
            self._loop = asyncio.get_event_loop()

        req_id = str(uuid.uuid4())
        resp_q: Queue = Queue()

        with self._lock:
            self._pending[req_id] = resp_q

        await self._loop.run_in_executor(
            None,
            self._write,
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "method": "session/prompt",
                "params": {
                    "sessionId": self._session_id,
                    "prompt": [{"type": "text", "text": message}],
                },
            },
        )

        try:
            resp = await asyncio.wait_for(resp_q.get(), timeout)
        except Empty:
            raise TimeoutError(f"等待 session/prompt 响应超时（{timeout}s）")

        if "error" in resp:
            raise RuntimeError(f"[ACP error] {resp['error']}")

        result = resp.get("result", {})
        if result.get("stopReason"):
            if result.get("parts"):
                for p in result["parts"]:
                    if p.get("type") == "text":
                        text = p.get("text", "")
                        if on_chunk:
                            on_chunk(text)
                        yield text
            return

        while True:
            try:
                msg = await asyncio.wait_for(self._recv_queue.get(), timeout)
            except Empty:
                raise TimeoutError(f"等待智能体回复超时（{timeout}s）")

            method = msg.get("method")
            if method == "session/update":
                params = msg.get("params", {})
                for part in params.get("parts", []):
                    if part.get("type") == "text":
                        text = part.get("text", "")
                        if on_chunk:
                            on_chunk(text)
                        yield text
                if params.get("stopReason"):
                    break
            elif method == "session/error":
                raise RuntimeError(f"[session error] {msg.get('params')}")

    def _initialize(self, timeout: int = 15):
        req_id = "init-1"
        resp_q: Queue = Queue()
        with self._lock:
            self._pending[req_id] = resp_q

        self._write(
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": 1,
                    "clientCapabilities": {},
                    "clientInfo": {"name": "openclaw-py", "version": "1.0.0"},
                },
            }
        )

        try:
            resp = resp_q.get(timeout=timeout)
        except Empty:
            raise TimeoutError("initialize 握手超时")

        if "error" in resp:
            raise RuntimeError(f"initialize 失败: {resp['error']}")

    def _new_session(self, timeout: int = 30) -> str:
        req_id = "sess-1"
        resp_q: Queue = Queue()
        with self._lock:
            self._pending[req_id] = resp_q

        self._write(
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "method": "session/new",
                "params": {"cwd": self.cwd, "mcpServers": []},
            }
        )

        try:
            resp = resp_q.get(timeout=timeout)
        except Empty:
            raise TimeoutError("session/new 超时")

        if "error" in resp:
            raise RuntimeError(f"session/new 失败: {resp['error']}")

        session_id = resp.get("result", {}).get("sessionId")
        if not session_id:
            raise RuntimeError("session/new 未返回 sessionId")
        return session_id

    def _write(self, obj: dict):
        line = json.dumps(obj, ensure_ascii=False) + "\n"
        self._proc.stdin.write(line)
        self._proc.stdin.flush()

    def _read_stdout(self):
        for raw in self._proc.stdout:
            raw = raw.strip()
            if not raw:
                continue
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_id = msg.get("id")
            if msg_id is not None:
                with self._lock:
                    q = self._pending.pop(msg_id, None)
                if q:
                    q.put(msg)
            else:
                self._recv_queue.put(msg)

    def _read_stderr(self):
        for line in self._proc.stderr:
            line = line.strip()
            if line:
                print(f"[ACP stderr] {line}")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    def __del__(self):
        if hasattr(self, "_started"):
            self.stop()
