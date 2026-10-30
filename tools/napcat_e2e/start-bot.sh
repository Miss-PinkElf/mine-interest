#!/usr/bin/env bash
# 单独启动「测试机器人」容器（17号）
#
# 用法：
#   bash tools/napcat_e2e/start-bot.sh
#   bash tools/napcat_e2e/start-bot.sh --stop-production   # 自动停止生产容器 napcat
#   bash tools/napcat_e2e/start-bot.sh --logs              # 启动后跟随日志
#   bash tools/napcat_e2e/start-bot.sh --restart           # 已在运行则 docker restart
#
# 说明：
#   - 17号 同时被生产容器 napcat 使用；默认检测到生产容器会中止。
#   - 扫码登录后，NapCat 会读取 onebot11_<qq>.json 并监听 6200。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

set_tab_title "测试机器人(17号)"

STOP_PRODUCTION=0
FOLLOW_LOGS=0
RESTART=0

while [ $# -gt 0 ]; do
  case "$1" in
    --stop-production) STOP_PRODUCTION=1 ;;
    --logs) FOLLOW_LOGS=1 ;;
    --restart) RESTART=1 ;;
    -h|--help)
      sed -n '2,/^$/p' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    *) die "未知参数：$1" ;;
  esac
  shift
done

ensure_docker
ensure_bot_config
check_production_container

# 原生 QQ 可能也登录了 17号；Docker 登录会把它顶下线，这里只提示不阻断。
if pgrep -f "/Applications/QQ.app/Contents/MacOS/QQ" >/dev/null 2>&1; then
  warn "检测到原生 QQ 正在运行；如果它登录了 17号，Docker 登录会把它顶下线。"
fi

if [ "${RESTART}" = "1" ] && docker ps --format '{{.Names}}' | grep -qx 'napcat-e2e-bot'; then
  # 已在运行：用 docker restart（等价于停掉再启动整个容器），
  # 不要进容器 kill QQ，否则入口脚本没有守护进程，容器可能直接退出。
  info "重启测试机器人容器 napcat-e2e-bot ..."
  docker restart napcat-e2e-bot >/dev/null
else
  info "启动测试机器人容器 napcat-e2e-bot ..."
  compose up -d napcat-e2e-bot
fi

info "容器已启动。首次运行请在日志或 WebUI 扫码登录 ${BOT_QQ}。"
print_endpoints

if [ "${FOLLOW_LOGS}" = "1" ]; then
  info "跟随日志（Ctrl-C 只退出日志，不会停止容器）..."
  docker logs -f napcat-e2e-bot
fi
