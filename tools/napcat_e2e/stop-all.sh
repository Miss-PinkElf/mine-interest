#!/usr/bin/env bash
# 停止 Docker 双容器 E2E 环境
#
# 用法：
#   bash tools/napcat_e2e/stop-all.sh
#
# 行为：
#   1. docker compose down 停止并删除两个测试容器（数据卷保留）；
#   2. 停止测试 AstrBot 实例（如果 6186 正在监听）；
#   3. 如果 start-all.sh 曾用 --stop-production 停止生产容器，
#      这里会自动 docker start napcat 恢复生产 bot。
#
# 注意：
#   - 数据卷在 ~/.qq-e2e-docker，删容器不会丢登录态。
#   - 生产容器恢复后会自动连回生产 AstrBot（6199）。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

# 1. 停止测试容器
if docker info >/dev/null 2>&1; then
  info "停止测试容器 ..."
  compose down --remove-orphans || warn "docker compose down 失败，请检查容器状态。"
else
  warn "Docker 未就绪，跳过容器停止。"
fi

# 2. 停止测试 AstrBot（只停止本工具能识别的测试实例）
if lsof -nP -iTCP:"${TEST_ASTRBOT_WEBUI_PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  if [ -x "${VENV_PY}" ] && [ -f "${E2E_CONFIG}" ]; then
    info "停止测试 AstrBot ..."
    (
      cd "${REPO_ROOT}"
      PYTHONPATH="${REPO_ROOT}/tools" "${VENV_PY}" -m astrbot_e2e.cli stop-instance \
        --config "${E2E_CONFIG}"
    ) || warn "测试 AstrBot 停止失败，请手动检查 6186 进程。"
  else
    warn "缺少 tools/astrbot_e2e 或 backend/.venv，跳过测试 AstrBot 停止。"
  fi
else
  info "测试 AstrBot 未在 ${TEST_ASTRBOT_WEBUI_PORT} 监听，跳过。"
fi

# 3. 恢复生产容器（仅当本工具停止过它）
if [ -f "${E2E_ROOT}/production-stopped" ]; then
  if docker info >/dev/null 2>&1; then
    info "恢复生产容器 napcat ..."
    if docker start napcat >/dev/null 2>&1; then
      rm -f "${E2E_ROOT}/production-stopped"
      info "生产容器已恢复。"
    else
      warn "生产容器恢复失败；标记保留：${E2E_ROOT}/production-stopped"
    fi
  else
    warn "Docker 未就绪，无法恢复生产容器；标记保留：${E2E_ROOT}/production-stopped"
  fi
else
  info "没有待恢复的生产容器标记。"
fi

info "停止流程完成。"
