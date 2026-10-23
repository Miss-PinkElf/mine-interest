"""角色、权限档位与危险操作识别（Permission Profiles）。

本模块只依赖标准库，审批 hook 会以脚本方式直接导入它，
因此不能在这里引入 AstrBot 或插件内其它运行时模块。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

try:  # 包内导入
    from .constants import (
        ALLOWED_WORK_DIRS_KEY,
        GUEST_PERMISSION_PROFILE_KEY,
        MEMBER_PERMISSION_PROFILE_KEY,
        OWNER_PERMISSION_PROFILE_KEY,
    )
except ImportError:  # 审批 hook 以独立脚本方式加载本文件时
    from constants import (
        ALLOWED_WORK_DIRS_KEY,
        GUEST_PERMISSION_PROFILE_KEY,
        MEMBER_PERMISSION_PROFILE_KEY,
        OWNER_PERMISSION_PROFILE_KEY,
    )

ROLE_GUEST = "guest"
ROLE_MEMBER = "member"
ROLE_ADMIN = "admin"
ROLE_OWNER = "owner"
ROLE_ORDER = {
    ROLE_GUEST: 0,
    ROLE_MEMBER: 1,
    ROLE_ADMIN: 2,
    ROLE_OWNER: 3,
}

PROFILE_READONLY = "readonly"
PROFILE_WORKSPACE = "workspace"
PROFILE_FULL = "full"
SUPPORTED_PROFILES = (PROFILE_READONLY, PROFILE_WORKSPACE, PROFILE_FULL)

DEFAULT_PROFILE_BY_ROLE = {
    ROLE_GUEST: PROFILE_READONLY,
    ROLE_MEMBER: PROFILE_WORKSPACE,
    ROLE_ADMIN: PROFILE_FULL,
    ROLE_OWNER: PROFILE_FULL,
}

# 角色 -> 配置键；管理员沿用 owner 档位。
PROFILE_CONFIG_KEY_BY_ROLE = {
    ROLE_GUEST: GUEST_PERMISSION_PROFILE_KEY,
    ROLE_MEMBER: MEMBER_PERMISSION_PROFILE_KEY,
    ROLE_ADMIN: OWNER_PERMISSION_PROFILE_KEY,
    ROLE_OWNER: OWNER_PERMISSION_PROFILE_KEY,
}

GROUP_PROFILE_OVERRIDE_KEY_BY_ROLE = {
    ROLE_GUEST: GUEST_PERMISSION_PROFILE_KEY,
    ROLE_MEMBER: MEMBER_PERMISSION_PROFILE_KEY,
}

DECISION_ALLOW = "allow"
DECISION_ASK = "ask"
DECISION_DENY = "deny"
DECISION_NONE = "none"

WRITE_TOOLS = frozenset({"Edit", "Write", "NotebookEdit"})
READ_TOOLS = frozenset({"Read", "Grep", "Glob"})

PROTECTED_READ_ROOTS = ("~/.ssh", "~/.aws", "~/.gnupg")
PROTECTED_WRITE_ROOTS = (
    "~/.ssh",
    "~/.aws",
    "~/.gnupg",
    "/etc",
    "/usr",
    "/System",
    "/Library",
)

# 只读档位可用的内置工具；刻意不包含 Bash 与联网工具。
READONLY_ALLOWED_TOOLS = ("Read", "Grep", "Glob", "TodoWrite")

# 即使 owner/管理员也不能通过的路径与命令；deny 规则优先于 allow。
CRITICAL_PATH_DENY_RULES = (
    "Read(~/.ssh/**)",
    "Read(~/.aws/**)",
    "Read(~/.gnupg/**)",
    "Edit(~/.ssh/**)",
    "Edit(~/.aws/**)",
    "Edit(~/.gnupg/**)",
    "Edit(/etc/**)",
    "Edit(/usr/**)",
    "Edit(/System/**)",
    "Edit(/Library/**)",
    "Write(~/.ssh/**)",
    "Write(~/.aws/**)",
    "Write(~/.gnupg/**)",
    "Write(/etc/**)",
    "Write(/usr/**)",
    "Write(/System/**)",
    "Write(/Library/**)",
    "NotebookEdit(~/.ssh/**)",
    "NotebookEdit(~/.aws/**)",
    "NotebookEdit(~/.gnupg/**)",
    "NotebookEdit(/etc/**)",
    "NotebookEdit(/usr/**)",
    "NotebookEdit(/System/**)",
    "NotebookEdit(/Library/**)",
    "Bash(sudo *)",
    "Bash(shutdown *)",
    "Bash(reboot *)",
    "Bash(mkfs *)",
    "Bash(dd *)",
    "Bash(diskutil *)",
    "Bash(rm -rf /)",
    "Bash(rm -rf /*)",
)

_HARD_COMMAND_PATTERNS = (
    (re.compile(r"(^|[\s;&|])(sudo|su)\s", re.IGNORECASE), "提权命令"),
    (re.compile(r"(^|[\s;&|])(shutdown|reboot|halt|poweroff)\b", re.IGNORECASE), "关机或重启"),
    (re.compile(r"(^|[\s;&|])mkfs", re.IGNORECASE), "格式化文件系统"),
    (re.compile(r"(^|[\s;&|])dd\s", re.IGNORECASE), "底层磁盘写入"),
    (re.compile(r"(^|[\s;&|])diskutil\s", re.IGNORECASE), "磁盘管理命令"),
    (re.compile(r"\brm\s+-[rf]{2}\s+/(\s|$|\*)", re.IGNORECASE), "删除根目录"),
)

_CRITICAL_COMMAND_PATTERNS = _HARD_COMMAND_PATTERNS + (
    (
        re.compile(
            r"(~/|\$\{?HOME\}?|/Users/[^/\s]+/|/home/[^/\s]+/|/root/)"
            r"[\"']?/?(\.ssh|\.aws|\.gnupg)\b",
            re.IGNORECASE,
        ),
        "访问凭据目录",
    ),
    (
        re.compile(r"\s(/(etc|System|Library|bin|sbin)/|/usr/(bin|sbin)/)", re.IGNORECASE),
        "访问系统目录",
    ),
    (
        re.compile(r">\s*/(etc|System|Library|bin|sbin|usr/(bin|sbin))/", re.IGNORECASE),
        "写入系统目录",
    ),
)

_DANGEROUS_COMMAND_PATTERNS = (
    (re.compile(r"(^|[\s;&|])rm\s", re.IGNORECASE), "包含删除命令 rm"),
    (re.compile(r"(^|[\s;&|])rmdir\s", re.IGNORECASE), "包含删除目录命令 rmdir"),
    (re.compile(r"(^|[\s;&|])sudo\s", re.IGNORECASE), "尝试使用 sudo 提权"),
    (re.compile(r"(^|[\s;&|])su\s", re.IGNORECASE), "尝试切换用户"),
    (re.compile(r"(^|[\s;&|])chmod\s", re.IGNORECASE), "修改文件权限"),
    (re.compile(r"(^|[\s;&|])chown\s", re.IGNORECASE), "修改文件所有者"),
    (re.compile(r"(^|[\s;&|])dd\s", re.IGNORECASE), "底层磁盘写入"),
    (re.compile(r"(^|[\s;&|])mkfs", re.IGNORECASE), "格式化文件系统"),
    (re.compile(r"(^|[\s;&|])(mount|umount)\s", re.IGNORECASE), "挂载或卸载文件系统"),
    (re.compile(r"(^|[\s;&|])(kill|pkill|killall)\s", re.IGNORECASE), "结束系统进程"),
    (re.compile(r"(^|[\s;&|])(shutdown|reboot|halt|poweroff)\b", re.IGNORECASE), "关机或重启"),
    (re.compile(r"\bgit\s+push\b", re.IGNORECASE), "推送远端仓库"),
    (re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE), "硬重置仓库"),
    (re.compile(r"\bgit\s+clean\b[^\n]*-[a-z]*f", re.IGNORECASE), "强制清理未跟踪文件"),
    (re.compile(r"\b(npm|pnpm|yarn)\s+(i|install|add)\b[^\n]*\s(-g|--global)\b", re.IGNORECASE), "全局安装 npm 包"),
    (re.compile(r"\bpip3?\s+install\b", re.IGNORECASE), "安装 Python 包"),
    (re.compile(r"\bbrew\s+(install|uninstall|reinstall)\b", re.IGNORECASE), "修改 Homebrew 包"),
    (re.compile(r"\b(apt|apt-get|yum|dnf)\s+(install|remove|purge)\b", re.IGNORECASE), "修改系统包"),
    (re.compile(r"\b(curl|wget)\b[^\n|]*\|\s*(ba|z)?sh\b", re.IGNORECASE), "下载内容直接交给 shell"),
    (re.compile(r"(^|[\s;&|])eval\s", re.IGNORECASE), "执行动态拼接命令"),
    (re.compile(r"\bfind\b[^\n]*-delete\b", re.IGNORECASE), "批量删除匹配文件"),
    (re.compile(r">\s*/(etc|usr|bin|sbin|System|Library)/", re.IGNORECASE), "写入系统目录"),
)


@dataclass(frozen=True)
class ToolDecision:
    """PreToolUse hook 需要的判定结果。"""

    outcome: str
    reason: str = ""


def normalize_profile(value, fallback: str) -> str:
    text = str(value or "").strip().lower()
    return text if text in SUPPORTED_PROFILES else fallback


def role_at_least(role: str, minimum: str) -> bool:
    return ROLE_ORDER.get(role, -1) >= ROLE_ORDER.get(minimum, len(ROLE_ORDER))


def resolve_permission_profile(role: str, config: dict, rule: dict | None = None) -> str:
    """按角色读取全局档位，群规则可覆盖 guest/member。非法值回落到安全默认值。"""
    default = DEFAULT_PROFILE_BY_ROLE.get(role, PROFILE_READONLY)
    override_key = GROUP_PROFILE_OVERRIDE_KEY_BY_ROLE.get(role)
    if isinstance(rule, dict) and override_key:
        override = rule.get(override_key)
        if str(override or "").strip():
            candidate = normalize_profile(override, default)
            if candidate in SUPPORTED_PROFILES:
                return candidate
    config_key = PROFILE_CONFIG_KEY_BY_ROLE.get(role)
    if config_key:
        return normalize_profile(config.get(config_key), default)
    return default


def resolve_path(value: str, base: str | Path | None = None) -> Path:
    path = Path(str(value)).expanduser()
    if not path.is_absolute() and base:
        path = Path(base).expanduser() / path
    return path.resolve(strict=False)


def is_within(path: Path, root: Path, casefold: bool = False) -> bool:
    if casefold:
        # macOS 默认文件系统大小写不敏感，保护路径按大小写折叠比较。
        normalized_path = str(path).casefold().rstrip("/")
        normalized_root = str(root).casefold().rstrip("/")
        return normalized_path == normalized_root or normalized_path.startswith(
            normalized_root + "/"
        )
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def workspace_roots(config: dict) -> list[Path]:
    values = config.get(ALLOWED_WORK_DIRS_KEY)
    if not isinstance(values, list):
        return []
    roots = []
    for value in values:
        text = str(value or "").strip()
        if text:
            roots.append(resolve_path(text))
    return roots


def allowed_work_dir(target: str, config: dict) -> bool:
    """`/cd` 的目标必须落在配置的根目录内，按 realpath 防符号链接逃逸。"""
    roots = workspace_roots(config)
    if not roots:
        return False
    candidate = resolve_path(target)
    return any(is_within(candidate, root) for root in roots)


def dangerous_command_reason(command: str) -> str:
    text = str(command or "")
    if not text.strip():
        return ""
    for pattern, reason in _DANGEROUS_COMMAND_PATTERNS:
        if pattern.search(text):
            return reason
    return ""


def hard_command_reason(command: str) -> str:
    """与 CLI deny 规则一致的硬拒绝命令，审批也不能放行。"""
    text = str(command or "")
    if not text.strip():
        return ""
    for pattern, reason in _HARD_COMMAND_PATTERNS:
        if pattern.search(text):
            return reason
    return ""


def critical_command_reason(command: str) -> str:
    text = str(command or "")
    if not text.strip():
        return ""
    for pattern, reason in _CRITICAL_COMMAND_PATTERNS:
        if pattern.search(text):
            return reason
    return ""


def _hits_roots(path: Path, roots) -> bool:
    return any(
        is_within(path, resolve_path(root), casefold=True) for root in roots
    )


def hard_denied_decision(
    tool_name: str, tool_input: dict, work_dir: str
) -> ToolDecision | None:
    """匹配 CLI deny 规则的高危操作：审批也不能放行。"""
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    root = resolve_path(work_dir) if work_dir else None
    if tool_name in READ_TOOLS:
        raw_path = _tool_path(tool_input)
        if raw_path:
            target = resolve_path(raw_path, root)
            if _hits_roots(target, PROTECTED_READ_ROOTS):
                return ToolDecision(DECISION_DENY, f"禁止读取凭据目录：{target}")
        return None
    if tool_name in WRITE_TOOLS:
        raw_path = _tool_path(tool_input)
        if raw_path:
            target = resolve_path(raw_path, root)
            if _hits_roots(target, PROTECTED_WRITE_ROOTS):
                return ToolDecision(DECISION_DENY, f"禁止写入受保护路径：{target}")
        return None
    if tool_name == "Bash":
        reason = hard_command_reason(str(tool_input.get("command") or ""))
        if reason:
            return ToolDecision(DECISION_DENY, reason)
    return None


def outside_path_reference(command: str, work_dir: str) -> str:
    """找出 Bash 命令里指向工作目录外的路径；只做启发式判断。"""
    text = str(command or "")
    if not text.strip():
        return ""
    root = resolve_path(work_dir) if work_dir else None
    if root is None:
        return ""
    tokens = re.findall(
        r"(?<![\w.-])(~[^\s\"';&|]*|\$\{?HOME\}?[^\s\"';&|]*|/[^\s\"';&|]+|\.\.(?:/[^\s\"';&|]*)*)",
        text,
    )
    for token in tokens:
        candidate = token.strip("\"'")
        if not candidate or candidate.startswith("//"):
            continue
        if candidate in ("/dev/null", "/dev/stdout", "/dev/stderr"):
            continue
        expanded = (
            candidate.replace("${HOME}", str(Path.home()))
            .replace("$HOME", str(Path.home()))
        )
        target = resolve_path(expanded, root)
        if not is_within(target, root):
            return f"命令引用了工作目录外路径：{target}"
    return ""


def full_access_decision(
    tool_name: str, tool_input: dict, work_dir: str
) -> ToolDecision:
    """完全权限档的守护：默认放行，只拦凭据、系统目录和系统级危险命令。

    Claude Code 2.1.202 的 bypassPermissions 实测不会执行 deny 规则，
    因此完全权限档改用 dontAsk + 本 hook 逐次放行。
    """
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    hard = hard_denied_decision(tool_name, tool_input, work_dir)
    if hard is not None:
        return hard
    if tool_name in WRITE_TOOLS and not _tool_path(tool_input):
        return ToolDecision(DECISION_DENY, "写入操作缺少可识别路径")
    if tool_name == "Bash":
        reason = critical_command_reason(str(tool_input.get("command") or ""))
        if reason:
            return ToolDecision(DECISION_DENY, reason)
    return ToolDecision(DECISION_ALLOW)


def _tool_path(tool_input: dict) -> str:
    for key in ("file_path", "path", "notebook_path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def classify_tool_call(
    tool_name: str,
    tool_input: dict,
    profile: str,
    work_dir: str,
) -> ToolDecision:
    """判断一次工具调用是否可以直接放行、拒绝或需要管理员审批。"""
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    profile = normalize_profile(profile, PROFILE_READONLY)

    if profile == PROFILE_READONLY:
        if tool_name in WRITE_TOOLS or tool_name == "Bash":
            return ToolDecision(DECISION_DENY, "只读档位不允许修改文件或执行命令")
        if tool_name in READ_TOOLS:
            raw_path = _tool_path(tool_input)
            if not raw_path:
                return ToolDecision(DECISION_NONE)
            root = resolve_path(work_dir) if work_dir else None
            target = resolve_path(raw_path, root)
            if root is not None and not is_within(target, root):
                return ToolDecision(DECISION_DENY, f"只读档位仅限工作目录：{target}")
            hard = hard_denied_decision(tool_name, tool_input, work_dir)
            if hard is not None:
                return hard
        return ToolDecision(DECISION_NONE)

    if profile == PROFILE_FULL:
        return full_access_decision(tool_name, tool_input, work_dir)

    root = resolve_path(work_dir) if work_dir else None
    hard = hard_denied_decision(tool_name, tool_input, work_dir)
    if hard is not None:
        return hard

    if tool_name in WRITE_TOOLS:
        raw_path = _tool_path(tool_input)
        if not raw_path:
            return ToolDecision(DECISION_ASK, f"{tool_name} 未提供可识别路径")
        target = resolve_path(raw_path, root)
        if root is not None and is_within(target, root):
            return ToolDecision(DECISION_NONE)
        return ToolDecision(
            DECISION_ASK, f"{tool_name} 目标路径在工作目录外：{target}"
        )

    if tool_name in READ_TOOLS:
        raw_path = _tool_path(tool_input)
        if not raw_path:
            # Grep/Glob 的 path 可省略，默认就是当前工作目录。
            return ToolDecision(DECISION_NONE)
        target = resolve_path(raw_path, root)
        if root is not None and is_within(target, root):
            return ToolDecision(DECISION_NONE)
        return ToolDecision(
            DECISION_ASK, f"{tool_name} 目标路径在工作目录外：{target}"
        )

    if tool_name == "Bash":
        if bool(tool_input.get("dangerouslyDisableSandbox")):
            return ToolDecision(DECISION_ASK, "申请脱离沙箱执行命令")
        command = str(tool_input.get("command") or "")
        reason = dangerous_command_reason(command)
        if reason:
            return ToolDecision(DECISION_ASK, reason)
        outside = outside_path_reference(command, work_dir)
        if outside:
            return ToolDecision(DECISION_ASK, outside)
        return ToolDecision(DECISION_NONE)

    return ToolDecision(DECISION_NONE)


def clamp_approval_timeout(value, default: int, minimum: int, maximum: int) -> int:
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, seconds))
