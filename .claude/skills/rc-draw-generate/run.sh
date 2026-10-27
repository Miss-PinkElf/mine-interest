#!/usr/bin/env bash
# Right Code 画图 skill 入口（macOS / Linux）
# 实际逻辑在 lib/rc_draw.py，仅依赖 Python 3 标准库。
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "错误：需要 Python 3（未找到 python3 / python）" >&2
  exit 1
fi

exec "$PYTHON" "$SCRIPT_DIR/lib/rc_draw.py" "$@"
