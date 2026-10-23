#!/usr/bin/env python3
"""完全权限档的 PreToolUse 守护 hook。

Claude Code 2.1.202 的 bypassPermissions 实测不会执行 deny 规则，
所以完全权限档使用 dontAsk + 本 hook：默认放行，只拦凭据目录、
系统目录和系统级危险命令。hook 异常时一律拒绝。
"""

from __future__ import annotations

import json
import os
import sys

from hook_common import emit, load_permissions, plugin_constants


def main() -> None:
    if plugin_constants is None:
        emit("deny", "审批配置加载失败，已拒绝")
        return
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        emit("deny", "守护 hook 无法解析工具事件")
        return
    if not isinstance(event, dict):
        emit("deny", "守护 hook 收到无效事件")
        return

    tool_name = str(event.get("tool_name") or "")
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    work_dir = os.environ.get(plugin_constants.AGENT_ENV_WORK_DIR, "")

    try:
        permissions = load_permissions()
        decision = permissions.full_access_decision(tool_name, tool_input, work_dir)
    except Exception:
        emit("deny", "守护策略加载失败，已拒绝")
        return

    if decision.outcome == permissions.DECISION_DENY:
        emit("deny", decision.reason or "关键路径保护")
    emit("allow", "完全权限档放行")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        emit("deny", "守护 hook 异常，已拒绝")
