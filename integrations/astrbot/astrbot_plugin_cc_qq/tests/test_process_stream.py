"""代理 stdout 的超长行不得中断整个执行（Regression: ValueError）。"""

import asyncio
import unittest

from astrbot_plugin_cc_qq.agents.process import iter_stdout_lines


class _FakeStream:
    """按预置分块返回数据，模拟 asyncio.StreamReader.read。"""

    def __init__(self, chunks):
        self._chunks = list(chunks)

    async def read(self, size):
        await asyncio.sleep(0)
        return self._chunks.pop(0) if self._chunks else b""


class _SlowStream:
    async def read(self, size):
        await asyncio.sleep(1)
        return b""


async def _collect(stream, max_line_bytes=1024, timeout=5):
    return [
        line
        async for line in iter_stdout_lines(stream, max_line_bytes, timeout)
    ]


class IterStdoutLinesTest(unittest.IsolatedAsyncioTestCase):
    async def test_splits_lines_and_strips_crlf(self):
        stream = _FakeStream([b'{"a":1}\r\n{"b":2}\n'])
        self.assertEqual(await _collect(stream), ['{"a":1}', '{"b":2}'])

    async def test_oversized_line_dropped_and_following_line_kept(self):
        stream = _FakeStream(
            [b"x" * 2048 + b"\n", b'{"type":"result","result":"ok"}\n']
        )
        self.assertEqual(
            await _collect(stream), ['{"type":"result","result":"ok"}']
        )

    async def test_oversized_line_split_across_chunks(self):
        # 第一块超上限且没有换行，第二块才出现该行结尾；随后是正常结果行。
        stream = _FakeStream(
            [b"x" * 1500, b"y" * 1500 + b"\n", b'ok\n']
        )
        self.assertEqual(await _collect(stream), ["ok"])

    async def test_eof_tail_without_newline_is_yielded(self):
        stream = _FakeStream([b'{"a":1}'])
        self.assertEqual(await _collect(stream), ['{"a":1}'])

    async def test_read_timeout_propagates(self):
        with self.assertRaises(asyncio.TimeoutError):
            await _collect(_SlowStream(), timeout=0.01)
