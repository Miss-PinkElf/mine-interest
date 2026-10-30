"""按权限档位生成代理参数与 Claude 策略文件（Agent Profiles）。"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from ..constants import (
    AGENT_POLICY_DIR_NAME,
    APPROVAL_HOOK_TIMEOUT_MARGIN_SECONDS,
    CLAUDE_SETTING_SOURCES_KEY,
    DEFAULT_CLAUDE_SETTING_SOURCES,
    DENIED_NATIVE_WEB_TOOL_RULES,
    GUARD_HOOK_SCRIPT_NAME,
    GUARD_HOOK_TIMEOUT_SECONDS,
    MCP_DEEPSEEK_SERVER_RULE,
    MCP_LOCAL_FETCH_SERVER_RULE,
    READONLY_HOOK_SCRIPT_NAME,
)
from ..permissions import (
    CRITICAL_PATH_DENY_RULES,
    PROFILE_FULL,
    PROFILE_READONLY,
    PROFILE_WORKSPACE,
    READONLY_ALLOWED_TOOLS,
)

CLAUDE_PERMISSION_MODE_BY_PROFILE = {
    PROFILE_READONLY: "dontAsk",
    PROFILE_WORKSPACE: "acceptEdits",
    # bypassPermissions 在本机 2.1.202 不执行 deny 规则；完全权限改用守护 hook。
    PROFILE_FULL: "dontAsk",
}

CODEX_READONLY_PROFILE_NAME = "ccqq-readonly"
CODEX_WORKSPACE_PROFILE_NAME = "ccqq-workspace"

# Codex 传统 read-only 只限制写入、不限制读取范围；权限档案可以同时收紧读取。
CODEX_READONLY_FILESYSTEM = (
    '{":root"="deny",":minimal"="read",":workspace_roots"="read",'
    '":tmpdir"="deny",":slash_tmp"="deny"}'
)
CODEX_WORKSPACE_FILESYSTEM = (
    '{":root"="deny",":minimal"="read",":workspace_roots"="write",'
    '":tmpdir"="deny",":slash_tmp"="deny"}'
)

APPROVAL_HOOK_MATCHER = "Bash|Edit|Write|NotebookEdit|Read|Grep|Glob"
WORKSPACE_SANDBOX_SETTINGS = {
    "enabled": True,
    "autoAllowBashIfSandboxed": True,
    "allowUnsandboxedCommands": True,
    "failIfUnavailable": True,
}


def claude_setting_sources(config: dict) -> str:
    """默认空字符串：屏蔽用户与仓库 settings，只使用插件注入的策略文件。"""
    raw = config.get(CLAUDE_SETTING_SOURCES_KEY, DEFAULT_CLAUDE_SETTING_SOURCES)
    return str(raw if raw is not None else DEFAULT_CLAUDE_SETTING_SOURCES).strip()


def _quote_command_part(value: str) -> str:
    escaped = str(value).replace('"', '\\"')
    return f'"{escaped}"'


def approval_hook_command(hook_script: Path, python_executable: str | None = None) -> str:
    python = python_executable or sys.executable
    return f"{_quote_command_part(python)} {_quote_command_part(str(hook_script))}"


def build_base_claude_settings() -> dict:
    """`/initbase` 写入工作区的手动 Claude 基础策略，与运行时共用同一真相源。"""
    return {
        "permissions": {"deny": list(CRITICAL_PATH_DENY_RULES)},
        "sandbox": dict(WORKSPACE_SANDBOX_SETTINGS),
    }


def build_permission_rules(profile: str, readonly_mcp_enabled: bool = True) -> dict:
    """生成 Claude 的 allow/deny：原生联网工具全禁，只放行服务端 MCP 搜索。"""
    deny = list(CRITICAL_PATH_DENY_RULES)
    deny.extend(DENIED_NATIVE_WEB_TOOL_RULES)
    deny.append(MCP_LOCAL_FETCH_SERVER_RULE)
    allow: list[str] = []
    if profile == PROFILE_READONLY and not readonly_mcp_enabled:
        deny.append(MCP_DEEPSEEK_SERVER_RULE)
    else:
        allow.append(MCP_DEEPSEEK_SERVER_RULE)
    rules: dict = {"deny": deny}
    if allow:
        rules["allow"] = allow
    return rules


def build_claude_settings(
    profile: str,
    hook_script: Path | None,
    approval_timeout_seconds: int,
    python_executable: str | None = None,
    readonly_mcp_enabled: bool = True,
) -> dict:
    """只放策略，不放任何凭据；工作区档才启用沙箱与审批 hook。"""
    settings: dict = {
        "permissions": build_permission_rules(profile, readonly_mcp_enabled),
    }
    if profile == PROFILE_WORKSPACE and hook_script is not None:
        settings["sandbox"] = dict(WORKSPACE_SANDBOX_SETTINGS)
        settings["hooks"] = {
            "PreToolUse": [
                {
                    "matcher": APPROVAL_HOOK_MATCHER,
                    "hooks": [
                        {
                            "type": "command",
                            "command": approval_hook_command(hook_script, python_executable),
                            "timeout": int(approval_timeout_seconds)
                            + APPROVAL_HOOK_TIMEOUT_MARGIN_SECONDS,
                        }
                    ],
                }
            ]
        }
    elif profile == PROFILE_READONLY and hook_script is not None:
        readonly_script = hook_script.parent / READONLY_HOOK_SCRIPT_NAME
        settings["hooks"] = {
            "PreToolUse": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": approval_hook_command(readonly_script, python_executable),
                            "timeout": GUARD_HOOK_TIMEOUT_SECONDS,
                        }
                    ],
                }
            ]
        }
    elif profile == PROFILE_FULL and hook_script is not None:
        guard_script = hook_script.parent / GUARD_HOOK_SCRIPT_NAME
        settings["hooks"] = {
            "PreToolUse": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": approval_hook_command(guard_script, python_executable),
                            "timeout": GUARD_HOOK_TIMEOUT_SECONDS,
                        }
                    ],
                }
            ]
        }
    return settings


def ensure_claude_settings(
    data_dir: Path,
    profile: str,
    hook_script: Path | None,
    approval_timeout_seconds: int,
    readonly_mcp_enabled: bool = True,
) -> str:
    """把策略写到插件数据区；内容变化时才重写，返回文件路径。"""
    payload = build_claude_settings(
        profile, hook_script, approval_timeout_seconds, None, readonly_mcp_enabled
    )
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
    target_dir = Path(data_dir) / AGENT_POLICY_DIR_NAME
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"claude-{profile}-{digest}.json"
    if not target.exists() or target.read_text(encoding="utf-8") != serialized:
        target.write_text(serialized, encoding="utf-8")
    return str(target)


def claude_args(
    profile: str,
    model: str,
    agent_session_id: str,
    new_session_id: str,
    settings_path: str,
    setting_sources: str,
) -> list[str]:
    mode = CLAUDE_PERMISSION_MODE_BY_PROFILE[profile]
    args = [
        "--permission-mode",
        mode,
        "--print",
        "--output-format",
        "stream-json",
        "--verbose",
    ]
    if settings_path:
        args.extend(("--settings", settings_path))
    if setting_sources is not None:
        args.extend(("--setting-sources", setting_sources))
    if profile == PROFILE_READONLY:
        args.extend(("--tools", ",".join(READONLY_ALLOWED_TOOLS)))
    if model:
        args.extend(("--model", model))
    if agent_session_id:
        args.extend(("--resume", agent_session_id))
    else:
        args.extend(("--session-id", new_session_id))
    return args


def codex_args(
    profile: str,
    model: str,
    agent_session_id: str,
    work_dir: str,
    images: tuple[str, ...] = (),
) -> list[str]:
    args = ["exec"]
    # `-i` 属于 exec 层参数；resume 是否接受待真机确认，不支持时需改为首轮传图。
    for image in images:
        args.extend(("-i", image))
    if agent_session_id:
        args.append("resume")
    # resume 子命令不接受 -s，统一走 config 覆盖。
    args.extend(("--skip-git-repo-check",))
    if profile == PROFILE_READONLY:
        args.extend(
            (
                "-c",
                f'default_permissions="{CODEX_READONLY_PROFILE_NAME}"',
                "-c",
                f'permissions.{CODEX_READONLY_PROFILE_NAME}.extends=":read-only"',
                "-c",
                f"permissions.{CODEX_READONLY_PROFILE_NAME}.filesystem="
                f"{CODEX_READONLY_FILESYSTEM}",
            )
        )
    elif profile == PROFILE_WORKSPACE:
        args.extend(
            (
                "-c",
                f'default_permissions="{CODEX_WORKSPACE_PROFILE_NAME}"',
                "-c",
                f'permissions.{CODEX_WORKSPACE_PROFILE_NAME}.extends=":workspace"',
                "-c",
                f"permissions.{CODEX_WORKSPACE_PROFILE_NAME}.filesystem="
                f"{CODEX_WORKSPACE_FILESYSTEM}",
                "-c",
                f"permissions.{CODEX_WORKSPACE_PROFILE_NAME}.network={{enabled=false}}",
            )
        )
    else:
        args.extend(("-c", 'sandbox_mode="danger-full-access"'))
    args.extend(("-c", 'approval_policy="never"'))
    args.append("--json")
    if model:
        args.extend(("--model", model))
    if agent_session_id:
        args.extend((agent_session_id, "-"))
    else:
        args.extend(("--cd", work_dir, "-"))
    return args
