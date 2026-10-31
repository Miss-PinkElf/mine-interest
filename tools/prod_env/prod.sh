#!/usr/bin/env bash
# 生产环境一键脚本：NapCat 容器 + AstrBot CLI
#
# 用法：
#   bash tools/prod_env/prod.sh start              # 幂等启动；已运行则不动
#   bash tools/prod_env/prod.sh start --restart    # 显式重启 AstrBot 与 NapCat
#   bash tools/prod_env/prod.sh start --no-iterm   # 不开 iTerm，在当前终端前台跑 AstrBot
#   bash tools/prod_env/prod.sh stop               # 停止 AstrBot、NapCat，并关闭脚本窗口
#   bash tools/prod_env/prod.sh status             # 只读状态
#
# 约定：
#   - 生产 NapCat 是 ~/napcat 下的容器 napcat（17号）。
#   - 生产 AstrBot 数据根是 ~/.astrbot，Dashboard 6185，反向 WS 6199。
#   - AstrBot 在 iTerm 标签或当前终端前台运行；关闭标签/终端即停止。
#   - 与 tools/napcat_e2e 的 E2E 环境互不管理；启动生产前会自动停 E2E 机器人（同一 17号）。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# ---------- 可覆盖配置 ----------
PROD_COMPOSE_DIR="${PROD_COMPOSE_DIR:-${HOME}/napcat}"
PROD_CONTAINER="${PROD_CONTAINER:-napcat}"
PROD_ASTRBOT_ROOT="${PROD_ASTRBOT_ROOT:-${HOME}/.astrbot}"
PROD_ASTRBOT_PORT="${PROD_ASTRBOT_PORT:-6185}"
PROD_ASTRBOT_REVERSE_PORT="${PROD_ASTRBOT_REVERSE_PORT:-6199}"
PROD_QQ="${PROD_QQ:-3254276668}"
PROD_ONEBOT_CONFIG="${PROD_COMPOSE_DIR}/config/onebot11_${PROD_QQ}.json"
PROD_WEBUI_CONFIG="${PROD_COMPOSE_DIR}/config/webui.json"
PROD_PID_FILE="${PROD_ASTRBOT_ROOT}/.prod-run.pid"
PROD_WINDOW_FILE="${PROD_ASTRBOT_ROOT}/.prod-iterm-window-id"

E2E_ROOT="${E2E_ROOT:-${HOME}/.qq-e2e-docker}"
E2E_BOT_CONTAINER="${E2E_BOT_CONTAINER:-napcat-e2e-bot}"
E2E_SENDER_CONTAINER="${E2E_SENDER_CONTAINER:-napcat-e2e-sender}"
E2E_MARKER="${E2E_ROOT}/production-stopped"

ASTRBOT_BIN="${ASTRBOT_BIN:-$(command -v astrbot 2>/dev/null || true)}"
[ -n "${ASTRBOT_BIN}" ] || ASTRBOT_BIN="${HOME}/.local/bin/astrbot"
VENV_PY="${REPO_ROOT}/backend/.venv/bin/python"
WAIT_ONEBOT_SCRIPT="${REPO_ROOT}/tools/napcat_e2e/wait_onebot.py"

ASTRBOT_WAIT_SECONDS="${ASTRBOT_WAIT_SECONDS:-120}"
ONEBOT_WAIT_SECONDS="${ONEBOT_WAIT_SECONDS:-600}"
TERM_WAIT_SECONDS="${TERM_WAIT_SECONDS:-10}"
ONEBOT_FALLBACK_HOST_PORT="${ONEBOT_FALLBACK_HOST_PORT:-13001}"
PROD_WEBUI_FALLBACK_HOST_PORT="${PROD_WEBUI_FALLBACK_HOST_PORT:-16099}"

# iTerm 标签内执行的命令；$$ 保持字面量，由标签里的 shell 展开为自身 PID。
NAPCAT_TAB_CMD="docker logs -f --tail 200 ${PROD_CONTAINER}"
ASTRBOT_TAB_CMD="cd ${PROD_ASTRBOT_ROOT} && echo \$\$ > .prod-run.pid && exec ${ASTRBOT_BIN} run"

# ---------- 输出 ----------
info() { printf '[prod] %s\n' "$*"; }
warn() { printf '[prod][warn] %s\n' "$*" >&2; }
die() { printf '[prod][error] %s\n' "$*" >&2; exit 1; }

