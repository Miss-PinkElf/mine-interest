"""通过 AstrBot 发送 QQ 回复（QQ Reply Adapter）。"""

from __future__ import annotations

from astrbot.core.message.components import Plain
from astrbot.core.message.message_event_result import MessageChain

from ..constants import LOG_PREFIX, MAX_QQ_TEXT_CHARS


def split_text(content: str):
    """按 QQ 文本长度分段，保持原始顺序。"""
    return [content[index:index + MAX_QQ_TEXT_CHARS]
            for index in range(0, len(content), MAX_QQ_TEXT_CHARS)]


async def send_text(context, origin: str, content: str, logger) -> bool:
    if not origin or not content:
        return False
    try:
        for part in split_text(content):
            await context.send_message(
                session=origin,
                message_chain=MessageChain([Plain(part)]),
            )
    except Exception as exc:
        logger.warning("%s QQ 文本回复失败：%s", LOG_PREFIX, type(exc).__name__)
        return False
    return True
