"""异步 CLI 子进程与取消（Async CLI Process）。"""

from __future__ import annotations

import asyncio
from collections import deque
from contextlib import suppress
from pathlib import Path
from typing import AsyncIterator

from ..constants import (
    DEFAULT_AGENT_TIMEOUT_SECONDS,
    MAX_AGENT_OUTPUT_LINE_BYTES,
    NO_WORK_DIR_REPLY,
    PROCESS_TERMINATE_GRACE_SECONDS,
    STDERR_TAIL_LINES,
)


class AgentProcessError(Exception):
    """只暴露可安全展示的失败类型，不携带可能含密钥的原始 stderr。"""


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
    ) -> AsyncIterator[str]:
        """通过标准输入传递用户消息，逐行读取标准输出。"""
        if conversation_key in self._active:
            raise AgentProcessError("当前会话已有代理进程在运行")
        if not Path(work_dir).is_dir():
            raise AgentProcessError(NO_WORK_DIR_REPLY)

        try:
            process = await asyncio.create_subprocess_exec(
                command,
                *args,
                cwd=work_dir,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
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
            process.stdin.write((prompt + "\n").encode("utf-8"))
            await process.stdin.drain()
            process.stdin.close()

            while True:
                try:
                    line = await asyncio.wait_for(
                        process.stdout.readline(), timeout=DEFAULT_AGENT_TIMEOUT_SECONDS
                    )
                except asyncio.TimeoutError as exc:
                    raise AgentProcessError("代理长时间没有输出，已中断") from exc
                if not line:
                    break
                yield line.decode("utf-8", errors="replace").rstrip("\r\n")

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
