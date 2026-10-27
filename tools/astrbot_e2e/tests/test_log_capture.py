import asyncio
import tempfile
import unittest
from pathlib import Path

from astrbot_e2e.log_capture import LogCapture


class LogCaptureTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "astrbot.log"

    def test_reads_only_new_lines(self):
        self.path.write_text("old\n", encoding="utf-8")
        capture = LogCapture(self.path)
        offset = capture.mark()
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write("new\n")
        self.assertEqual(capture.read_since(offset), "new\n")

    def test_read_since_chinese(self):
        self.path.write_text("中文日志\n", encoding="utf-8")
        capture = LogCapture(self.path)
        offset = capture.mark()
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write("新的中文日志\n")
        self.assertEqual(capture.read_since(offset), "新的中文日志\n")

    async def test_wait_for_needle(self):
        self.path.write_text("", encoding="utf-8")
        capture = LogCapture(self.path)

        async def writer():
            await asyncio.sleep(0.1)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write("[e2e_probe] echo hello\n")

        asyncio.create_task(writer())
        self.assertTrue(await capture.wait_for(["[e2e_probe] echo hello"], timeout=2))

    async def test_wait_for_recovers_after_truncation(self):
        self.path.write_text("old content that will be truncated away\n", encoding="utf-8")
        capture = LogCapture(self.path)

        async def truncate():
            await asyncio.sleep(0.05)
            self.path.write_text("new needle\n", encoding="utf-8")

        task = asyncio.create_task(capture.wait_for(["new needle"], timeout=3))
        await truncate()
        self.assertTrue(await task)

    async def test_wait_for_rejects_empty_needles(self):
        self.path.write_text("", encoding="utf-8")
        capture = LogCapture(self.path)
        with self.assertRaises(ValueError):
            await capture.wait_for([], timeout=1)
