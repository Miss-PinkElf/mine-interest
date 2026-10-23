#!/usr/bin/env python3
"""Claude Code PreToolUse 审批 hook。

由插件生成的 settings 调用。任何异常、超时或服务不可用都输出 deny，
不允许在不确定的情况下放行。
"""

from __future__ import annotations

import json
import os
import socket
import sys

from hook_common import emit, load_permissions, plugin_constants

SOCKET_TIMEOUT_MARGIN_SECONDS = 30


def _summary(tool_name: str, tool_input: dict) -> str:
    if tool_name == "Bash":
        text = str(tool_input.get("command") or "")
    else:
        text = str(
            tool_input.get("file_path")
            or tool_input.get("path")
            or tool_input.get("notebook_path")
            or ""
        )
    if not text:
        text = json.dumps(tool_input, ensure_ascii=False, sort_keys=True)
    return text[: plugin_constants.APPROVAL_SUMMARY_MAX_CHARS]


def _ask_broker(payload: dict) -> tuple[bool, str]:
    host = os.environ.get(plugin_constants.APPROVAL_ENV_HOST, "")
    port = os.environ.get(plugin_constants.APPROVAL_ENV_PORT, "")
    token = os.environ.get(plugin_constants.APPROVAL_ENV_TOKEN, "")
    if not host or not port or not token:
        return False, "审批服务未就绪，已拒绝"
    default_timeout = plugin_constants.DEFAULT_DANGER_APPROVAL_TIMEOUT_SECONDS
    try:
        timeout = int(os.environ.get(plugin_constants.APPROVAL_ENV_TIMEOUT, default_timeout))
    except ValueError:
        timeout = default_timeout
    request = dict(payload)
    request["token"] = token
    try:
        with socket.create_connection(
            (host, int(port)), timeout=timeout + SOCKET_TIMEOUT_MARGIN_SECONDS
        ) as connection:
            connection.sendall((json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8"))
            reader = connection.makefile("rb")
            line = reader.readline()
    except (OSError, ValueError):
        return False, "审批服务不可用，已拒绝"
    try:
        response = json.loads(line.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False, "审批响应无效，已拒绝"
    approved = str(response.get("decision") or "") == "allow"
    reason = str(response.get("reason") or ("管理员批准" if approved else "管理员拒绝"))
    return approved, reason


def main() -> None:
    if plugin_constants is None:
        emit("deny", "审批配置加载失败，已拒绝")
        return
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        emit("deny", "审批 hook 无法解析工具事件")
        return
    if not isinstance(event, dict):
        emit("deny", "审批 hook 收到无效事件")
        return

    profile = os.environ.get(plugin_constants.AGENT_ENV_PROFILE, "")
    work_dir = os.environ.get(plugin_constants.AGENT_ENV_WORK_DIR, "")
    tool_name = str(event.get("tool_name") or "")
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}

    try:
        permissions = load_permissions()
        decision = permissions.classify_tool_call(tool_name, tool_input, profile, work_dir)
    except Exception:
        emit("deny", "审批策略加载失败，已拒绝")
        return

    if decision.outcome in (permissions.DECISION_NONE, permissions.DECISION_ALLOW):
        sys.exit(0)
    if decision.outcome == permissions.DECISION_DENY:
        emit("deny", decision.reason or "权限策略拒绝")

    payload = {
        "conversation_key": os.environ.get(plugin_constants.AGENT_ENV_CONVERSATION_KEY, ""),
        "sender_id": os.environ.get(plugin_constants.AGENT_ENV_SENDER_ID, ""),
        "origin": os.environ.get(plugin_constants.AGENT_ENV_ORIGIN, ""),
        "role": os.environ.get(plugin_constants.AGENT_ENV_ROLE, ""),
        "profile": profile,
        "tool_name": tool_name,
        "summary": _summary(tool_name, tool_input),
    }
    approved, reason = _ask_broker(payload)
    emit("allow" if approved else "deny", reason)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        emit("deny", "审批 hook 异常，已拒绝")
