"""OneBot v11 消息构造、事件过滤与 WebSocket 客户端。"""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional

import aiohttp


class OneBotError(RuntimeError):
    """OneBot 调用失败或连接异常。"""


def build_group_message(
    text: str,
    at_qq: str,
    image: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """构造群消息；支持引用（reply）、@ 与图片（image 为文件路径或 URL）。"""
    message: List[Dict[str, Any]] = []
    if reply_to:
        message.append({"type": "reply", "data": {"id": str(reply_to)}})
    message.append({"type": "at", "data": {"qq": str(at_qq)}})
    if str(text or "").strip():
        message.append({"type": "text", "data": {"text": " " + str(text)}})
    if image:
        message.append({"type": "image", "data": {"file": str(image)}})
    return message


def count_images(event: Dict[str, Any]) -> int:
    """统计消息中的图片段数量，用于长图与图片输出断言。"""
    message = event.get("message")
    if not isinstance(message, list):
        return 0
    return sum(1 for segment in message if segment.get("type") == "image")


def extract_text(event: Dict[str, Any]) -> str:
    message = event.get("message")
    if not isinstance(message, list):
        # CQ 码字符串等非分段格式无法按段提取，直接按原文返回。
        return str(message).strip() if message else ""
    parts = []
    for segment in message:
        if segment.get("type") == "text":
            parts.append(str(segment.get("data", {}).get("text", "")))
    return "".join(parts).strip()


def is_bot_reply(event: Dict[str, Any], bot_qq: str, group_id: str) -> bool:
    if event.get("post_type") not in ("message", "message_sent"):
        return False
    if str(event.get("group_id")) != str(group_id):
        return False
    user_id = event.get("user_id")
    if user_id is None:
        user_id = (event.get("sender") or {}).get("user_id")
    if str(user_id) != str(bot_qq):
        return False
    if event.get("post_type") == "message" and str(event.get("self_id")) != str(bot_qq):
        return False
    return True


def is_history_bot_message(event: Dict[str, Any], bot_qq: str, group_id: str) -> bool:
    """群消息历史里的机器人消息没有稳定的 post_type，按 sender 判断。"""
    if str(event.get("group_id")) != str(group_id):
        return False
    sender = event.get("sender") or {}
    user_id = sender.get("user_id") or event.get("user_id")
    return str(user_id) == str(bot_qq)


class OneBotClient:
    def __init__(self, ws_url: str, token: str, timeout: float = 30.0):
        self.ws_url = ws_url
        self.token = token or ""
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._reader: Optional[asyncio.Task] = None
        self._pending: Dict[str, asyncio.Future] = {}
        self._events: asyncio.Queue = asyncio.Queue()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def connect(self) -> None:
        self.session = aiohttp.ClientSession()
        headers = {"Authorization": "Bearer {}".format(self.token)} if self.token else {}
        try:
            self.ws = await self.session.ws_connect(self.ws_url, headers=headers, heartbeat=30)
        except Exception:
            # 连接失败时关闭 session，避免句柄泄漏。
            await self.session.close()
            raise
        self._reader = asyncio.create_task(self._read_loop())

    async def close(self) -> None:
        if self._reader:
            self._reader.cancel()
            try:
                await self._reader
            except (asyncio.CancelledError, Exception):
                pass
            self._reader = None
        self._fail_pending("连接已关闭")
        if self.ws and not self.ws.closed:
            await self.ws.close()
        if self.session:
            await self.session.close()

    def _fail_pending(self, message: str) -> None:
        pending = self._pending
        self._pending = {}
        for future in pending.values():
            if not future.done():
                future.set_exception(OneBotError(message))

    async def _read_loop(self) -> None:
        assert self.ws is not None
        try:
            async for message in self.ws:
                if message.type == aiohttp.WSMsgType.TEXT:
                    try:
                        payload = json.loads(message.data)
                    except (json.JSONDecodeError, ValueError):
                        # 非 JSON 帧不应毒化 reader，直接忽略。
                        continue
                    if not isinstance(payload, dict):
                        continue
                    echo = payload.get("echo")
                    if echo:
                        future = self._pending.pop(echo, None)
                        if future and not future.done():
                            future.set_result(payload)
                        # 带 echo 但没有匹配 pending 的响应直接丢弃，不进事件队列。
                        continue
                    await self._events.put(payload)
                elif message.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    break
        finally:
            # reader 退出后，等待中的调用必须立即失败，而不是等满超时。
            self._fail_pending("连接已关闭")

    async def call(self, action: str, params: Dict[str, Any]) -> Any:
        if not self.ws or self.ws.closed:
            raise OneBotError("OneBot 未连接")
        echo = uuid.uuid4().hex
        future = asyncio.get_running_loop().create_future()
        self._pending[echo] = future
        await self.ws.send_json({"action": action, "params": params, "echo": echo})
        try:
            payload = await asyncio.wait_for(future, timeout=self.timeout)
        except asyncio.TimeoutError as exc:
            self._pending.pop(echo, None)
            raise OneBotError("OneBot 调用超时: {}".format(action)) from exc
        if payload.get("status") == "failed" or payload.get("retcode") not in (0, None):
            raise OneBotError("OneBot 调用失败: {} {}".format(action, payload))
        return payload.get("data")

    async def next_event(self, timeout: float) -> Dict[str, Any]:
        return await asyncio.wait_for(self._events.get(), timeout=timeout)


PROCESSING_HINT = "正在处理"


async def collect_replies(
    client: OneBotClient,
    bot_qq: str,
    group_id: str,
    timeout: float,
    since_time: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """收集机器人回复。

    插件会先回一条执行回执（含「正在处理」），代理结果稍后才到。收到回执后
    必须继续等到 timeout，不能把回执当成最终回复；同步命令在收到一条后再等
    一个很短的静默窗口即可结束。`since_time` 用于丢弃连接积压的旧消息。
    """
    replies: List[Dict[str, Any]] = []
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    idle_window = 2.0
    waiting_result = False
    while loop.time() < deadline:
        remaining = deadline - loop.time()
        wait = remaining if waiting_result else min(idle_window, remaining)
        try:
            event = await client.next_event(timeout=wait)
        except asyncio.TimeoutError:
            break
        if not is_bot_reply(event, bot_qq, group_id):
            continue
        if since_time is not None:
            event_time = event.get("time")
            if event_time is not None and int(event_time) < since_time - 1:
                continue
        text = extract_text(event)
        replies.append(
            {"text": text, "images": count_images(event), "raw": event}
        )
        if PROCESSING_HINT in text:
            waiting_result = True
        elif waiting_result:
            waiting_result = False
    return replies


async def history_bot_replies(
    client: OneBotClient,
    bot_qq: str,
    group_id: str,
    count: int = 20,
    since_time: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """拉取群消息历史中的机器人回复。

    ``since_time`` 为 Unix 秒级时间戳；提供后只保留该时间之后的回复，缺失
    ``time`` 的消息默认排除。runner 应在发送测试消息前记录时间并传入，
    避免旧回复造成假绿；Task 12 负责接入。
    """
    try:
        group_id_int = int(group_id)
    except (TypeError, ValueError) as exc:
        raise OneBotError("group_id 必须是数字") from exc
    data = await client.call(
        "get_group_msg_history",
        {"group_id": group_id_int, "count": count},
    )
    messages = (data or {}).get("messages", []) if isinstance(data, dict) else []
    replies: List[Dict[str, Any]] = []
    for event in messages:
        if since_time is not None:
            message_time = event.get("time")
            if message_time is None or message_time < since_time:
                continue
        if is_history_bot_message(event, bot_qq, group_id):
            replies.append(
                {"text": extract_text(event), "images": count_images(event), "raw": event}
            )
    return replies
