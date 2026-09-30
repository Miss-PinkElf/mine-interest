"""私聊短窗口去重（Private Duplicate Guard）。"""

from __future__ import annotations


def is_recent_duplicate(
    seen: dict[tuple[str, ...], int],
    key: tuple[str, ...],
    now: int,
    window_seconds: int,
) -> bool:
    """同一 key 在窗口内再次出现则为重复。窗口为 0 时不去重。"""
    if window_seconds <= 0:
        return False
    last = seen.get(key)
    seen[key] = now
    expired = [item for item, timestamp in seen.items() if now - timestamp > window_seconds]
    for item in expired:
        del seen[item]
    if last is None:
        return False
    age = now - last
    if age < 0:
        return False
    return age <= window_seconds