usage() {
  sed -n '2,/^$/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

# ---------- 基础检查 ----------
ensure_docker() {
  command -v docker >/dev/null 2>&1 || die "未找到 docker，请先启动 OrbStack/Docker Desktop"
  docker info >/dev/null 2>&1 || die "Docker daemon 未就绪，请先启动 OrbStack/Docker Desktop"
}

require_file() { [ -f "$1" ] || die "缺少文件：$1"; }
require_dir() { [ -d "$1" ] || die "缺少目录：$1"; }

ensure_prod_env() {
  require_file "${PROD_COMPOSE_DIR}/compose.yaml"
  require_dir "${PROD_ASTRBOT_ROOT}"
  require_file "${PROD_ONEBOT_CONFIG}"
  [ -x "${ASTRBOT_BIN}" ] || die "未找到可执行的 astrbot CLI：${ASTRBOT_BIN}"
}

port_listening() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

container_exists() {
  docker inspect "$1" >/dev/null 2>&1
}

container_running() {
  [ "$(docker inspect -f '{{.State.Running}}' "$1" 2>/dev/null || true)" = "true" ]
}

# ---------- AstrBot 进程 ----------
read_pid() {
  [ -f "${PROD_PID_FILE}" ] || return 1
  tr -d '[:space:]' < "${PROD_PID_FILE}"
}

pid_is_astrbot() {
  local pid="$1"
  [ -n "${pid}" ] || return 1
  kill -0 "${pid}" 2>/dev/null || return 1
  ps -p "${pid}" -o command= 2>/dev/null | grep -q 'astrbot'
}

term_pid() {
  local pid="$1" i
  kill -TERM "${pid}" 2>/dev/null || true
  for ((i = 0; i < TERM_WAIT_SECONDS * 2; i++)); do
    kill -0 "${pid}" 2>/dev/null || return 0
    sleep 0.5
  done
  return 1
}

# stop_astrbot [strict]
# strict=1 时：6185 被未知进程占用或无法停止就报错退出（用于 --restart）。
stop_astrbot() {
  local strict="${1:-0}" pid="" valid=0
  if pid="$(read_pid 2>/dev/null)"; then
    if pid_is_astrbot "${pid}"; then
      valid=1
    fi
  else
    pid=""
  fi

  if [ "${valid}" = "1" ]; then
    info "停止生产 AstrBot（PID ${pid}）..."
    if term_pid "${pid}"; then
      info "AstrBot 已退出"
    else
      warn "AstrBot（PID ${pid}）在 ${TERM_WAIT_SECONDS}s 内未退出；未强制 SIGKILL"
    fi
    rm -f "${PROD_PID_FILE}"
  else
    if [ -n "${pid}" ]; then
      warn "PID 文件已过期（${pid} 不是 astrbot），清理"
    fi
    rm -f "${PROD_PID_FILE}"
    if [ "${strict}" = "1" ] && port_listening "${PROD_ASTRBOT_PORT}"; then
      die "端口 ${PROD_ASTRBOT_PORT} 被未知进程占用（可能是 AstrBot 桌面 App）；请手动退出后再重启"
    fi
  fi

  if port_listening "${PROD_ASTRBOT_PORT}"; then
    if [ "${strict}" = "1" ]; then
      die "端口 ${PROD_ASTRBOT_PORT} 仍在监听，无法确认 AstrBot 已停止"
    fi
    warn "端口 ${PROD_ASTRBOT_PORT} 仍在监听：可能是 AstrBot 桌面 App 或其他进程，本脚本不会杀它"
  fi
}

# ---------- NapCat ----------
start_napcat() {
  info "启动生产 NapCat（${PROD_CONTAINER}）..."
  (cd "${PROD_COMPOSE_DIR}" && docker compose up -d) || die "启动 napcat 失败"
}

restart_napcat() {
  if container_exists "${PROD_CONTAINER}"; then
    info "重启生产 NapCat 容器（${PROD_CONTAINER}）..."
    (cd "${PROD_COMPOSE_DIR}" && docker compose restart "${PROD_CONTAINER}") || die "重启 napcat 失败"
  else
    start_napcat
  fi
}

stop_napcat() {
  if ! docker info >/dev/null 2>&1; then
    warn "Docker 未就绪，跳过停止 ${PROD_CONTAINER}"
    return 0
  fi
  if container_running "${PROD_CONTAINER}"; then
    info "停止生产 NapCat（${PROD_CONTAINER}）..."
    if [ -f "${PROD_COMPOSE_DIR}/compose.yaml" ]; then
      (cd "${PROD_COMPOSE_DIR}" && docker compose stop "${PROD_CONTAINER}") || warn "停止 napcat 失败"
    else
      docker stop "${PROD_CONTAINER}" >/dev/null || warn "停止 napcat 失败"
    fi
  else
    info "生产 NapCat 未运行"
  fi
}

# 同一 17号 只能一套在线：启动生产前自动停 E2E 机器人。
stop_e2e_bot_if_running() {
  if container_running "${E2E_BOT_CONTAINER}"; then
    warn "检测到 E2E 机器人 ${E2E_BOT_CONTAINER} 正在运行（同样占用 17号），自动停止 ..."
    docker stop "${E2E_BOT_CONTAINER}" >/dev/null || die "停止 E2E 机器人失败"
  fi
}

cleanup_stale_marker() {
  if [ -f "${E2E_MARKER}" ] && ! container_running "${E2E_BOT_CONTAINER}"; then
    rm -f "${E2E_MARKER}"
    info "已清理过期标记：${E2E_MARKER}"
  fi
}

# ---------- OneBot 配置与就绪 ----------
# 从生产配置读取容器内 OneBot 端口与 token。
read_onebot_settings() {
  local out
  out="$(python3 - "${PROD_ONEBOT_CONFIG}" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8-sig") as f:
    data = json.load(f)
servers = (data.get("network") or {}).get("websocketServers") or []
if not servers:
    raise SystemExit("no websocketServers")
server = servers[0]
print(server.get("port", ""), server.get("token", ""))
PY
)" || return 1
  read -r ONEBOT_CONTAINER_PORT ONEBOT_TOKEN <<< "${out}"
  [ -n "${ONEBOT_CONTAINER_PORT}" ] || return 1
}

