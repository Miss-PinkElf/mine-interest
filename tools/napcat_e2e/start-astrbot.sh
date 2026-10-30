#!/usr/bin/env bash
# 单独启动「测试 AstrBot」实例（WebUI 6186 / 反向 WS 6198）
#
# 用法：
#   bash tools/napcat_e2e/start-astrbot.sh
#   bash tools/napcat_e2e/start-astrbot.sh --detach      # 后台启动，终端关闭不影响
#   bash tools/napcat_e2e/start-astrbot.sh --restart     # 先停止已有实例再启动
#   bash tools/napcat_e2e/start-astrbot.sh --no-tail
#   bash tools/napcat_e2e/start-astrbot.sh --plugin astrbot_plugin_sourcehub_inspector
#
# 说明：
#   - 复用现有 tools/astrbot_e2e 的 start-instance，不另写启动器。
#   - start-instance 会连接 6200/6201 校验机器人/发送者账号；
#     所以默认先等待这两个 OneBot WS 上线（即等你扫码登录两个 QQ）。
#   - --detach 会在后台完成「等待 + 启动」，关闭当前终端不会杀掉测试 AstrBot。
#   - 已在运行或已有启动流程在等待时，不会重复启动，只 tail 日志。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

TAIL_LOGS=1
DETACH=0
WAIT_NAPCAT=1
RESTART=0
DETACH_LOG=""

while [ $# -gt 0 ]; do
  case "$1" in
    --no-tail) TAIL_LOGS=0 ;;
    --detach) DETACH=1 ;;
    --no-wait) WAIT_NAPCAT=0 ;;
    --restart) RESTART=1 ;;
    --plugin)
      shift
      [ $# -gt 0 ] || die "--plugin 需要一个插件 ID"
      E2E_PLUGIN="$1"
      export E2E_PLUGIN
      ;;
    -h|--help)
      sed -n '2,/^$/p' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    *) die "未知参数：$1" ;;
  esac
  shift
done

ensure_astrbot_prereqs
set_tab_title "测试AstrBot(6186)"

# 启动锁：防止重复 start-all / 重复 start-astrbot 同时拉起多个实例。
LOCK="${TEST_ASTRBOT_ROOT}/bootstrap-run/start-astrbot.lock"
mkdir -p "$(dirname "${LOCK}")"

lock_alive() {
  [ -f "${LOCK}" ] || return 1
  local pid
  pid="$(cat "${LOCK}" 2>/dev/null || true)"
  [ -n "${pid}" ] && kill -0 "${pid}" 2>/dev/null
}

if [ "${RESTART}" = "1" ]; then
  info "重启测试 AstrBot：先停止已有实例/等待中的启动流程 ..."
  if lock_alive; then
    pid="$(cat "${LOCK}")"
    kill "${pid}" 2>/dev/null || true
    sleep 1
    if kill -0 "${pid}" 2>/dev/null; then
      kill -9 "${pid}" 2>/dev/null || true
    fi
  fi
  rm -f "${LOCK}"
  if [ -f "${TEST_ASTRBOT_ROOT}/astrbot-e2e.pid" ] \
    || is_port_listening "${TEST_ASTRBOT_WEBUI_PORT}"; then
    (
      cd "${REPO_ROOT}"
      PYTHONPATH="${REPO_ROOT}/tools" "${VENV_PY}" -m astrbot_e2e.cli stop-instance \
        --config "${E2E_CONFIG}"
    ) || warn "stop-instance 失败；如果 6186 仍被占用，请手动检查。"
  fi
  # 等端口释放后再启动，避免新旧实例端口冲突。
  for _i in $(seq 1 10); do
    is_port_listening "${TEST_ASTRBOT_WEBUI_PORT}" || break
    sleep 1
  done
  if is_port_listening "${TEST_ASTRBOT_WEBUI_PORT}"; then
    die "${TEST_ASTRBOT_WEBUI_PORT} 仍被占用，无法重启；请手动检查测试 AstrBot 进程。"
  fi
fi

if lock_alive; then
  info "检测到测试 AstrBot 启动流程已在运行（PID $(cat "${LOCK}")），跳过重复启动。"
  if [ "${TAIL_LOGS}" = "1" ]; then
    tail -F "${TEST_ASTRBOT_LOG}"
  fi
  exit 0
fi

if is_port_listening "${TEST_ASTRBOT_WEBUI_PORT}"; then
  info "测试 AstrBot 已在运行（WebUI ${TEST_ASTRBOT_WEBUI_PORT}），跳过启动。"
  if [ "${TAIL_LOGS}" = "1" ]; then
    tail -F "${TEST_ASTRBOT_LOG}"
  fi
  exit 0
fi

start_foreground() {
  if [ "${WAIT_NAPCAT}" = "1" ]; then
    wait_for_onebot_ready "${BOT_ONEBOT_PORT}" "${BOT_WS_TOKEN}" "${BOT_QQ}" "机器人 17号"
    wait_for_onebot_ready "${SENDER_ONEBOT_PORT}" "${SENDER_WS_TOKEN}" "${SENDER_QQ}" "发送者 C#"
  fi
  info "启动测试 AstrBot（插件：${E2E_PLUGIN}）..."
  run_start_instance
}

if [ "${DETACH}" = "1" ]; then
  DETACH_LOG="${TEST_ASTRBOT_ROOT}/bootstrap-run/start-instance.log"
  mkdir -p "$(dirname "${DETACH_LOG}")"

  # 后台子进程独立于当前终端：先写锁，再等待 NapCat，最后启动 start-instance。
  # 参数通过位置参数传入，避免嵌套引号问题；插件/配置由 common.sh 的默认值读取。
  nohup bash -c '
    lock="$1"; script_dir="$2"; wait_flag="$3"
    echo $$ > "$lock"
    trap "rm -f \"$lock\"" EXIT
    cd "$script_dir"
    # shellcheck disable=SC1091
    source ./common.sh
    if [ "$wait_flag" = "1" ]; then
      wait_for_onebot_ready 6200 "$BOT_WS_TOKEN" "$BOT_QQ" "机器人 17号"
      wait_for_onebot_ready 6201 "$SENDER_WS_TOKEN" "$SENDER_QQ" "发送者 C#"
    fi
    run_start_instance
  ' _ "${LOCK}" "${SCRIPT_DIR}" "${WAIT_NAPCAT}" >>"${DETACH_LOG}" 2>&1 &
  child_pid=$!
  echo "${child_pid}" > "${LOCK}"
  disown 2>/dev/null || true

  info "已在后台等待 NapCat 并启动测试 AstrBot。"
  info "后台日志：${DETACH_LOG}"
  # 最多等 60 秒让 WebUI 起来；没起来也没关系，下面 tail 会持续显示日志。
  for _i in $(seq 1 60); do
    if is_port_listening "${TEST_ASTRBOT_WEBUI_PORT}"; then
      break
    fi
    sleep 1
  done
else
  echo $$ > "${LOCK}"
  trap 'rm -f "${LOCK}"' EXIT
  start_foreground
  rm -f "${LOCK}"
  trap - EXIT
fi

if [ "${TAIL_LOGS}" = "1" ]; then
  info "跟随测试 AstrBot 日志（Ctrl-C 只退出日志，不会停止实例）：${TEST_ASTRBOT_LOG}"
  if [ -n "${DETACH_LOG}" ]; then
    # 同时显示后台等待/启动日志，方便看到「等待扫码」进度。
    tail -F "${TEST_ASTRBOT_LOG}" "${DETACH_LOG}"
  else
    tail -F "${TEST_ASTRBOT_LOG}"
  fi
fi
