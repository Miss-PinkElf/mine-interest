#!/usr/bin/env python3
"""
Shared path helpers for the session-handoff skill.

Canonical layout:
    <project>/.codex/explore/<explore-slug>/
        handoff.md
        state.md
        handoffs/
            YYYY-MM-DD-HHMMSS-<slug>.md
"""

from __future__ import annotations

import os
from pathlib import Path


def find_project_root(start: str | Path | None = None) -> Path:
    """Find the nearest project root by looking for .codex or .git."""
    current = Path(start or os.getcwd()).resolve()

    for candidate in (current, *current.parents):
        if (candidate / ".codex").exists() or (candidate / ".git").exists():
            return candidate

    return current


def detect_explore_dir_from_path(start: str | Path | None = None) -> Path | None:
    """Detect whether a path is inside .codex/explore/<slug>/."""
    current = Path(start or os.getcwd()).resolve()

    for candidate in (current, *current.parents):
        if candidate.parent.name == "explore" and candidate.parent.parent.name == ".codex":
            return candidate

    return None


def resolve_explore_dir(
    project_path: str | Path,
    explore_dir: str | Path | None = None,
    cwd: str | Path | None = None,
    default_slug: str = "general",
) -> Path:
    """
    Resolve the active explore directory.

    Resolution order:
    1. Explicit --explore-dir argument
    2. Current working directory if already inside .codex/explore/<slug>/
    3. Fallback to .codex/explore/<default_slug>/
    """
    project_root = Path(project_path).resolve()

    if explore_dir:
        target = Path(explore_dir)
        if not target.is_absolute():
            target = (project_root / target).resolve()
        else:
            target = target.resolve()

        if target.name == "handoffs":
            return target.parent
        return target

    detected = detect_explore_dir_from_path(cwd)
    if detected is not None:
        return detected

    return project_root / ".codex" / "explore" / default_slug


def handoffs_dir_for_explore(explore_dir: str | Path) -> Path:
    """Return the canonical handoffs directory for an explore workspace."""
    return Path(explore_dir).resolve() / "handoffs"


def relative_to_project(path: str | Path, project_path: str | Path) -> str:
    """Format a path relative to project root when possible."""
    target = Path(path).resolve()
    project_root = Path(project_path).resolve()

    try:
        return str(target.relative_to(project_root)).replace("\\", "/")
    except ValueError:
        return str(target)


def infer_project_root_from_handoff(handoff_path: str | Path) -> Path:
    """Infer project root from a handoff file path."""
    path = Path(handoff_path).resolve()

    for candidate in (path.parent, *path.parents):
        if candidate.name == ".codex":
            return candidate.parent

    return find_project_root(path.parent)

