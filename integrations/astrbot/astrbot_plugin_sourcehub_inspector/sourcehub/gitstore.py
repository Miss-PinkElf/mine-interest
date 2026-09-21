"""Vault 本地 Git：只提交原文，不 push。"""

from __future__ import annotations

import subprocess
from pathlib import Path

GITIGNORE = "private/\nspool/\n*.sqlite3\n"


def ensure_repo(root: Path) -> None:
    if not (root / ".git").exists():
        _run(root, ["git", "init"])
        _run(root, ["git", "config", "user.email", "sourcehub@local"])
        _run(root, ["git", "config", "user.name", "sourcehub"])
    ignore = root / ".gitignore"
    if not ignore.exists():
        ignore.write_text(GITIGNORE, encoding="utf-8")


def commit_item(root: Path, item_id: str, relpath: str) -> None:
    ensure_repo(root)
    _run(root, ["git", "add", "--", relpath, ".gitignore"])
    status = _run(root, ["git", "status", "--porcelain"], check=False)
    if not status.stdout.strip():
        return
    _run(root, ["git", "commit", "-m", f"sourcehub: {item_id}"])


def _run(root: Path, command: list[str], check: bool = True):
    return subprocess.run(
        command,
        cwd=root,
        check=check,
        capture_output=True,
        text=True,
    )
