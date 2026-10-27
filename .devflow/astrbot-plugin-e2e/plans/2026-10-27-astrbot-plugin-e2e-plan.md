# AstrBot 插件端到端自动化测试实施计划（Implementation Plan）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> 本计划承接 `.devflow/astrbot-plugin-e2e/plans/2026-10-27-astrbot-plugin-e2e-align.md`。执行前先读设计稿；设计与本计划冲突时，以设计稿为准并先回写记录。

**Goal（目标）：** 在 `tools/astrbot_e2e/` 建立通用的 AstrBot 插件端到端测试运行器（Runner），先用探针插件打通“发送 → 采集 → 断言 → 重载”，再用 `cc_qq /help` 验证真实插件。

**Architecture（架构）：** 独立 Runner 通过两个 NapCat OneBot WebSocket 通道发消息与收事件；AstrBot 测试实例使用独立数据根、端口与插件目录，由 Runner 子进程管理；断言以消息为主、日志为辅，语义断言按用例可选启用。

**Tech Stack（技术栈）：** Python 3.9.6（`backend/.venv`）、`aiohttp`、`unittest`、`asyncio`、JSON 配置与用例；AstrBot 4.29.3 CLI；NapCat OneBot v11。

---

## 0. 执行前置与硬约束

- **先做 Spike 0**：同机双开 QQ 未验证前，不实现 Runner 的端到端部分。
- **生产隔离**：禁止修改 `~/.astrbot`、生产端口 `6185 / 6199 / 6099`、生产 QQ 配置；Runner 只管理自己启动的测试实例。
- **凭据不入库**：QQ 号、群号、Token、WebUI 密码、LLM Key 只放在 `tools/astrbot_e2e/config.local.json`；该文件与 `reports/` 必须加入 `.gitignore`。
- **提交策略**：本仓库要求每次提交前征得用户同意；本计划中的改动完成后先列给用户，确认后再用中文提交信息提交，不自动 `git commit`。
- **测试框架**：`backend/.venv` 没有 `pytest`，统一使用 `unittest`；不新增第三方依赖。
- **Python 3.9 兼容**：使用 `typing.Optional / List / Dict / Any`，不使用 `list[str]`、`dict | None` 等 3.10+ 写法。
- **不碰生产插件**：只从 `integrations/astrbot/<plugin>` 复制到测试实例，不修改源目录。
- **人工登录**：两个测试 QQ 号的登录由用户完成；Runner 只验证登录后的 OneBot 状态，不自动扫码、不绕过风控。

## 1. 文件地图

| 文件 | 责任 |
| --- | --- |
| `tools/astrbot_e2e/__init__.py` | 包标记与版本号 |
| `tools/astrbot_e2e/config.py` | 读取、校验、脱敏本地配置 |
| `tools/astrbot_e2e/cases.py` | 加载与校验用例 JSON |
| `tools/astrbot_e2e/assertions.py` | 包含、正则断言与结果对象 |
| `tools/astrbot_e2e/reports.py` | 运行目录、JSON 报告、证据写入 |
| `tools/astrbot_e2e/log_capture.py` | 按文件偏移截取日志窗口 |
| `tools/astrbot_e2e/onebot.py` | OneBot 消息构造、事件过滤、WS 客户端 |
| `tools/astrbot_e2e/bootstrap.py` | 初始化测试实例、写测试配置、同步插件 |
| `tools/astrbot_e2e/orchestrator.py` | 启动/停止测试实例、PID 归属、就绪检查 |
| `tools/astrbot_e2e/reloader.py` | WebUI 登录与插件重载 |
| `tools/astrbot_e2e/llm_judge.py` | OpenAI 兼容接口的语义判定 |
| `tools/astrbot_e2e/runner.py` | 单个用例的执行流水线 |
| `tools/astrbot_e2e/cli.py` | CLI 入口与退出码 |
| `tools/astrbot_e2e/config.example.json` | 配置模板（占位值，无凭据） |
| `tools/astrbot_e2e/cases/probe_echo.json` | 探针插件用例 |
| `tools/astrbot_e2e/cases/cc_qq_help.json` | 真实插件用例 |
| `tools/astrbot_e2e/fixtures/astrbot_plugin_e2e_probe/` | 探针插件源码 |
| `tools/astrbot_e2e/fixtures/napcat/` | 两个 NapCat 实例的 OneBot 配置样例 |
| `tools/astrbot_e2e/tests/` | 单元测试与本地集成测试 |

## 2. 任务依赖

```text
Task 0 Spike 0（硬前置）
  └─ Task 13 探针 E2E
       └─ Task 14 cc_qq E2E

Task 1 配置
  ├─ Task 2 用例
  ├─ Task 3 断言
  ├─ Task 4 报告
  ├─ Task 5 日志
  └─ Task 6 OneBot
       ├─ Task 7 测试实例引导
       ├─ Task 8 实例编排
       ├─ Task 9 重载
       └─ Task 11 语义判定
            └─ Task 12 Runner + CLI
                 ├─ Task 13
                 └─ Task 14

Task 10 探针插件 ── Task 13
Task 15 Verify / Close
```

## 3. 任务清单

### Task 0：Spike 0 — 同机双开 QQ 可行性

**目标：** 确认 macOS 上能否同时运行两个 QQ 实例、各自加载 NapCat、各自暴露 OneBot 端口，并且测试 AstrBot 实例不碰生产数据。

**前置：** 用户在场，准备两个测试 QQ 号和专用测试群；QQ 登录由用户人工完成。

**文件：**
- Create: `.devflow/astrbot-plugin-e2e/plans/2026-10-27-spike-0-dual-qq-result.md`

- [ ] **Step 1：记录生产基线**

Run:
```bash
lsof -nP -iTCP -sTCP:LISTEN | grep -E ':(6185|6199|6099)' || true
ps aux | grep -E 'astrbot run|QQ.app/Contents/MacOS/QQ' | grep -v grep || true
git status --short
```

Expected: 看到生产 AstrBot、QQ、NapCat WebUI 端口；记录 PID 与端口，供最后对比。

- [ ] **Step 2：尝试启动第二个 QQ 实例**

Run:
```bash
QQ_E2E_DIR="$HOME/.qq-e2e"
mkdir -p "$QQ_E2E_DIR"
open -n -a /Applications/QQ.app --args --no-sandbox --user-data-dir="$QQ_E2E_DIR"
```

若 `open -n` 无效，改用直接启动：

```bash
/Applications/QQ.app/Contents/MacOS/QQ --no-sandbox --user-data-dir="$QQ_E2E_DIR" &
```

Expected: 出现第二个 QQ 进程与登录窗口；用户登录第二个测试号。

- [ ] **Step 3：检查进程与 NapCat 配置隔离**

Run:
```bash
ps aux | grep '/Applications/QQ.app/Contents/MacOS/QQ' | grep -v grep
lsof -nP -iTCP -sTCP:LISTEN | grep -E ':(6099|6198|6200|6201)' || true
ls -la "$HOME/Library/Containers/com.tencent.qq/Data/Library/Application Support/QQ/NapCat/config" | head
ls -la "$HOME/.qq-e2e" | head
```

Expected: 两个 QQ 进程；两个 NapCat 配置目录或至少两套 `onebot11_<uin>.json`；端口不冲突。

若两个实例共用同一 NapCat 配置目录，进入 Step 4。

- [ ] **Step 4（仅在配置冲突时）：复制 QQ.app 并改写副本入口**

> 该步骤会复制 `/Applications/QQ.app`，执行前必须得到用户确认。

Run:
```bash
cp -R /Applications/QQ.app /Applications/QQ-e2e.app
mkdir -p "$HOME/.qq-e2e/Documents/napcat"
cp "$HOME/Library/Containers/com.tencent.qq/Data/Documents/loadNapCat.js" \
   "$HOME/.qq-e2e/Documents/loadNapCat.js"
mkdir -p "$HOME/.qq-e2e/Documents/napcat"
cp -R "$HOME/Library/Containers/com.tencent.qq/Data/Documents/napcat/." \
   "$HOME/.qq-e2e/Documents/napcat/"
```

编辑 `/Applications/QQ-e2e.app/Contents/Resources/app/package.json`，把 `main` 改成：

```text
../../../../../Users/<your-user>/.qq-e2e/Documents/loadNapCat.js
```

并编辑 `$HOME/.qq-e2e/Documents/loadNapCat.js`，把其中 `napcat.mjs` 的绝对路径改为 `$HOME/.qq-e2e/Documents/napcat/napcat.mjs`。

Expected: 第二个实例使用独立 NapCat 目录；生产 `QQ.app` 未被修改。

- [ ] **Step 5：为两个实例写入 OneBot 配置**

先创建配置样例：

`tools/astrbot_e2e/fixtures/napcat/onebot11.bot.example.json`：

```json
{
  "network": {
    "httpServers": [],
    "httpSseServers": [],
    "httpClients": [],
    "websocketServers": [
      {
        "enable": true,
        "name": "e2e-observer",
        "host": "127.0.0.1",
        "port": 6200,
        "reportSelfMessage": true,
        "enableForcePushEvent": true,
        "messagePostFormat": "array",
        "token": "<bot-token>",
        "debug": false,
        "heartInterval": 30000
      }
    ],
    "websocketClients": [
      {
        "enable": true,
        "name": "AstrBot-E2E",
        "url": "ws://127.0.0.1:6198/ws",
        "reportSelfMessage": true,
        "messagePostFormat": "array",
        "token": "<reverse-ws-token>",
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
```

`tools/astrbot_e2e/fixtures/napcat/onebot11.sender.example.json`：

```json
{
  "network": {
    "httpServers": [],
    "httpSseServers": [],
    "httpClients": [],
    "websocketServers": [
      {
        "enable": true,
        "name": "e2e-sender",
        "host": "127.0.0.1",
        "port": 6201,
        "reportSelfMessage": false,
        "enableForcePushEvent": true,
        "messagePostFormat": "array",
        "token": "<sender-token>",
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
```

按样例生成实际配置：

- 机器人号：`websocketClients` 指向 `ws://127.0.0.1:6198/ws`（测试 AstrBot），`websocketServers` 监听 `6200`，`reportSelfMessage: true`。
- 发送者号：只监听 `6201`，不接测试 AstrBot。
- 两边 Token 分别与本地配置的 `bot.token`、`sender.token`、`astrbot.reverse_ws_token` 一致。

重启两个 QQ 实例，让配置生效。

- [ ] **Step 6：验证两个 OneBot 端口**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python - <<'PY'
import asyncio, json
import aiohttp

async def login(url, token):
    async with aiohttp.ClientSession() as s:
        async with s.ws_connect(url, headers={"Authorization": f"Bearer {token}"}) as ws:
            await ws.send_json({"action": "get_login_info", "params": {}, "echo": "1"})
            while True:
                msg = await ws.receive_json()
                if msg.get("echo") == "1":
                    print(url, msg)
                    return

