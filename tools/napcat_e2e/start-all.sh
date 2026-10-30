#!/usr/bin/env bash
# 一键启动 Docker 双容器 E2E 环境
#
# 用法：
#   bash tools/napcat_e2e/start-all.sh --stop-production
#   bash tools/napcat_e2e/start-all.sh --no-iterm
#   bash tools/napcat_e2e/start-all.sh --force-tabs
#   bash tools/napcat_e2e/start-all.sh --restart        # 容器/测试实例已在运行则重启
#   bash tools/napcat_e2e/start-all.sh --plugin astrbot_plugin_sourcehub_inspector
#
# 行为：
#   1. 检查 Docker、测试 AstrBot 前置文件；
#   2. 生成两个容器的 NapCat 配置（已存在则不覆盖）；
#   3. 检查生产容器 napcat 是否占用 17号（默认中止，--stop-production 才停）；
#   4. 检查原生 QQ（默认中止，--allow-native-qq 才放行）；
#   5. docker compose up -d 启动 napcat-e2e-bot 与 napcat-e2e-sender；
#   6. 打开 iTerm2 三个标签：
#        - napcat-e2e-bot 日志（扫码登录 17号）
#        - napcat-e2e-sender 日志（扫码登录 C#）
#        - 测试 AstrBot 后台启动 + 日志（等待 6200/6201 后自动启动）
#
# 说明：
#   - 测试 AstrBot 只连 6198；生产 AstrBot（6199）不需要暂停。
#   - 生产容器若被本脚本停止，stop-all.sh 会自动恢复。
#   - 测试容器 restart="no"，不会随开机自动启动。
#   - 重复执行时：docker compose up -d 是幂等的；如果两个容器和测试 AstrBot
#     都已在运行，默认不再打开重复标签；需要新的日志窗口请加 --force-tabs。
#   - 测试 AstrBot 使用 --detach 后台启动；关闭标签一般不会杀掉实例。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

STOP_PRODUCTION=0
ALLOW_NATIVE_QQ=0
OPEN_ITERM=1
FORCE_TABS=0
RESTART=0

while [ $# -gt 0 ]; do
  case "$1" in
    --stop-production) STOP_PRODUCTION=1 ;;
    --allow-native-qq) ALLOW_NATIVE_QQ=1 ;;
    --no-iterm) OPEN_ITERM=0 ;;
    --force-tabs) FORCE_TABS=1 ;;
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

ensure_docker
ensure_astrbot_prereqs
ensure_bot_config
ensure_sender_config
check_production_container
check_native_qq

info "启动两个 NapCat 容器 ..."
compose up -d napcat-e2e-bot napcat-e2e-sender

if [ "${RESTART}" = "1" ]; then
  # 已在运行则重启整个容器（数据卷保留）；不要进容器 kill QQ，
  # 入口脚本没有守护进程，kill 后容器可能直接退出。
  info "重启两个 NapCat 容器 ..."
  compose restart napcat-e2e-bot napcat-e2e-sender
fi

info "容器已启动。首次运行需要分别扫码登录 17号 与 C#。"
print_endpoints

# 重复执行保护：两个容器和测试 AstrBot 都已在运行时，默认不再打开重复标签。
# --restart 时强制继续，以便看到重启后的日志。
if [ "${FORCE_TABS}" = "0" ] && [ "${RESTART}" = "0" ] \
  && is_port_listening "${TEST_ASTRBOT_WEBUI_PORT}" \
  && docker ps --format '{{.Names}}' | grep -qx 'napcat-e2e-bot' \
  && docker ps --format '{{.Names}}' | grep -qx 'napcat-e2e-sender'; then
  info "环境已在运行（两个容器 + 测试 AstrBot），跳过重复打开标签。"
  info "需要新的日志窗口请加 --force-tabs；需要重启请加 --restart。"
  exit 0
fi

# 没有 iTerm2 时退化为打印命令，避免脚本失败。
if [ "${OPEN_ITERM}" = "0" ] || [ ! -d "/Applications/iTerm.app" ]; then
  warn "未打开 iTerm2（--no-iterm 或未安装）。请手动执行："
  print_manual_log_commands
  info "另开一个终端启动测试 AstrBot：bash ${SCRIPT_DIR}/start-astrbot.sh --plugin ${E2E_PLUGIN}"
  exit 0
fi

