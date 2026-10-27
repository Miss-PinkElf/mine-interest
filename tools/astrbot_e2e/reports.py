"""运行目录、JSON 报告与失败证据（Report）。"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def slugify(name: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z_-]+", "-", str(name)).strip("-")
    return slug or "case"


def create_run_dir(base: Any, case_name: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    path = Path(base) / "{}-{}".format(stamp, slugify(case_name))
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_json(path: Any, data: Any) -> None:
    Path(path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def write_summary(
    run_dir: Any,
    case_name: str,
    status: str,
    results: List[Any],
    duration_seconds: float,
    extra: Dict[str, Any] = None,
) -> Dict[str, Any]:
    summary = {
        "case": case_name,
        "status": status,
        "duration_seconds": round(float(duration_seconds), 3),
        "assertions": [
            {
                "kind": item.kind,
                "ok": item.ok,
                "expected": item.expected,
                "actual": item.actual,
                "detail": item.detail,
            }
            for item in results
        ],
    }
    if extra:
        summary.update(extra)
    write_json(Path(run_dir) / "summary.json", summary)
    return summary