asyncio.run(login("ws://127.0.0.1:6200/onebot/v11/ws", "<bot-token>"))
asyncio.run(login("ws://127.0.0.1:6201/onebot/v11/ws", "<sender-token>"))
PY
```

Expected: 两次都返回 `status: ok`，`user_id` 分别等于机器人号与发送者号。

- [ ] **Step 7：测试群收发**

用发送者号向专用测试群发一条 `@机器人 hello-e2e`，确认机器人号能收到并回复；记录消息 ID 与时间。

- [ ] **Step 8：启动测试 AstrBot 实例并确认不碰生产**

Run（在 Task 7 的 `bootstrap.py` 实现完成后执行）：

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli init-instance --config tools/astrbot_e2e/config.local.json
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli start-instance --config tools/astrbot_e2e/config.local.json
```

Expected: 测试实例监听 `6186 / 6198`；生产 `6185 / 6199` 仍在；`~/.astrbot` 未被修改。

- [ ] **Step 9：落盘 Spike 结果**

把命令、输出、端口、账号、配置路径、结论写入：

`.devflow/astrbot-plugin-e2e/plans/2026-10-27-spike-0-dual-qq-result.md`

**通过标准：**

- 两个 QQ 号同时在线；
- 两个 NapCat 配置与日志互不覆盖；
- `6200 / 6201 / 6198 / 6186` 同时可用；
- 发送者能在测试群发消息，机器人能回复；
- 生产实例与生产 QQ 配置未被触碰。

Spike 0 已于 2026-10-27 通过。macOS App Sandbox 下 `NAPCAT_WORKDIR` 必须放在容器内（`~/Library/Containers/com.tencent.qq/Data/Library/Application Support/QQ/NapCat-e2e`）；放在 `~/.qq-e2e/NapCat` 会报 `EPERM mkdir`。双开实例的 native addon / FFmpeg / PacketBackend 警告不阻断文本收发，但富媒体能力保留为风险。详细账号、端口与证据见 `2026-10-27-spike-0-dual-qq-result.md`。

**失败回退：** 按设计稿 6.4 执行：Linux 容器/WSL 发送方 → 第二台设备半自动 → 单账号内部事件注入。把失败原因与选择写回 `decision-log.md`，并暂停后续任务。

---

### Task 1：Runner 包骨架与配置加载

**文件：**
- Create: `tools/astrbot_e2e/__init__.py`
- Create: `tools/astrbot_e2e/config.py`
- Create: `tools/astrbot_e2e/config.example.json`
- Create: `tools/astrbot_e2e/tests/__init__.py`
- Test: `tools/astrbot_e2e/tests/test_config.py`

- [ ] **Step 1：写失败测试**

`tools/astrbot_e2e/tests/test_config.py`：

```python
import json
import tempfile
import unittest
from pathlib import Path

from astrbot_e2e.config import ConfigError, load_config, mask_config


def minimal_config(root: Path) -> dict:
    return {
        "test_root": str(root),
        "webui": {"host": "127.0.0.1", "port": 6186, "username": "e2e", "password": "e2e-pass-123"},
        "astrbot": {
            "command": "astrbot",
            "reverse_ws_host": "127.0.0.1",
            "reverse_ws_port": 6198,
            "reverse_ws_token": "reverse-token",
            "plugins": ["astrbot_plugin_e2e_probe", "astrbot_plugin_cc_qq"],
            "startup_timeout_seconds": 120,
        },
        "bot": {"qq": "10001", "onebot_ws": "ws://127.0.0.1:6200/onebot/v11/ws", "token": "bot-token"},
        "sender": {"qq": "10002", "onebot_ws": "ws://127.0.0.1:6201/onebot/v11/ws", "token": "sender-token"},
        "group_id": "123456789",
        "judge": {"base_url": "", "api_key": "", "model": ""},
        "timeouts": {"message_seconds": 60, "reload_seconds": 120, "log_window_padding_seconds": 5},
    }


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "astrbot-e2e"
        self.path = Path(self.tmp.name) / "config.local.json"

    def write(self, **overrides):
        cfg = minimal_config(self.root)
        cfg.update(overrides)
        self.path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        return cfg

    def test_accepts_minimal_config(self):
        self.write()
        cfg = load_config(self.path)
        self.assertEqual(cfg["group_id"], "123456789")
        self.assertEqual(cfg["test_root"], str(self.root.resolve()))

    def test_rejects_production_root(self):
        self.write(test_root=str(Path.home() / ".astrbot"))
        with self.assertRaisesRegex(ConfigError, "生产数据根"):
            load_config(self.path)

    def test_rejects_same_qq(self):
        cfg = minimal_config(self.root)
        cfg["sender"]["qq"] = cfg["bot"]["qq"]
        self.path.write_text(json.dumps(cfg), encoding="utf-8")
        with self.assertRaisesRegex(ConfigError, "必须不同"):
            load_config(self.path)

    def test_rejects_production_port(self):
        cfg = minimal_config(self.root)
        cfg["webui"]["port"] = 6185
        self.path.write_text(json.dumps(cfg), encoding="utf-8")
        with self.assertRaisesRegex(ConfigError, "生产端口冲突"):
            load_config(self.path)

    def test_masks_secrets(self):
        self.write()
        cfg = load_config(self.path)
        masked = mask_config(cfg)
        self.assertEqual(masked["webui"]["password"], "***")
        self.assertEqual(masked["bot"]["token"], "***")
        self.assertEqual(masked["sender"]["token"], "***")
```

- [ ] **Step 2：运行测试确认失败**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools -v
```

Expected: FAIL，提示 `ModuleNotFoundError: No module named 'astrbot_e2e'` 或 `ImportError`。

- [ ] **Step 3：写最小实现**

`tools/astrbot_e2e/__init__.py`：

```python
"""AstrBot 插件端到端测试运行器（E2E Runner）。"""

__version__ = "0.1.0"
```

`tools/astrbot_e2e/config.py`：

```python
"""本地配置加载、校验与脱敏（Config）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

PRODUCTION_ROOT = (Path.home() / ".astrbot").resolve()
PRODUCTION_PORTS = frozenset({6185, 6199, 6099})
SECRET_KEYS = frozenset({"password", "token", "api_key", "jwt_secret", "secret"})


class ConfigError(ValueError):
    """配置缺失或非法。"""


def load_config(path: Any) -> Dict[str, Any]:
    config_path = Path(path).expanduser()
    if not config_path.exists():
        raise ConfigError("配置文件不存在: {}".format(config_path))
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ConfigError("配置文件不是合法 JSON: {}".format(exc)) from exc
    if not isinstance(raw, dict):
        raise ConfigError("配置文件顶层必须是对象")
    if not str(raw.get("test_root") or "").strip():
        raise ConfigError("缺少配置项: test_root")
    raw["test_root"] = str(Path(raw["test_root"]).expanduser().resolve())
    validate_config(raw)
    return raw


def _port(value: Any, label: str) -> int:
    try:
        port = int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError("{} 必须是整数端口".format(label)) from exc
    if not 1 <= port <= 65535:
        raise ConfigError("{} 端口超出范围: {}".format(label, port))
    return port


def _url_port(value: Any, label: str) -> int:
    parsed = urlparse(str(value or ""))
    if not parsed.hostname:
        raise ConfigError("{} 不是合法 WebSocket URL".format(label))
    try:
        return _port(parsed.port, label)
    except ConfigError:
        raise
    except Exception as exc:
        raise ConfigError("{} 缺少端口".format(label)) from exc


def validate_config(cfg: Dict[str, Any]) -> None:
    for key in ("test_root", "webui", "astrbot", "bot", "sender", "group_id"):
        if not cfg.get(key):
            raise ConfigError("缺少配置项: {}".format(key))

    test_root = Path(cfg["test_root"]).resolve()
    if test_root == PRODUCTION_ROOT:
        raise ConfigError("test_root 不能是生产数据根 ~/.astrbot")

    if not str(cfg["astrbot"].get("command") or "").strip():
        raise ConfigError("astrbot.command 必填")

    bot_qq = str(cfg["bot"].get("qq") or "").strip()
    sender_qq = str(cfg["sender"].get("qq") or "").strip()
    if not bot_qq or not sender_qq:
        raise ConfigError("bot.qq 与 sender.qq 必填")
    if bot_qq == sender_qq:
        raise ConfigError("bot.qq 与 sender.qq 必须不同")

    ports = {
        "webui.port": _port(cfg["webui"].get("port"), "webui.port"),
        "astrbot.reverse_ws_port": _port(cfg["astrbot"].get("reverse_ws_port"), "astrbot.reverse_ws_port"),
        "bot.onebot_ws": _url_port(cfg["bot"].get("onebot_ws"), "bot.onebot_ws"),
        "sender.onebot_ws": _url_port(cfg["sender"].get("onebot_ws"), "sender.onebot_ws"),
    }
    overlap = set(ports.values()) & PRODUCTION_PORTS
    if overlap:
        raise ConfigError("端口与生产端口冲突: {}".format(sorted(overlap)))

    group_id = str(cfg["group_id"]).strip()
    if not group_id.isdigit():
        raise ConfigError("group_id 必须是数字字符串")
    cfg["group_id"] = group_id
    cfg["bot"]["qq"] = bot_qq
    cfg["sender"]["qq"] = sender_qq


def mask_config(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: ("***" if key.lower() in SECRET_KEYS else mask_config(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [mask_config(item) for item in value]
    return value
```

- [ ] **Step 4：写配置模板**

`tools/astrbot_e2e/config.example.json`：

```json
{
  "test_root": "~/.astrbot-e2e",
  "webui": {
    "host": "127.0.0.1",
    "port": 6186,
    "username": "e2e",
    "password": "<webui-password>"
  },
  "astrbot": {
    "command": "astrbot",
    "reverse_ws_host": "127.0.0.1",
    "reverse_ws_port": 6198,
    "reverse_ws_token": "<reverse-ws-token>",
    "plugins": ["astrbot_plugin_e2e_probe", "astrbot_plugin_cc_qq"],
    "startup_timeout_seconds": 120
  },
  "bot": {
    "qq": "<bot-qq>",
    "onebot_ws": "ws://127.0.0.1:6200/onebot/v11/ws",
    "token": "<bot-token>"
  },
  "sender": {
    "qq": "<sender-qq>",
    "onebot_ws": "ws://127.0.0.1:6201/onebot/v11/ws",
    "token": "<sender-token>"
  },
  "group_id": "<dedicated-test-group-id>",
  "judge": {
    "base_url": "<openai-compatible-base-url>",
    "api_key": "<judge-api-key>",
    "model": "<judge-model>"
  },
  "timeouts": {
    "message_seconds": 60,
    "reload_seconds": 120,
    "log_window_padding_seconds": 5
  }
}
```

同时更新 `.gitignore`，加入：

```text
tools/astrbot_e2e/config.local.json
tools/astrbot_e2e/reports/
```

- [ ] **Step 5：运行测试确认通过**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools -v
```

Expected: `Ran 5 tests ... OK`。

- [ ] **Step 6：列入待提交清单**

Run:
```bash
git status --short tools/astrbot_e2e
```

Expected: 看到新增文件。**不要自动提交**，等用户确认。

**实施结果（2026-10-27 18:35）：** 按代码质量审查补齐了 `_url_port` 错误语义、`validate_config` 的 `~` 展开、dict/OSError/bool/float 校验，并新增 15 个契约测试；当前 20 个测试全部通过，规格与质量复审均通过。剩余的 malformed URL `urlparse` 包装、相对 `test_root` 解析基准、重复归一化与 `assertRaisesRegex` 文案耦合已登记到 `deferred/2026-10-27-config-validation-deferred.md`。

---

### Task 2：用例加载与校验

**文件：**
- Create: `tools/astrbot_e2e/cases.py`
- Test: `tools/astrbot_e2e/tests/test_cases.py`

- [ ] **Step 1：写失败测试**

```python
import json
import tempfile
import unittest
from pathlib import Path

from astrbot_e2e.cases import CaseError, load_case, render_case


class CaseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "case.json"

    def write(self, data):
        self.path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_loads_and_renders_group_id(self):
        self.write({
            "name": "probe",
            "plugin": "astrbot_plugin_e2e_probe",
            "send": {"group_id": "{{group_id}}", "text": "/e2e_echo hello", "at_bot": True},
            "expect": {"messages": [{"contains": ["e2e_echo:hello"]}]},
        })
        case = load_case(self.path)
        rendered = render_case(case, {"group_id": "123456789"})
        self.assertEqual(rendered["send"]["group_id"], "123456789")

    def test_rejects_missing_expectation(self):
        self.write({
            "name": "bad",
            "plugin": "astrbot_plugin_e2e_probe",
            "send": {"text": "/e2e_echo hello"},
            "expect": {},
        })
        with self.assertRaisesRegex(CaseError, "至少包含"):
            load_case(self.path)

    def test_rejects_unknown_key(self):
        self.write({"name": "x", "plugin": "p", "send": {"text": "x"}, "expect": {"steps": []}})
        with self.assertRaisesRegex(CaseError, "未知字段"):
            load_case(self.path)
```

- [ ] **Step 2：运行确认失败**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_cases -v
```

Expected: FAIL，`ModuleNotFoundError` 或 `ImportError`。

- [ ] **Step 3：写实现**

```python
"""用例加载与校验（Test Case）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ALLOWED_TOP = frozenset({"name", "plugin", "reload", "send", "expect"})
ALLOWED_SEND = frozenset({"group_id", "text", "at_bot"})
ALLOWED_EXPECT = frozenset({"timeout_seconds", "messages", "logs", "semantic"})


