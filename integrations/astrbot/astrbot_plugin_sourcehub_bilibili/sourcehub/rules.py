"""来源规则包（Rule Pack）。判断槽默认关闭。"""

from __future__ import annotations

from dataclasses import dataclass

from .constants import (
    DEFAULT_MEDIA_MAX_BYTES,
    DEFAULT_SESSION_END,
    DEFAULT_SESSION_IDLE_SECONDS,
    DEFAULT_SESSION_START,
)


@dataclass
class RulePack:
    session_start: str = DEFAULT_SESSION_START
    session_end: str = DEFAULT_SESSION_END
    session_idle_seconds: int = DEFAULT_SESSION_IDLE_SECONDS
    download_images: bool = True
    video_as_link: bool = True
    media_max_bytes: int = DEFAULT_MEDIA_MAX_BYTES
    judge_enabled: bool = False


def default_qq_pack() -> RulePack:
    return RulePack()


def default_bili_pack() -> RulePack:
    return RulePack(session_start="", session_end="")
