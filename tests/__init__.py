"""测试包引导（Test Bootstrap）：固定 sys.path，消除 sourcehub 多副本歧义。

`sourcehub` 核心包在两处 AstrBot 插件目录下各存一份：

- `integrations/astrbot/astrbot_plugin_sourcehub_bilibili/sourcehub`
- `integrations/astrbot/astrbot_plugin_sourcehub_inspector/sourcehub`

AstrBot 插件需要自包含才能打包上传，所以副本本身是预期内的。危险在于：19 个测试文件
都写 `from sourcehub.xxx import ...`，**到底加载哪一份取决于 PYTHONPATH 顺序**，
而顺序没有任何地方约束——测试可能一直在验证错误的那份副本，且不会报错。

此处显式声明 inspector 那份为测试加载路径。两份当前字节级一致，这个选择本身没有
强弱之分；写死它的意义是让选择**可见**。一旦两份出现差异，
`tests/test_sourcehub_vendoring.py` 会失败，那时再决定真正的源头，而不是静默选一份。

同时把同样的路径写进 `PYTHONPATH` 环境变量：部分测试会 spawn 子进程执行
`tools/` 下的脚本，子进程不继承本进程的 `sys.path`，必须靠环境变量才能解析
`sourcehub`。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# 测试加载的 sourcehub 副本（见模块 docstring 的取舍说明）。
CANONICAL_PLUGIN_DIR = (
    REPO_ROOT / "integrations" / "astrbot" / "astrbot_plugin_sourcehub_inspector"
)

# 引导路径，按解析优先级排列。
BOOTSTRAP_PATHS = (CANONICAL_PLUGIN_DIR, REPO_ROOT)


def _install_paths() -> None:
    """把引导路径写入 sys.path 与 PYTHONPATH，且不重复追加。"""
    resolved = [str(path) for path in BOOTSTRAP_PATHS]

    # 置顶，确保不会被外部 PYTHONPATH 抢先解析到另一份副本。
    for path in reversed(resolved):
        if path in sys.path:
            sys.path.remove(path)
        sys.path.insert(0, path)

    # 子进程（tools/ 下的脚本）只认环境变量。
    existing = [item for item in os.environ.get("PYTHONPATH", "").split(os.pathsep) if item]
    merged = resolved + [item for item in existing if item not in resolved]
    os.environ["PYTHONPATH"] = os.pathsep.join(merged)


_install_paths()
