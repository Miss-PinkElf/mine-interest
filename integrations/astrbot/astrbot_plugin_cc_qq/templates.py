"""基础模板库与 /initbase 初始化（Base Templates）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from .agents.profiles import build_base_claude_settings
from .constants import BASE_TEMPLATE_DIR_NAME, BASE_TEMPLATE_ROOT_NAME

# 需要根据运行时常量生成、而不是静态复制的模板文件。
GENERATED_TEMPLATE_FILES: dict[Path, Callable[[], dict]] = {
    Path(".claude/settings.json"): build_base_claude_settings,
}


def template_root() -> Path:
    return Path(__file__).resolve().parent / BASE_TEMPLATE_DIR_NAME / BASE_TEMPLATE_ROOT_NAME


def init_base_templates(work_dir: str | Path) -> tuple[int, int]:
    """只补缺失文件，不覆盖工作目录里已有内容；返回（新建数，跳过数）。"""
    target_root = Path(work_dir).expanduser()
    if not target_root.is_dir():
        raise FileNotFoundError(str(target_root))
    source_root = template_root()
    relative_paths = {
        source.relative_to(source_root)
        for source in source_root.rglob("*")
        if source.is_file() and "__pycache__" not in source.parts
    }
    relative_paths |= set(GENERATED_TEMPLATE_FILES)

    created = 0
    skipped = 0
    for relative in sorted(relative_paths, key=str):
        target = target_root / relative
        if target.exists():
            skipped += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        generator = GENERATED_TEMPLATE_FILES.get(relative)
        if generator is not None:
            content = json.dumps(
                generator(), ensure_ascii=False, sort_keys=True, indent=2
            )
            target.write_text(content + "\n", encoding="utf-8")
        else:
            target.write_bytes((source_root / relative).read_bytes())
        created += 1
    return created, skipped
