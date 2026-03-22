# Copyright 2024 HDAnzz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
OpenClaw ACP (Agent Client Protocol) Client

提供与 OpenClaw Gateway 通信的 Python 包装类，支持同步、异步和流式响应。
"""

import asyncio
import hashlib
import json
import logging
import os
import subprocess
import threading
import time
import uuid
from queue import Empty, Queue
from typing import AsyncGenerator, Generator, Optional

logger = logging.getLogger(__name__)

from .utils import require_api_key


class OpenClawAgent:
    """
    简化使用的 OpenClaw Agent 包装类。

    通过 ACP 协议与 OpenClaw Gateway 通信，支持：
    - 同步调用
    - 异步调用
    - 流式响应

    Args:
        gateway_url: Gateway WebSocket URL（默认：ws://127.0.0.1:18789）
        agent: Agent 名称（默认：main）
        cwd: 工作目录（默认：~/.openclaw/workspace-<agent-name>）
        auto_start: 是否自动启动（默认：True）

    Attributes:
        agent: Agent 名称
        gateway_url: Gateway URL
        cwd: 工作目录

    Example:
        # 同步用法
        agent = OpenClawAgent(agent="programmer-a")
        response = agent.step("你的消息")

        # 异步用法
        response = await agent.astep("你的消息")

        # 流式用法
        async for chunk in agent.stream("你的消息"):
            print(chunk, end="", flush=True)

        # 上下文管理器
        with OpenClawAgent() as agent:
            response = agent.step("你好")
    """

    @require_api_key("OPENCLAW_GATEWAY_TOKEN")
    def __init__(
        self,
        gateway_url: Optional[str] = None,
        agent: Optional[str] = None,
        cwd: Optional[str] = None,
        auto_start: bool = True,
    ):
        """
        初始化 OpenClaw Agent。

        Args:
            gateway_url: Gateway WebSocket URL
            agent: Agent 名称
            cwd: 工作目录
            auto_start: 是否自动启动
        """
        self.gateway_url = (
            gateway_url or os.getenv("OPENCLAW_GATEWAY_URL") or "ws://127.0.0.1:18789"
        )
        self.agent = agent or "main"
        self.cwd = cwd or "/workspace"
        self._session_suffix = hashlib.sha256(self.agent.encode()).hexdigest()[:12]

        self._proc: Optional[subprocess.Popen] = None
        self._recv_queue: Queue = Queue()
        self._pending: dict[str, Queue] = {}
        self._session_id: Optional[str] = None
        self._lock: threading.Lock = threading.Lock()
        self._pending_lock: threading.Lock = threading.Lock()
        self._started: bool = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

        if auto_start:
            self.start()

    def start(self) -> None:
        """
        启动 Agent 并创建会话。

        执行以下步骤：
        1. 启动 openclaw acp 子进程
        2. 启动 stdout/stderr 读取线程
        3. 发送 initialize 握手
        4. 创建新会话

        Raises:
            TimeoutError: 握手或会话创建超时
            RuntimeError: 初始化失败
        """
        with self._lock:
            if self._started:
                return

            logger.debug("Starting OpenClawAgent: %s", self.agent)
            cmd = [
                "openclaw",
                "acp",
                "--url",
                self.gateway_url,
                "--session",
                f"agent:{self.agent}:{self._session_suffix}",
                "--reset-session",
            ]
            logger.debug("Running command: %s", " ".join(cmd))

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

    def stop(self) -> None:
        """
        停止 Agent 并关闭子进程。

        关闭 stdin，终止子进程，清除会话 ID。
        """
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
        """
        使用调用语法发送消息。

        Args:
            message: 发送的消息
            timeout: 超时时间（秒）

        Returns:
            Agent 响应文本
        """
        return self.step(message, timeout)

    def step(self, message: str, timeout: int = 120) -> str:
        """
        发送消息并等待完整响应。

        Args:
            message: 发送的消息
            timeout: 超时时间（秒）

        Returns:
            Agent 响应文本

        Raises:
            RuntimeError: Agent 未启动或发生错误
            TimeoutError: 等待响应超时
        """
        if not self._proc or not self._session_id:
            raise RuntimeError("请先调用 start()")

        req_id = str(uuid.uuid4())
        resp_q: Queue = Queue()

        with self._pending_lock:
            self._pending[req_id] = resp_q

        logger.debug("[%s] step() sending prompt, message=%r", req_id, message[:100])
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

        resp = None
        collected = []
        deadline = time.time() + timeout

        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                logger.error("[%s] step() timeout after %ds", req_id, timeout)
                raise TimeoutError(f"等待 session/prompt 响应超时（{timeout}s）")

            if resp is None:
                try:
                    resp = resp_q.get(timeout=min(remaining, 0.5))
                    logger.debug("[%s] step() received response", req_id)
                except Empty:
                    continue

            try:
                msg = self._recv_queue.get(timeout=min(remaining, 0.5))
            except Empty:
                if resp is not None:
                    break
                continue

            method = msg.get("method")
            if method == "session/update":
                params = msg.get("params", {})
                update = params.get("update", {})
                if update.get("sessionUpdate") == "agent_message_chunk":
                    content = update.get("content", {})
                    if content.get("type") == "text":
                        collected.append(content.get("text", ""))
                for part in params.get("parts", []):
                    if part.get("type") == "text":
                        collected.append(part.get("text", ""))
            elif method == "session/error":
                raise RuntimeError(f"[session error] {msg.get('params')}")

        if "error" in resp:
            raise RuntimeError(f"[ACP error] {resp['error']}")

        result = resp.get("result", {})
        if not collected and result.get("parts"):
            collected = [
                p.get("text", "") for p in result["parts"] if p.get("type") == "text"
            ]

        return "".join(collected).strip()

    async def astep(self, message: str, timeout: int = 120) -> str:
        """
        异步发送消息并等待响应。

        Args:
            message: 发送的消息
            timeout: 超时时间（秒）

        Returns:
            Agent 响应文本
        """
        loop = asyncio.get_event_loop()
        return await asyncio.wait_for(
            loop.run_in_executor(None, self.step, message, timeout),
            timeout=timeout,
        )

    def stream(self, message: str, timeout: int = 120) -> AsyncGenerator[str, None]:
        """
        流式发送消息，逐块返回响应。

        Args:
            message: 发送的消息
            timeout: 超时时间（秒）

        Yields:
            响应文本片段

        Example:
            async for chunk in agent.stream("你好"):
                print(chunk, end="", flush=True)
        """

        async def _stream():
            loop = asyncio.get_event_loop()
            q: asyncio.Queue = asyncio.Queue()

            def _collector():
                try:
                    for chunk in self._stream_internal(message, timeout):
                        asyncio.run_coroutine_threadsafe(q.put(chunk), loop)
                    asyncio.run_coroutine_threadsafe(q.put(None), loop)
                except Exception as e:
                    asyncio.run_coroutine_threadsafe(q.put(e), loop)

            threading.Thread(target=_collector, daemon=True).start()

            while True:
                item = await q.get()
                if item is None:
                    break
                if isinstance(item, Exception):
                    raise item
                yield item

        return _stream()

    def _stream_internal(
        self, message: str, timeout: int = 120
    ) -> Generator[str, None, None]:
        if not self._proc or not self._session_id:
            raise RuntimeError("请先调用 start()")

        req_id = str(uuid.uuid4())
        resp_q: Queue = Queue()

        with self._pending_lock:
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
            logger.debug(
                "[%s] _stream_internal() received final response, stopReason=%s",
                req_id,
                resp.get("result", {}).get("stopReason"),
            )
        except Empty:
            raise TimeoutError(f"等待 session/prompt 响应超时（{timeout}s）")

        if "error" in resp:
            raise RuntimeError(f"[ACP error] {resp['error']}")

        logger.debug(
            "[%s] _stream_internal() draining recv_queue, size≈%d",
            req_id,
            self._recv_queue.qsize(),
        )
        while True:
            try:
                msg = self._recv_queue.get(timeout=0.1)
                logger.debug(
                    "[%s] _stream_internal() drained msg method=%s update=%s",
                    req_id,
                    msg.get("method"),
                    msg.get("params", {}).get("update", {}).get("sessionUpdate"),
                )
                method = msg.get("method")
                if method == "session/update":
                    params = msg.get("params", {})
                    update = params.get("update", {})
                    if update.get("sessionUpdate") == "agent_message_chunk":
                        content = update.get("content", {})
                        if content.get("type") == "text":
                            yield content.get("text", "")
                    for part in params.get("parts", []):
                        if part.get("type") == "text":
                            yield part.get("text", "")
                    if params.get("stopReason"):
                        break
                elif method == "session/error":
                    raise RuntimeError(f"[session error] {msg.get('params')}")
            except Empty:
                logger.debug("[%s] _stream_internal() drain done", req_id)
                break

    def _initialize(self, timeout: int = 60) -> None:
        """
        发送 ACP 初始化握手。

        Args:
            timeout: 超时时间

        Raises:
            TimeoutError: 握手超时
            RuntimeError: 握手失败
        """
        req_id = "init-1"
        resp_q: Queue = Queue()
        with self._pending_lock:
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
        """
        创建新会话。

        Args:
            timeout: 超时时间

        Returns:
            会话 ID

        Raises:
            TimeoutError: 会话创建超时
            RuntimeError: 会话创建失败
        """
        req_id = "sess-1"
        resp_q: Queue = Queue()
        with self._pending_lock:
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

        flushed = 0
        while True:
            try:
                self._recv_queue.get_nowait()
                flushed += 1
            except Empty:
                break
        logger.debug("_new_session() flushed %d leftover notifications", flushed)
        return session_id

    def _write(self, obj: dict) -> None:
        """向子进程 stdin 写入 JSON-RPC 消息。"""
        line = json.dumps(obj, ensure_ascii=False) + "\n"
        logger.debug(
            ">>> SEND id=%s method=%s body=%s",
            obj.get("id"),
            obj.get("method"),
            json.dumps(obj, ensure_ascii=False),
        )
        self._proc.stdin.write(line)
        self._proc.stdin.flush()

    def _read_stdout(self) -> None:
        """读取子进程 stdout，处理 JSON-RPC 响应和通知。"""
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
                logger.debug(
                    "<<< RECV id=%s body=%s",
                    msg_id,
                    json.dumps(msg, ensure_ascii=False),
                )
                with self._pending_lock:
                    q = self._pending.pop(msg_id, None)
                if q:
                    q.put(msg)
            else:
                method = msg.get("method", "unknown")
                logger.debug(
                    "<<< RECV method=%s body=%s",
                    method,
                    json.dumps(msg, ensure_ascii=False),
                )
                self._recv_queue.put(msg)

    def _read_stderr(self) -> None:
        """读取子进程 stderr，记录日志。"""
        for line in self._proc.stderr:
            line = line.strip()
            if line:
                print(f"[ACP stderr] {line}")

    def __enter__(self) -> "OpenClawAgent":
        """上下文管理器入口，自动启动 Agent。"""
        self.start()
        return self

    def __exit__(self, *_: None) -> None:
        """上下文管理器出口，自动停止 Agent。"""
        self.stop()

    def __del__(self) -> None:
        """析构时自动停止 Agent。"""
        if hasattr(self, "_started"):
            self.stop()
