#!/usr/bin/env bash
# 单独启动「测试发送者」容器（C#）
#
# 用法：
#   bash tools/napcat_e2e/start-sender.sh
#   bash tools/napcat_e2e/start-sender.sh --allow-native-qq   # 原生 QQ 在跑也继续
#   bash tools/napcat_e2e/start-sender.sh --logs              # 启动后跟随日志
#   bash tools/napcat_e2e/start-sender.sh --restart           # 已在运行则 docker restart
#
# 说明：
#   - 发送者容器只暴露 OneBot WS 6201，不连接 AstrBot。
#   - E2E 工具通过 6201 冒充 C# 给测试群发消息。
#   - 如果原生 QQ 仍登录 C#，Docker 登录会把它顶下线；默认中止，需显式放行。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

set_tab_title "测试发送者(C#)"

ALLOW_NATIVE_QQ=0
FOLLOW_LOGS=0
RESTART=0

while [ $# -gt 0 ]; do
  case "$1" in
    --allow-native-qq) ALLOW_NATIVE_QQ=1 ;;
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
ensure_sender_config
check_native_qq

if [ "${RESTART}" = "1" ] && docker ps --format '{{.Names}}' | grep -qx 'napcat-e2e-sender'; then
  # 已在运行：用 docker restart，避免进容器 kill 后入口脚本不守护的问题。
  info "重启测试发送者容器 napcat-e2e-sender ..."
  docker restart napcat-e2e-sender >/dev/null
else
  info "启动测试发送者容器 napcat-e2e-sender ..."
  compose up -d napcat-e2e-sender
fi

info "容器已启动。首次运行请在日志或 WebUI 扫码登录 ${SENDER_QQ}。"
print_endpoints

if [ "${FOLLOW_LOGS}" = "1" ]; then
  info "跟随日志（Ctrl-C 只退出日志，不会停止容器）..."
  docker logs -f napcat-e2e-sender
fi
