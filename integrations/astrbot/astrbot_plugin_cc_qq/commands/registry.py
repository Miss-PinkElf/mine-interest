"""显式命令注册、解析与角色门禁（Command Registry）。"""

from __future__ import annotations

from dataclasses import dataclass

from ..permissions import ROLE_ADMIN, ROLE_GUEST, ROLE_MEMBER, role_at_least


@dataclass(frozen=True)
class Command:
    name: str
    usage: str
    description: str
    min_role: str = ROLE_MEMBER


COMMANDS = (
    Command("/help", "/help", "查看当前角色可用的命令", ROLE_GUEST),
    Command("/info", "/info", "查看当前会话、工作目录与权限档", ROLE_GUEST),
    Command("/new", "/new [初始消息]", "新建会话", ROLE_MEMBER),
    Command("/resume", "/resume [会话ID]", "恢复本群或私聊的历史会话", ROLE_MEMBER),
    Command("/end", "/end", "结束当前会话", ROLE_MEMBER),
    Command("/goon", "/goon", "中断当前执行并继续", ROLE_MEMBER),
    Command("/cc", "/cc <代理消息>", "直接向代理发送内容", ROLE_MEMBER),
    Command("/!", "/!", "中断当前执行", ROLE_MEMBER),
    Command("/pwd", "/pwd", "查看当前工作目录、角色与权限档", ROLE_MEMBER),
    Command("/cd", "/cd <工作目录>", "切换当前会话工作目录（owner/管理员）", ROLE_ADMIN),
    Command("/initbase", "/initbase", "补齐基础 CLAUDE.md/AGENTS.md/skills 模板（owner/管理员）", ROLE_ADMIN),
    Command("/approve", "/approve <审批号>", "批准危险操作（owner/管理员）", ROLE_ADMIN),
    Command("/deny", "/deny <审批号>", "拒绝危险操作（owner/管理员）", ROLE_ADMIN),
)
INTERRUPT_PREFIXES = ("/!", "/！", "!", "！")
INVALID_INTERRUPT_PREFIXES = ("!!", "！！")
COMMAND_BY_NAME = {command.name: command for command in COMMANDS}


def commands_for_role(role: str) -> tuple[Command, ...]:
    return tuple(command for command in COMMANDS if role_at_least(role, command.min_role))


def command_allowed(role: str, name: str) -> bool:
    command = COMMAND_BY_NAME.get(name)
    return command is not None and role_at_least(role, command.min_role)


def parse_command(text: str) -> tuple[str, str] | None:
    stripped = text.strip()
    if not stripped.startswith(INVALID_INTERRUPT_PREFIXES):
        for prefix in INTERRUPT_PREFIXES:
            if stripped.startswith(prefix):
                return "/!", stripped[len(prefix):].strip()
    parts = stripped.split(maxsplit=1)
    name = parts[0].lower() if parts else ""
    if name not in COMMAND_BY_NAME:
        return None
    return name, parts[1].strip() if len(parts) > 1 else ""