class CaseError(ValueError):
    """用例缺失或非法。"""


def load_case(path: Any) -> Dict[str, Any]:
    case_path = Path(path).expanduser()
    if not case_path.exists():
        raise CaseError("用例文件不存在: {}".format(case_path))
    try:
        case = json.loads(case_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise CaseError("用例不是合法 JSON: {}".format(exc)) from exc
    validate_case(case)
    return case


def validate_case(case: Dict[str, Any]) -> None:
    if not isinstance(case, dict):
        raise CaseError("用例顶层必须是对象")
    unknown = set(case) - ALLOWED_TOP
    if unknown:
        raise CaseError("未知字段: {}".format(sorted(unknown)))
    if not str(case.get("name") or "").strip():
        raise CaseError("name 必填")
    if not str(case.get("plugin") or "").strip():
        raise CaseError("plugin 必填")
    send = case.get("send")
    if not isinstance(send, dict):
        raise CaseError("send 必须是对象")
    unknown_send = set(send) - ALLOWED_SEND
    if unknown_send:
        raise CaseError("send 未知字段: {}".format(sorted(unknown_send)))
    if not str(send.get("text") or "").strip():
        raise CaseError("send.text 必填")
    expect = case.get("expect")
    if not isinstance(expect, dict):
        raise CaseError("expect 必须是对象")
    unknown_expect = set(expect) - ALLOWED_EXPECT
    if unknown_expect:
        raise CaseError("expect 未知字段: {}".format(sorted(unknown_expect)))
    if not any(key in expect for key in ("messages", "logs", "semantic")):
        raise CaseError("expect 至少包含 messages / logs / semantic 之一")


def render_case(case: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    rendered = json.loads(json.dumps(case))
    send = rendered.get("send", {})
    if send.get("group_id") == "{{group_id}}":
        send["group_id"] = str(config["group_id"])
    return rendered
```

- [ ] **Step 4：运行确认通过**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_cases -v
```

Expected: `Ran 3 tests ... OK`。

**实施结果（2026-10-27 21:15）：** 按质量复审补强：`load_case` 包装 `OSError` / `UnicodeDecodeError`；`validate_case` 拒绝空 `messages` / `logs` 与非对象 `semantic`；`render_case` 缺少 `config["group_id"]` 时抛 `CaseError`。测试增至 13 个，全量 33 个通过。空断言数组的收紧是为了避免零断言假 PASSED，属于有意变更；更深的值形状校验见 `deferred/2026-10-27-case-validation-deferred.md`。

---

### Task 3：断言模块

**文件：**
- Create: `tools/astrbot_e2e/assertions.py`
- Test: `tools/astrbot_e2e/tests/test_assertions.py`

- [ ] **Step 1：写失败测试**

```python
import unittest

from astrbot_e2e.assertions import contains, evaluate_messages, regex


class AssertionsTest(unittest.TestCase):
    def test_contains_all(self):
        result = contains("hello world", ["hello", "world"])
        self.assertTrue(result.ok)

    def test_contains_any(self):
        result = contains("hello", ["hello", "missing"], mode="any")
        self.assertTrue(result.ok)

    def test_contains_failure_keeps_actual(self):
        result = contains("hello", ["missing"])
        self.assertFalse(result.ok)
        self.assertIn("hello", result.actual)

    def test_regex(self):
        self.assertTrue(regex("id=42", r"id=\d+").ok)
        self.assertFalse(regex("id=x", r"id=\d+").ok)

    def test_evaluate_messages_stops_after_failure(self):
        results = evaluate_messages(["hello"], [{"contains": ["hello"]}, {"contains": ["missing"]}])
        self.assertEqual(len(results), 2)
        self.assertFalse(results[1].ok)
```

- [ ] **Step 2：运行确认失败**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_assertions -v
```

Expected: FAIL。

- [ ] **Step 3：写实现**

```python
"""消息与日志断言（Assertion）。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class AssertionResult:
    kind: str
    ok: bool
    expected: Any
    actual: str
    detail: str = ""


def contains(text: str, needles: Iterable[str], mode: str = "all") -> AssertionResult:
    if mode not in ("all", "any"):
        raise ValueError("contains.mode 只能是 all 或 any")
    wants = [str(item) for item in needles]
    hits = [item for item in wants if item in text]
    ok = len(hits) == len(wants) if mode == "all" else bool(hits)
    return AssertionResult(
        kind="contains",
        ok=ok,
        expected={"needles": wants, "mode": mode},
        actual=text,
        detail="命中 {}/{}".format(len(hits), len(wants)),
    )


def regex(text: str, pattern: str) -> AssertionResult:
    match = re.search(pattern, text, re.S)
    return AssertionResult(
        kind="regex",
        ok=bool(match),
        expected=pattern,
        actual=text,
        detail=match.group(0) if match else "未匹配",
    )


def evaluate_messages(messages: List[str], specs: List[Dict[str, Any]]) -> List[AssertionResult]:
    text = "\n".join(messages)
    results: List[AssertionResult] = []
    for spec in specs:
        if not isinstance(spec, dict):
            raise ValueError("断言必须是对象")
        if "contains" in spec:
            result = contains(text, spec["contains"], spec.get("mode", "all"))
        elif "regex" in spec:
            result = regex(text, spec["regex"])
        else:
            raise ValueError("断言必须包含 contains 或 regex")
        results.append(result)
        if not result.ok:
            break
    return results


def evaluate_logs(log_text: str, specs: List[Dict[str, Any]]) -> List[AssertionResult]:
    return evaluate_messages([log_text], specs)
```

- [ ] **Step 4：运行确认通过**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_assertions -v
```

Expected: `Ran 5 tests ... OK`。

---

### Task 4：报告与失败证据

**文件：**
- Create: `tools/astrbot_e2e/reports.py`
- Test: `tools/astrbot_e2e/tests/test_reports.py`

- [ ] **Step 1：写失败测试**

```python
import json
import tempfile
import unittest
from pathlib import Path

from astrbot_e2e.reports import create_run_dir, slugify, write_json, write_summary


class ReportsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def test_slugify(self):
        self.assertEqual(slugify("cc_qq /help 群聊回执"), "cc_qq-help")

    def test_create_run_dir_is_unique(self):
        first = create_run_dir(self.base, "case")
        second = create_run_dir(self.base, "case")
        self.assertNotEqual(first, second)
        self.assertTrue(first.is_dir())

    def test_write_summary_contains_status(self):
        run_dir = create_run_dir(self.base, "case")
        summary = write_summary(run_dir, "case", "PASSED", [], 1.2, {"evidence": "x"})
        saved = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "PASSED")
        self.assertEqual(summary["duration_seconds"], 1.2)

    def test_write_json(self):
        path = self.base / "a.json"
        write_json(path, {"ok": True})
        self.assertTrue(json.loads(path.read_text(encoding="utf-8"))["ok"])
```

- [ ] **Step 2：运行确认失败**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_reports -v
```

Expected: FAIL。

- [ ] **Step 3：写实现**

```python
"""运行目录、JSON 报告与失败证据（Report）。"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def slugify(name: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z_-]+", "-", str(name)).strip("-")
    return slug or "case"


def create_run_dir(base: Any, case_name: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    path = Path(base) / "{}-{}".format(stamp, slugify(case_name))
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_json(path: Any, data: Any) -> None:
    Path(path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def write_summary(
    run_dir: Any,
    case_name: str,
    status: str,
    results: List[Any],
    duration_seconds: float,
    extra: Dict[str, Any] = None,
) -> Dict[str, Any]:
    summary = {
        "case": case_name,
        "status": status,
        "duration_seconds": round(float(duration_seconds), 3),
        "assertions": [
            {
                "kind": item.kind,
                "ok": item.ok,
                "expected": item.expected,
                "actual": item.actual,
                "detail": item.detail,
            }
            for item in results
        ],
    }
    if extra:
        summary.update(extra)
    write_json(Path(run_dir) / "summary.json", summary)
    return summary
```

- [ ] **Step 4：运行确认通过**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_reports -v
```

Expected: `Ran 4 tests ... OK`。

---

### Task 5：日志窗口采集

**文件：**
- Create: `tools/astrbot_e2e/log_capture.py`
- Test: `tools/astrbot_e2e/tests/test_log_capture.py`

- [ ] **Step 1：写失败测试**

```python
import asyncio
import tempfile
import unittest
from pathlib import Path

from astrbot_e2e.log_capture import LogCapture


class LogCaptureTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "astrbot.log"

    def test_reads_only_new_lines(self):
        self.path.write_text("old\n", encoding="utf-8")
        capture = LogCapture(self.path)
        offset = capture.mark()
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write("new\n")
        self.assertEqual(capture.read_since(offset), "new\n")

    async def test_wait_for_needle(self):
        self.path.write_text("", encoding="utf-8")
        capture = LogCapture(self.path)

        async def writer():
            await asyncio.sleep(0.1)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write("[e2e_probe] echo hello\n")

        asyncio.create_task(writer())
        self.assertTrue(await capture.wait_for(["[e2e_probe] echo hello"], timeout=2))
```

- [ ] **Step 2：运行确认失败**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_log_capture -v
```

Expected: FAIL。

- [ ] **Step 3：写实现**

```python
"""按文件偏移采集日志窗口（Log Capture）。"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Iterable


class LogCapture:
    def __init__(self, path):
        self.path = Path(path)

    def mark(self) -> int:
        return self.path.stat().st_size if self.path.exists() else 0

    def read_since(self, offset: int) -> str:
        if not self.path.exists():
            return ""
        with self.path.open("r", encoding="utf-8", errors="replace") as handle:
            handle.seek(offset)
            return handle.read()

    async def wait_for(self, needles: Iterable[str], timeout: float, interval: float = 0.5) -> bool:
        wants = [str(item) for item in needles]
        deadline = time.monotonic() + timeout
        offset = self.mark()
        buffer = ""
        while time.monotonic() < deadline:
            buffer += self.read_since(offset)
            offset = self.mark()
            if all(item in buffer for item in wants):
                return True
            await asyncio.sleep(interval)
        return False
```

- [ ] **Step 4：运行确认通过**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_log_capture -v
```

Expected: `Ran 2 tests ... OK`。

---

### Task 6：OneBot 消息构造与 WebSocket 客户端

**文件：**
- Create: `tools/astrbot_e2e/onebot.py`
- Test: `tools/astrbot_e2e/tests/test_onebot.py`

- [ ] **Step 1：写失败测试**

```python
import json
import unittest

from aiohttp import web
from aiohttp.test_utils import TestServer

from astrbot_e2e.onebot import (
    OneBotClient,
    build_group_message,
    extract_text,
    is_bot_reply,
    is_history_bot_message,
)


async def _ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for message in ws:
        data = json.loads(message.data)
        await ws.send_json({
            "status": "ok",
            "retcode": 0,
            "data": {"user_id": 10001},
            "echo": data["echo"],
        })
    return ws


class OneBotPureTest(unittest.TestCase):
    def test_build_group_message(self):
        self.assertEqual(
            build_group_message("/help", "10001"),
            [
                {"type": "at", "data": {"qq": "10001"}},
                {"type": "text", "data": {"text": " /help"}},
            ],
        )

    def test_extract_text(self):
        event = {"message": [{"type": "text", "data": {"text": "hello"}}, {"type": "at", "data": {"qq": "1"}}]}
        self.assertEqual(extract_text(event), "hello")

    def test_is_bot_reply(self):
        event = {"post_type": "message_sent", "group_id": 1, "user_id": 10001, "self_id": 10001, "message": []}
        self.assertTrue(is_bot_reply(event, "10001", "1"))
        self.assertFalse(is_bot_reply(event, "10002", "1"))
        self.assertFalse(is_bot_reply(event, "10001", "2"))

    def test_is_history_bot_message(self):
        event = {"group_id": 1, "sender": {"user_id": 10001}, "message": []}
        self.assertTrue(is_history_bot_message(event, "10001", "1"))
        self.assertFalse(is_history_bot_message(event, "10002", "1"))


class OneBotClientTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        app = web.Application()
        app.router.add_get("/onebot/v11/ws", _ws_handler)
        self.server = TestServer(app)
        await self.server.start_server()

    async def asyncTearDown(self):
        await self.server.close()

    async def test_call_returns_data(self):
        url = str(self.server.make_url("/onebot/v11/ws"))
        async with OneBotClient(url, token="") as client:
            data = await client.call("get_login_info", {})
            self.assertEqual(data["user_id"], 10001)
```

- [ ] **Step 2：运行确认失败**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_onebot -v
```

Expected: FAIL。

- [ ] **Step 3：写实现**

```python
"""OneBot v11 消息构造、事件过滤与 WebSocket 客户端。"""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional

import aiohttp


class OneBotError(RuntimeError):
    """OneBot 调用失败或连接异常。"""


def build_group_message(text: str, at_qq: str) -> List[Dict[str, Any]]:
    return [
        {"type": "at", "data": {"qq": str(at_qq)}},
        {"type": "text", "data": {"text": " " + str(text)}},
    ]


def extract_text(event: Dict[str, Any]) -> str:
    parts = []
    for segment in event.get("message") or []:
        if segment.get("type") == "text":
            parts.append(str(segment.get("data", {}).get("text", "")))
    return "".join(parts).strip()


def is_bot_reply(event: Dict[str, Any], bot_qq: str, group_id: str) -> bool:
    if event.get("post_type") not in ("message", "message_sent"):
        return False
    if str(event.get("group_id")) != str(group_id):
        return False
    user_id = event.get("user_id")
    if user_id is None:
        user_id = (event.get("sender") or {}).get("user_id")
    if str(user_id) != str(bot_qq):
        return False
    if event.get("post_type") == "message" and str(event.get("self_id")) != str(bot_qq):
        return False
    return True


def is_history_bot_message(event: Dict[str, Any], bot_qq: str, group_id: str) -> bool:
    """群消息历史里的机器人消息没有稳定的 post_type，按 sender 判断。"""
    if str(event.get("group_id")) != str(group_id):
        return False
    sender = event.get("sender") or {}
    user_id = sender.get("user_id") or event.get("user_id")
    return str(user_id) == str(bot_qq)


class OneBotClient:
    def __init__(self, ws_url: str, token: str, timeout: float = 30.0):
        self.ws_url = ws_url
        self.token = token or ""
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._reader: Optional[asyncio.Task] = None
        self._pending: Dict[str, asyncio.Future] = {}
        self._events: asyncio.Queue = asyncio.Queue()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def connect(self) -> None:
        self.session = aiohttp.ClientSession()
        headers = {"Authorization": "Bearer {}".format(self.token)} if self.token else {}
        self.ws = await self.session.ws_connect(self.ws_url, headers=headers, heartbeat=30)
        self._reader = asyncio.create_task(self._read_loop())

    async def close(self) -> None:
        if self._reader:
            self._reader.cancel()
            try:
                await self._reader
            except asyncio.CancelledError:
                pass
        if self.ws and not self.ws.closed:
            await self.ws.close()
        if self.session:
            await self.session.close()

    async def _read_loop(self) -> None:
        assert self.ws is not None
        async for message in self.ws:
            if message.type == aiohttp.WSMsgType.TEXT:
                payload = json.loads(message.data)
                echo = payload.get("echo")
                future = self._pending.pop(echo, None) if echo else None
                if future and not future.done():
                    future.set_result(payload)
                else:
                    await self._events.put(payload)
            elif message.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                break

    async def call(self, action: str, params: Dict[str, Any]) -> Any:
        if not self.ws or self.ws.closed:
            raise OneBotError("OneBot 未连接")
        echo = uuid.uuid4().hex
        future = asyncio.get_running_loop().create_future()
        self._pending[echo] = future
        await self.ws.send_json({"action": action, "params": params, "echo": echo})
        try:
            payload = await asyncio.wait_for(future, timeout=self.timeout)
        except asyncio.TimeoutError as exc:
            self._pending.pop(echo, None)
            raise OneBotError("OneBot 调用超时: {}".format(action)) from exc
        if payload.get("status") == "failed" or payload.get("retcode") not in (0, None):
            raise OneBotError("OneBot 调用失败: {} {}".format(action, payload))
        return payload.get("data")

    async def next_event(self, timeout: float) -> Dict[str, Any]:
        return await asyncio.wait_for(self._events.get(), timeout=timeout)


async def collect_replies(
    client: OneBotClient,
    bot_qq: str,
    group_id: str,
    timeout: float,
) -> List[Dict[str, Any]]:
    replies: List[Dict[str, Any]] = []
    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        remaining = deadline - asyncio.get_running_loop().time()
        try:
            event = await client.next_event(timeout=remaining)
        except asyncio.TimeoutError:
            break
        if is_bot_reply(event, bot_qq, group_id):
            replies.append({"text": extract_text(event), "raw": event})
            if replies:
                # 给插件连续多条回复留一个短窗口。
                try:
                    extra = await client.next_event(timeout=1.0)
                except asyncio.TimeoutError:
                    break
                if is_bot_reply(extra, bot_qq, group_id):
                    replies.append({"text": extract_text(extra), "raw": extra})
                else:
                    break
    return replies


async def history_bot_replies(
    client: OneBotClient,
    bot_qq: str,
    group_id: str,
    count: int = 20,
) -> List[Dict[str, Any]]:
    data = await client.call(
        "get_group_msg_history",
        {"group_id": int(group_id), "count": count},
    )
    messages = (data or {}).get("messages", []) if isinstance(data, dict) else []
    replies: List[Dict[str, Any]] = []
    for event in messages:
        if is_history_bot_message(event, bot_qq, group_id):
            replies.append({"text": extract_text(event), "raw": event})
    return replies
```

- [ ] **Step 4：运行确认通过**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_onebot -v
```

Expected: `Ran 5 tests ... OK`。

---

### Task 7：测试实例引导（Bootstrap）

**文件：**
- Create: `tools/astrbot_e2e/bootstrap.py`
- Test: `tools/astrbot_e2e/tests/test_bootstrap.py`

- [ ] **Step 1：写失败测试**

```python
import json
import tempfile
import unittest
from pathlib import Path

from astrbot_e2e.bootstrap import patch_config, sync_plugins, write_cc_qq_config


class BootstrapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "astrbot-e2e"
        (self.root / "data").mkdir(parents=True)
        self.cfg = {
            "test_root": str(self.root),
            "webui": {"port": 6186, "username": "e2e", "password": "e2e-pass-123"},
            "astrbot": {
                "reverse_ws_host": "127.0.0.1",
                "reverse_ws_port": 6198,
                "reverse_ws_token": "reverse-token",
                "plugins": ["astrbot_plugin_e2e_probe"],
            },
            "bot": {"qq": "10001"},
            "sender": {"qq": "10002"},
            "group_id": "123456789",
        }

    def test_patch_config_sets_platform_and_ports(self):
        (self.root / "data" / "cmd_config.json").write_text(
            json.dumps({"dashboard": {}, "platform": []}), encoding="utf-8"
        )
        patch_config(self.cfg)
        data = json.loads((self.root / "data" / "cmd_config.json").read_text(encoding="utf-8"))
        self.assertEqual(data["dashboard"]["port"], 6186)
        self.assertEqual(data["platform"][0]["id"], "Test-E2E")
        self.assertTrue(data["platform"][0]["enable"])
        self.assertEqual(data["platform"][0]["ws_reverse_port"], 6198)
        self.assertEqual(data["plugin_set"], ["astrbot_plugin_e2e_probe"])

    def test_write_cc_qq_config_uses_test_group(self):
        write_cc_qq_config(self.cfg)
        path = self.root / "data" / "config" / "astrbot_plugin_cc_qq_config.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["qq_platform_id"], "Test-E2E")
        self.assertEqual(data["enabled_group_ids"], ["123456789"])
        self.assertEqual(data["owner_qq_id"], "10002")
        rules = json.loads(data["group_rules_json"])
        self.assertIn("123456789", rules)
        self.assertTrue(Path(rules["123456789"]["work_dir"]).exists())

    def test_write_cc_qq_config_can_disable(self):
        write_cc_qq_config(self.cfg, enabled=False)
        path = self.root / "data" / "config" / "astrbot_plugin_cc_qq_config.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["enabled_group_ids"], [])
        self.assertEqual(json.loads(data["group_rules_json"]), {})

    def test_sync_plugins_copies_without_tests(self):
        source = Path(self.tmp.name) / "repo" / "integrations" / "astrbot" / "demo_plugin"
        (source / "tests").mkdir(parents=True)
        (source / "main.py").write_text("print('ok')", encoding="utf-8")
        (source / "tests" / "test_demo.py").write_text("x", encoding="utf-8")
        sync_plugins(self.cfg, repo_root=Path(self.tmp.name) / "repo", plugins=["demo_plugin"])
        target = self.root / "data" / "plugins" / "demo_plugin"
        self.assertTrue((target / "main.py").exists())
        self.assertFalse((target / "tests").exists())
```

- [ ] **Step 2：运行确认失败**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_bootstrap -v
```

Expected: FAIL。

- [ ] **Step 3：写实现**

```python
"""测试实例初始化、配置写入与插件同步（Bootstrap）。"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

PLATFORM_ID = "Test-E2E"


def ensure_test_root(cfg: Dict[str, Any]) -> Path:
    root = Path(cfg["test_root"]).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _run(argv: List[str], cwd: Path, input_text: Optional[str] = None) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        argv,
        cwd=str(cwd),
        input=input_text,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "命令失败: {}\nstdout:\n{}\nstderr:\n{}".format(argv, proc.stdout, proc.stderr)
        )
    return proc


def run_init(cfg: Dict[str, Any]) -> None:
    root = ensure_test_root(cfg)
    _run([str(cfg["astrbot"]["command"]), "init", "-y"], cwd=root)


def set_dashboard_password(cfg: Dict[str, Any]) -> None:
    root = ensure_test_root(cfg)
    password = str(cfg["webui"]["password"])
    _run(
        [str(cfg["astrbot"]["command"]), "password", "--username", str(cfg["webui"]["username"])],
        cwd=root,
        input_text="{}\n{}\n".format(password, password),
    )


def patch_config(cfg: Dict[str, Any]) -> None:
    root = ensure_test_root(cfg)
    path = root / "data" / "cmd_config.json"
    if not path.exists():
        raise RuntimeError("cmd_config.json 不存在，请先执行 astrbot init 与 password")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    data.setdefault("dashboard", {})
    data["dashboard"].update(
        {"enable": True, "host": "127.0.0.1", "port": int(cfg["webui"]["port"])}
    )
    data["platform"] = [
        {
            "id": PLATFORM_ID,
            "type": "aiocqhttp",
            "enable": True,
            "ws_reverse_host": cfg["astrbot"]["reverse_ws_host"],
            "ws_reverse_port": int(cfg["astrbot"]["reverse_ws_port"]),
            "ws_reverse_token": cfg["astrbot"]["reverse_ws_token"],
        }
    ]
    data["plugin_set"] = list(cfg["astrbot"]["plugins"])
    data["log_level"] = "INFO"
    data["log_file_enable"] = True
    data["log_file_path"] = "logs/astrbot.log"
    data["wake_prefix"] = ["/"]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "data" / "logs").mkdir(parents=True, exist_ok=True)


def sync_plugins(cfg: Dict[str, Any], repo_root: Path, plugins: List[str]) -> None:
    target_base = ensure_test_root(cfg) / "data" / "plugins"
    target_base.mkdir(parents=True, exist_ok=True)
    for name in plugins:
        source = Path(repo_root) / "integrations" / "astrbot" / name
        if not source.exists():
            raise RuntimeError("插件源目录不存在: {}".format(source))
        target = target_base / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "tests"),
        )


