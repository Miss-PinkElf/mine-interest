#!/usr/bin/env python3
"""
List available handoff documents in the current project.

Searches for handoff documents in .codex/explore/<explore-slug>/handoffs/ and displays:
- Filename with date
- Title extracted from document
- Status (if marked complete)

Usage:
    python list_handoffs.py                                 # List handoffs in current project
    python list_handoffs.py .codex/explore/auth-debug      # List handoffs in one explore workspace
    python list_handoffs.py /path/to/project               # List handoffs across all explore workspaces
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from handoff_paths import detect_explore_dir_from_path, find_project_root


def extract_title(filepath: Path) -> str:
    """Extract the title from a handoff document."""
    try:
        content = filepath.read_text()
        # Look for first H1 header
        match = re.search(r'^#\s+(?:Handoff:\s*)?(.+)$', content, re.MULTILINE)
        if match:
            title = match.group(1).strip()
            # Clean up placeholder text
            if title.startswith("[") and title.endswith("]"):
                return "[Untitled - needs completion]"
            return title[:50] + "..." if len(title) > 50 else title
    except Exception:
        pass
    return "[Unable to read title]"


def check_completion_status(filepath: Path) -> str:
    """Check if handoff appears complete or has TODOs remaining."""
    try:
        content = filepath.read_text()
        todo_count = content.count("[TODO:")
        if todo_count == 0:
            return "Complete"
        elif todo_count <= 3:
            return f"In Progress ({todo_count} TODOs)"
        else:
            return f"Needs Work ({todo_count} TODOs)"
    except Exception:
        return "Unknown"


def parse_date_from_filename(filename: str) -> datetime | None:
    """Extract date from filename like 2024-01-15-143022-slug.md"""
    match = re.match(r'(\d{4}-\d{2}-\d{2})-(\d{6})', filename)
    if match:
        try:
            date_str = match.group(1)
            time_str = match.group(2)
            return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H%M%S")
        except ValueError:
            pass
    return None


def collect_handoffs_dirs(target_path: Path) -> list[Path]:
    """Resolve which handoff directories should be scanned."""
    if target_path.name == "handoffs":
        return [target_path]

    if (target_path / "handoffs").exists():
        return [target_path / "handoffs"]

    detected_explore = detect_explore_dir_from_path(target_path)
    if detected_explore is not None:
        return [detected_explore / "handoffs"]

    project_root = find_project_root(target_path)
    explore_root = project_root / ".codex" / "explore"
    if not explore_root.exists():
        return []

    return sorted(
        [child / "handoffs" for child in explore_root.iterdir() if child.is_dir() and (child / "handoffs").exists()],
        key=lambda path: path.parent.name.lower(),
    )


def list_handoffs(target_path: str) -> list[dict]:
    """List all handoff documents reachable from a target path."""
    resolved_target = Path(target_path).resolve()
    handoffs = []

    for handoffs_dir in collect_handoffs_dirs(resolved_target):
        explore_slug = handoffs_dir.parent.name
        for filepath in handoffs_dir.glob("*.md"):
            parsed_date = parse_date_from_filename(filepath.name)
            handoffs.append({
                "path": str(filepath),
                "filename": filepath.name,
                "title": extract_title(filepath),
                "status": check_completion_status(filepath),
                "date": parsed_date,
                "size": filepath.stat().st_size,
                "explore": explore_slug,
                "handoffs_dir": str(handoffs_dir),
            })

    handoffs.sort(key=lambda x: x["date"] or datetime.min, reverse=True)
    return handoffs


def format_date(dt: datetime | None) -> str:
    """Format datetime for display."""
    if dt is None:
        return "Unknown date"
    return dt.strftime("%Y-%m-%d %H:%M")


def main():
    parser = argparse.ArgumentParser(
        description="List handoff documents from one explore workspace or across the project"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=os.getcwd(),
        help="Project root, explore directory, or handoffs directory"
    )
    args = parser.parse_args()

    target_path = args.path
    handoffs = list_handoffs(target_path)

    if not handoffs:
        print(f"No handoffs found under .codex/explore/*/handoffs/ from {Path(target_path).resolve()}")
        print("\nTo create a handoff, run: python create_handoff.py [task-slug]")
        return

    print(f"Found {len(handoffs)} handoff(s) under .codex/explore/*/handoffs/\n")
    print("-" * 80)

    for h in handoffs:
        print(f"  Date: {format_date(h['date'])}")
        print(f"  Explore: {h['explore']}")
        print(f"  Title: {h['title']}")
        print(f"  Status: {h['status']}")
        print(f"  File: {h['filename']}")
        print("-" * 80)

    print(f"\nTo resume from a handoff, read the document and follow the resume checklist.")
    print(f"Most recent: {handoffs[0]['path']}")


if __name__ == "__main__":
    main()
