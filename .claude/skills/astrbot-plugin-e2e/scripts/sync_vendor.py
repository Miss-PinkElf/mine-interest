"""把执行引擎同步为 skill 的 vendor 快照。"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from pathlib import Path

IGNORE = shutil.ignore_patterns(
    "__pycache__", "*.pyc", "reports", "config.local.json", "tests"
)


def _tree_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if not item.is_file():
            continue
        relative = item.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def sync_vendor(source: Path, dest: Path) -> dict:
    source = Path(source).expanduser()
    dest = Path(dest).expanduser()
    if not (source / "__init__.py").exists():
        raise RuntimeError("源目录不是 astrbot_e2e 包: {}".format(source))
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest, ignore=IGNORE)
    manifest = {
        "source": str(source),
        "synced_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "sha256": _tree_hash(dest),
    }
    (dest / "VERSION.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="同步 astrbot_e2e 执行引擎到 vendor")
    parser.add_argument("--source", required=True)
    parser.add_argument("--dest", required=True)
    args = parser.parse_args(argv)
    manifest = sync_vendor(Path(args.source), Path(args.dest))
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