def write_cc_qq_config(cfg: Dict[str, Any], enabled: bool = True) -> None:
    root = ensure_test_root(cfg)
    config_dir = root / "data" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    work_dir = root / "workdir"
    work_dir.mkdir(exist_ok=True)
    enabled_groups = [str(cfg["group_id"])] if enabled else []
    rules = {str(cfg["group_id"]): {"work_dir": str(work_dir)}} if enabled else {}
    data = {
        "qq_platform_id": PLATFORM_ID,
        "enabled_group_ids": enabled_groups,
        "private_enabled": False,
        "owner_qq_id": str(cfg["sender"]["qq"]),
        "admin_qq_ids": [],
        "global_allowed_user_ids": [],
        "private_user_ids": [],
        "guest_permission_profile": "readonly",
        "member_permission_profile": "workspace",
        "owner_permission_profile": "full",
        "readonly_mcp_enabled": True,
        "danger_approval_enabled": True,
        "danger_approval_timeout_seconds": 60,
        "allowed_work_dirs": [],
        "private_work_dir": "",
        "group_rules_json": json.dumps(rules, ensure_ascii=False),
        "default_agent": "claude",
        "default_claude_model": "",
        "default_codex_model": "",
        "claude_command": "claude",
        "codex_command": "codex",
        "claude_setting_sources": "",
        "stale_message_max_age_seconds": 180,
    }
    (config_dir / "astrbot_plugin_cc_qq_config.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def prepare_instance(
    cfg: Dict[str, Any],
    active_plugin: Optional[str] = None,
    repo_root: Optional[Path] = None,
) -> None:
    root = ensure_test_root(cfg)
    if not (root / ".astrbot").exists():
        run_init(cfg)
    if not (root / "data" / "cmd_config.json").exists():
        set_dashboard_password(cfg)
    patch_config(cfg)
    repo = Path(repo_root) if repo_root else Path(__file__).resolve().parents[2]
    sync_plugins(cfg, repo, list(cfg["astrbot"]["plugins"]))
    write_cc_qq_config(cfg, enabled=active_plugin in (None, "astrbot_plugin_cc_qq"))
