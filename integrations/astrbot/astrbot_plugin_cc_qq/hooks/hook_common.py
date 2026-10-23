"""Hook 共用的插件加载与输出工具（Hook Common）。"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))
try:  # 与插件共用常量真相源，避免变量名漂移
    import constants as plugin_constants
except Exception:  # 缺少常量文件时由调用方 fail-closed
    plugin_constants = None


def load_permissions():
    """按文件路径加载，避免依赖插件在 AstrBot 中的目录名。"""
    spec = importlib.util.spec_from_file_location(
        "cc_qq_permissions", PLUGIN_ROOT / "permissions.py"
    )
    module = importlib.util.module_from_spec(spec)
    # dataclass 在延迟注解下需要模块已登记到 sys.modules。
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def emit(decision: str, reason: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(0)