host_port_for_container_port() {
  local container_port="$1" fallback="$2" mapping
  mapping="$(docker port "${PROD_CONTAINER}" "${container_port}/tcp" 2>/dev/null | head -n 1 || true)"
  if [ -n "${mapping}" ]; then
    printf '%s' "${mapping##*:}"
  else
    printf '%s' "${fallback}"
  fi
}

onebot_check_available() {
  [ -x "${VENV_PY}" ] && [ -f "${WAIT_ONEBOT_SCRIPT}" ]
}

run_wait_onebot() {
  local port="$1" token="$2"
  PYTHONPATH="${REPO_ROOT}/tools" "${VENV_PY}" "${WAIT_ONEBOT_SCRIPT}" \
    "${port}" "${token}" "${PROD_QQ}" >/dev/null 2>&1
}

wait_for_astrbot() {
  local i
  info "等待生产 AstrBot Dashboard（${PROD_ASTRBOT_PORT}）..."
  for ((i = 0; i < ASTRBOT_WAIT_SECONDS; i += 2)); do
    if port_listening "${PROD_ASTRBOT_PORT}"; then
      info "生产 AstrBot 已监听 ${PROD_ASTRBOT_PORT}"
      return 0
    fi
    sleep 2
  done
  warn "等待 AstrBot 超时（${ASTRBOT_WAIT_SECONDS}s）；请查看 AstrBot 标签日志"
  return 1
}

wait_for_onebot() {
  local i host_port
  if ! read_onebot_settings; then
    warn "无法从 ${PROD_ONEBOT_CONFIG} 读取 OneBot 端口/token，跳过就绪校验"
    return 0
  fi
  host_port="$(host_port_for_container_port "${ONEBOT_CONTAINER_PORT}" "${ONEBOT_FALLBACK_HOST_PORT}")"
  ONEBOT_HOST_PORT="${host_port}"

  if ! onebot_check_available; then
    warn "缺少 ${VENV_PY} 或 ${WAIT_ONEBOT_SCRIPT}，跳过 get_login_info 校验"
    return 0
  fi

  info "等待生产 NapCat 登录就绪（OneBot ${host_port}，账号 ${PROD_QQ}）..."
  for ((i = 0; i < ONEBOT_WAIT_SECONDS; i += 3)); do
    if port_listening "${host_port}" \
      && run_wait_onebot "${host_port}" "${ONEBOT_TOKEN}"; then
      info "生产 NapCat 已就绪（${PROD_QQ}）"
      return 0
    fi
    if [ $((i % 30)) -eq 0 ] && [ "${i}" -gt 0 ]; then
      info "仍在等待 OneBot 就绪（${i}s/${ONEBOT_WAIT_SECONDS}s）..."
    fi
    sleep 3
  done
  warn "等待 OneBot 就绪超时（${ONEBOT_WAIT_SECONDS}s）；可打开 WebUI 检查是否需要重新扫码"
  return 1
}

