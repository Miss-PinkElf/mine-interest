"""根据功能清单生成用例草案（Case Generation）。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

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
ARG_PLACEHOLDER = re.compile(r"[<\[{].*?[>\]}]")
SAFE_REPLY_PATTERN = r"\S"


def _slugify(value: str) -> str:
    text = str(value).strip()
    slug = re.sub(r"[^0-9A-Za-z_\-一-鿿]+", "-", text).strip("-")
    if not slug:
        slug = "case-" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return slug


def _generatable(feature: Dict[str, Any]) -> Tuple[bool, str]:
    if feature.get("kind") != "command":
        return False, "非命令功能，需人工设计用例"
    testability = str(feature.get("testability") or "text")
    if testability in ("manual", "config", "rich_media"):
        return False, "功能标记为 {}，需人工设计用例".format(testability)
    trigger = str(feature.get("trigger") or "").strip()
    if not trigger:
        return False, "缺少触发文本"
    base = trigger.split()[0]
    if base in DANGEROUS_COMMANDS:
        return False, "命令会启动代理或改变会话状态，需人工确认用例"
    if ARG_PLACEHOLDER.search(trigger):
        return False, "命令需要参数，需人工补充"
    return True, ""


def _case_for(feature: Dict[str, Any], plugin: str, timeout: float) -> Dict[str, Any]:
    trigger = str(feature["trigger"]).strip()
    return {
        "name": "命令 {}".format(trigger),
        "plugin": plugin,
        "send": {
            "group_id": "{{group_id}}",
            "text": trigger,
            "at_bot": True,
        },
        "expect": {
            "timeout_seconds": timeout,
            "messages": [{"regex": SAFE_REPLY_PATTERN}],
        },
    }


def generate_cases(
    features: Dict[str, Any], output_dir: Path, timeout: float = 30.0
) -> Dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plugin = str(features.get("plugin") or "unknown_plugin")
    generated = 0
    skipped: List[Tuple[str, str]] = []

    for feature in features.get("features") or []:
        ok, reason = _generatable(feature)
        if not ok:
            skipped.append((feature.get("title") or feature.get("id") or "?", reason))
            continue
        case = _case_for(feature, plugin, timeout)
        path = output_dir / (_slugify(feature.get("id") or case["name"]) + ".json")
        path.write_text(
            json.dumps(case, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        generated += 1

    lines = [
        "# 未自动生成的用例",
        "",
        "| 功能 | 原因 |",
        "| --- | --- |",
    ]
    for title, reason in skipped:
        lines.append("| {} | {} |".format(title, reason))
    lines.append("")
    (output_dir / "SKIPPED.md").write_text("\n".join(lines), encoding="utf-8")

    return {
        "plugin": plugin,
        "output_dir": str(output_dir),
        "generated": generated,
        "skipped": len(skipped),
        "skipped_items": [{"title": title, "reason": reason} for title, reason in skipped],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="生成 AstrBot 插件用例草案")
    parser.add_argument("--features", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(argv)
    features = json.loads(Path(args.features).read_text(encoding="utf-8-sig"))
    result = generate_cases(features, Path(args.out), args.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
