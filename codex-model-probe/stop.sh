#!/usr/bin/env bash
#
# 停止本机 Codex 模型探测代理（probe_proxy.py）。
#
# 只结束「正在监听 127.0.0.1:$PROBE_PORT（默认 8787）」
# 且命令行包含 probe_proxy.py 的进程。
# 该端口上若是别的程序，拒绝结束并退出。
#
#     ./stop.sh
#     PROBE_PORT=8787 ./stop.sh
#
set -euo pipefail

PORT="${PROBE_PORT:-8787}"
ADDR="127.0.0.1:${PORT}"

say() { printf '%s\n' "$*"; }

if ! command -v lsof >/dev/null 2>&1; then
  say "找不到 lsof，无法确认 ${ADDR} 上的进程。"
  exit 1
fi

listen_pids() {
  lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN -t 2>/dev/null | awk 'NF && !seen[$0]++' || true
}

pids="$(listen_pids)"

if [ -z "${pids}" ]; then
  say "探测代理未在运行（${ADDR} 没有监听）。"
  exit 0
fi

probe_pids=""

for pid in ${pids}; do
  cmd="$(ps -p "${pid}" -o command= 2>/dev/null || true)"
  case "${cmd}" in
    *probe_proxy.py*)
      probe_pids="${probe_pids} ${pid}"
      ;;
    *)
      say "端口 ${ADDR} 上的进程不是探测代理，已跳过：pid=${pid} ${cmd:-（无法读取命令行）}"
      ;;
  esac
done

if [ -z "${probe_pids}" ]; then
  say "没有结束任何进程。请确认占用 ${ADDR} 的是不是探测代理。"
  exit 1
fi

stop_one() {
  pid="$1"
  kill -TERM "${pid}" 2>/dev/null || true
  i=0
  while [ "${i}" -lt 10 ]; do
    if ! kill -0 "${pid}" 2>/dev/null; then
      return 0
    fi
    sleep 0.3
    i=$((i + 1))
  done
  if kill -0 "${pid}" 2>/dev/null; then
    kill -KILL "${pid}" 2>/dev/null || true
    say "pid=${pid} 未响应 SIGTERM，已发送 SIGKILL。"
  fi
}

for pid in ${probe_pids}; do
  say "正在停止探测代理 pid=${pid}（${ADDR}）"
  stop_one "${pid}"
done

still=""
for pid in $(listen_pids); do
  cmd="$(ps -p "${pid}" -o command= 2>/dev/null || true)"
  case "${cmd}" in
    *probe_proxy.py*) still="${still} ${pid}" ;;
  esac
done

if [ -n "${still}" ]; then
  say "停止失败，探测代理仍在监听：${still}"
  exit 1
fi

say "探测代理已停止。"
exit 0
