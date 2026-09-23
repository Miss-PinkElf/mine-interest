"""Vault 安全发布（Safe Publication）：独立 Git 历史与 Markdown 允许清单。"""

from __future__ import annotations

import fcntl
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit, urlunsplit


DEFAULT_PUBLISH_REMOTE = "git@github.com:Miss-PinkElf/data-hub.git"
PUBLISH_DIR_SUFFIX = "-publish"
PUBLISH_BRANCH = "main"
PUBLISH_COMMIT_MESSAGE = "资料同步"
PUBLISH_LOCK_FILE = "publish.lock"
GIT_TIMEOUT_SECONDS = 30
PRIVATE_CHECK_TIMEOUT_SECONDS = 10
PUBLISH_INTERVAL_SECONDS = 30
SENSITIVE_TEXT = re.compile(
    r"(?i)\b(?:rkey|sessdata|access_token|refresh_token|csrf|authorization|cookie)\b\s*[:=]\s*\S+"
)
EXTERNAL_URL = re.compile(r"https?://[^\s<>)\]\"']+")
REDACTED_CREDENTIAL = "[鉴权信息已移除]"
GITHUB_REMOTE = re.compile(r"^git@github\.com:([\w.-]+/[\w.-]+)\.git$")
GITHUB_API_REPOSITORY = "https://api.github.com/repos/"
GIT_SSH_READ_ONLY = "ssh -o BatchMode=yes -o ConnectTimeout=5"


class PublishError(Exception):
    """发布失败类别；不包含正文或鉴权链接。"""


def sanitize_markdown(body: str) -> str:
    """发布副本移除外链查询参数与已知凭据，保留 Vault 原文。"""
    def strip_query(match: re.Match) -> str:
        parts = urlsplit(match.group(0))
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))

    return SENSITIVE_TEXT.sub(REDACTED_CREDENTIAL, EXTERNAL_URL.sub(strip_query, body))


def verify_private_remote(remote: str) -> bool:
    """匿名 API 不可见且 SSH 可访问，才认定目标为私有仓库。"""
    match = GITHUB_REMOTE.fullmatch(remote)
    if not match:
        return False
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        opener.open(
            urllib.request.Request(GITHUB_API_REPOSITORY + match.group(1)),
            timeout=PRIVATE_CHECK_TIMEOUT_SECONDS,
        )
        return False
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            return False
    except (OSError, ValueError):
        return False
    try:
        result = subprocess.run(
            ["git", "ls-remote", remote, "HEAD"],
            capture_output=True, text=True, timeout=PRIVATE_CHECK_TIMEOUT_SECONDS,
            env={**os.environ, "GIT_SSH_COMMAND": GIT_SSH_READ_ONLY},
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


class Publisher:
    """只投影 `items/**/*.md`，不接触 Vault 自身 Git 历史。"""

    def __init__(
        self,
        source: Path,
        publish_dir: Path | None = None,
        remote: str = DEFAULT_PUBLISH_REMOTE,
        private_check: Callable[[], bool] | None = None,
    ):
        self.source = source
        self.publish_dir = publish_dir or source.with_name(source.name + PUBLISH_DIR_SUFFIX)
        self.remote = remote
        self.private_check = private_check or (lambda: verify_private_remote(self.remote))
        if self.source.resolve() == self.publish_dir.resolve() or self.source.resolve() in self.publish_dir.resolve().parents:
            raise PublishError("publish_dir_inside_vault")

    def sync_once(self) -> bool:
        sources = self._allowed_files()
        if not self.private_check():
            raise PublishError("remote_private_unverified")
        spool = self.source / "spool"
        spool.mkdir(parents=True, exist_ok=True)
        with (spool / PUBLISH_LOCK_FILE).open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            self._ensure_repo()
            self._project(sources)
            self._git("add", "--all", "--", "items")
            changed = bool(self._git("status", "--porcelain", "--", "items").stdout.strip())
            if changed:
                self._git("commit", "-m", PUBLISH_COMMIT_MESSAGE)
            self._git("push", "origin", PUBLISH_BRANCH)
            return changed

    def _allowed_files(self) -> dict[Path, str]:
        allowed = {}
        for path in (self.source / "items").rglob("*.md"):
            if path.is_symlink() or not path.is_file():
                raise PublishError("unsafe_source_file")
            body = sanitize_markdown(path.read_text(encoding="utf-8"))
            if SENSITIVE_TEXT.search(body):
                raise PublishError(f"sensitive_markdown:{path.relative_to(self.source)}")
            allowed[path.relative_to(self.source)] = body
        return allowed

    def _ensure_repo(self) -> None:
        if self.publish_dir.exists():
            if not (self.publish_dir / ".git").is_dir():
                raise PublishError("publish_dir_not_git")
            if self._git("remote", "get-url", "origin").stdout.strip() != self.remote:
                raise PublishError("publish_remote_mismatch")
            return
        try:
            subprocess.run(
                ["git", "clone", "--", self.remote, str(self.publish_dir)],
                check=True, capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise PublishError("git_clone_failed") from exc
        self._git("branch", "-M", PUBLISH_BRANCH)
        self._git("config", "user.email", "sourcehub@local")
        self._git("config", "user.name", "sourcehub")

    def _project(self, sources: dict[Path, str]) -> None:
        item_root = self.publish_dir / "items"
        if item_root.exists():
            for old in item_root.rglob("*.md"):
                if old.relative_to(self.publish_dir) not in sources:
                    old.unlink()
        for relative, body in sources.items():
            target = self.publish_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or target.read_text(encoding="utf-8") != body:
                target.write_text(body, encoding="utf-8")

    def _git(self, *args: str) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                ["git", "-C", str(self.publish_dir), *args],
                check=True, capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise PublishError(f"git_{args[0]}_failed") from exc
