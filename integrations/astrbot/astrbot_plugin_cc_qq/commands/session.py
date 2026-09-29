"""会话命令的展示文本与代理透传规则（Session Command Views）。"""

from __future__ import annotations

from ..constants import NEW_SESSION_REPLY_TEMPLATE, RESUMED_SESSION_REPLY_TEMPLATE
from ..contracts import SessionRecord
from .registry import COMMANDS


def help_text() -> str:
    return "可用命令：\n" + "\n".join(
        f"{command.usage} — {command.description}" for command in COMMANDS
    )


def info_text(record: SessionRecord | None) -> str:
    if record is None:
        return "当前没有活跃会话。发送消息或使用 /new 开始。"
    return f"当前会话 #{record.id}，代理：{record.agent_type}，状态：{record.status}。"


def cc_prompt(argument: str) -> str:
    """沿用源项目 /cc 的代理斜杠命令补全行为。"""
    return argument if argument.startswith("/") else f"/{argument}"


def new_session_text(record: SessionRecord) -> str:
    return NEW_SESSION_REPLY_TEMPLATE.format(session_id=record.id, agent_type=record.agent_type)


def resumed_session_text(record: SessionRecord) -> str:
    return RESUMED_SESSION_REPLY_TEMPLATE.format(
        session_id=record.id, agent_type=record.agent_type
    )
