"""重新生成 suite 报告（Aggregate Report）。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:  # 直接执行 scripts/aggregate_report.py
    from engine_path import ensure_engine_importable
except ImportError:  # 作为模块执行（python3 -m scripts.aggregate_report）
    from scripts.engine_path import ensure_engine_importable


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="重新生成 AstrBot 插件测试报告")
    parser.add_argument("--suite-dir", required=True)
    parser.add_argument("--config", default=None)
    parser.add_argument("--no-redact", action="store_true")
    args = parser.parse_args(argv)

    suite_dir = Path(args.suite_dir).expanduser()
    report = suite_dir / "report.json"
    if not report.exists():
        print("报告不存在: {}".format(report), file=sys.stderr)
        return 2
    ensure_engine_importable()
    from astrbot_e2e.config import load_config
    from astrbot_e2e.reports import write_suite_report

    cfg = load_config(args.config) if args.config else {}
    suite = json.loads(report.read_text(encoding="utf-8-sig"))
    write_suite_report(suite_dir, suite, cfg, redact=not args.no_redact)
    print(str(suite_dir / "report.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
