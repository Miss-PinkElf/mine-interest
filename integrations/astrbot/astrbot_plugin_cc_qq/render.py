"""长文本转长图（Long-text Rendering）。

渲染复用 AstrBot 自带的 T2I：本地策略用 Pillow 直接绘制 Markdown，
不依赖浏览器；AstrBot 相关导入延迟到函数内部，便于单元测试。
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from PIL import Image as PILImage

from .constants import (
    CODE_FENCE_MARKER,
    DEFAULT_LONG_TEXT_IMAGE_MAX_HEIGHT,
    DEFAULT_LONG_TEXT_IMAGE_THRESHOLD,
    IMAGE_MARKER_PREFIX,
    LONG_TEXT_IMAGE_THRESHOLD_KEY,
    MAX_LONG_TEXT_IMAGE_THRESHOLD,
    MIN_LONG_TEXT_IMAGE_THRESHOLD,
)


def should_render_image(text: str, enabled: bool, threshold: int) -> bool:
    """超过阈值或包含围栏代码块时渲染长图；含图片标记时交给图文发送处理。"""
    if not enabled or not text or IMAGE_MARKER_PREFIX in text:
        return False
    if threshold > 0 and len(text) >= threshold:
        return True
    return CODE_FENCE_MARKER in text


def config_flag(config: dict, key: str, default: bool) -> bool:
    """AstrBot 会把未填写的配置写成 null，不能把 None 当成 False。"""
    raw = config.get(key)
    return default if raw is None else bool(raw)


def threshold_from_config(config: dict) -> int:
    """读取并夹取阈值；非法值回退默认值。"""
    raw = config.get(LONG_TEXT_IMAGE_THRESHOLD_KEY, DEFAULT_LONG_TEXT_IMAGE_THRESHOLD)
    if isinstance(raw, bool) or not isinstance(raw, int):
        return DEFAULT_LONG_TEXT_IMAGE_THRESHOLD
    return max(MIN_LONG_TEXT_IMAGE_THRESHOLD, min(MAX_LONG_TEXT_IMAGE_THRESHOLD, raw))


def split_long_image(path: Path, max_height: int) -> list[Path]:
    """把超高长图按纵向切分，避免 QQ 压缩后不可读。"""
    try:
        with PILImage.open(path) as image:
            width, height = image.size
            if max_height <= 0 or height <= max_height:
                return [path]
            parts: list[Path] = []
            for index, top in enumerate(range(0, height, max_height), start=1):
                target = path.with_name(f"{path.stem}-{index}{path.suffix}")
                bottom = min(top + max_height, height)
                image.crop((0, top, width, bottom)).save(target)
                parts.append(target)
        return parts
    except (OSError, ValueError):
        return [path]


async def _render_async(text: str, use_network: bool) -> str:
    from astrbot.core.utils.astrbot_path import get_astrbot_temp_path
    from astrbot.core.utils.t2i.renderer import HtmlRenderer

    # 本地策略把图片保存到 AstrBot 临时目录；插件在非标准 cwd 下运行时该目录可能不存在。
    Path(get_astrbot_temp_path()).mkdir(parents=True, exist_ok=True)
    renderer = HtmlRenderer()
    if use_network:
        await renderer.initialize()
    return await renderer.render_t2i(text, use_network=use_network, return_url=False)


def _render_sync(text: str, use_network: bool) -> str:
    """在线程内建立独立事件循环，避免 Pillow 绘制阻塞插件主循环。"""
    return asyncio.run(_render_async(text, use_network))


async def render_long_images(
    text: str,
    use_network: bool = False,
    max_height: int = DEFAULT_LONG_TEXT_IMAGE_MAX_HEIGHT,
) -> list[Path]:
    """渲染并切分长图；任何失败都返回空列表，由调用方回退文本。"""
    try:
        rendered = await asyncio.to_thread(_render_sync, text, use_network)
    except Exception:
        return []
    if not rendered:
        return []
    return split_long_image(Path(rendered), max_height)
