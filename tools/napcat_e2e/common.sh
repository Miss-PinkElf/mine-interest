#!/usr/bin/env bash
# 共享变量与函数（Docker 双容器 E2E）
#
# 被 start-all.sh / start-bot.sh / start-sender.sh / start-astrbot.sh /
# stop-all.sh / status.sh 通过 source 引入。
#
# 约定：
#   - 运行数据放在仓库外：默认 ~/.qq-e2e-docker
#   - 两个 QQ 账号：bot=17号(3254276668)，sender=C#(1961618848)
#   - token 与 tools/astrbot_e2e/config.local.json 保持一致
#   - 不把真实 token、rkey、完整鉴权 URL 写入仓库

set -euo pipefail

# ---------- 路径 ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/compose.yaml"
E2E_CONFIG="${REPO_ROOT}/tools/astrbot_e2e/config.local.json"
VENV_PY="${REPO_ROOT}/backend/.venv/bin/python"

# ---------- 可选本地覆盖 ----------
# 如需修改端口/账号/token，复制 .env.example 为 .env 后修改；
# .env 已在 .gitignore 中忽略。
if [ -f "${SCRIPT_DIR}/.env" ]; then
  # set -a 让 .env 中的变量自动 export，供 docker compose 读取。
  set -a
  # shellcheck disable=SC1091
  . "${SCRIPT_DIR}/.env"
  set +a
fi

# ---------- 默认值 ----------
E2E_ROOT="${E2E_ROOT:-${HOME}/.qq-e2e-docker}"

# 测试账号
BOT_QQ="${BOT_QQ:-3254276668}"          # 17号
SENDER_QQ="${SENDER_QQ:-1961618848}"    # C#

# OneBot token（与 tools/astrbot_e2e/config.local.json 对齐）
BOT_WS_TOKEN="${BOT_WS_TOKEN:-e2e-bot-token}"
SENDER_WS_TOKEN="${SENDER_WS_TOKEN:-e2e-sender-token}"
REVERSE_WS_TOKEN="${REVERSE_WS_TOKEN:-e2e-reverse-token}"

# NapCat WebUI token（仅本机 127.0.0.1 可访问）
BOT_WEBUI_TOKEN="${BOT_WEBUI_TOKEN:-e2e-bot-webui}"
SENDER_WEBUI_TOKEN="${SENDER_WEBUI_TOKEN:-e2e-sender-webui}"

# 测试 AstrBot
E2E_PLUGIN="${E2E_PLUGIN:-astrbot_plugin_cc_qq}"
TEST_ASTRBOT_ROOT="${TEST_ASTRBOT_ROOT:-${HOME}/.astrbot-e2e}"
TEST_ASTRBOT_LOG="${TEST_ASTRBOT_ROOT}/data/logs/astrbot.log"

# 固定端口
BOT_ONEBOT_PORT=6200
SENDER_ONEBOT_PORT=6201
BOT_WEBUI_PORT=16299
SENDER_WEBUI_PORT=16398
TEST_ASTRBOT_WEBUI_PORT=6186
TEST_ASTRBOT_REVERSE_PORT=6198

# 宿主机 UID/GID（供 compose 使用）
NAPCAT_UID="${NAPCAT_UID:-$(id -u)}"
NAPCAT_GID="${NAPCAT_GID:-$(id -g)}"
TZ="${TZ:-Asia/Shanghai}"

# 导出给 docker compose 做变量替换
export E2E_ROOT
export BOT_QQ SENDER_QQ
export BOT_WS_TOKEN SENDER_WS_TOKEN REVERSE_WS_TOKEN
export BOT_WEBUI_TOKEN SENDER_WEBUI_TOKEN
export E2E_PLUGIN
export TEST_ASTRBOT_ROOT
export NAPCAT_UID NAPCAT_GID TZ

# ---------- 日志 ----------
info() { printf '[e2e] %s\n' "$*"; }
warn() { printf '[e2e][warn] %s\n' "$*" >&2; }
die() { printf '[e2e][error] %s\n' "$*" >&2; exit 1; }

