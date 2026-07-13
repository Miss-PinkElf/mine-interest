#!/usr/bin/env bash
# 一键启动视频情感化转写本地前后端。
# - 端口占用时先尝试结束占用进程
# - 无法结束时自动切换到下一个可用端口
# - Ctrl+C 时清理本脚本拉起的子进程
#
# 用法（仓库根目录）：
#   ./scripts/start-local-dev.sh
#   BACKEND_PORT=8010 FRONTEND_PORT=5180 ./scripts/start-local-dev.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"

# 默认端口与主机。
DEFAULT_BACKEND_PORT=8000
DEFAULT_FRONTEND_PORT=5173
HOST="127.0.0.1"

# 换端口时最多向后尝试的次数。
MAX_PORT_SHIFT=20
# kill 后等待端口释放的秒数。
PORT_RELEASE_WAIT_SECONDS=2

BACKEND_PID=""
FRONTEND_PID=""
LOG_DIR="${ROOT_DIR}/.dev-logs"
BACKEND_LOG="${LOG_DIR}/backend.log"
FRONTEND_LOG="${LOG_DIR}/frontend.log"

mkdir -p "${LOG_DIR}"

# 日志一律打到 stderr，避免污染端口号的 stdout 捕获。
log() {
  printf '[start-local-dev] %s\n' "$*" >&2
}

fail() {
  printf '[start-local-dev] 错误：%s\n' "$*" >&2
  exit 1
}

# 判断端口是否空闲（无 LISTEN）。
is_port_free() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    ! lsof -nP -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1
  else
    python3 - "$port" <<'PY'
import socket, sys
port = int(sys.argv[1])
s = socket.socket()
try:
    s.bind(("127.0.0.1", port))
except OSError:
    raise SystemExit(1)
finally:
    s.close()
raise SystemExit(0)
PY
  fi
}

# 列出占用端口的 PID（可能多个）。
pids_on_port() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"${port}" -sTCP:LISTEN -t 2>/dev/null | sort -u || true
  fi
}

# 尝试结束占用端口的进程；成功释放返回 0，否则 1。
try_free_port() {
  local port="$1"
  local pids
  pids="$(pids_on_port "${port}" | tr '\n' ' ' | sed 's/[[:space:]]*$//')"
  if [[ -z "${pids}" ]]; then
    return 0
  fi

  log "端口 ${port} 被占用，PID: ${pids}，尝试结束..."
  # shellcheck disable=SC2086
  kill ${pids} 2>/dev/null || true
  sleep "${PORT_RELEASE_WAIT_SECONDS}"

  if is_port_free "${port}"; then
    log "端口 ${port} 已释放"
    return 0
  fi

  log "温和结束失败，尝试 kill -9..."
  # shellcheck disable=SC2086
  kill -9 ${pids} 2>/dev/null || true
  sleep "${PORT_RELEASE_WAIT_SECONDS}"

  if is_port_free "${port}"; then
    log "端口 ${port} 已强制释放"
    return 0
  fi

  log "无法释放端口 ${port}"
  return 1
}

# 确保得到可用端口：先尝试 preferred，占用则 kill，仍失败则递增切换。
# 仅向 stdout 输出端口号；日志走 stderr。
ensure_port() {
  local preferred="$1"
  local label="$2"
  local candidate
  local i

  if is_port_free "${preferred}"; then
    printf '%s\n' "${preferred}"
    return 0
  fi

  if try_free_port "${preferred}"; then
    printf '%s\n' "${preferred}"
    return 0
  fi

  log "${label} 默认端口 ${preferred} 无法释放，自动寻找备用端口..."
  i=1
  while [[ "${i}" -le "${MAX_PORT_SHIFT}" ]]; do
    candidate=$((preferred + i))
    if is_port_free "${candidate}"; then
      log "${label} 切换到端口 ${candidate}"
      printf '%s\n' "${candidate}"
      return 0
    fi
    if try_free_port "${candidate}"; then
      log "${label} 释放备用端口 ${candidate} 成功"
      printf '%s\n' "${candidate}"
      return 0
    fi
    i=$((i + 1))
  done

  fail "${label} 在 ${preferred}-$((preferred + MAX_PORT_SHIFT)) 范围内找不到可用端口"
}

