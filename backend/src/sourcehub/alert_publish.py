"""独立 GitHub 提醒发布器（Alert Publisher）。"""

from __future__ import annotations

import fcntl
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Callable

from .alerts import EVENT_LABELS
from .publish import GIT_TIMEOUT_SECONDS, verify_private_remote

ALERT_BRANCH = "main"
ALERT_COMMIT_AUTHOR = "sourcehub-alerts"
ALERT_COMMIT_EMAIL = "sourcehub-alerts@local"
ALERT_DIR_SUFFIX = "-alerts-publish"
ALERT_FILE = re.compile(r"events/[0-9]+\.md")
REDACTED_ACCOUNT = re.compile(r"尾号 [0-9]{1,4}")


class AlertPublishError(Exception):
    """仅暴露失败类别，不包含 Git remote 或凭据。"""


class AlertPublisher:
    def __init__(self, directory: Path, remote: str, private_check: Callable[[], bool] | None = None):
        self.directory = directory
        self.remote = remote
        self.private_check = private_check or (lambda: verify_private_remote(remote))
        if not remote:
            raise AlertPublishError("alert_remote_missing")
        self.lock_path = directory.with_suffix(".lock")

    def _git(self, workdir: Path, *args: str) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                ["git", "-C", str(workdir), *args],
                check=True, capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise AlertPublishError(f"alert_git_{args[0]}_failed") from exc

    def _fresh_clone(self, workdir: Path) -> None:
        try:
            subprocess.run(
                ["git", "clone", "--", self.remote, str(workdir)],
                check=True, capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise AlertPublishError("alert_git_clone_failed") from exc
        main_ref = subprocess.run(
            ["git", "-C", str(workdir), "show-ref", "--verify", "--quiet", "refs/remotes/origin/main"],
            capture_output=True,
        )
        if main_ref.returncode == 0:
            self._git(workdir, "checkout", "-B", ALERT_BRANCH, "origin/main")
        else:
            self._git(workdir, "checkout", "-B", ALERT_BRANCH)
        head = subprocess.run(["git", "-C", str(workdir), "rev-parse", "--verify", "HEAD"], capture_output=True)
        if head.returncode == 0:
            files = self._git(workdir, "ls-tree", "-r", "--name-only", "HEAD").stdout.splitlines()
            if any(not ALERT_FILE.fullmatch(name) for name in files):
                raise AlertPublishError("alert_remote_unexpected_files")
        self._git(workdir, "config", "user.name", ALERT_COMMIT_AUTHOR)
        self._git(workdir, "config", "user.email", ALERT_COMMIT_EMAIL)

    def publish(self, event: dict) -> bool:
        if not self.private_check():
            raise AlertPublishError("alert_remote_private_unverified")
        event_id = str(event.get("id") or "")
        status = str(event.get("status") or "")
        platform = str(event.get("platform") or "")
        account = str(event.get("account") or "")
        observed_at = str(event.get("time") or "")
        try:
            datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        except ValueError:
            raise AlertPublishError("invalid_alert_time") from None
        if not event_id.isdecimal() or status not in EVENT_LABELS or platform not in {"bilibili", "qq"} or not REDACTED_ACCOUNT.fullmatch(account):
            raise AlertPublishError("invalid_alert_event")
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            with tempfile.TemporaryDirectory(prefix="sourcehub-alert-", dir=self.directory.parent) as temporary:
                workdir = Path(temporary) / "repo"
                self._fresh_clone(workdir)
                path = workdir / "events" / f"{event_id}.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                body = (
                    f"# {platform} {EVENT_LABELS[status]}\n\n"
                    f"- 账号：{account}\n"
                    f"- 时间：{observed_at}\n"
                    f"- 状态：{status}\n"
                )
                if not path.exists() or path.read_text(encoding="utf-8") != body:
                    path.write_text(body, encoding="utf-8")
                relative = str(path.relative_to(workdir))
                self._git(workdir, "add", "--", relative)
                changed = bool(self._git(workdir, "status", "--porcelain", "--", relative).stdout.strip())
                if changed:
                    self._git(workdir, "commit", "--only", "-m", f"提醒：{platform} {EVENT_LABELS[status]}", "--", relative)
                self._git(workdir, "push", "origin", f"HEAD:{ALERT_BRANCH}")
                return changed