# ---------- 通用 ----------
compose() {
  docker compose -f "${COMPOSE_FILE}" "$@"
}

require_file() {
  [ -f "$1" ] || die "缺少文件：$1"
}

require_exec() {
  [ -x "$1" ] || die "缺少可执行文件：$1"
}

ensure_docker() {
  command -v docker >/dev/null 2>&1 || die "未找到 docker，请先安装并启动 OrbStack/Docker Desktop"
  docker info >/dev/null 2>&1 || die "Docker daemon 未就绪，请先启动 OrbStack/Docker Desktop"
}

ensure_astrbot_prereqs() {
  require_exec "${VENV_PY}"
  require_file "${E2E_CONFIG}"
}

ensure_dirs() {
  mkdir -p \
    "${E2E_ROOT}/bot/QQ" \
    "${E2E_ROOT}/bot/config" \
    "${E2E_ROOT}/bot/plugins" \
    "${E2E_ROOT}/sender/QQ" \
    "${E2E_ROOT}/sender/config" \
    "${E2E_ROOT}/sender/plugins"
}

# 检查端口是否在监听（NapCat 登录后会开 OneBot WS 服务端）。
is_port_listening() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

# 等待 NapCat 的 OneBot 账号真正就绪。
# 只检查端口不够：容器刚启动/重连时端口可能已开，但账号还没登录；
# 这里用 wait_onebot.py 实际连接并调用 get_login_info。
wait_for_onebot_ready() {
  local port="$1"
  local token="$2"
  local expected_qq="$3"
  local label="$4"
  local i
  info "等待 ${label}（OneBot ${port}）登录就绪；请先在对应 NapCat 标签扫码登录 ..."
  for i in $(seq 1 600); do
    if is_port_listening "${port}" \
      && PYTHONPATH="${REPO_ROOT}/tools" "${VENV_PY}" \
        "${SCRIPT_DIR}/wait_onebot.py" "${port}" "${token}" "${expected_qq}" >/dev/null 2>&1; then
      info "${label} 已就绪（${port}）"
      return 0
    fi
    if [ $((i % 10)) -eq 0 ]; then
      info "仍在等待 ${label}（${port}）..."
    fi
    sleep 3
  done
  die "等待 ${label}（${port}）就绪超时（30 分钟）"
}

# 等待 NapCat 的 OneBot WS 端口上线。
# 测试 AstrBot 的 start-instance 会连接 6200/6201 校验账号；
# 如果容器还没扫码登录，start-instance 会超时并停掉刚启动的实例。
wait_for_onebot() {
  local port="$1"
  local label="$2"
  local i
  if is_port_listening "${port}"; then
    info "${label} 已监听 ${port}"
    return 0
  fi
  info "等待 ${label}（OneBot ${port}）上线；请先在对应 NapCat 标签扫码登录 ..."
  for i in $(seq 1 600); do
    if is_port_listening "${port}"; then
      info "${label} 已监听 ${port}"
      return 0
    fi
    if [ $((i % 10)) -eq 0 ]; then
      info "仍在等待 ${label}（${port}）..."
    fi
    sleep 3
  done
  die "等待 ${label}（${port}）超时（30 分钟）"
}

# 给当前 iTerm2 标签设置标题（只在终端里执行时生效）。
set_tab_title() {
  if [ -t 1 ]; then
    printf '\033]0;%s\007' "$1"
  fi
}

# 调用 tools/astrbot_e2e 的 start-instance。
# 容器刚重启/刚扫码时，bot 的 OneBot WS 可能瞬断，start-instance 会报
# "Server disconnected"；这里做少量重试，避免一次瞬时断连就失败。
START_INSTANCE_RETRY_ATTEMPTS="${START_INSTANCE_RETRY_ATTEMPTS:-3}"
START_INSTANCE_RETRY_DELAY_SECONDS="${START_INSTANCE_RETRY_DELAY_SECONDS:-3}"