```

- [ ] **Step 4：运行确认通过**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_bootstrap -v
```

Expected: `Ran 4 tests ... OK`。

---

### Task 8：测试实例编排（Orchestrator）

**文件：**
- Create: `tools/astrbot_e2e/orchestrator.py`
- Test: `tools/astrbot_e2e/tests/test_orchestrator.py`

- [ ] **Step 1：写失败测试**

```python
import os
import signal
import tempfile
import unittest
from pathlib import Path

from astrbot_e2e.orchestrator import AstrBotInstance, pid_is_astrbot, port_open


class OrchestratorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "astrbot-e2e"
        self.root.mkdir()
        (self.root / ".astrbot").write_text("", encoding="utf-8")
        self.fake = Path(self.tmp.name) / "fake_astrbot"
        self.fake.write_text("#!/bin/sh\nexec sleep 30\n", encoding="utf-8")
        self.fake.chmod(0o755)
        self.cfg = {
            "test_root": str(self.root),
            "astrbot": {"command": str(self.fake)},
        }

    def test_start_writes_pid_and_stop_terminates(self):
        instance = AstrBotInstance(self.cfg, Path(self.tmp.name))
        instance.start()
        pid_file = self.root / "astrbot-e2e.pid"
        self.assertTrue(pid_file.exists())
        pid = int(pid_file.read_text(encoding="utf-8"))
        self.assertTrue(pid_is_astrbot(pid))
        instance.stop()
        self.assertFalse(pid_file.exists())

    def test_port_open_detects_closed_port(self):
        self.assertFalse(port_open("127.0.0.1", 1, timeout=0.1))
```

- [ ] **Step 2：运行确认失败**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_orchestrator -v
```

Expected: FAIL。

- [ ] **Step 3：写实现**

```python
"""AstrBot 测试实例的启动、停止与健康检查（Orchestrator）。"""

from __future__ import annotations

import asyncio
import os
import signal
import socket
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .log_capture import LogCapture

PID_NAME = "astrbot-e2e.pid"


def port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


