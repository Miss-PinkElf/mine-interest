"""合并转发（Forward Message）展开器。

背景：OneBot v11 推送的转发段只带 `{"type": "forward", "data": {"id": "<res_id>"}}`，
正文必须再调用一次 `get_forward_msg` 才能取到。

实测（NapCat 4.18.28）：
1. `get_forward_msg` 返回的每条内层消息都是完整 OneBot 消息对象，含发送者、时间、
   消息 ID、群 ID 以及 text / image 等消息段。
2. 嵌套转发在响应里已经内联 `content`（本身又是一组完整消息对象）；
   按内层 id 再调一次会失败（retcode 1200）。
   因此递归**优先使用内联 content**，只在缺失时才按 id 补取。

本模块只负责取数和结构化，不拼接展示文本、不落盘。
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from .constants import (
    FORWARD_ERROR_KEY,
    FORWARD_ID_PARAM_KEYS,
    FORWARD_SEGMENT_TYPE,
    FORWARD_TRUNCATED_KEY,
    GET_FORWARD_MSG_ACTION,
    MAX_FORWARD_DEPTH,
)


def resolve_call_action(event: Any) -> Optional[Callable]:
    """取出 event 上的 bot.call_action；仅 aiocqhttp 平台具备该能力，其余返回 None。"""
    bot = getattr(event, "bot", None)
    if bot is None:
        return None

    # aiocqhttp 的 bot 对象直接暴露 call_action
    call_action = getattr(bot, "call_action", None)
    if callable(call_action):
        return call_action

    # 部分实现把它挂在 bot.api 下
    api = getattr(bot, "api", None)
    call_action = getattr(api, "call_action", None) if api is not None else None
    return call_action if callable(call_action) else None


async def fetch_forward_messages(
    call_action: Callable, forward_id: str
) -> Optional[list]:
    """调用 get_forward_msg 取内层消息列表。

    依次尝试多个参数名，只要拿到**非空**列表就返回，避免被某个参数名的空结果短路。
    全部参数都调用成功但都没内容时返回空列表；全部调用失败时返回 None。
    """
    got_empty_result = False
    for param_key in FORWARD_ID_PARAM_KEYS:
        try:
            response = await call_action(GET_FORWARD_MSG_ACTION, **{param_key: forward_id})
        except Exception:
            continue
        messages = _extract_messages(response)
        if messages:
            return messages
        if messages is not None:
            got_empty_result = True
    return [] if got_empty_result else None


async def expand_forward_tree(
    messages: Optional[list],
    call_action: Callable,
    depth: int = 1,
) -> None:
    """就地补全 messages 里所有嵌套转发的 `content`。

    已内联 content 的嵌套转发直接递归；缺失 content 的按 id 补取一次。
    超过深度上限的内层保留原样并打截断标记。
    """
    for message in messages or []:
        if not isinstance(message, dict):
            continue
        await _expand_segments(message.get("message"), call_action, depth)


def summarize_forward_tree(messages: Optional[list]) -> dict:
    """统计内层树的层数、消息条数与消息段类型，供日志和人工核对使用。"""
    summary: dict[str, Any] = {
        "max_depth": 0,
        "message_count": 0,
        "segment_type_counts": {},
    }
    _summarize(messages, 1, summary)
    return summary


def _extract_messages(response: Any) -> Optional[list]:
    """从不同 OneBot 实现的响应结构里取出消息列表。"""
    if isinstance(response, list):
        return response
    if not isinstance(response, dict):
        return None

    for key in ("messages", "message"):
        value = response.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            nested = _extract_messages(value)
            if nested is not None:
                return nested

    data = response.get("data")
    return _extract_messages(data) if data is not None else None


async def _expand_segments(
    segments: Any, call_action: Callable, depth: int
) -> None:
    """遍历一组消息段，补全其中的转发段。"""
    if not isinstance(segments, list):
        return

    for segment in segments:
        if not isinstance(segment, dict) or segment.get("type") != FORWARD_SEGMENT_TYPE:
            continue

        data = segment.get("data")
        if not isinstance(data, dict):
            continue

        content = data.get("content")
        if not isinstance(content, list) or not content:
            if depth >= MAX_FORWARD_DEPTH:
                data[FORWARD_TRUNCATED_KEY] = f"超过最大展开深度 {MAX_FORWARD_DEPTH}"
                continue
            content = await fetch_forward_messages(call_action, data.get("id"))
            if content is None:
                data[FORWARD_ERROR_KEY] = "get_forward_msg 调用失败"
                continue
            data["content"] = content

        await expand_forward_tree(content, call_action, depth + 1)


def _summarize(messages: Any, depth: int, summary: dict) -> None:
    """递归统计层数、条数与消息段类型。"""
    if not isinstance(messages, list):
        return

    summary["max_depth"] = max(summary["max_depth"], depth)
    for message in messages:
        if not isinstance(message, dict):
            continue
        summary["message_count"] += 1
        for segment in message.get("message") or []:
            if not isinstance(segment, dict):
                continue
            segment_type = segment.get("type") or "unknown"
            counts = summary["segment_type_counts"]
            counts[segment_type] = counts.get(segment_type, 0) + 1
            if segment_type == FORWARD_SEGMENT_TYPE:
                data = segment.get("data")
                if isinstance(data, dict):
                    _summarize(data.get("content"), depth + 1, summary)