# ---------- 展示 ----------
webui_token() {
  [ -f "${PROD_WEBUI_CONFIG}" ] || return 1
  python3 - "${PROD_WEBUI_CONFIG}" <<'PY' 2>/dev/null || true
import json
import sys

with open(sys.argv[1], encoding="utf-8-sig") as f:
    data = json.load(f)
print(data.get("token", ""))
PY
}

print_endpoints() {
  local onebot_port="${ONEBOT_HOST_PORT:-${ONEBOT_FALLBACK_HOST_PORT}}"
  local webui_port token url
  webui_port="$(host_port_for_container_port 6099 "${PROD_WEBUI_FALLBACK_HOST_PORT}")"
  token="$(webui_token || true)"
  url="http://127.0.0.1:${webui_port}/webui"
  [ -z "${token}" ] || url="${url}?token=${token}"

  printf '\n[prod] 入口：\n'
  printf '  AstrBot Dashboard: http://127.0.0.1:%s\n' "${PROD_ASTRBOT_PORT}"
  printf '  NapCat WebUI:      %s\n' "${url}"
  printf '  OneBot WS:         ws://127.0.0.1:%s\n' "${onebot_port}"
  printf '  重启:              bash %s start --restart\n\n' "${BASH_SOURCE[0]}"
}

print_manual_commands() {
  cat <<EOF
手动启动命令：
  cd ${PROD_ASTRBOT_ROOT}
  echo \$\$ > .prod-run.pid && exec ${ASTRBOT_BIN} run

NapCat 日志：
  ${NAPCAT_TAB_CMD}
EOF
}

# ---------- iTerm ----------
iterm_installed() {
  [ -d /Applications/iTerm.app ] || [ -d "${HOME}/Applications/iTerm.app" ]
}

read_window_id() {
  [ -f "${PROD_WINDOW_FILE}" ] || return 1
  local wid
  wid="$(tr -d '[:space:]' < "${PROD_WINDOW_FILE}")"
  case "${wid}" in
    ''|*[!0-9]*) return 1 ;;
  esac
  printf '%s' "${wid}"
}

save_window_id() {
  printf '%s\n' "$1" > "${PROD_WINDOW_FILE}"
}

iterm_window_exists() {
  local wid="$1"
  case "${wid}" in
    ''|*[!0-9]*) return 1 ;;
  esac
  osascript -e "tell application \"iTerm\" to (exists window id ${wid})" 2>/dev/null | grep -qi true
}

iterm_create_window_double() {
  local napcat_cmd="$1" astrbot_cmd="$2"
  osascript <<EOF
tell application "iTerm"
  set w to create window with default profile
  set wid to id of w
  tell current session of w to write text "${napcat_cmd}"
  tell w
    set t to create tab with default profile
    tell current session of t to write text "${astrbot_cmd}"
  end tell
  return wid
end tell
EOF
}

iterm_create_window_single() {
  local cmd="$1"
  osascript <<EOF
tell application "iTerm"
  set w to create window with default profile
  set wid to id of w
  tell current session of w to write text "${cmd}"
  return wid
end tell
EOF
}

iterm_add_tab() {
  local wid="$1" cmd="$2"
  osascript <<EOF
tell application "iTerm"
  tell window id ${wid}
    set t to create tab with default profile
    tell current session of t to write text "${cmd}"
  end tell
end tell
EOF
}

iterm_close_window() {
  local wid="$1"
  osascript -e "tell application \"iTerm\" to close window id ${wid}" 2>/dev/null
}