run_start_instance() {
  local attempt
  for attempt in $(seq 1 "${START_INSTANCE_RETRY_ATTEMPTS}"); do
    info "调用 start-instance（第 ${attempt}/${START_INSTANCE_RETRY_ATTEMPTS} 次）..."
    if (
      cd "${REPO_ROOT}"
      PYTHONPATH="${REPO_ROOT}/tools" "${VENV_PY}" -m astrbot_e2e.cli start-instance \
        --plugin "${E2E_PLUGIN}" \
        --config "${E2E_CONFIG}"
    ); then
      return 0
    fi
    warn "start-instance 失败；${START_INSTANCE_RETRY_DELAY_SECONDS} 秒后重试 ..."
    sleep "${START_INSTANCE_RETRY_DELAY_SECONDS}"
  done
  return 1
}

# 只在文件不存在时写入，避免覆盖用户手工修改。
write_if_missing() {
  local path="$1"
  if [ -f "${path}" ]; then
    info "保留已有配置：${path}"
    return 0
  fi
  cat > "${path}"
  info "已生成配置：${path}"
}

# NapCat 运行时配置（通用与账号级共用同一份内容）。
write_napcat_runtime_config() {
  local path="$1"
  write_if_missing "${path}" <<'EOF'
{
  "fileLog": false,
  "consoleLog": true,
  "fileLogLevel": "debug",
  "consoleLogLevel": "info",
  "packetBackend": "auto",
  "packetServer": "",
  "o3HookMode": 1,
  "bypass": {
    "hook": false,
    "window": false,
    "module": false,
    "process": false,
    "container": false,
    "js": false
  },
  "autoTimeSync": true
}
EOF
}

write_webui_config() {
  local path="$1"
  local token="$2"
  write_if_missing "${path}" <<EOF
{
  "host": "0.0.0.0",
  "port": 6099,
  "token": "${token}",
  "loginRate": 10
}
EOF
}

# ---------- 机器人容器配置 ----------
ensure_bot_config() {
  ensure_dirs

  # 通用 napcat.json 必须存在：否则 entrypoint 会复制镜像默认配置，
  # 可能覆盖我们生成的 webui.json。
  write_napcat_runtime_config "${E2E_ROOT}/bot/config/napcat.json"
  write_napcat_runtime_config "${E2E_ROOT}/bot/config/napcat_${BOT_QQ}.json"
  write_webui_config "${E2E_ROOT}/bot/config/webui.json" "${BOT_WEBUI_TOKEN}"

  write_if_missing "${E2E_ROOT}/bot/config/onebot11_${BOT_QQ}.json" <<EOF
{
  "network": {
    "httpServers": [],
    "httpSseServers": [],
    "httpClients": [],
    "websocketServers": [
      {
        "enable": true,
        "name": "e2e-observer",
        "host": "0.0.0.0",
        "port": ${BOT_ONEBOT_PORT},
        "reportSelfMessage": false,
        "enableForcePushEvent": true,
        "messagePostFormat": "array",
        "token": "${BOT_WS_TOKEN}",
        "debug": false,
        "heartInterval": 30000
      }
    ],
    "websocketClients": [
      {
        "enable": true,
        "name": "AstrBot-E2E",
        "url": "ws://host.docker.internal:${TEST_ASTRBOT_REVERSE_PORT}/ws",
        "reportSelfMessage": false,
        "messagePostFormat": "array",
        "token": "${REVERSE_WS_TOKEN}",
        "debug": false,
        "heartInterval": 30000,
        "reconnectInterval": 30000,
        "verifyCertificate": true
      }
    ],
    "plugins": []
  },
  "musicSignUrl": "",
  "enableLocalFile2Url": false,
  "parseMultMsg": false,
  "imageDownloadProxy": "",
  "timeout": {
    "baseTimeout": 10000,
    "uploadSpeedKBps": 256,
    "downloadSpeedKBps": 256,
    "maxTimeout": 1800000
  }
}
EOF
}

