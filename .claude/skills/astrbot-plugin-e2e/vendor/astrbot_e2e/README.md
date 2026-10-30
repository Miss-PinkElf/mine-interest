# astrbot_e2e — AstrBot 插件端到端测试工具

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 22:40:00 CST。
- 更新时间（Updated At）：2026-10-27 22:40:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：说明第一版 AstrBot 插件端到端测试（End-to-End Test，E2E）工具的用法、边界与排障。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：第一版已完成（Completed）。
- 文档边界（Scope / Boundary）：使用说明；mission 的决策与延期项以 `.devflow/astrbot-plugin-e2e/` 为准。

## 能做什么

- 启动/停止独立测试 AstrBot 实例（不复用生产实例）。
- 用测试发送者 QQ 在专用测试群发消息。
- 采集测试机器人回复与 AstrBot 日志。
- 断言消息包含、正则、日志包含。
- 可选 LLM 语义判定（OpenAI 兼容接口）。
- 通过 WebUI 登录 + Bearer token 热重载插件；失败时重启测试实例兜底。
- 输出 JSON/日志证据到 `tools/astrbot_e2e/reports/`。

## 环境拓扑（第一版）

| 角色 | QQ / 端口 |
| --- | --- |
| 测试机器人 | `3254276668（17号）` |
| 测试发送者 | `1961618848（C#）` |
| 专用测试群 | `701292201` |
| 测试 AstrBot | WebUI `6186`，反向 OneBot WS `6198` |
| 生产 AstrBot | WebUI `6185`，反向 OneBot WS `6199` |
| 生产 bot NapCat | `6099`（WebUI），`6200`（OneBot） |
| 测试发送者 NapCat | `6098`（WebUI），`6201`（OneBot） |

macOS 下两个 QQ 实例共享同一个 App Sandbox 容器，只隔离 `NAPCAT_WORKDIR` 与端口。

## 快速开始

```bash
# 1. 复制配置并填写本地值（不要提交）
cp tools/astrbot_e2e/config.example.json tools/astrbot_e2e/config.local.json

# 2. 环境自检
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor \
  --config tools/astrbot_e2e/config.local.json

# 3. 运行探针用例
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run \
  --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/probe_echo.json

# 4. 运行真实插件用例
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run \
  --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/cc_qq_help.json
```

## 命令

| 命令 | 作用 |
| --- | --- |
| `doctor` | 校验配置、端口、账号与测试根目录 |
| `init-instance --plugin <id>` | 初始化测试实例并同步指定插件 |
| `start-instance --plugin <id>` | 启动测试实例并等待就绪 |
| `stop-instance` | 停止由本工具启动的测试实例 |
| `run --case <path>` | 执行用例；非 attach 模式会自动准备/启动/停止 |
| `run --attach` | 复用已运行的测试实例 |
| `run --reload` | 执行前通过 WebUI 热重载插件 |

退出码：`0` 通过，`1` 失败，`2` 用例/配置错误，`3` 环境错误。

## 用例格式

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
    "logs": [{"contains": ["[e2e_probe] echo hello-e2e"]}],
    "semantic": {
      "enabled": true,
      "criteria": "回复是一份命令列表，且包含 /new 与 /info"
    }
  }
}
```

- `send.group_id` 支持 `{{group_id}}` 占位符，运行时替换为配置中的测试群。
- `expect.messages` / `expect.logs` 不能为空；支持 `contains` 与 `regex`。
- `semantic` 需要配置 `judge.base_url`、`judge.api_key`、`judge.model`；未配置时该断言为 `SKIPPED`。
- 语义判定返回 `pass` 与 `reason`；不通过时用例失败。

## 配置

`config.example.json` 是模板，`config.local.json` 为本地真实配置：

- 含 QQ 号、OneBot token、WebUI 密码与 LLM key。
- 本地 `.gitignore` 已忽略 `config.local.json` 与 `reports/`。
- **不要提交** `config.local.json` 或 `reports/`。
- 生产实例根目录、生产端口与测试实例根目录不能相同；配置模块会拒绝明显冲突。

## 目录

```text
tools/astrbot_e2e/
├─ cli.py / runner.py / config.py / cases.py
├─ assertions.py / reports.py / log_capture.py
├─ onebot.py / bootstrap.py / orchestrator.py
├─ reloader.py / llm_judge.py
├─ fixtures/astrbot_plugin_e2e_probe/
├─ cases/probe_echo.json, cc_qq_help.json
└─ tests/
```

## 已知边界

- 首版只支持文本消息；富媒体延期。
- 首版只支持单次发送 + 单组断言；多轮对话延期。
- 首版串行执行；并行与 CI 延期。
- QQ 登录需要人工扫码；不承诺自动登录。
- 仅验证 macOS 双开路径。
- 非 attach 用例结束会停止测试实例；生产 bot 的 `6198` 客户端会每 30 秒重试，属预期。
- NapCat 可能输出 native addon / FFmpeg / PacketBackend 警告；文本链路不受影响。

## 排障

| 现象 | 可能原因 | 处理 |
| --- | --- | --- |
| `EPERM mkdir .../NapCat/logs` | macOS App Sandbox 拒绝沙盒外写入 | `NAPCAT_WORKDIR` 放到 QQ 容器内 |
| 端口 `6186` 被占用 | 旧测试实例未退出 | 停止旧进程或等待 `stop-instance` 释放端口 |
| Reload 返回 401 | Secure cookie 在 http 下不回传 | 使用登录响应的 Bearer token（工具已实现） |
| 历史消息导致假通过 | 测试群有旧回复 | 工具按 `since_time` 过滤；确认时间窗口 |
| `6198` 持续重试 | 测试实例已停止 | 启动测试实例；或按 `backlog.md` Q2 决定是否保留客户端 |

## 相关文档

- `.devflow/astrbot-plugin-e2e/state.md`：当前状态。
- `.devflow/astrbot-plugin-e2e/backlog.md`：未决问题与首版限定。
- `.devflow/astrbot-plugin-e2e/deferred/2026-10-27-post-mvp-deferred.md`：延期项。
- `.devflow/astrbot-plugin-e2e/handoffs/2026-10-27-002-第一版完成交接.md`：第一版交接。