# open_tabs <need_astrbot 0/1>
# 正常路径：
#   - 窗口存在：只补 AstrBot 标签（NapCat 日志标签视为已存在）
#   - 窗口不存在：按需创建双标签窗口
open_tabs() {
  local need_astrbot="$1" wid=""
  iterm_installed || {
    warn "未找到 iTerm.app"
    print_manual_commands
    return 1
  }

  if wid="$(read_window_id 2>/dev/null)" && iterm_window_exists "${wid}"; then
    if [ "${need_astrbot}" = "1" ]; then
      info "复用 iTerm 窗口 ${wid}，新增 AstrBot 标签 ..."
      iterm_add_tab "${wid}" "${ASTRBOT_TAB_CMD}" || return 1
    fi
    return 0
  fi

  if [ "${need_astrbot}" = "1" ] && container_running "${PROD_CONTAINER}"; then
    wid="$(iterm_create_window_double "${NAPCAT_TAB_CMD}" "${ASTRBOT_TAB_CMD}")" || return 1
  elif [ "${need_astrbot}" = "1" ]; then
    wid="$(iterm_create_window_single "${ASTRBOT_TAB_CMD}")" || return 1
  elif container_running "${PROD_CONTAINER}"; then
    wid="$(iterm_create_window_single "${NAPCAT_TAB_CMD}")" || return 1
  else
    return 0
  fi
  save_window_id "${wid}"
  info "已创建 iTerm 窗口 ${wid}"
}

close_recorded_window() {
  local wid=""
  if ! wid="$(read_window_id 2>/dev/null)"; then
    return 0
  fi
  if iterm_window_exists "${wid}"; then
    info "关闭脚本创建的 iTerm 窗口 ${wid} ..."
    if iterm_close_window "${wid}"; then
      rm -f "${PROD_WINDOW_FILE}"
    else
      warn "iTerm 窗口 ${wid} 关闭失败；保留窗口 ID 记录"
    fi
  else
    rm -f "${PROD_WINDOW_FILE}"
  fi
}

# ---------- 子命令 ----------
cmd_start() {
  local restart=0 no_wait=0 no_iterm=0
  while [ $# -gt 0 ]; do
    case "$1" in
      --restart) restart=1 ;;
      --no-wait) no_wait=1 ;;
      --no-iterm) no_iterm=1 ;;
      -h|--help) usage; exit 0 ;;
      *) die "未知参数：$1" ;;
    esac
    shift
  done

  ensure_docker
  ensure_prod_env

  local astrbot_running=0 napcat_running=0 need_astrbot=0
  port_listening "${PROD_ASTRBOT_PORT}" && astrbot_running=1
  container_running "${PROD_CONTAINER}" && napcat_running=1

  # 幂等：两边都在运行且没有 --restart，直接返回。
  if [ "${restart}" = "0" ] && [ "${astrbot_running}" = "1" ] && [ "${napcat_running}" = "1" ]; then
    info "生产环境已在运行：NapCat + AstrBot（${PROD_ASTRBOT_PORT}）"
    if onebot_check_available && read_onebot_settings; then
      ONEBOT_HOST_PORT="$(host_port_for_container_port "${ONEBOT_CONTAINER_PORT}" "${ONEBOT_FALLBACK_HOST_PORT}")"
      if ! run_wait_onebot "${ONEBOT_HOST_PORT}" "${ONEBOT_TOKEN}"; then
        warn "服务已启动，但 OneBot（${ONEBOT_HOST_PORT}）尚未就绪；可能需要扫码，请打开 NapCat WebUI 检查"
      fi
    fi
    cleanup_stale_marker
    print_endpoints
    exit 0
  fi

  if [ "${restart}" = "1" ]; then
    stop_astrbot 1
    stop_e2e_bot_if_running
    restart_napcat
    astrbot_running=0
    napcat_running=1
  else
    stop_e2e_bot_if_running
    if [ "${napcat_running}" = "0" ]; then
      start_napcat
      napcat_running=1
    fi
  fi

  [ "${astrbot_running}" = "1" ] || need_astrbot=1

  # 清理过期标记：生产容器已经启动，标记的“恢复生产”语义已满足。
  cleanup_stale_marker

  if [ "${no_iterm}" = "1" ]; then
    # 当前终端前台模式：先等 OneBot，再 exec AstrBot。
    if [ "${no_wait}" = "0" ]; then
      wait_for_onebot || warn "OneBot 未就绪；继续启动 AstrBot，稍后可用 status 复查"
    fi
    print_endpoints
    if [ "${need_astrbot}" = "1" ]; then
      info "在当前终端前台启动生产 AstrBot；Ctrl-C 或关闭终端即停止"
      cd "${PROD_ASTRBOT_ROOT}"
      echo $$ > .prod-run.pid
      exec "${ASTRBOT_BIN}" run
    fi
    exit 0
  fi

  if [ "${need_astrbot}" = "1" ] || [ "${napcat_running}" = "1" ]; then
    if ! open_tabs "${need_astrbot}"; then
      warn "iTerm 自动化失败，NapCat 可能已在运行；请按上面的手动命令启动 AstrBot"
      exit 1
    fi
  fi

  if [ "${need_astrbot}" = "1" ] && [ "${no_wait}" = "0" ]; then
    wait_for_astrbot || {
      print_manual_commands
      exit 1
    }
  fi

  local onebot_ok=1
  if [ "${no_wait}" = "0" ]; then
    wait_for_onebot || onebot_ok=0
  fi

  print_endpoints
  if [ "${onebot_ok}" = "0" ]; then
    warn "启动完成但 OneBot 未就绪：服务保持运行，请扫码后重新执行 start 或 status 复查"
    exit 1
  fi
}

