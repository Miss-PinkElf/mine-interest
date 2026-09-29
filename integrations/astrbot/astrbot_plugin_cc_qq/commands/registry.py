"""显式命令注册与解析（Command Registry）。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    name: str
    usage: str
    description: str


COMMANDS = (
    Command("/help", "/help", "查看基础命令"),
    Command("/info", "/info", "查看当前会话"),
    Command("/new", "/new [初始消息]", "新建会话"),
    Command("/resume", "/resume [会话ID]", "恢复本群或私聊的历史会话"),
    Command("/end", "/end", "结束当前会话"),
    Command("/goon", "/goon", "中断当前执行并继续"),
    Command("/cc", "/cc <代理消息>", "直接向代理发送内容"),
    Command("/!", "/!", "中断当前执行"),
)
INTERRUPT_PREFIXES = ("/!", "/！", "!", "！")
INVALID_INTERRUPT_PREFIXES = ("!!", "！！")
COMMAND_BY_NAME = {command.name: command for command in COMMANDS}


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
