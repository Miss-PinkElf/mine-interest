"""Vault 安全发布（Safe Publication）：独立 Git 历史与 Markdown 允许清单。"""

from __future__ import annotations

import fcntl
import json
import os
import re
import subprocess
import tempfile
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
PUSH_CHECK_BRANCH = "refs/heads/main"
PUSH_CHECK_AUTHOR = "sourcehub-access-check"
PUSH_CHECK_EMAIL = "sourcehub-access-check@local"
REMOTE_INVALID = "remote_invalid"
REMOTE_NOT_PRIVATE = "not_private"
REMOTE_PRIVATE_UNKNOWN = "private_check_failed"
REMOTE_UNREADABLE = "ssh_unreadable"
REMOTE_PUSH_OK = "push_ok"
REMOTE_PUSH_DENIED = "push_denied"
REMOTE_PUSH_FAILED = "push_failed"
PUSH_DENIED_MARKERS = ("permission denied", "denied to", "not authorized", "forbidden")


class PublishError(Exception):
    """发布失败类别；不包含正文或鉴权链接。"""


def sanitize_markdown(body: str) -> str:
    """发布副本移除外链查询参数与已知凭据，保留 Vault 原文。"""
    def strip_query(match: re.Match) -> str:
        parts = urlsplit(match.group(0))
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))

    return SENSITIVE_TEXT.sub(REDACTED_CREDENTIAL, EXTERNAL_URL.sub(strip_query, body))


def _git_env() -> dict[str, str]:
    return {**os.environ, "GIT_SSH_COMMAND": GIT_SSH_READ_ONLY, "GIT_TERMINAL_PROMPT": "0"}


def _repository_name(remote: str) -> str:
    match = GITHUB_REMOTE.fullmatch(remote)
    return match.group(1) if match else ""


def github_account_access(repository: str) -> dict[str, bool] | None:
    """用本机已登录的 gh 读取私有性和推送权限。未登录或接口失败时不猜测。"""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{repository}", "--jq", "{private:.private,push:.permissions.push}"],
            capture_output=True, text=True, timeout=PRIVATE_CHECK_TIMEOUT_SECONDS,
            env={**os.environ, "GH_PROMPT_DISABLED": "1"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
    except ValueError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("private"), bool):
        return None
    return {"private": data["private"], "push": bool(data.get("push"))}


def _anonymous_private(remote: str) -> bool | None:
    """匿名接口返回 404 才是私有。公开仓库返回 False，网络或其它状态返回 None。"""
    name = _repository_name(remote)
    if not name:
        return None
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        opener.open(
            urllib.request.Request(GITHUB_API_REPOSITORY + name),
            timeout=PRIVATE_CHECK_TIMEOUT_SECONDS,
        )
        return False
    except urllib.error.HTTPError as exc:
        return True if exc.code == 404 else None
    except (OSError, ValueError):
        return None


def _ssh_readable(remote: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "ls-remote", remote, "HEAD"],
            capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS,
            env=_git_env(),
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _run_git(workdir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(workdir), *args],
        capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS, env=_git_env(),
    )


def ssh_push_dry_run(remote: str) -> str:
    """用演练推送确认当前身份能否写入。不更新远端引用。"""
    with tempfile.TemporaryDirectory(prefix="sourcehub-push-check-") as temporary:
        workdir = Path(temporary) / "repo"
        try:
            cloned = subprocess.run(
                ["git", "clone", "--depth", "1", "--", remote, str(workdir)],
                capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS, env=_git_env(),
            )
        except (OSError, subprocess.TimeoutExpired):
            return REMOTE_UNREADABLE
        if cloned.returncode != 0:
            return REMOTE_UNREADABLE
        has_head = _run_git(workdir, "rev-parse", "--verify", "HEAD").returncode == 0
        if not has_head:
            if _run_git(workdir, "checkout", "-B", "main").returncode != 0:
                return REMOTE_PUSH_FAILED
            _run_git(workdir, "config", "user.name", PUSH_CHECK_AUTHOR)
            _run_git(workdir, "config", "user.email", PUSH_CHECK_EMAIL)
            if _run_git(workdir, "commit", "--allow-empty", "-m", "push permission check").returncode != 0:
                return REMOTE_PUSH_FAILED
        try:
            pushed = _run_git(workdir, "push", "--dry-run", "origin", f"HEAD:{PUSH_CHECK_BRANCH}")
        except (OSError, subprocess.TimeoutExpired):
            return REMOTE_PUSH_FAILED
    if pushed.returncode == 0:
        return REMOTE_PUSH_OK
    detail = f"{pushed.stderr}\n{pushed.stdout}".lower()
    if any(marker in detail for marker in PUSH_DENIED_MARKERS):
        return REMOTE_PUSH_DENIED
    return REMOTE_PUSH_FAILED


def verify_private_remote(remote: str) -> bool:
    """匿名 API 不可见且 SSH 可访问，才认定目标为私有仓库。"""
    return _anonymous_private(remote) is True and _ssh_readable(remote)


def verify_remote_access(remote: str) -> dict[str, object]:
    """检查地址、私有性、SSH 读取和演练推送。失败原因只使用类别码。"""
    repository = _repository_name(remote)
    result = {
        "repository": repository,
        "private": False,
        "readable": False,
        "pushable": False,
        "reason": REMOTE_INVALID,
    }
    if not repository:
        return result
    account = github_account_access(repository)
    if account is None:
        private = _anonymous_private(remote)
    else:
        private = account["private"]
    result["private"] = private
    if not _ssh_readable(remote):
        result["reason"] = REMOTE_UNREADABLE
        return result
    result["readable"] = True
    reason = ssh_push_dry_run(remote)
    result["pushable"] = reason == REMOTE_PUSH_OK
    if private is False:
        result["reason"] = REMOTE_NOT_PRIVATE
    elif private is None and reason == REMOTE_PUSH_OK:
        result["reason"] = REMOTE_PRIVATE_UNKNOWN
    else:
        result["reason"] = reason
    return result


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