cmd_stop() {
  if [ $# -gt 0 ]; then
    case "$1" in
      -h|--help) usage; exit 0 ;;
      *) die "未知参数：$1" ;;
    esac
  fi

  stop_astrbot 0
  stop_napcat
  close_recorded_window

  if [ -f "${E2E_MARKER}" ]; then
    warn "存在 E2E 标记 ${E2E_MARKER}：之后执行 tools/napcat_e2e/stop-all.sh 可能再次启动生产容器"
  fi
  info "停止流程完成"
}

cmd_status() {
  local docker_ok=0
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    docker_ok=1
  else
    warn "Docker 未就绪，容器状态可能不准确"
  fi

  printf '== 容器（Container）==\n'
  local c st
  for c in "${PROD_CONTAINER}" "${E2E_BOT_CONTAINER}" "${E2E_SENDER_CONTAINER}"; do
    if [ "${docker_ok}" = "1" ]; then
      st="$(docker inspect -f '{{.State.Status}}' "${c}" 2>/dev/null || true)"
      [ -n "${st}" ] || st="不存在"
    else
      st="未知"
    fi
    printf '  %-20s %s\n' "${c}" "${st}"
  done

  printf '\n== 端口（Ports）==\n'
  local p
  for p in "${PROD_ASTRBOT_PORT}" "${PROD_ASTRBOT_REVERSE_PORT}" "${ONEBOT_FALLBACK_HOST_PORT}" 6186 6198; do
    if port_listening "${p}"; then
      printf '  %-6s LISTEN\n' "${p}"
    else
      printf '  %-6s -\n' "${p}"
    fi
  done

  printf '\n== 生产 AstrBot ==\n'
  local pid=""
  if pid="$(read_pid 2>/dev/null)" && pid_is_astrbot "${pid}"; then
    printf '  PID %s（与 PID 文件一致）\n' "${pid}"
  else
    printf '  PID 文件：%s\n' "$([ -f "${PROD_PID_FILE}" ] && echo "存在但无效/已过期" || echo "不存在")"
  fi

  printf '\n== iTerm 窗口 ==\n'
  local wid=""
  if wid="$(read_window_id 2>/dev/null)"; then
    if iterm_window_exists "${wid}"; then
      printf '  窗口 %s（存在）\n' "${wid}"
    else
      printf '  窗口 %s（记录存在但窗口已关闭）\n' "${wid}"
    fi
  else
    printf '  无记录\n'
  fi

  printf '\n== E2E 标记 ==\n'
  if [ -f "${E2E_MARKER}" ]; then
    printf '  %s（存在）\n' "${E2E_MARKER}"
  else
    printf '  无\n'
  fi
}

main() {
  [ $# -gt 0 ] || { usage; exit 2; }
  local cmd="$1"
  shift
  case "${cmd}" in
    start) cmd_start "$@" ;;
    stop) cmd_stop "$@" ;;
    status) cmd_status "$@" ;;
    -h|--help|help) usage ;;
    *) usage; exit 2 ;;
  esac
}

main "$@"
