"""合并转发展开结果的可读渲染。

把 `get_forward_msg` 的结构化结果渲染成纯文本，方便人工核对。
只做展示，不改动原始数据；原始数据仍以 JSON 为准。
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from .constants import FORWARD_ERROR_KEY, FORWARD_TRUNCATED_KEY

INDENT_UNIT = "  "

# 消息段类型 -> 展示名
SEGMENT_LABELS = {
    "text": "文本",
    "image": "图片",
    "face": "表情",
    "at": "At",
    "reply": "引用",
    "video": "视频",
    "record": "语音",
    "file": "文件",
    "json": "卡片",
    "xml": "卡片",
}

# 单个字段过长时截断，避免一行刷屏
MAX_FIELD_LEN = 200


def render_forward(payload: dict) -> str:
    """把一条转发展开结果渲染成可读文本。"""
    summary = payload.get("summary") or {}
    lines = [
        f"转发展开结果  forward_id={payload.get('forward_id')}",
        f"采集时间（UTC）={payload.get('received_at')}  事件 ID={payload.get('event_id')}",
        "共 {} 层 / {} 条 / 段类型 {}".format(
            summary.get("max_depth"),
            summary.get("message_count"),
            summary.get("segment_type_counts"),
        ),
        "",
    ]
    _render_messages(payload.get("messages") or [], 0, lines)
    return "\n".join(lines) + "\n"


def _render_messages(messages: Any, depth: int, lines: list[str]) -> None:
    """按层渲染消息；遇到内嵌转发继续递归。"""
    if not isinstance(messages, list):
        return

    indent = INDENT_UNIT * depth
    for index, message in enumerate(messages, 1):
        if not isinstance(message, dict):
            continue

        lines.append(
            f"{indent}[第{depth + 1}层 第{index}条] "
            f"{_describe_sender(message)}  {_format_time(message.get('time'))}"
        )

        for segment in message.get("message") or []:
            if not isinstance(segment, dict):
                continue
            segment_type = segment.get("type")
            data = segment.get("data") or {}

            if segment_type == "forward":
                lines.append(f"{indent}  └─ 内嵌转发 id={data.get('id')}")
                content = data.get("content")
                if isinstance(content, list) and content:
                    _render_messages(content, depth + 1, lines)
                else:
                    reason = (
                        data.get(FORWARD_ERROR_KEY)
                        or data.get(FORWARD_TRUNCATED_KEY)
                        or "NapCat 返回为空，无内层内容"
                    )
                    lines.append(f"{indent}     （未展开：{reason}）")
            else:
                for segment_line in _render_segment(segment_type, data):
                    lines.append(f"{indent}  {segment_line}")

        lines.append("")


def _describe_sender(message: dict) -> str:
    """拼出「昵称(QQ号)」。"""
    sender = message.get("sender") or {}
    user_id = message.get("user_id") or sender.get("user_id") or "?"
    nickname = sender.get("nickname") or sender.get("card") or ""
    return f"{nickname}({user_id})" if nickname else str(user_id)


def _format_time(timestamp: Any) -> str:
    """Unix 时间戳转成本地时间字符串。"""
    if not isinstance(timestamp, (int, float)) or not timestamp:
        return ""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def _render_segment(segment_type: str, data: dict) -> list[str]:
    """渲染单个消息段，返回若干行。

    注意：`url` 是回取媒体资源的唯一凭据（含 rkey 鉴权），**必须完整输出、禁止截断**，
    否则复制出去会直接失效。所以 URL 单独占一行，且不走 `_truncate`。
    """
    label = SEGMENT_LABELS.get(segment_type, segment_type or "未知")

    if segment_type == "text":
        return [f"[{label}] {_truncate(data.get('text'))}"]

    if segment_type == "image":
        return [
            f"[{label}] file={data.get('file')} size={data.get('file_size')}",
            *_url_lines(data.get("url")),
        ]

    if segment_type == "face":
        return [f"[{label}] id={data.get('id')}"]

    if segment_type == "at":
        return [f"[{label}] qq={data.get('qq')}"]

    if segment_type in ("video", "record", "file"):
        return [
            f"[{label}] file={data.get('file')}",
            *_url_lines(data.get("url")),
        ]

    return [f"[{label}] {_truncate(json.dumps(data, ensure_ascii=False))}"]


def _url_lines(url: Any) -> list[str]:
    """URL 完整输出到独立一行，不做任何截断。"""
    if not url:
        return []
    return [f"url={url}"]


def _truncate(value: Any, limit: int = MAX_FIELD_LEN) -> str:
    """长字段截断，保留长度提示。"""
    if value is None:
        return ""
    text = str(value)
    if len(text) <= limit:
        return text
    return f"{text[:limit]}…(共 {len(text)} 字符)"
