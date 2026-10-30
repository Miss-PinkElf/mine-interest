"""定位执行引擎：优先项目内 tools/astrbot_e2e，其次 vendor 快照。"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional


def engine_dir(start: Optional[Path] = None) -> Optional[Path]:
    skill_root = Path(__file__).resolve().parents[1]
    current = Path(start or Path.cwd()).resolve()
    for base in [current, *current.parents]:
        candidate = base / "tools" / "astrbot_e2e"
        if (candidate / "__init__.py").exists():
            return candidate
    vendor = skill_root / "vendor" / "astrbot_e2e"
    if (vendor / "__init__.py").exists():
        return vendor
    return None


def ensure_engine_importable(start: Optional[Path] = None) -> Path:
    engine = engine_dir(start)
    if engine is None:
        raise RuntimeError(
            "未找到 astrbot_e2e 执行引擎；请在本仓库运行，或先执行 scripts/sync_vendor.py"
        )
    package_root = engine.parent
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))
    return engine
