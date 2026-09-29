#!/usr/bin/env python3
"""
Codex 降级探测代理（流式版）

- 逐块实时转发，不破坏流式体验
- 记录服务端真实信号：x-codex-* 响应头 + SSE 事件里的 model
- 绝不记录 Authorization / token 等凭据
- 启动时读取 ~/.codex/.env 里的 HTTPS_PROXY（Codex 走代理连 chatgpt.com，本代理必须同样）
- 进程里已经存在的环境变量不会被这个文件覆盖

启动：
    python3 probe_proxy.py

Codex 侧配置：
    [model_providers.probe]
    name                  = "probe"
    base_url              = "http://127.0.0.1:8787/backend-api/codex"
    wire_api              = "responses"
    supports_websockets   = false
    requires_openai_auth  = true
"""
import codecs
import http.server
import json
import os
import socketserver
import sys
import time
import urllib.error
import urllib.request

UPSTREAM = "https://chatgpt.com"
OUT = os.path.expanduser("~/.codex-probe/turns.jsonl")
CODEX_ENV = os.path.expanduser("~/.codex/.env")
PORT = int(os.environ.get("PROBE_PORT", "8787"))
PROXY_ENV_KEYS = ("HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy")

# 只保留这些前缀的响应头（服务端真实信号）
HEADER_ALLOW = ("x-codex", "x-models", "x-openai")
# 关心的 SSE 事件
INTERESTING = (
    "response.created",
    "response.completed",
    "response.failed",
    "response.incomplete",
)
# 读上游时的分块大小
CHUNK = 2048
# 上游读超时（秒）。SSE 有空闲 keepalive，通常远小于此值
UPSTREAM_TIMEOUT = 300


def parse_env_line(line):
    """解析一行 KEY=VALUE。注释、空行和非法键返回 None。"""
    text = line.strip()
    if not text or text.startswith("#"):
        return None
    if text.startswith("export "):
        text = text[len("export "):].strip()
    if "=" not in text:
        return None
    key, value = text.split("=", 1)
    key = key.strip()
    if not key or any(not (ch.isalnum() or ch == "_") for ch in key):
        return None
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return key, value


def load_codex_env(path=CODEX_ENV):
    """把 ~/.codex/.env 读进当前进程。已有环境变量保持不动。返回新写入的键数量。"""
    try:
        lines = open(path, encoding="utf-8")
    except FileNotFoundError:
        print(f"[warn] 未找到 {path}，无法读取代理变量。", file=sys.stderr)
        return 0
    except OSError as exc:
        print(f"[warn] 读取 {path} 失败：{exc}", file=sys.stderr)
        return 0

    applied = 0
    with lines:
        for line in lines:
            item = parse_env_line(line)
            if item is None:
                continue
            key, value = item
            if key in os.environ:
                continue
            os.environ[key] = value
            applied += 1
    return applied


def proxy_env_ready():
    return any(os.environ.get(key) for key in PROXY_ENV_KEYS)


def write_record(rec):
    """追加一条记录。失败不影响转发。"""
    try:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


