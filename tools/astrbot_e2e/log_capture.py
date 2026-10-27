"""按文件偏移采集日志窗口（Log Capture）。"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Iterable


class LogCapture:
    def __init__(self, path):
        self.path = Path(path)

    def mark(self) -> int:
        return self.path.stat().st_size if self.path.exists() else 0

    def read_since(self, offset: int) -> str:
        if not self.path.exists():
            return ""
        with self.path.open("rb") as handle:
            handle.seek(offset)
            return handle.read().decode("utf-8", errors="replace")

    async def wait_for(self, needles: Iterable[str], timeout: float, interval: float = 0.5) -> bool:
        wants = [str(item) for item in needles]
        if not wants:
            raise ValueError("needles 不能为空")
        deadline = time.monotonic() + timeout
        offset = self.mark()
        buffer = ""
        while True:
            if self.path.exists():
                size = self.path.stat().st_size
                if size < offset:
                    offset = 0
                    buffer = ""
                with self.path.open("rb") as handle:
                    handle.seek(offset)
                    raw = handle.read()
                if raw:
                    offset += len(raw)
                    buffer += raw.decode("utf-8", errors="replace")
            if all(item in buffer for item in wants):
                return True
            if time.monotonic() >= deadline:
                return False
            await asyncio.sleep(interval)
