"""媒体任务队列（Media Job Queue）：用持久状态控制后台下载并发。"""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Awaitable, Callable

from .vault import atomic_write

MEDIA_JOBS_FILE = "media_jobs.json"
JOB_STATUS_QUEUED = "queued"
JOB_STATUS_DONE = "done"
JOB_STATUS_FAILED = "failed"


@dataclass
class MediaJob:
    item_id: str
    node_path: str
    url: str
    status: str = JOB_STATUS_QUEUED

    @property
    def key(self) -> str:
        return "|".join((self.item_id, self.node_path, self.url))


class MediaJobQueue:
    """只允许一个 drain 运行；状态先落盘，因此进程重启可继续处理。"""

    def __init__(self, spool_root: Path, concurrency: int = 2):
        self.path = spool_root / MEDIA_JOBS_FILE
        self.concurrency = concurrency
        self._jobs = self._load()

    def enqueue(self, item_id: str, node_path: str, url: str) -> bool:
        job = MediaJob(item_id=item_id, node_path=node_path, url=url)
        if any(existing.key == job.key for existing in self._jobs):
            return False
        self._jobs.append(job)
        self._save()
        return True

    def pending(self) -> list[MediaJob]:
        return [job for job in self._jobs if job.status == JOB_STATUS_QUEUED]

    async def drain(self, worker: Callable[[MediaJob], Awaitable[None]]) -> None:
        semaphore = asyncio.Semaphore(self.concurrency)

        async def run(job: MediaJob) -> None:
            async with semaphore:
                try:
                    await worker(job)
                    job.status = JOB_STATUS_DONE
                except Exception:
                    job.status = JOB_STATUS_FAILED
                finally:
                    self._save()

        await asyncio.gather(*(run(job) for job in self.pending()))

    def _load(self) -> list[MediaJob]:
        if not self.path.exists():
            return []
        return [MediaJob(**item) for item in json.loads(self.path.read_text(encoding="utf-8"))]

    def _save(self) -> None:
        atomic_write(
            self.path,
            json.dumps([asdict(job) for job in self._jobs], ensure_ascii=False, indent=2).encode("utf-8"),
        )