class Proxy(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    # SSE 场景下禁用 Nagle，减少转发延迟
    disable_nagle_algorithm = True

    def log_message(self, *args):
        pass

    # ---------- 请求处理 ----------

    def do_POST(self):
        self._handle("POST")

    def do_GET(self):
        self._handle("GET")

    def _handle(self, method):
        try:
            self._run(method)
        except (BrokenPipeError, ConnectionResetError):
            # Codex 主动取消，属正常现象
            pass
        except Exception as e:
            write_record({"kind": "handler_error", "path": self.path, "error": repr(e)})

    def _run(self, method):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None

        req_model = None
        if body:
            try:
                req_model = json.loads(body).get("model")
            except Exception:
                pass

        req = urllib.request.Request(UPSTREAM + self.path, data=body, method=method)
        for k, v in self.headers.items():
            if k.lower() in ("host", "content-length", "accept-encoding"):
                continue
            req.add_header(k, v)
        req.add_header("Accept-Encoding", "identity")

        try:
            resp = urllib.request.urlopen(req, timeout=UPSTREAM_TIMEOUT)
        except urllib.error.HTTPError as e:
            resp = e
        except Exception as e:
            write_record({"kind": "proxy_error", "path": self.path, "error": str(e)})
            self.send_error(502, "upstream unreachable")
            return

        # 采集信号头
        signals = {}
        for k, v in resp.headers.items():
            kl = k.lower()
            if kl.startswith(HEADER_ALLOW):
                signals[kl] = v

        # 是否流式：chunked / 无 Content-Length / text/event-stream
        te = (resp.headers.get("Transfer-Encoding") or "").lower()
        cl = resp.headers.get("Content-Length")
        ctype = resp.headers.get("Content-Type") or ""
        streaming = ("chunked" in te) or (cl is None) or ("event-stream" in ctype)

        # 透传响应头
        self.send_response(resp.status)
        for k, v in resp.headers.items():
            if k.lower() in ("content-length", "content-encoding", "transfer-encoding", "connection"):
                continue
            self.send_header(k, v)
        if streaming:
            self.send_header("Transfer-Encoding", "chunked")
        else:
            self.send_header("Content-Length", cl)
        self.end_headers()

        events = {}
        if streaming:
            timing = self._relay_stream(resp, events)
        else:
            self.wfile.write(resp.read())
            timing = {}

        rec = {
            "ts": int(time.time()),
            "path": self.path,
            "status": resp.status,
            "req_model": req_model,
            "signals": signals,
        }
        rec.update(timing)
        rec.update(events)
        write_record(rec)

    # ---------- 流式转发 ----------

    def _relay_stream(self, resp, events):
        """逐块转发上游响应，同时增量解析 SSE。返回计时信息。"""
        decoder = codecs.getincrementaldecoder("utf-8")("ignore")
        buf = ""
        t0 = time.monotonic()
        first_chunk_ms = None
        n_chunks = 0

        while True:
            try:
                chunk = resp.read(CHUNK)
            except Exception as e:
                write_record({"kind": "stream_error", "path": self.path, "error": str(e)})
                break
            if not chunk:
                break

            if first_chunk_ms is None:
                first_chunk_ms = int((time.monotonic() - t0) * 1000)
            n_chunks += 1

            # 1) 增量解析（不影响转发）
            buf += decoder.decode(chunk)
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                self._parse_sse_line(line.strip(), events)

            # 2) 实时转发
            self.wfile.write(b"%x\r\n" % len(chunk) + chunk + b"\r\n")
            self.wfile.flush()

        total_ms = int((time.monotonic() - t0) * 1000)

        try:
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
        except Exception:
            pass

        return {
            "first_chunk_ms": first_chunk_ms,
            "total_stream_ms": total_ms,
            "chunks": n_chunks,
        }

    def _parse_sse_line(self, line, events):
        if not line.startswith("data:"):
            return
        payload = line[5:].strip()
        if not payload or payload == "[DONE]":
            return
        try:
            ev = json.loads(payload)
        except Exception:
            return
        t = ev.get("type")
        if t not in INTERESTING:
            return
        inner = ev.get("response") if isinstance(ev.get("response"), dict) else ev
        events[t] = {
            "model": inner.get("model"),
            "status": inner.get("status"),
            "id": inner.get("id"),
        }


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    applied = load_codex_env()
    if not proxy_env_ready():
        print("[warn] 未检测到 HTTPS_PROXY —— 上游 chatgpt.com 大概率连不上。", file=sys.stderr)
        print(f"       已尝试读取 {CODEX_ENV}。", file=sys.stderr)
    elif applied:
        print(f"[probe] 已从 {CODEX_ENV} 读取代理变量", flush=True)

    print(f"[probe] listening on 127.0.0.1:{PORT}", flush=True)
    print(f"[probe] 记录写入 {OUT}", flush=True)
    server = ThreadingServer(("127.0.0.1", PORT), Proxy)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[probe] 退出", flush=True)


if __name__ == "__main__":
    main()
