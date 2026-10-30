# AstrBot 插件端到端自动化测试设计（Design）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 17:41:14 CST。
- 更新时间（Updated At）：2026-10-27 17:41:14 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：固定端到端测试运行器的结构、边界、数据流、接口与关键实现决策。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 关联提案（Related Proposal）：`./proposal.md`。
- 关联计划（Related Plan）：`../plans/2026-10-27-astrbot-plugin-e2e-plan.md`。
- 当前状态（Status）：待用户确认（Pending Approval）。
- 文档边界（Scope / Boundary）：设计真相源；实现细节与任务顺序以 Plan 为准。

## 总体思路

Runner 是独立 Python 进程，不嵌入 AstrBot。它通过两个 NapCat OneBot v11 WebSocket 通道工作：

- 发送通道（Sender Channel）：连接发送者号 NapCat 的 WS 服务端，调用 `send_group_msg`。
- 观察通道（Observer Channel）：连接机器人号 NapCat 的 WS 服务端，订阅 `message_sent` / 群消息事件。
- 兜底通道：观察不到时，用发送者号调用 `get_group_msg_history` 回填。

AstrBot 测试实例由 Runner 用子进程启动，使用独立数据根、WebUI 端口、OneBot 反向 WS 端口与插件目录。每次用例运行前，Runner 按用例插件重写测试实例配置，停止旧实例并启动新实例，确保插件开关与用例一致。

## 结构与边界

```text
tools/astrbot_e2e/
├─ cli.py              # CLI 入口与退出码
├─ config.py           # 配置加载、校验、脱敏
├─ cases.py            # 用例加载与校验
├─ assertions.py       # 包含/正则断言
├─ reports.py          # 报告与证据
├─ log_capture.py      # 日志窗口
├─ onebot.py           # OneBot 消息与 WS 客户端
├─ bootstrap.py        # 测试实例初始化与插件同步
├─ orchestrator.py     # 启停、PID 归属、就绪检查
├─ reloader.py         # WebUI 登录与重载
├─ llm_judge.py        # LLM 语义判定
├─ runner.py           # 单用例流水线
├─ fixtures/           # 探针插件与 NapCat 配置样例
├─ cases/              # 用例 JSON
└─ tests/              # 单元测试
```

边界：

- `config.py` 只读本地配置，不写凭据。
- `bootstrap.py` 只操作 `test_root`，拒绝生产数据根。
- `orchestrator.py` 只停止自己 PID 文件记录且命令行含 `astrbot` 的进程。
- `runner.py` 只向配置的测试群发送消息。
- `reloader.py` 只访问测试实例 WebUI。
- 被测插件从 `integrations/astrbot/<plugin>` 复制，运行时只改测试实例副本。

## 数据流与接口

### 1. 配置

`config.local.json` 提供：

- `test_root`、`webui`、`astrbot`（命令、反向 WS、插件列表、超时）。
- `bot` / `sender`（QQ 号、OneBot WS URL、Token）。
- `group_id`、`judge`、`timeouts`。

校验规则：

- `test_root` 不得等于 `~/.astrbot`。
- 端口不得与生产 `6185 / 6199 / 6099` 重叠。
- `bot.qq` 与 `sender.qq` 必须不同。
- `group_id` 必须是数字字符串。

### 2. 用例

```json
{
  "name": "探针插件回显",
  "plugin": "astrbot_plugin_e2e_probe",
  "reload": true,
  "send": {"group_id": "{{group_id}}", "text": "/e2e_echo hello-e2e", "at_bot": true},
  "expect": {
    "timeout_seconds": 30,
    "messages": [{"contains": ["e2e_echo:hello-e2e"]}],
    "logs": [{"contains": ["[e2e_probe] echo hello-e2e"]}],
    "semantic": {"enabled": false, "criteria": ""}
  }
}
```

首版只支持单步 `send` + `expect`；多轮 `steps` 属于延期项。

### 3. 执行流水线

