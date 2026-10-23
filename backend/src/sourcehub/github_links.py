"""GitHub 仓库链接解析（GitHub Repository Link Parsing）。"""

from __future__ import annotations

import re

# 支持带协议、不带协议、www 前缀，以及 /tree/main 这类子路径。
# 前面的负向断言避免把 gist.github.com 之类子域误识别成仓库链接。
GITHUB_REPOSITORY_URL = re.compile(
    r"(?<![\w.-])(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)",
    re.IGNORECASE,
)

# /fork 作为独立 token 识别：允许前面是中文或空格，但不允许 /forked、//fork。
FORK_COMMAND = re.compile(r"(?i)(?<![A-Za-z0-9_/])/fork(?![A-Za-z0-9_/])")

# GitHub 的固定功能路径不是仓库，不能触发 star/fork。
RESERVED_OWNERS = frozenset(
    {
        "about",
        "account",
        "apps",
        "collections",
        "contact",
        "customer-stories",
        "dashboard",
        "enterprise",
        "events",
        "explore",
        "features",
        "git-guides",
        "home",
        "issues",
        "join",
        "login",
        "marketplace",
        "mobile",
        "new",
        "notifications",
        "organizations",
        "orgs",
        "pricing",
        "pulls",
        "readme",
        "search",
        "security",
        "settings",
        "site",
        "solutions",
        "sponsors",
        "topics",
        "trending",
        "users",
        "watching",
    }
)

TRAILING_REPOSITORY_CHARS = ".-"


def _clean_repository(owner: str, repository: str) -> str | None:
    """把 URL 片段规范成 owner/repo；非仓库路径返回 None。"""
    owner = owner.strip(TRAILING_REPOSITORY_CHARS)
    repository = repository.rstrip(TRAILING_REPOSITORY_CHARS)
    if repository.lower().endswith(".git"):
        repository = repository[:-4].rstrip(TRAILING_REPOSITORY_CHARS)
    if not owner or not repository:
        return None
    if owner.lower() in RESERVED_OWNERS:
        return None
    return f"{owner}/{repository}"


def extract_repository_links(text: str) -> list[str]:
    """按出现顺序返回去重后的仓库全名；大小写不同视为同一个仓库。"""
    repositories: list[str] = []
    seen: set[str] = set()
    for match in GITHUB_REPOSITORY_URL.finditer(text or ""):
        normalized = _clean_repository(match.group(1), match.group(2))
        if normalized is None:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        repositories.append(normalized)
    return repositories


def fork_requested(text: str) -> bool:
    """判断文本中是否出现独立的 /fork 命令。"""
    return bool(FORK_COMMAND.search(text or ""))