def pid_is_astrbot(pid: int) -> bool:
    try:
        output = subprocess.check_output(
            ["ps", "-p", str(pid), "-o", "command="],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return "astrbot" in output.lower()


class AstrBotInstance:
    def __init__(self, cfg: Dict[str, Any], run_dir: Path):
        self.cfg = cfg
        self.root = Path(cfg["test_root"]).expanduser().resolve()
        self.run_dir = Path(run_dir)
        self.proc: Optional[subprocess.Popen] = None
        self.log_handle = None

    def pid_file(self) -> Path:
        return self.root / PID_NAME

    def is_running(self) -> bool:
        path = self.pid_file()
        if not path.exists():
            return False
        try:
            pid = int(path.read_text(encoding="utf-8").strip())
        except ValueError:
            return False
        return pid_is_astrbot(pid)

    def start(self) -> subprocess.Popen:
        self.root.mkdir(parents=True, exist_ok=True)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        webui = self.cfg.get("webui") or {}
        for label, port in (
            ("WebUI", int(webui.get("port", 6186))),
            ("OneBot 反向 WS", int(self.cfg["astrbot"].get("reverse_ws_port", 6198))),
        ):
            if port_open("127.0.0.1", port):
                raise RuntimeError(
                    "端口已被占用: {} {}；请先停止旧的测试实例".format(label, port)
                )
        log_path = self.run_dir / "astrbot.log"
        self.log_handle = log_path.open("ab")
        env = os.environ.copy()
        env["ASTRBOT_ROOT"] = str(self.root)
        self.proc = subprocess.Popen(
            [str(self.cfg["astrbot"]["command"]), "run"],
            cwd=str(self.root),
            env=env,
            stdout=self.log_handle,
            stderr=subprocess.STDOUT,
        )
        self.pid_file().write_text(str(self.proc.pid), encoding="utf-8")
        time.sleep(0.2)
        if self.proc.poll() is not None:
            raise RuntimeError("AstrBot 测试实例启动后立即退出，请查看 {}".format(log_path))
        return self.proc

    async def wait_ready(
        self,
        bot_client,
        timeout: Optional[float] = None,
        require_platform_log: bool = True,
    ) -> None:
        limit = float(timeout or self.cfg["astrbot"].get("startup_timeout_seconds", 120))
        deadline = time.monotonic() + limit
        webui = self.cfg.get("webui") or {}
        bot_qq = str(self.cfg.get("bot", {}).get("qq", ""))
        log = LogCapture(Path(self.cfg["test_root"]) / "data" / "logs" / "astrbot.log")
        log_mark = log.mark() if require_platform_log else 0
        while time.monotonic() < deadline:
            if self.proc and self.proc.poll() is not None:
                raise RuntimeError("AstrBot 测试实例提前退出")
            if port_open(str(webui.get("host", "127.0.0.1")), int(webui.get("port", 6186))):
                try:
                    info = await bot_client.call("get_login_info", {})
                    if str(info.get("user_id")) == bot_qq:
                        if not require_platform_log:
                            return
                        if "适配器已连接" in log.read_since(log_mark):
                            return
                except Exception:
                    pass
            await asyncio.sleep(1)
        raise TimeoutError("等待 AstrBot 测试实例就绪超时")

    def stop(self) -> None:
        path = self.pid_file()
        if not path.exists():
            return
        try:
            pid = int(path.read_text(encoding="utf-8").strip())
        except ValueError:
            path.unlink(missing_ok=True)
            return
        if not pid_is_astrbot(pid):
            raise RuntimeError("PID {} 不是 AstrBot 测试实例，拒绝终止".format(pid))
        os.kill(pid, signal.SIGTERM)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if not pid_is_astrbot(pid):
                break
            time.sleep(0.2)
        else:
            os.kill(pid, signal.SIGKILL)
        if self.proc is not None:
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            self.proc = None
        path.unlink(missing_ok=True)
        if self.log_handle:
            self.log_handle.close()
            self.log_handle = None
```

- [ ] **Step 4：运行确认通过**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_orchestrator -v
```

Expected: `Ran 2 tests ... OK`。

---

### Task 9：插件重载（WebUI 登录 + Reload）

**文件：**
- Create: `tools/astrbot_e2e/reloader.py`
- Test: `tools/astrbot_e2e/tests/test_reloader.py`

- [ ] **Step 1：写失败测试**

```python
import json
import unittest

from aiohttp import web
from aiohttp.test_utils import TestServer

from astrbot_e2e.reloader import login_and_reload


class ReloaderTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.logged_in = False
        self.reloaded = None

        async def login(request):
            body = await request.json()
            self.logged_in = body["username"] == "e2e" and body["password"] == "pass"
            response = web.json_response({"status": "ok", "data": {}})
            response.set_cookie("dashboard_jwt", "fake-token")
            return response

        async def reload(request):
            body = await request.json()
            self.reloaded = body["plugin_id"]
            return web.json_response({"status": "ok", "data": {}})

        app = web.Application()
        app.router.add_post("/api/v1/auth/login", login)
        app.router.add_post("/api/v1/plugins/reload", reload)
        self.server = TestServer(app)
        await self.server.start_server()

    async def asyncTearDown(self):
        await self.server.close()

    async def test_login_and_reload(self):
        base = str(self.server.make_url("")).rstrip("/")
        await login_and_reload(base, "e2e", "pass", "astrbot_plugin_cc_qq")
        self.assertTrue(self.logged_in)
        self.assertEqual(self.reloaded, "astrbot_plugin_cc_qq")

    async def test_reload_rejects_wrong_password(self):
        base = str(self.server.make_url("")).rstrip("/")
        with self.assertRaisesRegex(RuntimeError, "登录失败"):
            await login_and_reload(base, "e2e", "wrong", "x")
```

- [ ] **Step 2：运行确认失败**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_reloader -v
```

Expected: FAIL。

- [ ] **Step 3：写实现**

```python
"""WebUI 登录与插件重载（Reloader）。"""

from __future__ import annotations

import aiohttp


async def login_and_reload(
    base_url: str,
    username: str,
    password: str,
    plugin_id: str,
    timeout: float = 30.0,
) -> None:
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=client_timeout) as session:
        async with session.post(
            "{}/api/v1/auth/login".format(base_url.rstrip("/")),
            json={"username": username, "password": password},
        ) as response:
            body = await response.json()
            if response.status != 200 or body.get("status") != "ok":
                raise RuntimeError(
                    "WebUI 登录失败: {} {}".format(response.status, body)
                )
        async with session.post(
            "{}/api/v1/plugins/reload".format(base_url.rstrip("/")),
            json={"plugin_id": plugin_id},
        ) as response:
            body = await response.json()
            if response.status != 200 or body.get("status") not in ("ok", "success"):
                raise RuntimeError(
                    "插件重载失败: {} {}".format(response.status, body)
                )
```

- [ ] **Step 4：运行确认通过**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_reloader -v
```

Expected: `Ran 2 tests ... OK`。

---

### Task 10：探针插件（Probe Plugin）

**文件：**
- Create: `tools/astrbot_e2e/fixtures/astrbot_plugin_e2e_probe/main.py`
- Create: `tools/astrbot_e2e/fixtures/astrbot_plugin_e2e_probe/metadata.yaml`
- Test: `tools/astrbot_e2e/tests/test_probe_fixture.py`

- [ ] **Step 1：写失败测试**

```python
import py_compile
import unittest
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "astrbot_plugin_e2e_probe"


class ProbeFixtureTest(unittest.TestCase):
    def test_main_compiles(self):
        py_compile.compile(str(FIXTURE / "main.py"), doraise=True)

    def test_metadata_has_name(self):
        text = (FIXTURE / "metadata.yaml").read_text(encoding="utf-8")
        self.assertIn("name: astrbot_plugin_e2e_probe", text)

    def test_commands_are_present(self):
        text = (FIXTURE / "main.py").read_text(encoding="utf-8")
        for name in ("e2e_echo", "e2e_sleep", "e2e_log"):
            self.assertIn('@filter.command("{}")'.format(name), text)
```

- [ ] **Step 2：运行确认失败**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_probe_fixture -v
```

Expected: FAIL，文件不存在。

- [ ] **Step 3：写探针插件**

`metadata.yaml`：

```yaml
name: astrbot_plugin_e2e_probe
display_name: E2E Probe
desc: 端到端测试探针插件，仅用于独立测试实例。
version: 0.1.0
author: Claude
support_platforms:
  - aiocqhttp
```

`main.py`：

```python
"""端到端测试探针插件（Probe Plugin）。"""

from __future__ import annotations

import asyncio

from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

LOG_PREFIX = "[e2e_probe]"


def _argument(event: AstrMessageEvent, command: str) -> str:
    text = str(getattr(event, "message_str", "") or "").strip()
    for prefix in ("/" + command, command):
        if text.startswith(prefix):
            return text[len(prefix):].strip()
    return text


@register("astrbot_plugin_e2e_probe", "Claude", "端到端测试探针插件", "0.1.0")
class E2EProbe(Star):
    def __init__(self, context: Context, config=None):
        super().__init__(context, config)

    @filter.command("e2e_echo")
    async def e2e_echo(self, event: AstrMessageEvent):
        text = _argument(event, "e2e_echo")
        self.logger.info("%s echo %s", LOG_PREFIX, text)
        yield event.plain_result("e2e_echo:{}".format(text))

    @filter.command("e2e_sleep")
    async def e2e_sleep(self, event: AstrMessageEvent):
        raw = _argument(event, "e2e_sleep") or "0"
        milliseconds = int(raw)
        await asyncio.sleep(milliseconds / 1000)
        self.logger.info("%s sleep %s", LOG_PREFIX, milliseconds)
        yield event.plain_result("e2e_sleep:{}".format(milliseconds))

    @filter.command("e2e_log")
    async def e2e_log(self, event: AstrMessageEvent):
        text = _argument(event, "e2e_log")
        self.logger.info("%s log %s", LOG_PREFIX, text)
        yield event.plain_result("e2e_log:ok")
```

- [ ] **Step 4：运行确认通过**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_probe_fixture -v
```

Expected: `Ran 3 tests ... OK`。

---

### Task 11：LLM 语义判定

**文件：**
- Create: `tools/astrbot_e2e/llm_judge.py`
- Test: `tools/astrbot_e2e/tests/test_llm_judge.py`

- [ ] **Step 1：写失败测试**

```python
import json
import unittest

from aiohttp import web
from aiohttp.test_utils import TestServer

from astrbot_e2e.llm_judge import JudgeError, judge


class JudgeTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        async def chat(request):
            return web.json_response({
                "choices": [{"message": {"content": json.dumps({"pass": True, "reason": "符合"})}}]
            })

        app = web.Application()
        app.router.add_post("/v1/chat/completions", chat)
        self.server = TestServer(app)
        await self.server.start_server()

    async def asyncTearDown(self):
        await self.server.close()

    async def test_judge_returns_pass(self):
        base = str(self.server.make_url("")).rstrip("/")
        result = await judge(base, "key", "model", "必须是命令列表", "可用命令：/new /info")
        self.assertTrue(result["pass"])
        self.assertEqual(result["reason"], "符合")

    async def test_missing_config_raises(self):
        with self.assertRaisesRegex(JudgeError, "未配置"):
            await judge("", "", "", "criteria", "actual")
```

- [ ] **Step 2：运行确认失败**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_llm_judge -v
```

Expected: FAIL。

- [ ] **Step 3：写实现**

```python
"""OpenAI 兼容接口的语义判定（LLM-as-a-Judge）。"""

from __future__ import annotations

import json
from typing import Any, Dict

import aiohttp

SYSTEM_PROMPT = (
    "你是自动化测试的断言器。根据用户消息、机器人实际回复和判定标准，"
    "判断实际回复是否满足标准。只返回 JSON：{\"pass\": true/false, \"reason\": \"简短理由\"}。"
)


class JudgeError(RuntimeError):
    """语义判定不可用或返回非法。"""


