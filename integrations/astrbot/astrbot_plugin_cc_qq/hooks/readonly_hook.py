#!/usr/bin/env python3
"""只读档的 PreToolUse hook。

`--tools` 已把工具面限制在只读工具；本 hook 再补上工作目录边界，
越界读取直接拒绝。hook 异常时 fail-closed。
"""

from __future__ import annotations

import json
import os
import sys

from hook_common import emit, load_permissions, plugin_constants


def main() -> None:
    if plugin_constants is None:
        emit("deny", "只读策略加载失败，已拒绝")
        return
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        emit("deny", "只读 hook 无法解析工具事件")
        return
    if not isinstance(event, dict):
        emit("deny", "只读 hook 收到无效事件")
        return

    tool_name = str(event.get("tool_name") or "")
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    work_dir = os.environ.get(plugin_constants.AGENT_ENV_WORK_DIR, "")
    media_root = os.environ.get(plugin_constants.AGENT_ENV_MEDIA_ROOT, "")
    extra_read_roots = (media_root,) if media_root else ()

    try:
        permissions = load_permissions()
        decision = permissions.classify_tool_call(
            tool_name,
            tool_input,
            permissions.PROFILE_READONLY,
            work_dir,
            extra_read_roots,
        )
    except Exception:
        emit("deny", "只读策略加载失败，已拒绝")
        return

    if decision.outcome == permissions.DECISION_DENY:
        emit("deny", decision.reason or "只读档位拒绝")
    emit("allow", "只读档位放行")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        emit("deny", "只读 hook 异常，已拒绝")
