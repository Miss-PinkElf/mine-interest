"""媒体任务队列（Media Job Queue）行为测试。"""

from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from sourcehub.media_jobs import MediaJobQueue


class MediaJobQueueTests(unittest.IsolatedAsyncioTestCase):
    async def test_duplicate_job_runs_once_and_marks_done(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        queue = MediaJobQueue(Path(temp.name), concurrency=1)
        calls = []

        self.assertTrue(queue.enqueue("qq:session:1", "content.0", "https://example.test/a.jpg"))
        self.assertFalse(queue.enqueue("qq:session:1", "content.0", "https://example.test/a.jpg"))

        async def worker(job):
            calls.append(job.key)

        await queue.drain(worker)
        self.assertEqual(len(calls), 1)
        self.assertEqual(queue.pending(), [])


if __name__ == "__main__":
    unittest.main()