async def judge(
    base_url: str,
    api_key: str,
    model: str,
    criteria: str,
    actual: str,
    timeout: float = 60.0,
) -> Dict[str, Any]:
    if not base_url or not model:
        raise JudgeError("LLM 判定未配置")
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "判定标准：{}\n实际回复：{}".format(criteria, actual)},
        ],
    }
    headers = {"Authorization": "Bearer {}".format(api_key)} if api_key else {}
    base = base_url.rstrip("/")
    endpoint = "{}/chat/completions".format(base) if base.endswith("/v1") else "{}/v1/chat/completions".format(base)
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=client_timeout) as session:
        async with session.post(
            endpoint,
            json=payload,
            headers=headers,
        ) as response:
            if response.status != 200:
                raise JudgeError("LLM 判定请求失败: HTTP {}".format(response.status))
            body = await response.json()
    try:
        content = body["choices"][0]["message"]["content"]
        result = json.loads(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise JudgeError("LLM 判定返回非法: {}".format(body)) from exc
    if not isinstance(result.get("pass"), bool):
        raise JudgeError("LLM 判定缺少 pass 布尔值: {}".format(result))
    return {"pass": result["pass"], "reason": str(result.get("reason", ""))}
```

- [ ] **Step 4：运行确认通过**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_llm_judge -v
```

Expected: `Ran 2 tests ... OK`。

---

### Task 12：Runner 与 CLI

**文件：**
- Create: `tools/astrbot_e2e/runner.py`
- Create: `tools/astrbot_e2e/cli.py`
- Test: `tools/astrbot_e2e/tests/test_cli.py`

- [ ] **Step 1：写失败测试**

```python
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from astrbot_e2e.cli import main


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.config = Path(self.tmp.name) / "config.local.json"
        self.config.write_text(json.dumps({
            "test_root": str(Path(self.tmp.name) / "root"),
            "webui": {"host": "127.0.0.1", "port": 6186, "username": "e2e", "password": "pass"},
            "astrbot": {
                "command": "astrbot",
                "reverse_ws_host": "127.0.0.1",
                "reverse_ws_port": 6198,
                "reverse_ws_token": "token",
                "plugins": ["astrbot_plugin_e2e_probe"],
                "startup_timeout_seconds": 120,
            },
            "bot": {"qq": "10001", "onebot_ws": "ws://127.0.0.1:6200/onebot/v11/ws", "token": "t"},
            "sender": {"qq": "10002", "onebot_ws": "ws://127.0.0.1:6201/onebot/v11/ws", "token": "t"},
            "group_id": "123456789",
            "judge": {},
            "timeouts": {"message_seconds": 60, "reload_seconds": 120, "log_window_padding_seconds": 5},
        }), encoding="utf-8")

    def test_missing_config_returns_2(self):
        code = main(["doctor", "--config", str(Path(self.tmp.name) / "missing.json")])
        self.assertEqual(code, 2)

    @mock.patch("astrbot_e2e.cli._doctor", new_callable=mock.AsyncMock)
    def test_doctor_dispatches(self, doctor):
        doctor.return_value = 0
        code = main(["doctor", "--config", str(self.config)])
        self.assertEqual(code, 0)
        doctor.assert_called_once()
```

- [ ] **Step 2：运行确认失败**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_cli -v
```

Expected: FAIL。

- [ ] **Step 3：写 Runner**

`runner.py` 负责单个用例流水线，核心函数：

```python
"""单个用例的执行流水线（Case Runner）。"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .assertions import AssertionResult, evaluate_logs, evaluate_messages
from .bootstrap import prepare_instance
from .cases import load_case, render_case
from .llm_judge import JudgeError, judge
from .log_capture import LogCapture
from .onebot import OneBotClient, build_group_message, collect_replies, history_bot_replies
from .orchestrator import AstrBotInstance
from .reloader import login_and_reload
from .reports import create_run_dir, write_json, write_summary

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORTS_DIR = REPO_ROOT / "tools" / "astrbot_e2e" / "reports"


async def run_case(
    cfg: Dict[str, Any],
    case_path: str,
    reload: bool = False,
    reports_dir: Optional[str] = None,
    attach: bool = False,
) -> Dict[str, Any]:
    case = render_case(load_case(case_path), cfg)
    started = time.monotonic()
    run_dir = create_run_dir(reports_dir or str(DEFAULT_REPORTS_DIR), case["name"])
    instance = AstrBotInstance(cfg, run_dir)
    started_by_runner = False
    bot_client = OneBotClient(cfg["bot"]["onebot_ws"], cfg["bot"]["token"])
    sender_client = OneBotClient(cfg["sender"]["onebot_ws"], cfg["sender"]["token"])
    log_capture = LogCapture(Path(cfg["test_root"]) / "data" / "logs" / "astrbot.log")
    results: List[AssertionResult] = []

    try:
        if attach:
            if not instance.is_running():
                raise RuntimeError("--attach 需要测试实例已启动")
        else:
            prepare_instance(cfg, case["plugin"])
            if instance.is_running():
                instance.stop()
            instance.start()
            started_by_runner = True

        await bot_client.connect()
        await sender_client.connect()
        bot_info = await bot_client.call("get_login_info", {})
        if str(bot_info.get("user_id")) != str(cfg["bot"]["qq"]):
            raise RuntimeError(
                "机器人号不匹配: 期望 {} 实际 {}".format(cfg["bot"]["qq"], bot_info.get("user_id"))
            )
        sender_info = await sender_client.call("get_login_info", {})
        if str(sender_info.get("user_id")) != str(cfg["sender"]["qq"]):
            raise RuntimeError(
                "发送者号不匹配: 期望 {} 实际 {}".format(cfg["sender"]["qq"], sender_info.get("user_id"))
            )
        await instance.wait_ready(bot_client, require_platform_log=not attach)

        if reload or case.get("reload"):
            try:
                await login_and_reload(
                    "http://{}:{}".format(cfg["webui"]["host"], cfg["webui"]["port"]),
                    cfg["webui"]["username"],
                    cfg["webui"]["password"],
                    case["plugin"],
                )
            except Exception:
                # 设计稿要求：WebUI 重载失败时用重启兜底，不静默跳过。
                instance.stop()
                instance.start()
                started_by_runner = True
            await instance.wait_ready(bot_client, require_platform_log=not attach)

        mark = log_capture.mark()
        send = case["send"]
        sent = await sender_client.call(
            "send_group_msg",
            {
                "group_id": int(send["group_id"]),
                "message": build_group_message(send["text"], cfg["bot"]["qq"]),
            },
        )
        write_json(run_dir / "sent.json", {"response": sent, "case": case})

        timeout = float(case["expect"].get("timeout_seconds", cfg["timeouts"]["message_seconds"]))
        replies = await collect_replies(
            bot_client, cfg["bot"]["qq"], str(send["group_id"]), timeout
        )
        if not replies:
            replies = await history_bot_replies(
                sender_client, cfg["bot"]["qq"], str(send["group_id"])
            )
        texts: List[str] = [item["text"] for item in replies]
        write_json(run_dir / "messages.json", replies)

        expect = case["expect"]
        if expect.get("messages"):
            results.extend(evaluate_messages(texts, expect["messages"]))
        log_text = log_capture.read_since(mark)
        if expect.get("logs"):
            results.extend(evaluate_logs(log_text, expect["logs"]))
        (run_dir / "log-window.log").write_text(log_text, encoding="utf-8")

        semantic = expect.get("semantic")
        if semantic and semantic.get("enabled"):
            judge_cfg = cfg.get("judge") or {}
            criteria = semantic.get("criteria", "")
            if not judge_cfg.get("base_url") or not judge_cfg.get("model"):
                write_json(
                    run_dir / "judge.json",
                    {"pass": False, "reason": "LLM 判定未配置", "skipped": True},
                )
                results.append(
                    AssertionResult(
                        kind="semantic",
                        ok=False,
                        expected=criteria,
                        actual="\n".join(texts),
                        detail="SKIPPED: LLM 判定未配置",
                    )
                )
            else:
                try:
                    verdict = await judge(
                        judge_cfg.get("base_url", ""),
                        judge_cfg.get("api_key", ""),
                        judge_cfg.get("model", ""),
                        criteria,
                        "\n".join(texts),
                    )
                    write_json(run_dir / "judge.json", verdict)
                    results.append(
                        AssertionResult(
                            kind="semantic",
                            ok=bool(verdict["pass"]),
                            expected=criteria,
                            actual="\n".join(texts),
                            detail=verdict.get("reason", ""),
                        )
                    )
                except JudgeError as exc:
                    write_json(
                        run_dir / "judge.json",
                        {"pass": False, "reason": str(exc), "skipped": False},
                    )
                    results.append(
                        AssertionResult(
                            kind="semantic",
                            ok=False,
                            expected=criteria,
                            actual="\n".join(texts),
                            detail=str(exc),
                        )
                    )

        failed = [item for item in results if not item.ok and "SKIPPED" not in item.detail]
        skipped = any("SKIPPED" in item.detail for item in results)
        if failed:
            status = "FAILED"
        elif skipped:
            status = "SKIPPED"
        elif results:
            status = "PASSED"
        else:
            status = "FAILED"
        duration = time.monotonic() - started
        write_json(
            run_dir / "assertions.json",
            [
                {
                    "kind": item.kind,
                    "ok": item.ok,
                    "expected": item.expected,
                    "actual": item.actual,
                    "detail": item.detail,
                }
                for item in results
            ],
        )
        return write_summary(
            run_dir,
            case["name"],
            status,
            results,
            duration,
            {"run_dir": str(run_dir)},
        )
    except Exception as exc:
        duration = time.monotonic() - started
        return write_summary(
            run_dir,
            case["name"],
            "ERROR",
            results,
            duration,
            {"error": repr(exc), "run_dir": str(run_dir)},
        )
    finally:
        await sender_client.close()
        await bot_client.close()
        if started_by_runner:
            instance.stop()
```

- [ ] **Step 4：写 CLI**

```python
"""命令行入口（CLI）。"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List

from .bootstrap import prepare_instance
from .config import ConfigError, load_config
from .onebot import OneBotClient
from .orchestrator import AstrBotInstance
from .runner import run_case

DEFAULT_CONFIG = "tools/astrbot_e2e/config.local.json"


def _add_subcommand(sub, name: str):
    parser = sub.add_parser(name)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    return parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="astrbot-e2e")
    sub = parser.add_subparsers(dest="command", required=True)
    _add_subcommand(sub, "doctor")
    init = _add_subcommand(sub, "init-instance")
    init.add_argument("--plugin", default=None)
    start = _add_subcommand(sub, "start-instance")
    start.add_argument("--plugin", default=None)
    _add_subcommand(sub, "stop-instance")
    run = _add_subcommand(sub, "run")
    run.add_argument("--case", required=True)
    run.add_argument("--reload", action="store_true")
    run.add_argument("--attach", action="store_true")
    return parser


async def _check_login(name: str, section: Dict[str, Any]) -> int:
    client = OneBotClient(section["onebot_ws"], section["token"])
    try:
        await client.connect()
        info = await client.call("get_login_info", {})
    except Exception as exc:
        print("{} OneBot 不可用: {}".format(name, exc))
        return 2
    finally:
        await client.close()
    if str(info.get("user_id")) != str(section["qq"]):
        print("{} 不匹配: 期望 {} 实际 {}".format(name, section["qq"], info.get("user_id")))
        return 2
    return 0


async def _doctor(cfg: Dict[str, Any]) -> int:
    code = await _check_login("机器人号", cfg["bot"])
    if code:
        return code
    code = await _check_login("发送者号", cfg["sender"])
    if code:
        return code
    root = Path(cfg["test_root"])
    if not (root / ".astrbot").exists():
        print("测试实例未初始化: {}".format(root))
        return 2
    print(
        "doctor OK: bot={} sender={} test_root={}".format(
            cfg["bot"]["qq"], cfg["sender"]["qq"], root
        )
    )
    return 0


async def _wait_instance(cfg: Dict[str, Any], instance: AstrBotInstance) -> None:
    client = OneBotClient(cfg["bot"]["onebot_ws"], cfg["bot"]["token"])
    try:
        await client.connect()
        await instance.wait_ready(client)
    finally:
        await client.close()


