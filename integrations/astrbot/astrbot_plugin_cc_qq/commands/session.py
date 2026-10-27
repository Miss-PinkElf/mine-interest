"""会话命令的展示文本与代理透传规则（Session Command Views）。"""

from __future__ import annotations

from pathlib import Path

from ..constants import (
    CD_LIST_CURRENT_MARKER,
    CD_LIST_CURRENT_TEMPLATE,
    CD_LIST_EMPTY_REPLY,
    CD_LIST_HEADER,
    CD_LIST_HINT,
    CD_LIST_ITEM_TEMPLATE,
    CD_SUCCESS_TEMPLATE,
    INITBASE_NOTHING_TEMPLATE,
    INITBASE_SUCCESS_TEMPLATE,
    NEW_SESSION_REPLY_TEMPLATE,
    NO_COMMANDS_REPLY,
    PWD_TEMPLATE,
    RESUMED_SESSION_REPLY_TEMPLATE,
)
from ..contracts import SessionRecord, SessionSettings
from ..permissions import ROLE_GUEST, resolve_path
from .registry import commands_for_role


def help_text(role: str = ROLE_GUEST) -> str:
    commands = commands_for_role(role)
    if not commands:
        return NO_COMMANDS_REPLY
    return "可用命令：\n" + "\n".join(
        f"{command.usage} — {command.description}" for command in commands
    )


def info_text(record: SessionRecord | None) -> str:
    if record is None:
        return "当前没有活跃会话。发送消息或使用 /new 开始。"
    return f"当前会话 #{record.id}，代理：{record.agent_type}，状态：{record.status}。"


def pwd_text(settings: SessionSettings) -> str:
    return PWD_TEMPLATE.format(
        work_dir=settings.work_dir,
        role=settings.role,
        profile=settings.permission_profile,
        agent_type=settings.agent_type,
    )


def cd_success_text(work_dir: str) -> str:
    return CD_SUCCESS_TEMPLATE.format(work_dir=work_dir)


def cd_list_text(roots: list[Path], current_work_dir: str) -> str:
    """按配置顺序列出可切换目录，并标出当前生效目录。"""
    if not roots:
        return CD_LIST_EMPTY_REPLY
    current = str(resolve_path(current_work_dir)) if current_work_dir else ""
    lines = [CD_LIST_HEADER]
    for index, root in enumerate(roots, start=1):
        line = CD_LIST_ITEM_TEMPLATE.format(index=index, work_dir=root)
        if current and str(root) == current:
            line += CD_LIST_CURRENT_MARKER
        lines.append(line)
    if current:
        lines.append("")
        lines.append(CD_LIST_CURRENT_TEMPLATE.format(work_dir=current))
    lines.append(CD_LIST_HINT)
    return "\n".join(lines)


def initbase_text(created: int, skipped: int) -> str:
    if created <= 0:
        return INITBASE_NOTHING_TEMPLATE.format(skipped=skipped)
    return INITBASE_SUCCESS_TEMPLATE.format(created=created, skipped=skipped)


def cc_prompt(argument: str) -> str:
    """沿用源项目 /cc 的代理斜杠命令补全行为。"""
    return argument if argument.startswith("/") else f"/{argument}"


def new_session_text(record: SessionRecord) -> str:
    return NEW_SESSION_REPLY_TEMPLATE.format(session_id=record.id, agent_type=record.agent_type)


def resumed_session_text(record: SessionRecord) -> str:
    return RESUMED_SESSION_REPLY_TEMPLATE.format(
        session_id=record.id, agent_type=record.agent_type
    )