cleanup() {
  local code=$?
  # 避免重复 cleanup 递归。
  trap - INT TERM EXIT

  log "正在停止本脚本启动的服务..."
  if [[ -n "${FRONTEND_PID}" ]] && kill -0 "${FRONTEND_PID}" 2>/dev/null; then
    kill "${FRONTEND_PID}" 2>/dev/null || true
  fi
  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" 2>/dev/null; then
    kill "${BACKEND_PID}" 2>/dev/null || true
  fi
  sleep 1
  if [[ -n "${FRONTEND_PID}" ]] && kill -0 "${FRONTEND_PID}" 2>/dev/null; then
    kill -9 "${FRONTEND_PID}" 2>/dev/null || true
  fi
  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" 2>/dev/null; then
    kill -9 "${BACKEND_PID}" 2>/dev/null || true
  fi
  log "已清理。日志：${BACKEND_LOG} / ${FRONTEND_LOG}"
  exit "${code}"
}

trap cleanup INT TERM EXIT

# --- 前置检查 ---
[[ -x "${BACKEND_DIR}/.venv/bin/uvicorn" ]] || fail "缺少 backend/.venv，请先：cd backend && python3.11 -m venv .venv && .venv/bin/python -m pip install -e \".[dev]\""
[[ -d "${FRONTEND_DIR}/node_modules" ]] || fail "缺少 frontend/node_modules，请先：cd frontend && npm install"

if [[ -n "${BACKEND_PORT:-}" ]]; then
  if ! is_port_free "${BACKEND_PORT}"; then
    if ! try_free_port "${BACKEND_PORT}"; then
      BACKEND_PORT="$(ensure_port "${BACKEND_PORT}" "后端")"
    fi
  fi
else
  BACKEND_PORT="$(ensure_port "${DEFAULT_BACKEND_PORT}" "后端")"
fi

if [[ -n "${FRONTEND_PORT:-}" ]]; then
  if ! is_port_free "${FRONTEND_PORT}"; then
    if ! try_free_port "${FRONTEND_PORT}"; then
      FRONTEND_PORT="$(ensure_port "${FRONTEND_PORT}" "前端")"
    fi
  fi
else
  FRONTEND_PORT="$(ensure_port "${DEFAULT_FRONTEND_PORT}" "前端")"
fi

BACKEND_TARGET="http://${HOST}:${BACKEND_PORT}"

log "后端：${BACKEND_TARGET}"
log "前端：http://${HOST}:${FRONTEND_PORT}"
log "API 代理：/api -> ${BACKEND_TARGET}"

# --- 启动后端 ---
(
  cd "${BACKEND_DIR}"
  exec .venv/bin/uvicorn app.main:app --reload --host "${HOST}" --port "${BACKEND_PORT}"
) >"${BACKEND_LOG}" 2>&1 &
BACKEND_PID=$!

ready=0
i=0
while [[ "${i}" -lt 40 ]]; do
  if curl -sf "http://${HOST}:${BACKEND_PORT}/api/health" >/dev/null 2>&1; then
    log "后端健康检查通过"
    ready=1
    break
  fi
  if ! kill -0 "${BACKEND_PID}" 2>/dev/null; then
    fail "后端进程已退出，见日志：${BACKEND_LOG}"
  fi
  sleep 0.25
  i=$((i + 1))
done
[[ "${ready}" -eq 1 ]] || fail "后端启动超时，见日志：${BACKEND_LOG}"

# --- 启动前端 ---
(
  cd "${FRONTEND_DIR}"
  export BACKEND_TARGET
  export FRONTEND_PORT
  export FRONTEND_HOST="${HOST}"
  exec npm run dev -- --host "${HOST}" --port "${FRONTEND_PORT}" --strictPort
) >"${FRONTEND_LOG}" 2>&1 &
FRONTEND_PID=$!

ready=0
i=0
while [[ "${i}" -lt 60 ]]; do
  if ! is_port_free "${FRONTEND_PORT}"; then
    log "前端已监听端口 ${FRONTEND_PORT}"
    ready=1
    break
  fi
  if ! kill -0 "${FRONTEND_PID}" 2>/dev/null; then
    fail "前端进程已退出，见日志：${FRONTEND_LOG}"
  fi
  sleep 0.25
  i=$((i + 1))
done
[[ "${ready}" -eq 1 ]] || fail "前端启动超时，见日志：${FRONTEND_LOG}"

cat <<INFO

========================================
本地开发已启动
  前端工作台: http://${HOST}:${FRONTEND_PORT}
  后端 API  : ${BACKEND_TARGET}
  健康检查  : ${BACKEND_TARGET}/api/health
  后端日志  : ${BACKEND_LOG}
  前端日志  : ${FRONTEND_LOG}
按 Ctrl+C 停止前后端
========================================

INFO

# macOS 自带 bash 3.2 无 wait -n：轮询等待子进程。
while kill -0 "${BACKEND_PID}" 2>/dev/null && kill -0 "${FRONTEND_PID}" 2>/dev/null; do
  sleep 1
done

log "有服务退出，准备收尾"
# 主动触发 cleanup（EXIT trap）
exit 0
