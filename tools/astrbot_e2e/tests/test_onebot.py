import asyncio
import json
import unittest

import aiohttp
from aiohttp import web
from aiohttp.test_utils import TestServer

from astrbot_e2e.onebot import (
    OneBotClient,
    OneBotError,
    build_group_message,
    extract_text,
    history_bot_replies,
    is_bot_reply,
    is_history_bot_message,
)


async def _ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for message in ws:
        data = json.loads(message.data)
        await ws.send_json({
            "status": "ok",
            "retcode": 0,
            "data": {"user_id": 10001},
            "echo": data["echo"],
        })
    return ws


async def _ws_fail_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for message in ws:
        data = json.loads(message.data)
        await ws.send_json({
            "status": "failed",
            "retcode": 1200,
            "data": None,
            "echo": data["echo"],
        })
    return ws


async def _ws_bad_frame_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    await ws.send_str("not-json")
    async for message in ws:
        data = json.loads(message.data)
        await ws.send_json({
            "status": "ok",
            "retcode": 0,
            "data": {"user_id": 10001},
            "echo": data["echo"],
        })
    return ws


class _BrokenReaderClient(OneBotClient):
    """模拟 reader 任务异常退出，用于验证 close() 仍能完成清理。"""

    async def _read_loop(self) -> None:
        raise ValueError("模拟 reader 异常退出")


class _FakeHistoryClient:
    def __init__(self, messages):
        self.messages = messages
        self.calls = []

    async def call(self, action, params):
        self.calls.append((action, params))
        return {"messages": self.messages}


class OneBotPureTest(unittest.TestCase):
    def test_build_group_message(self):
        self.assertEqual(
            build_group_message("/help", "10001"),
            [
                {"type": "at", "data": {"qq": "10001"}},
                {"type": "text", "data": {"text": " /help"}},
            ],
        )

    def test_extract_text(self):
        event = {"message": [{"type": "text", "data": {"text": "hello"}}, {"type": "at", "data": {"qq": "1"}}]}
        self.assertEqual(extract_text(event), "hello")

    def test_extract_text_accepts_cq_string(self):
        event = {"message": "hello [CQ:at,qq=1]"}
        self.assertEqual(extract_text(event), "hello [CQ:at,qq=1]")

    def test_is_bot_reply(self):
        event = {"post_type": "message_sent", "group_id": 1, "user_id": 10001, "self_id": 10001, "message": []}
        self.assertTrue(is_bot_reply(event, "10001", "1"))
        self.assertFalse(is_bot_reply(event, "10002", "1"))
        self.assertFalse(is_bot_reply(event, "10001", "2"))

    def test_is_history_bot_message(self):
        event = {"group_id": 1, "sender": {"user_id": 10001}, "message": []}
        self.assertTrue(is_history_bot_message(event, "10001", "1"))
        self.assertFalse(is_history_bot_message(event, "10002", "1"))


class OneBotClientTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        app = web.Application()
        app.router.add_get("/onebot/v11/ws", _ws_handler)
        app.router.add_get("/onebot/v11/ws-fail", _ws_fail_handler)
        app.router.add_get("/onebot/v11/ws-bad-frame", _ws_bad_frame_handler)
        self.server = TestServer(app)
        await self.server.start_server()

    async def asyncTearDown(self):
        await self.server.close()

    async def test_call_returns_data(self):
        url = str(self.server.make_url("/onebot/v11/ws"))
        async with OneBotClient(url, token="") as client:
            data = await client.call("get_login_info", {})
            self.assertEqual(data["user_id"], 10001)

    async def test_call_raises_on_failed_response(self):
        url = str(self.server.make_url("/onebot/v11/ws-fail"))
        async with OneBotClient(url, token="") as client:
            with self.assertRaises(OneBotError):
                await client.call("send_msg", {})

    async def test_ignores_non_json_frame(self):
        url = str(self.server.make_url("/onebot/v11/ws-bad-frame"))
        async with OneBotClient(url, token="") as client:
            data = await client.call("get_login_info", {})
            self.assertEqual(data["user_id"], 10001)

    async def test_close_fails_pending_call(self):
        received = asyncio.Event()

        async def silent_handler(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            async for _ in ws:
                received.set()
            return ws

        app = web.Application()
        app.router.add_get("/onebot/v11/ws", silent_handler)
        server = TestServer(app)
        await server.start_server()
        self.addAsyncCleanup(server.close)
        client = OneBotClient(str(server.make_url("/onebot/v11/ws")), token="", timeout=5.0)
        self.addAsyncCleanup(client.close)
        await client.connect()
        started = asyncio.get_running_loop().time()
        call_task = asyncio.create_task(client.call("send_msg", {}))
        await asyncio.wait_for(received.wait(), timeout=2)
        await client.close()
        with self.assertRaises(OneBotError):
            await call_task
        self.assertLess(asyncio.get_running_loop().time() - started, 4.0)

    async def test_close_survives_reader_crash(self):
        url = str(self.server.make_url("/onebot/v11/ws"))
        client = _BrokenReaderClient(url, token="")
        await client.connect()
        await asyncio.sleep(0.05)
        assert client._reader is not None
        self.assertTrue(client._reader.done())
        self.assertIsNotNone(client._reader.exception())
        await client.close()
        assert client.ws is not None
        assert client.session is not None
        self.assertTrue(client.ws.closed)
        self.assertTrue(client.session.closed)

    async def test_connect_failure_closes_session(self):
        client = OneBotClient("http://127.0.0.1:1/onebot/v11/ws", token="")
        with self.assertRaises(aiohttp.ClientError):
            await client.connect()
        assert client.session is not None
        self.assertTrue(client.session.closed)
        await client.close()


class OneBotHistoryTest(unittest.IsolatedAsyncioTestCase):
    async def test_history_since_time_filters_old_messages(self):
        client = _FakeHistoryClient([
            {
                "group_id": 1,
                "sender": {"user_id": 10001},
                "message": [{"type": "text", "data": {"text": "old"}}],
                "time": 100,
            },
            {
                "group_id": 1,
                "sender": {"user_id": 10001},
                "message": [{"type": "text", "data": {"text": "new"}}],
                "time": 200,
            },
            {
                "group_id": 1,
                "sender": {"user_id": 10001},
                "message": [{"type": "text", "data": {"text": "untimed"}}],
            },
        ])
        replies = await history_bot_replies(client, "10001", "1", since_time=150)
        self.assertEqual([item["text"] for item in replies], ["new"])

    async def test_history_invalid_group_id(self):
        client = _FakeHistoryClient([])
        with self.assertRaises(OneBotError):
            await history_bot_replies(client, "10001", "not-a-number")
        self.assertEqual(client.calls, [])