async def _run(cfg: Dict[str, Any], case_path: str, reload: bool, attach: bool) -> int:
    summary = await run_case(cfg, case_path, reload=reload, attach=attach)
    print("{}: {} ({})".format(summary["case"], summary["status"], summary.get("run_dir")))
    if summary["status"] == "PASSED":
        return 0
    if summary["status"] == "ERROR":
        return 2
    if summary["status"] == "SKIPPED":
        return 3
    return 1


def main(argv: List[str] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print("配置错误: {}".format(exc), file=sys.stderr)
        return 2
    if args.command == "doctor":
        return asyncio.run(_doctor(cfg))
    if args.command == "init-instance":
        prepare_instance(cfg, args.plugin)
        return 0
    if args.command == "start-instance":
        prepare_instance(cfg, args.plugin)
        instance = AstrBotInstance(cfg, Path(cfg["test_root"]) / "bootstrap-run")
        instance.start()
        try:
            asyncio.run(_wait_instance(cfg, instance))
        except Exception as exc:
            print("测试实例未就绪: {}".format(exc), file=sys.stderr)
            return 2
        print(instance.proc.pid)
        return 0
    if args.command == "stop-instance":
        AstrBotInstance(cfg, Path(cfg["test_root"]) / "bootstrap-run").stop()
        return 0
    if args.command == "run":
        return asyncio.run(_run(cfg, args.case, args.reload, args.attach))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5：运行确认通过**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_cli -v
```

Expected: `Ran 2 tests ... OK`。

- [ ] **Step 6：全量单元测试**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools -v
```

Expected: 全部通过。

---

### Task 13：端到端验证 — 探针用例

**前置：** Task 0 通过；两个 QQ 号在线；NapCat 两个 OneBot 端口可用；用户已登录。

**文件：**
- Create: `tools/astrbot_e2e/cases/probe_echo.json`

- [ ] **Step 1：写用例**

```json
{
  "name": "探针插件回显",
  "plugin": "astrbot_plugin_e2e_probe",
  "reload": true,
  "send": {
    "group_id": "{{group_id}}",
    "text": "/e2e_echo hello-e2e",
    "at_bot": true
  },
  "expect": {
    "timeout_seconds": 30,
    "messages": [{"contains": ["e2e_echo:hello-e2e"]}],
    "logs": [{"contains": ["[e2e_probe] echo hello-e2e"]}]
  }
}
```

- [ ] **Step 2：准备本地配置**

```bash
test -f tools/astrbot_e2e/config.local.json || cp tools/astrbot_e2e/config.example.json tools/astrbot_e2e/config.local.json
```

按实际情况填写：两个 QQ 号、测试群号、四个端口、三个 Token、WebUI 密码、LLM 判定配置。

- [ ] **Step 3：初始化测试实例**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli init-instance --config tools/astrbot_e2e/config.local.json
```

Expected: `test_root/.astrbot`、`data/cmd_config.json`、`data/plugins/` 与 `data/config/` 已生成。

说明：`run` 会先按用例插件重写测试实例配置，再停止旧的测试实例并重新启动，确保探针用例运行时 `cc_qq` 处于禁用状态，`cc_qq` 用例运行时才启用测试群。不要预先 `start-instance`，避免配置与用例不一致。

- [ ] **Step 4：doctor 自检**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor --config tools/astrbot_e2e/config.local.json
```

Expected: `doctor OK: bot=<bot-qq> test_root=...`。

- [ ] **Step 5：运行探针用例**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run \
  --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/probe_echo.json --reload
```

Expected: 输出 `探针插件回显: PASSED (...)`，括号内是本次报告目录。

- [ ] **Step 6：检查证据**

```bash
RUN_DIR="$(ls -dt tools/astrbot_e2e/reports/* | head -1)"
ls -la "$RUN_DIR"
cat "$RUN_DIR/summary.json"
cat "$RUN_DIR/messages.json"
cat "$RUN_DIR/log-window.log"
tail -n 50 "$HOME/.astrbot-e2e/data/logs/astrbot.log"
```

Expected: `summary.json` 状态 `PASSED`；`messages.json` 含 `e2e_echo:hello-e2e`；`log-window.log` 与测试实例日志含 `[e2e_probe] echo hello-e2e`。

说明：AstrBot 的 `log_file_path` 相对路径以 `data/` 为基准，因此实际日志是 `$HOME/.astrbot-e2e/data/logs/astrbot.log`，不是根目录下的 `logs/`。

- [ ] **Step 7：失败处理**

若失败，保留证据目录，按 `bug-log.md` 记录：现象、原因、解决方案；不要删证据，不要改生产代码。

---

### Task 14：端到端验证 — `cc_qq /help` 与重载

**前置：** Task 13 通过。

**文件：**
- Create: `tools/astrbot_e2e/cases/cc_qq_help.json`

- [ ] **Step 1：写用例**

```json
{
  "name": "cc_qq /help 群聊回执",
  "plugin": "astrbot_plugin_cc_qq",
  "reload": true,
  "send": {
    "group_id": "{{group_id}}",
    "text": "/help",
    "at_bot": true
  },
  "expect": {
    "timeout_seconds": 30,
    "messages": [{"contains": ["/new", "/info"]}],
    "semantic": {
      "enabled": true,
      "criteria": "回复是一份命令列表，且包含 /new 与 /info"
    }
  }
}
```

- [ ] **Step 2：初始化实例（确保 cc_qq 与配置已同步）**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli init-instance --config tools/astrbot_e2e/config.local.json
```

Expected: `test_root/data/plugins/astrbot_plugin_cc_qq` 存在；`test_root/data/config/astrbot_plugin_cc_qq_config.json` 含测试群。

说明：`cc_qq /help` 的语义断言需要 `config.local.json` 中 `judge.base_url` 与 `judge.model`；未配置时该用例会以 `SKIPPED` 结束，不视为通过。

- [ ] **Step 3：运行用例**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run \
  --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/cc_qq_help.json --reload
```

Expected: `cc_qq /help 群聊回执: PASSED`。

- [ ] **Step 4：验证重载确实生效（增量验证）**

1. 初始化并启动只启用探针插件的测试实例（`cc_qq` 被禁用，避免拦截探针消息）：

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli init-instance \
  --plugin astrbot_plugin_e2e_probe --config tools/astrbot_e2e/config.local.json
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli start-instance \
  --plugin astrbot_plugin_e2e_probe --config tools/astrbot_e2e/config.local.json
```

2. 确认修改前通过：

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run --attach \
  --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/probe_echo.json
```

Expected: `PASSED`，收到 `e2e_echo:hello-e2e`。

3. 修改测试实例副本（不要改 fixture 源，`--attach` 不会同步，正好用于验证热重载）：

```bash
PLUGIN_DIR="$HOME/.astrbot-e2e/data/plugins/astrbot_plugin_e2e_probe"
python3 - <<'PY'
from pathlib import Path
path = Path.home() / ".astrbot-e2e/data/plugins/astrbot_plugin_e2e_probe/main.py"
text = path.read_text(encoding="utf-8")
path.write_text(
    text.replace('"e2e_echo:{}".format(text)', '"e2e_echo-v2:{}".format(text)'),
    encoding="utf-8",
)
PY
```

4. 创建临时 v2 用例 `tools/astrbot_e2e/cases/probe_echo_v2.json`：

```json
{
  "name": "探针插件重载验证",
  "plugin": "astrbot_plugin_e2e_probe",
  "reload": true,
  "send": {
    "group_id": "{{group_id}}",
    "text": "/e2e_echo hello-e2e",
    "at_bot": true
  },
  "expect": {
    "timeout_seconds": 30,
    "messages": [{"contains": ["e2e_echo-v2:hello-e2e"]}]
  }
}
```

5. 附加运行并触发重载：

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run --attach --reload \
  --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/probe_echo_v2.json
```

Expected: `PASSED`，说明无需重启整个实例即可加载新代码。

6. 恢复测试实例副本并删除临时用例：

```bash
cp tools/astrbot_e2e/fixtures/astrbot_plugin_e2e_probe/main.py "$PLUGIN_DIR/main.py"
rm tools/astrbot_e2e/cases/probe_echo_v2.json
```

- [ ] **Step 5：检查证据与边界**

```bash
RUN_DIR="$(ls -dt tools/astrbot_e2e/reports/* | head -1)"
cat "$RUN_DIR/summary.json"
cat "$RUN_DIR/judge.json"
lsof -nP -iTCP -sTCP:LISTEN | grep -E ':(6185|6199|6099)'
```

Expected: 语义判定结果存在；生产端口仍在；未向测试群以外发送消息。

---

### Task 15：Verify / Close

- [ ] **Step 1：全量单元测试**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools -v
```

Expected: 全部通过。

- [ ] **Step 2：完整 E2E 回归**

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run \
  --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/probe_echo.json --reload
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run \
  --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/cc_qq_help.json --reload
```

Expected: 两条都 `PASSED`；若 `judge` 未配置，`cc_qq` 用例会以 `SKIPPED` 结束，需先补齐 `judge.base_url` 与 `judge.model` 再验收。

- [ ] **Step 3：生产影响检查**

```bash
lsof -nP -iTCP -sTCP:LISTEN | grep -E ':(6185|6199|6099)' || true
ps aux | grep -E 'astrbot run|QQ.app/Contents/MacOS/QQ' | grep -v grep || true
git status --short
```

Expected: 生产实例仍在；测试实例使用独立端口；没有误改生产目录。

- [ ] **Step 4：更新 mission 记录**

- `state.md`：当前阶段、已完成、风险、下一步。
- `checkpoints.md`：新增一条本轮完成 checkpoint。
- `decision-log.md`：记录 Spike 0 结论、任何回退或实现取舍。
- `deferred/`：新建 `deferred/2026-10-27-deferred-scope.md`，把延期项（cc_qq 长任务、多轮对话、CI、WebUI）按模板落盘。

- [ ] **Step 5：提交前询问**

把改动清单、测试证据、报告路径列给用户，询问是否提交；只有明确同意后才执行中文提交信息。

## 4. 完成定义（Definition of Done）

- Spike 0 有书面结论，且未通过时没有继续实现。
- 单元测试全部通过。
- 探针用例与 `cc_qq /help` 用例都能稳定 `PASSED`。
- 重载验证有前后对比证据。
- 生产实例、生产端口、生产 QQ 配置未被修改。
- `.devflow/astrbot-plugin-e2e/` 的 state、checkpoint、decision-log、deferred 已更新。

## 5. 本轮不做（Deferred Scope）

- `cc_qq` 长任务（Claude/Codex 实际执行）、审批流程、多轮对话；
- WebUI 页面、CI 集成、并行用例；
- 图片、文件、引用等消息段；
- 自动扫码登录；
- WebUI API 之外的插件热重载策略。

这些延期项在 Task 15 写入 `.devflow/astrbot-plugin-e2e/deferred/`，不是永久放弃。