1. `prepare_instance(cfg, active_plugin)`：初始化测试根、设置 WebUI 密码、写平台/端口/插件配置、同步插件、按用例插件启用或禁用 `cc_qq`。
2. 若测试实例已运行，停止；启动新实例；记录 PID。
3. 连接机器人号与发送者号 OneBot，校验 `get_login_info`。
4. 等待 WebUI 端口、OneBot 机器人登录与“适配器已连接”日志。
5. 按需调用 WebUI 登录与插件重载；失败则重启实例兜底。
6. 记录日志偏移；发送 `at + text` 群消息。
7. 从观察通道收集机器人回复；无回复时用群消息历史回填。
8. 执行消息断言、日志断言；按需调用 LLM 判定。
9. 写 `summary.json`、`messages.json`、`assertions.json`、`judge.json`、`log-window.log`。
10. 停止本次启动的测试实例。

### 4. 状态与退出码

| 状态 | 含义 | 退出码 |
| --- | --- | --- |
| `PASSED` | 所有断言通过 | `0` |
| `FAILED` | 硬断言或语义断言失败 | `1` |
| `ERROR` | 环境、连接或运行错误 | `2` |
| `SKIPPED` | 仅语义断言因未配置而跳过，硬断言通过 | `3` |

### 5. 插件隔离

- 探针用例：`cc_qq` 的 `enabled_group_ids=[]`、`private_enabled=false`，避免把 `/e2e_echo` 当普通消息启动 Claude/Codex。
- `cc_qq` 用例：启用测试群，写入 `group_rules_json` 与临时工作目录。
- 每次 Run 按 `case.plugin` 重写配置并重启实例，避免内存中的旧配置生效。

## 复用点

- `integrations/astrbot/astrbot_plugin_cc_qq`：真实被测插件；复用其命令与配置 schema。
- `.devflow/astrbot-napcat-terminal/`：终端联启调研结论；复用端口与部署风险判断。
- AstrBot WebUI API：`/api/v1/auth/login` 与 `/api/v1/plugins/reload`。
- OneBot v11：`send_group_msg`、`get_login_info`、`get_group_msg_history`。
- 现有 `backend/.venv` 的 `aiohttp`，不新增依赖。

## 风险与权衡

| 风险 | 影响 | 权衡 |
| --- | --- | --- |
| 同机双开 QQ 不可行 | 主方案阻塞 | Spike 0 先行；失败回退容器/半自动 |
| NapCat 配置串用 | 两个号互相覆盖 | 独立配置目录；必要时复制 QQ.app 并只改副本 |
| 自身消息不上报 | 观察不到回复 | 事件流 + 历史回填双通道 |
| WebUI 鉴权变化 | 重载失败 | 登录失败时重启实例兜底 |
| 探针被 `cc_qq` 拦截 | 误启动代理 | 按用例禁用非被测插件 |
| 测试实例误连生产 | 污染生产 | 配置校验 + PID 归属 + 端口检查 |
| 重启实例耗时 | 用例变慢 | 首版优先正确性；后续再优化为热重载复用 |
| LLM 判定不稳定 | 误判 | 默认硬断言；语义判定仅按用例启用并保留原文 |

## 关键实现决策

1. **Runner 独立于 AstrBot**：不耦合 AstrBot 内部事件总线，保证真实 E2E。
2. **独立测试实例**：`test_root`、`6186`、`6198`、`6200`、`6201` 与生产隔离。
3. **双账号**：机器人号接入测试实例，发送者号只向 Runner 暴露 OneBot。
4. **按用例重配并重启**：保证插件开关、配置与日志从干净状态开始。
5. **消息为主、日志为辅**：消息是用户实际看到的结果；日志补充后台行为。
6. **SKIPPED 不等于 PASSED**：未配置 LLM 判定时明确标记跳过，退出码 `3`。
7. **可附加模式 `--attach`**：用于在运行中的实例上做真实热重载增量验证。
