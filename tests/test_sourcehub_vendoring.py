"""sourcehub 多副本一致性守卫（Vendoring Guard）。

背景见 `tests/__init__.py`：`sourcehub` 在两处插件目录下各存一份。本测试把两件
原本靠人肉记忆保证的事变成会失败的断言：

1. 测试实际加载的是哪一份副本（不能由 PYTHONPATH 顺序决定）；
2. 两份副本是否保持一致（只改一边时必须立刻失败）。
"""

from __future__ import annotations

import filecmp
import unittest
from pathlib import Path

import sourcehub

from . import CANONICAL_PLUGIN_DIR

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO_ROOT / "integrations" / "astrbot"

#: sourcehub 包目录名，两份副本与内置变量 `sourcehub.__name__` 共用同一取值。
PACKAGE_DIR_NAME = "sourcehub"

#: 各插件内自包含的 sourcehub 副本；键仅用于报错信息。
VENDORED_COPIES = {
    "bilibili": PLUGIN_ROOT / "astrbot_plugin_sourcehub_bilibili" / PACKAGE_DIR_NAME,
    "inspector": PLUGIN_ROOT / "astrbot_plugin_sourcehub_inspector" / PACKAGE_DIR_NAME,
}

#: 与 `tests/__init__.py` 保持一致；副本一致时该选择无强弱之分，只求显式。
CANONICAL_COPY = "inspector"

#: 字节码目录随运行环境变化，不参与一致性比对。
IGNORED_NAMES = ["__pycache__", "*.pyc"]


class SourceHubVendoringTests(unittest.TestCase):
    def test_imported_sourcehub_comes_from_declared_copy(self):
        """实际加载的副本必须等于显式声明的那一份。"""
        expected = VENDORED_COPIES[CANONICAL_COPY].resolve()
        actual = Path(sourcehub.__file__).resolve().parent
        self.assertEqual(
            actual,
            expected,
            f"sourcehub 实际加载自 {actual}，期望 {expected}；"
            f"确认 tests/__init__.py 的引导未被绕过",
        )

    def test_declared_copy_is_the_bootstrapped_one(self):
        """声明路径与引导路径必须指向同一份副本，避免两处各写各的。"""
        bootstrapped = (CANONICAL_PLUGIN_DIR / PACKAGE_DIR_NAME).resolve()
        self.assertEqual(
            VENDORED_COPIES[CANONICAL_COPY].resolve(),
            bootstrapped,
            "本文件的 CANONICAL_COPY 与 tests/__init__.py 的 CANONICAL_PLUGIN_DIR 不一致",
        )

    def test_vendored_copies_stay_identical(self):
        """两份副本必须字节级一致；出现差异说明只改了一边。"""
        names = sorted(VENDORED_COPIES)
        base_name, base = names[0], VENDORED_COPIES[names[0]]
        for other_name in names[1:]:
            other = VENDORED_COPIES[other_name]
            self.assertTrue(base.is_dir(), f"副本目录不存在：{base}")
            self.assertTrue(other.is_dir(), f"副本目录不存在：{other}")
            differences = self._differences(filecmp.dircmp(base, other, ignore=IGNORED_NAMES))
            self.assertEqual(
                differences,
                [],
                f"{base_name} 与 {other_name} 的 sourcehub 副本已分叉，请同步两份：\n  "
                + "\n  ".join(differences),
            )

    def _differences(self, comparison: filecmp.dircmp) -> list[str]:
        """递归收集目录比较结果，返回可读的差异描述。"""
        found = [f"仅存在于 {comparison.left}：{name}" for name in comparison.left_only]
        found += [f"仅存在于 {comparison.right}：{name}" for name in comparison.right_only]
        found += [
            f"内容不同：{Path(comparison.left) / name}" for name in comparison.diff_files
        ]
        for subdir in comparison.subdirs.values():
            found += self._differences(subdir)
        return found


if __name__ == "__main__":
    unittest.main()
