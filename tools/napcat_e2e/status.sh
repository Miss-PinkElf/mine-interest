#!/usr/bin/env bash
# 查看 Docker 双容器 E2E 环境状态
#
# 用法：
#   bash tools/napcat_e2e/status.sh
#
# 输出：
#   - 两个测试容器的状态；
#   - 关键端口是否监听；
#   - 两个 NapCat WebUI 地址；
#   - 生产容器 napcat 当前状态；
#   - 是否有待恢复的生产停止标记。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

echo "=== 测试容器 ==="
if docker info >/dev/null 2>&1; then
  compose ps || true
else
  warn "Docker 未就绪。"
fi

echo
echo "=== 关键端口 ==="
for port in "${BOT_ONEBOT_PORT}" "${SENDER_ONEBOT_PORT}" "${TEST_ASTRBOT_WEBUI_PORT}" "${TEST_ASTRBOT_REVERSE_PORT}" "${BOT_WEBUI_PORT}" "${SENDER_WEBUI_PORT}"; do
  if lsof -nP -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1; then
    printf '  %-5s LISTEN\n' "${port}"
  else
    printf '  %-5s -\n' "${port}"
  fi
done

echo
echo "=== WebUI ==="
info "机器人：$(webui_url "${E2E_ROOT}/bot/config" "${BOT_WEBUI_PORT}")"
info "发送者：$(webui_url "${E2E_ROOT}/sender/config" "${SENDER_WEBUI_PORT}")"
info "测试 AstrBot：http://127.0.0.1:${TEST_ASTRBOT_WEBUI_PORT}"

echo
echo "=== 生产容器 ==="
if docker info >/dev/null 2>&1; then
  if docker ps --format '{{.Names}}' | grep -qx 'napcat'; then
    echo "  napcat: running"
  else
    echo "  napcat: not running"
  fi
else
  echo "  Docker 未就绪，无法查询"
fi

if [ -f "${E2E_ROOT}/production-stopped" ]; then
  warn "存在生产停止标记：${E2E_ROOT}/production-stopped（stop-all.sh 会恢复）"
fi

echo
echo "=== 建议自检 ==="
cat <<EOF
cd ${REPO_ROOT}
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor \\
  --config tools/astrbot_e2e/config.local.json
EOF