# 给 iTerm2 标签设置颜色、徽章与标题。
# 关键：这里只做字符串拼接，不能让外层 printf 解释 \033，
# 否则会把真正的 ESC 字节写进终端，zsh 行编辑器会吃掉控制序列。
make_tab_prefix() {
  local color="$1"
  local badge_text="$2"
  local title="$3"
  local badge_b64 esc bel
  badge_b64=$(printf '%s' "${badge_text}" | base64)
  esc='\033'
  bel='\007'
  printf '%s' "printf '${esc}]1337;SetColors=tab=${color}${bel}'; printf '${esc}]1337;SetBadgeFormat=${badge_b64}${bel}'; printf '${esc}]0;${title}${bel}'; ( sleep 4; printf '${esc}]0;${title}${bel}' ) & "
}

PREFIX_BOT=$(make_tab_prefix "ff5f56" "测试机器人 17号" "测试机器人(17号)")
PREFIX_SENDER=$(make_tab_prefix "4f9dff" "测试发送者 C#" "测试发送者(C#)")
PREFIX_ASTRBOT=$(make_tab_prefix "27c93f" "测试AstrBot 6186" "测试AstrBot(6186)")

# iTerm2 三个标签：两个 NapCat 日志 + 测试 AstrBot。
# AstrBot 标签使用 --detach：后台等待扫码并启动，关闭标签一般不会杀掉实例。
RESTART_ARG=""
if [ "${RESTART}" = "1" ]; then
  RESTART_ARG="--restart"
fi
CMD_BOT="${PREFIX_BOT}cd '${SCRIPT_DIR}' && docker logs -f napcat-e2e-bot"
CMD_SENDER="${PREFIX_SENDER}cd '${SCRIPT_DIR}' && docker logs -f napcat-e2e-sender"
CMD_ASTRBOT="${PREFIX_ASTRBOT}cd '${SCRIPT_DIR}' && bash start-astrbot.sh --detach ${RESTART_ARG} --plugin '${E2E_PLUGIN}'"

# 首次执行时 macOS 可能提示「终端想控制 iTerm2」，选择允许即可。
# 注意：iTerm2 3.6.7 的 AppleScript 应用名是 "iTerm"（不是 "iTerm2"，
# 后者会报 -1728 / -2741）。这里必须用 "iTerm"。
osascript - "${CMD_BOT}" "${CMD_SENDER}" "${CMD_ASTRBOT}" <<'APPLESCRIPT'
on run argv
  tell application "iTerm"
    activate
    set targetWindow to (create window with default profile)
    set tabIndex to 0
    repeat with commandRef in argv
      set tabIndex to tabIndex + 1
      if tabIndex > 1 then
        tell targetWindow to create tab with default profile
      end if
      tell current session of targetWindow
        write text (commandRef as text)
      end tell
      delay 0.5
    end repeat
  end tell
end run
APPLESCRIPT

cat <<EOF

已打开 iTerm2 三个标签：
  1. napcat-e2e-bot      → 扫码登录 17号（${BOT_QQ}）
  2. napcat-e2e-sender   → 扫码登录 C#（${SENDER_QQ}）
  3. 测试 AstrBot        → 等待扫码后后台启动，并跟随日志（${TEST_ASTRBOT_WEBUI_PORT}/${TEST_ASTRBOT_REVERSE_PORT}）

重复执行说明：
  - docker compose up 是幂等的，不会创建重复容器；
  - 两个容器和测试 AstrBot 都已在运行时，本脚本默认跳过打开新标签；
  - 需要新的日志窗口：加 --force-tabs；
  - 关闭终端不会停止 Docker 容器；测试 AstrBot 是 --detach 后台启动，
    关闭标签一般也不会停止它，需要停止请用 stop-all.sh。

下一步：
  1. 在前两个标签扫码登录（或打开上面的 WebUI 扫码）；
  2. 等测试 AstrBot 启动、两个 NapCat 反向连接成功；
  3. 运行环境自检：
     cd "${REPO_ROOT}"
     PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor \\
       --config tools/astrbot_e2e/config.local.json
  4. 运行用例：
     PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run-suite \\
       --cases-dir tools/astrbot_e2e/cases \\
       --config tools/astrbot_e2e/config.local.json --attach

停止：
  bash ${SCRIPT_DIR}/stop-all.sh
EOF
