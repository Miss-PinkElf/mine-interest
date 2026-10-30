"""从插件源码与文档提取功能清单（Feature Inventory）。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

COMMAND_PATTERNS = (
    re.compile(r"@filter\.command\(\s*[\"']([^\"']+)[\"']"),
    re.compile(r"@filter\.command_group\(\s*[\"']([^\"']+)[\"']"),
    re.compile(r"register_command\(\s*[\"']([^\"']+)[\"']"),
    re.compile(r"\bCommand\(\s*[\"'](/[^\"']+)[\"']"),
)
EVENT_PATTERN = re.compile(
    r"@filter\.event_message_type\(\s*([A-Za-z0-9_.]+)"
)
HOOK_PATTERN = re.compile(
    r"@filter\.(on_llm_request|on_decorating_result|on_after_message_sent)"
)
README_COMMAND_PATTERN = re.compile(r"`(/[A-Za-z0-9_!]+)(?:\s+[^`]*)?`")
DANGEROUS_COMMANDS = frozenset(
    {
        "/cc",
        "/goon",
        "/!",
        "/new",
        "/resume",
        "/end",
        "/cd",
        "/initbase",
        "/approve",
        "/deny",
    }
)
NON_COMMAND_PATHS = frozenset(
    {
        "/tmp",
        "/etc",
        "/usr",
        "/System",
        "/Library",
        "/var",
        "/home",
        "/bin",
        "/sbin",
        "/opt",
        "/private",
        "/Applications",
        "/Volumes",
        "/dev",
        "/root",
        "/proc",
    }
)


def parse_metadata(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    current = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current:
            data.setdefault(current, []).append(line[4:].strip())
            continue
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value:
                data[key] = value
                current = None
            else:
                data[key] = []
                current = key
    return data


def _slugify(value: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z_-]+", "-", value).strip("-")
    return slug or "feature"


def scan_python(plugin_dir: Path) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[Dict[str, str]]]:
    commands: List[Dict[str, str]] = []
    events: List[Dict[str, str]] = []
    hooks: List[Dict[str, str]] = []
    for path in sorted(plugin_dir.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = str(path.relative_to(plugin_dir))
        for pattern in COMMAND_PATTERNS:
            for match in pattern.findall(text):
                commands.append({"command": "/" + match.lstrip("/"), "source": relative})
        for match in EVENT_PATTERN.findall(text):
            events.append({"event": match, "source": relative})
        for match in HOOK_PATTERN.findall(text):
            hooks.append({"hook": match, "source": relative})
    return commands, events, hooks


def scan_readme(plugin_dir: Path) -> List[Dict[str, str]]:
    readme = plugin_dir / "README.md"
    if not readme.exists():
        return []
    commands: List[Dict[str, str]] = []
    for line_no, line in enumerate(readme.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        for match in README_COMMAND_PATTERN.finditer(line):
            commands.append(
                {
                    "command": match.group(1),
                    "source": "README.md:{}".format(line_no),
                    "line": line.strip()[:200],
                }
            )
    return commands


def build_features(plugin_dir: Path) -> Dict[str, Any]:
    plugin_dir = Path(plugin_dir)
    if not plugin_dir.is_dir():
        raise RuntimeError("插件目录不存在: {}".format(plugin_dir))
    metadata_path = plugin_dir / "metadata.yaml"
    metadata = (
        parse_metadata(metadata_path.read_text(encoding="utf-8", errors="replace"))
        if metadata_path.exists()
        else {}
    )
    schema_path = plugin_dir / "_conf_schema.json"
    schema = {}
    if schema_path.exists():
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
        except ValueError:
            schema = {}

    decorator_commands, events, hooks = scan_python(plugin_dir)
    readme_commands = scan_readme(plugin_dir)

    features: List[Dict[str, Any]] = []
    seen = set()
    for item in readme_commands + decorator_commands:
        command = item["command"]
        if command in NON_COMMAND_PATHS:
            continue
        if command in seen:
            continue
        seen.add(command)
        features.append(
            {
                "id": "command-" + _slugify(command.lstrip("/")),
                "title": "命令 {}".format(command),
                "kind": "command",
                "trigger": command,
                "expected": "",
                "testability": "text",
                "risk": "high" if command in DANGEROUS_COMMANDS else "medium",
                "notes": item.get("line") or item.get("source", ""),
            }
        )

    seen_events = set()
    for item in events:
        if item["event"] in seen_events:
            continue
        seen_events.add(item["event"])
        features.append(
            {
                "id": "event-" + _slugify(item["event"]),
                "title": "事件 {}".format(item["event"]),
                "kind": "event",
                "trigger": item["event"],
                "expected": "",
                "testability": "manual",
                "risk": "medium",
                "notes": item["source"],
            }
        )

    seen_hooks = set()
    for item in hooks:
        if item["hook"] in seen_hooks:
            continue
        seen_hooks.add(item["hook"])
        features.append(
            {
                "id": "hook-" + _slugify(item["hook"]),
                "title": "钩子 {}".format(item["hook"]),
                "kind": "hook",
                "trigger": item["hook"],
                "expected": "",
                "testability": "manual",
                "risk": "medium",
                "notes": item["source"],
            }
        )

    if isinstance(schema, dict):
        for key in schema:
            features.append(
                {
                    "id": "config-" + _slugify(str(key)),
                    "title": "配置 {}".format(key),
                    "kind": "config",
                    "trigger": str(key),
                    "expected": "",
                    "testability": "config",
                    "risk": "low",
                    "notes": "_conf_schema.json",
                }
            )

    plugin_name = metadata.get("name") or plugin_dir.name
    return {
        "plugin": plugin_name,
        "plugin_dir": str(plugin_dir),
        "metadata": metadata,
        "features": features,
        "summary": {
            "total": len(features),
            "commands": sum(1 for item in features if item["kind"] == "command"),
            "events": sum(1 for item in features if item["kind"] == "event"),
            "hooks": sum(1 for item in features if item["kind"] == "hook"),
            "config": sum(1 for item in features if item["kind"] == "config"),
            "manual": sum(
                1 for item in features if item["testability"] in ("manual", "config")
            ),
        },
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="提取 AstrBot 插件功能清单")
    parser.add_argument("--plugin-dir", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)
    result = build_features(Path(args.plugin_dir).expanduser())
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
