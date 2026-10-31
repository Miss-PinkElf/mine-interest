"""通过 AstrBot 发送 QQ 回复（QQ Reply Adapter）。"""

from __future__ import annotations

from astrbot.core.message.components import Image, Plain, Video
from astrbot.core.message.message_event_result import MessageChain

from ..constants import LOG_PREFIX, MAX_QQ_TEXT_CHARS
from ..reply_media import (
    MEDIA_KIND_TEXT,
    MEDIA_KIND_VIDEO,
    parse_reply_parts,
)

URL_PREFIXES = ("http://", "https://")
IMAGE_SEND_FAILED_WARNING = "%s 图片发送失败：%s"
VIDEO_SEND_FAILED_WARNING = "%s 视频发送失败：%s"


def split_text(content: str):
    """按 QQ 文本长度分段，保持原始顺序。"""
    return [content[index:index + MAX_QQ_TEXT_CHARS]
            for index in range(0, len(content), MAX_QQ_TEXT_CHARS)]


def _media_component(kind: str, value: str):
    """URL 交给 AstrBot 抓取，本地路径直接读取。"""
    is_url = value.startswith(URL_PREFIXES)
    if kind == MEDIA_KIND_VIDEO:
        return Video.fromURL(value) if is_url else Video.fromFileSystem(value)
    return Image.fromURL(value) if is_url else Image.fromFileSystem(value)


async def _send_chain(context, origin: str, components: list, logger) -> bool:
    try:
        delivered = await context.send_message(
            session=origin,
            message_chain=MessageChain(components),
        )
    except Exception as exc:
        logger.warning("%s QQ 消息发送失败：%s", LOG_PREFIX, type(exc).__name__)
        return False
    return bool(delivered)


async def send_parts(
    context, origin: str, parts: list[tuple[str, str]], logger
) -> bool:
    """按顺序发送文本、图片与视频；单个媒体失败只影响该条。"""
    if not origin or not parts:
        return False
    delivered = True
    for kind, value in parts:
        if kind == MEDIA_KIND_TEXT:
            for chunk in split_text(value):
                if not await _send_chain(context, origin, [Plain(chunk)], logger):
                    delivered = False
                    break
            if not delivered:
                break
            continue
        if not await _send_chain(context, origin, [_media_component(kind, value)], logger):
            warning = (
                VIDEO_SEND_FAILED_WARNING
                if kind == MEDIA_KIND_VIDEO
                else IMAGE_SEND_FAILED_WARNING
            )
            logger.warning(warning, LOG_PREFIX, value)
    return delivered


async def send_reply(
    context,
    origin: str,
    content: str,
    logger,
    work_dir: str = "",
    media_root=None,
    auto_send: bool = False,
) -> bool:
    """发送回复；`[[image:<path>]]` 与自动识别的媒体按原位置发送。"""
    if not origin or not content:
        return False
    parts, ignored = parse_reply_parts(
        content, work_dir, media_root, auto_send=auto_send
    )
    if ignored:
        logger.warning("%s 忽略 %s 个不可信的图片路径", LOG_PREFIX, ignored)
    if not parts:
        return False
    return await send_parts(context, origin, parts, logger)


async def send_images(context, origin: str, paths, logger) -> bool:
    """按顺序发送本地图片，用于长图等插件自己生成的产物。"""
    if not origin or not paths:
        return False
    delivered = True
    for path in paths:
        if not await _send_chain(
            context, origin, [Image.fromFileSystem(str(path))], logger
        ):
            delivered = False
    return delivered


async def send_text(context, origin: str, content: str, logger) -> bool:
    """纯文本兼容入口；未传工作目录时图片标记会被视为不可信路径忽略。"""
    return await send_reply(context, origin, content, logger)
