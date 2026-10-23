"""插件主类命名守卫（Name Guard）：实例属性不得遮蔽同名方法。

背景：inspector 插件曾把 `self._github_reply` 赋成布尔开关，同时又定义了同名
方法，导致 `await self._github_reply(event)` 实际是在 `await True(event)`，
QQ 消息处理在入口处直接抛 TypeError。此类错误不依赖运行环境，静态即可发现。
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "integrations" / "astrbot"
MAIN_FILE_PATTERN = "*/main.py"


def _assigned_self_attributes(method: ast.AST) -> set[str]:
    """收集方法体内所有 `self.<name> = ...` 形式的属性名。"""
    names: set[str] = set()
    for node in ast.walk(method):
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        for target in targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
            ):
                names.add(target.attr)
    return names


def _method_names(class_def: ast.ClassDef) -> set[str]:
    return {
        node.name
        for node in class_def.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _assigned_in_class(class_def: ast.ClassDef) -> set[str]:
    names: set[str] = set()
    for node in class_def.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names |= _assigned_self_attributes(node)
    return names


class PluginNameCollisionTests(unittest.TestCase):
    def test_no_instance_attribute_shadows_method(self):
        problems: list[str] = []
        for main_path in sorted(PLUGIN_ROOT.glob(MAIN_FILE_PATTERN)):
            tree = ast.parse(main_path.read_text(encoding="utf-8"))
            for class_def in (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)):
                collisions = _method_names(class_def) & _assigned_in_class(class_def)
                if collisions:
                    relative = main_path.relative_to(ROOT)
                    names = "、".join(sorted(collisions))
                    problems.append(f"{relative}::{class_def.name} -> {names}")
        self.assertFalse(
            problems,
            "实例属性遮蔽了同名方法（实例属性优先，方法将无法调用）：\n" + "\n".join(problems),
        )


if __name__ == "__main__":
    unittest.main()