# ---------- 发送者容器配置 ----------
ensure_sender_config() {
  ensure_dirs

  write_napcat_runtime_config "${E2E_ROOT}/sender/config/napcat.json"
  write_napcat_runtime_config "${E2E_ROOT}/sender/config/napcat_${SENDER_QQ}.json"
  write_webui_config "${E2E_ROOT}/sender/config/webui.json" "${SENDER_WEBUI_TOKEN}"

  write_if_missing "${E2E_ROOT}/sender/config/onebot11_${SENDER_QQ}.json" <<EOF
{
  "network": {
    "httpServers": [],
    "httpSseServers": [],
    "httpClients": [],
    "websocketServers": [
      {
        "enable": true,
        "name": "e2e-sender",
        "host": "0.0.0.0",
        "port": ${SENDER_ONEBOT_PORT},
        "reportSelfMessage": false,
        "enableForcePushEvent": true,
        "messagePostFormat": "array",
        "token": "${SENDER_WS_TOKEN}",
        "debug": false,
        "heartInterval": 30000
      }
    ],
    "websocketClients": [],
    "plugins": []
  },
  "musicSignUrl": "",
  "enableLocalFile2Url": false,
  "parseMultMsg": false,
  "imageDownloadProxy": "",
  "timeout": {
    "baseTimeout": 10000,
    "uploadSpeedKBps": 256,
    "downloadSpeedKBps": 256,
    "maxTimeout": 1800000
  }
}
EOF
}

# ---------- 安全预检 ----------
# 生产容器 napcat 也使用 17号；测试机器人启动前必须停止它。
# STOP_PRODUCTION=1 时自动停止并记录标记，stop-all.sh 会恢复。
check_production_container() {
  if ! docker ps --format '{{.Names}}' | grep -qx 'napcat'; then
    return 0
  fi
  if [ "${STOP_PRODUCTION:-0}" = "1" ]; then
    info "停止生产容器 napcat（17号 让给测试机器人）..."
    docker stop napcat >/dev/null
    mkdir -p "${E2E_ROOT}"
    touch "${E2E_ROOT}/production-stopped"
    info "已记录生产停止标记：${E2E_ROOT}/production-stopped"
    return 0
  fi
  die "生产容器 napcat 正在运行并占用 17号。请先 docker stop napcat，或加 --stop-production。"
}

# 原生 QQ 与 Docker 发送者共用 C#；未退出时会被 Docker 顶下线。
check_native_qq() {
  if ! pgrep -f "/Applications/QQ.app/Contents/MacOS/QQ" >/dev/null 2>&1; then
    return 0
  fi
  if [ "${ALLOW_NATIVE_QQ:-0}" = "1" ]; then
    warn "检测到原生 QQ 正在运行；Docker 发送者登录 C# 时会把原生 C# 顶下线。"
    return 0
  fi
  die "检测到原生 QQ 正在运行。请先退出原生 QQ，或加 --allow-native-qq。"
}

# ---------- 展示 ----------
webui_url() {
  local config_dir="$1"
  local host_port="$2"
  local token=""
  if [ -f "${config_dir}/webui.json" ]; then
    token="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1],encoding="utf-8-sig")).get("token",""))' "${config_dir}/webui.json" 2>/dev/null || true)"
  fi
  if [ -n "${token}" ]; then
    printf 'http://127.0.0.1:%s/webui?token=%s' "${host_port}" "${token}"
  else
    printf 'http://127.0.0.1:%s/webui' "${host_port}"
  fi
}

print_endpoints() {
  info "机器人 17号（${BOT_QQ}）OneBot WS：ws://127.0.0.1:${BOT_ONEBOT_PORT}"
  info "发送者 C#（${SENDER_QQ}）OneBot WS：ws://127.0.0.1:${SENDER_ONEBOT_PORT}"
  info "机器人 WebUI：$(webui_url "${E2E_ROOT}/bot/config" "${BOT_WEBUI_PORT}")"
  info "发送者 WebUI：$(webui_url "${E2E_ROOT}/sender/config" "${SENDER_WEBUI_PORT}")"
  info "测试 AstrBot：WebUI ${TEST_ASTRBOT_WEBUI_PORT} / 反向 WS ${TEST_ASTRBOT_REVERSE_PORT}"
}

print_manual_log_commands() {
  cat <<EOF
手动查看日志：
  docker logs -f napcat-e2e-bot
  docker logs -f napcat-e2e-sender
  tail -F ${TEST_ASTRBOT_LOG}
EOF
}
