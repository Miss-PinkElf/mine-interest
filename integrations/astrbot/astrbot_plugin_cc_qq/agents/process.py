"""异步 CLI 子进程与取消（Async CLI Process）。"""

from __future__ import annotations

import asyncio
import logging
import os
from collections import deque
from contextlib import suppress
from pathlib import Path
from typing import AsyncIterator

from ..constants import (
    DEFAULT_AGENT_TIMEOUT_SECONDS,
    LOG_PREFIX,
    MAX_AGENT_OUTPUT_LINE_BYTES,
    NO_WORK_DIR_REPLY,
    PROCESS_TERMINATE_GRACE_SECONDS,
    STDERR_LOG_LINE_CHARS,
    STDERR_LOG_LINE_COUNT,
    STDERR_TAIL_LINES,
    STDOUT_READ_CHUNK_BYTES,
)

logger = logging.getLogger("astrbot_plugin_cc_qq.agents.process")


class AgentProcessError(Exception):
    """只暴露可安全展示的失败类型，不携带可能含密钥的原始 stderr。"""


async def deliver_prompt(stdin, prompt: str, process) -> None:
    """把用户文本写入标准输入。对端已关闭时转成代理错误。"""
    try:
        stdin.write((prompt + "\n").encode("utf-8"))
        await stdin.drain()
        stdin.close()
    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError) as exc:
        code = process.returncode
        if code is None:
            with suppress(asyncio.TimeoutError):
                await asyncio.wait_for(process.wait(), timeout=PROCESS_TERMINATE_GRACE_SECONDS)
            code = process.returncode
        shown = "未知" if code is None else str(code)
        raise AgentProcessError(f"代理进程在接收消息前退出，退出码 {shown}") from exc


def _log_dropped_line(total_bytes: int) -> None:
    logger.warning("%s 丢弃超长代理输出行：%s 字节", LOG_PREFIX, total_bytes)


async def iter_stdout_lines(
    stream: asyncio.StreamReader, max_line_bytes: int, read_timeout_seconds: int
) -> AsyncIterator[str]:
    """分块读取 stdout 并按换行切分。

    asyncio 的 StreamReader.readline() 在单行超过 limit 时会抛 ValueError；
    Claude 的 stream-json 会把图片 base64 等工具结果作为单行输出，
    因此改为分块读取：超限行整行丢弃并告警，不影响后续事件与本轮执行。
    """
    buffer = bytearray()
    discarding = False
    dropped_bytes = 0
    while True:
        chunk = await asyncio.wait_for(
            stream.read(STDOUT_READ_CHUNK_BYTES), timeout=read_timeout_seconds
        )
        if not chunk:
            break
        buffer.extend(chunk)
        start = 0
        while True:
            index = buffer.find(b"\n", start)
            if index < 0:
                break
            line = bytes(buffer[start:index])
            start = index + 1
            if discarding:
                _log_dropped_line(dropped_bytes + len(line))
                discarding = False
                dropped_bytes = 0
                continue
            if len(line) > max_line_bytes:
                _log_dropped_line(len(line))
                continue
            yield line.decode("utf-8", errors="replace").rstrip("\r")
        if start:
            del buffer[:start]
        if discarding:
            dropped_bytes += len(buffer)
            buffer.clear()
        elif len(buffer) > max_line_bytes:
            discarding = True
            dropped_bytes = len(buffer)
            buffer.clear()
    if discarding:
        _log_dropped_line(dropped_bytes)
    elif buffer:
        if len(buffer) > max_line_bytes:
            _log_dropped_line(len(buffer))
        else:
            yield bytes(buffer).decode("utf-8", errors="replace").rstrip("\r")


def _stderr_for_log(tail: deque[str]) -> str:
    lines = list(tail)[-STDERR_LOG_LINE_COUNT:]
    clipped = [line[:STDERR_LOG_LINE_CHARS] for line in lines]
    return " | ".join(clipped) if clipped else "无"


class ProcessRunner:
    def __init__(self):
        self._active: dict[str, asyncio.subprocess.Process] = {}

    async def run(
        self,
        conversation_key: str,
        command: str,
        args: list[str],
        work_dir: str,
        prompt: str,
        env: dict | None = None,
    ) -> AsyncIterator[str]:
        """通过标准输入传递用户消息，逐行读取标准输出。"""
        if conversation_key in self._active:
            raise AgentProcessError("当前会话已有代理进程在运行")
        if not Path(work_dir).is_dir():
            raise AgentProcessError(NO_WORK_DIR_REPLY)

        process_env = {**os.environ, **env} if env else None
        try:
            process = await asyncio.create_subprocess_exec(
                command,
                *args,
                cwd=work_dir,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=process_env,
                limit=MAX_AGENT_OUTPUT_LINE_BYTES,
            )
        except FileNotFoundError as exc:
            raise AgentProcessError("代理命令未安装或不可访问") from exc
        except OSError as exc:
            raise AgentProcessError("代理进程启动失败") from exc

        self._active[conversation_key] = process
        stderr_tail: deque[str] = deque(maxlen=STDERR_TAIL_LINES)
        stderr_task = asyncio.create_task(self._read_stderr(process, stderr_tail))
        try:
            assert process.stdin is not None
            assert process.stdout is not None
            try:
                await deliver_prompt(process.stdin, prompt, process)
            except AgentProcessError:
                logger.error(
                    "%s 代理标准输入已关闭，stderr 尾部：%s",
                    LOG_PREFIX,
                    _stderr_for_log(stderr_tail),
                )
                raise

            try:
                async for line in iter_stdout_lines(
                    process.stdout,
                    MAX_AGENT_OUTPUT_LINE_BYTES,
                    DEFAULT_AGENT_TIMEOUT_SECONDS,
                ):
                    yield line
            except asyncio.TimeoutError as exc:
                raise AgentProcessError("代理长时间没有输出，已中断") from exc

            return_code = await process.wait()
            if return_code:
                raise AgentProcessError(f"代理进程异常退出，退出码 {return_code}")
        finally:
            if process.returncode is None:
                await self._terminate(process)
            stderr_task.cancel()
            with suppress(asyncio.CancelledError):
                await stderr_task
            self._active.pop(conversation_key, None)

    async def interrupt(self, conversation_key: str) -> bool:
        process = self._active.get(conversation_key)
        if process is None or process.returncode is not None:
            return False
        await self._terminate(process)
        return True

    async def shutdown(self) -> None:
        await asyncio.gather(*(self._terminate(process) for process in tuple(self._active.values())))
        self._active.clear()

    @staticmethod
    async def _read_stderr(process: asyncio.subprocess.Process, tail: deque[str]) -> None:
        assert process.stderr is not None
        while True:
            line = await process.stderr.readline()
            if not line:
                return
            tail.append(line.decode("utf-8", errors="replace").rstrip("\r\n"))

    @staticmethod
    async def _terminate(process: asyncio.subprocess.Process) -> None:
        if process.returncode is not None:
            return
        with suppress(ProcessLookupError):
            process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=PROCESS_TERMINATE_GRACE_SECONDS)
        except asyncio.TimeoutError:
            with suppress(ProcessLookupError):
                process.kill()
            await process.wait()
