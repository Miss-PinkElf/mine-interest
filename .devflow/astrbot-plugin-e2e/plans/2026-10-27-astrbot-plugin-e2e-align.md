# AstrBot 插件端到端自动化测试设计稿（Align）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 17:10:00 CST。
- 更新时间（Updated At）：2026-10-27 17:10:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：把 AstrBot 插件端到端自动化测试（End-to-End Test，E2E）的目标、已确认决策、架构、MVP 范围与验收标准固化为可审阅的对齐稿。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 原始需求（Raw Input）：`zzz-prompt-debug/插件自动化测试验证/prompt-01.md`。
- 关联调研（Related Research）：`.devflow/astrbot-napcat-terminal/plans/2026-10-01-astrbot-napcat终端联启调研与候选方案.md`。
- 关联决策（Related Decisions）：`.devflow/astrbot-plugin-e2e/decision-log.md`。
- 当前状态（Status）：已对齐（Aligned），待用户书面审阅；不是已批准的实施计划（Plan），不会触发实施（Apply）。
- 文档边界（Scope / Boundary）：本稿是设计对齐的唯一真相源（source of truth）；用户审阅通过后才会进入实施计划（Plan）。

## 一、背景与目标

用户希望自动测试 AstrBot 插件：使用专门的测试群和测试账号，通过终端启动 AstrBot 与 NapCat，自动发送消息、采集插件回复与日志、判断是否符合预期，并支持插件重载。

本 mission 的目标是建立一套可重复、可判定的端到端测试能力，而不是替代现有的单元测试与集成测试。现有 `tests/` 与各插件目录下的 `tests/` 继续负责逻辑级验证；本 mission 负责真实 QQ 链路下的黑盒验证。

## 二、已确认决策

| 序号 | 决策 | 结论 |
| --- | --- | --- |
| 1 | 首版范围 | 通用测试运行器（Runner） + 一个简单用例，先打通“发送 → 采集 → 断言 → 重载”闭环 |
| 2 | 实例隔离 | 使用独立测试实例（Isolated Test Instance），独立数据根、端口与插件数据，不复用当前生产实例 |
| 3 | 账号拓扑 | 双账号：测试机器人号接入独立实例，测试发送者号在测试群发消息 |
| 4 | 断言依据 | 消息为主、日志为辅；按用例可选启用 LLM 语义判定（LLM-as-a-Judge） |
| 5 | 发送方在线方式 | 同机双开 QQ：独立 `--user-data-dir` + 第二个 NapCat 实例 + 独立 OneBot 端口；必须先做技术验证（Spike 0） |

## 三、现状与约束

### 3.1 已核实的环境事实

| 对象 | 现状 |
| --- | --- |
| AstrBot | CLI 4.29.3，uv 安装；当前生产数据根 `~/.astrbot`，生产 WebUI `6185`，生产 OneBot 反向 WebSocket `6199` |
| NapCat | 不是独立终端进程；QQ 以 `--no-sandbox` 启动后，由 `loadNapCat.js` 注入 `napcat.mjs`；NapCat WebUI `6099` |
| QQ 账号配置 | NapCat 配置目录下存在 3 个 QQ 号的历史配置；具体机器人号与发送者号由本地配置提供，不写入仓库 |
| 被测插件 | `astrbot_plugin_cc_qq` 0.2.2；`cc_qq` 会过滤机器人自身消息（`integrations/astrbot/astrbot_plugin_cc_qq/platform/qq_events.py:100`） |
| 测试群 | 由本地配置提供；必须是专用测试群，Runner 只允许向该群发消息 |
| AstrBot 日志 | 当前生产实例 `log_file_enable=False`；测试实例将单独开启文件日志，并同时捕获标准输出（stdout） |
| 测试运行环境 | `backend/.venv` 为 Python 3.9.6，已具备 `aiohttp`；不新增第三方依赖 |
| 插件重载 | AstrBot 提供 `POST /api/v1/plugins/reload`，需 WebUI 登录后的 JWT；重启实例作为兜底 |

### 3.2 关键约束

1. `cc_qq` 忽略 `self_id` 消息，不能用机器人号自己发消息触发自身，因此必须双账号。
2. macOS 上 QQ 是否为单例、第二个实例能否隔离 NapCat 配置，尚未验证；这是方案前置条件。
3. 当前生产实例正在运行，测试实例必须使用不同的数据根与端口，禁止共用 `~/.astrbot`。
4. 测试实例的插件代码来自工作区快照，不能直接改生产插件目录。
5. 凭据、QQ 号、群号、Token 只允许放在本地配置，不进入 Git。
6. 测试消息只能发往专用测试群；Runner 必须有硬性群号白名单。

## 四、方案对比与选型

| 方案 | 做法 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- | --- |
| A. 外部黑盒 Runner | 独立进程；通过两个 NapCat 的 OneBot 通道发消息与收事件；AstrBot 测试实例用子进程管理 | 真正端到端；与插件解耦；可测任意插件 | 依赖双开 QQ、两个 OneBot 端口与 WebUI 鉴权 | **主方案** |
| B. 进程内插件 Runner | 写测试插件，直接构造 `AstrMessageEvent` 注入内部事件总线 | 快、不需要双开、稳定 | 不覆盖 OneBot/NapCat 链路；耦合 AstrBot 内部 API | 后续快速回归层，不替代 E2E |
| C. 外部黑盒 + 历史轮询 | 发消息后用 `get_group_msg_history` 轮询回复 | 实现简单；不依赖事件流 | 有延迟；需要消息去重 | A 的观察通道兜底 |

选型：**A 为主，C 作为观察通道兜底；B 不在本轮实现。**

## 五、总体设计

### 5.1 架构

```text
+-------------------------------------------------------------+
|                        Runner CLI                           |
|  doctor / run / suite / start-instance / stop-instance      |
+----------------+----------------+----------------+----------+
                 |                |                |
                 v                v                v
      +------------------+ +--------------+ +------------------+
      | 环境编排         | | 发送通道     | | 观察通道         |
      | Orchestrator     | | Sender       | | Observer         |
      | 启动/停止/健康检查| | OneBot WS    | | OneBot WS / 轮询 |
      +------------------+ +--------------+ +------------------+
                 |                |                |
                 v                v                v
      +------------------+ +--------------+ +------------------+
      | AstrBot 测试实例 | | 发送者 NapCat| | 机器人 NapCat    |
      | ~/.astrbot-e2e   | | OneBot 6201  | | OneBot 6200      |
      | WebUI 6186       | +--------------+ +------------------+
      | 反向 WS 6198     |                        |
      +------------------+                        | 反向 WS 6198
                 ^                                |（仅机器人号）
                 |                                |
                 +--------------------------------+
```

说明：

- 发送者 NapCat 只向 Runner 暴露 `6201`，**不接入 AstrBot 实例**，避免测试消息被测试实例重复处理。
- 机器人 NapCat 既向 AstrBot 测试实例建立 `6198` 反向 WebSocket，又向 Runner 暴露 `6200` 观察端口。
- Runner 自身运行在 `backend/.venv`（Python 3.9.6 + `aiohttp`）；AstrBot 测试实例仍运行在 AstrBot 自己的 uv Python 环境。

端口规划（均可配置，以下为候选默认值）：

| 端口 | 用途 | 与生产实例关系 |
| --- | --- | --- |
| `6186` | 测试实例 WebUI | 生产为 `6185`，不冲突 |
| `6198` | 测试实例 OneBot 反向 WebSocket 服务端 | 生产为 `6199`，不冲突 |
| `6200` | 机器人号 NapCat 观察用 WebSocket 服务端 | 新增，仅供 Runner 订阅 |
| `6201` | 发送者号 NapCat 控制用 WebSocket 服务端 | 新增，仅供 Runner 发消息 |

### 5.2 组件职责

| 组件 | 职责 | 不做什么 |
| --- | --- | --- |
| `cli.py` | 命令入口、参数解析、退出码 | 不直接拼接 OneBot 报文 |
| `config.py` | 读取并校验本地配置；脱敏 | 不写入凭据 |
| `bootstrap.py` | 初始化测试实例、写入测试配置、同步插件 | 不启动、不停止实例 |
| `orchestrator.py` | 启动/停止测试实例、等待就绪、捕获 stdout | 不管理生产实例 |
| `runner.py` | 执行单个用例的完整流程（发送、观察、断言、报告） | 不管理 CLI 参数 |
| `cases.py` | 用例加载与校验 | 不执行用例 |
| `onebot.py` | OneBot 连接、发消息、订阅事件、历史轮询 | 不判断业务预期 |
| `log_capture.py` | 按时间窗口截取测试实例日志 | 不做断言 |
| `assertions.py` | 包含、正则、结构化断言 | 不调用 LLM |
| `llm_judge.py` | LLM 语义判定 | 不作为默认硬断言 |
| `reloader.py` | WebUI 登录、插件重载、就绪等待 | 不重启生产实例 |
| `reports.py` | 生成 JSON 报告与证据目录 | 不改动被测插件 |

### 5.3 目录结构

```text
tools/astrbot_e2e/
├─ cli.py
├─ config.py
├─ bootstrap.py
├─ orchestrator.py
├─ runner.py
├─ cases.py
├─ onebot.py
├─ log_capture.py
├─ assertions.py
├─ llm_judge.py
├─ reloader.py
├─ reports.py
├─ config.example.json
├─ config.local.json          # 本地配置，加入 .gitignore
├─ cases/
│  ├─ probe_echo.json
│  └─ cc_qq_help.json
├─ fixtures/
│  ├─ astrbot_plugin_e2e_probe/
│  │  ├─ main.py
│  │  └─ metadata.yaml
│  ├─ cc_qq_config.json
│  └─ napcat/
│     ├─ onebot11.bot.example.json
│     └─ onebot11.sender.example.json
└─ reports/                   # 运行产物，加入 .gitignore
```

### 5.4 配置模型

`config.example.json` 入库，只含占位值和字段说明；`config.local.json` 由用户本地填写，不提交。

```json
{
  "test_root": "~/.astrbot-e2e",
  "webui": {
    "host": "127.0.0.1",
    "port": 6186,
    "username": "<webui-username>",
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

校验规则：

- 被测插件由每个用例的 `plugin` 字段声明，不在全局配置里写死。
- `group_id` 必填，且 Runner 只允许向该群发送消息。
- `test_root` 不得等于生产数据根 `~/.astrbot`；端口不得与生产端口重叠。
- `bot.qq` 与 `sender.qq` 必须不同；缺失时 `doctor` 直接失败。
- `judge` 可缺省；缺省时语义断言标记为 `SKIPPED`，不得视为通过。

测试实例根目录约束：

- `orchestrator.py` 在 `test_root` 下创建 `.astrbot` 标记文件，并用 `cwd=test_root` 启动 AstrBot，满足 CLI 的 `check_astrbot_root` 检查。
- `astrbot.command` 使用绝对路径或 `shutil.which("astrbot")` 解析；不依赖交互式 shell 里的同名函数。
- 测试实例首次启动时写入独立的 `cmd_config.json`，只启用被测插件与测试平台，不复制生产配置。
- 被测插件从 `integrations/astrbot/<plugin>` 同步到 `test_root/data/plugins/<plugin>`；插件配置由 `fixtures/` 提供，不复制生产插件数据。
- `cc_qq` 的夹具至少写入 `qq_platform_id`、`enabled_group_ids` 与 `group_rules_json`，并把测试群指向测试实例内的临时工作目录；否则插件会按配置无效拒绝消息。
- 非被测插件必须避免拦截探针消息：探针用例运行时，`cc_qq` 的 `enabled_group_ids` 写空、`private_enabled` 关闭；只有 `cc_qq` 用例才启用测试群。这样避免 `cc_qq` 把 `/e2e_echo` 当成普通消息启动 Claude/Codex。
- 机器人号 NapCat 必须开启 `reportSelfMessage`，否则观察通道看不到机器人发出的回复；该字段不生效时走群消息历史兜底。

### 5.5 用例模型

首版只实现单步 `send` + `expect`；多轮 `steps` 字段属于延期项，本轮不解析。

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
    "messages": [
      { "contains": ["hello-e2e"] }
    ],
    "logs": [
      { "contains": ["[e2e_probe] echo hello-e2e"] }
    ]
  }
}
```

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
    "messages": [
      { "contains": ["/new", "/info"] }
    ],
    "semantic": {
      "enabled": true,
      "criteria": "回复是一份命令列表，且包含 /new 与 /info"
    }
  }
}
```

### 5.6 执行流程

1. `doctor`：校验配置、端口、两个 OneBot 连接、测试实例状态与插件版本。
2. `start-instance`：若测试实例未启动，用子进程启动；捕获 stdout 到 `reports/<run>/astrbot.log`；等待 WebUI、OneBot 心跳与插件加载就绪。
3. `stop-instance`：只停止 Runner 自己启动并记录在案的 PID；发现端口或数据根属于生产实例时直接拒绝，不使用宽泛进程终止。
4. `reload`：同步工作区插件到测试实例插件目录，再调用 WebUI 重载接口；失败时按配置重启实例。
5. `send`：通过发送者号 OneBot 调用 `send_group_msg`，构造 `at` 段，记录消息 ID 与时间。
6. `observe`：订阅机器人号 OneBot 事件流；优先采集 `message_sent` 与群消息事件；超时后用 `get_group_msg_history` 兜底。
7. `assert`：执行消息断言、日志断言；若启用 `semantic`，调用 LLM 判定。
8. `report`：写 `summary.json`、`messages.json`、`assertions.json`、`judge.json` 与日志窗口。
9. `cleanup`：按用例配置清理测试实例的插件数据与会话；不清理生产实例。

### 5.7 插件重载

- 主路径：`POST /api/auth/login` 获取 JWT，再 `POST /api/v1/plugins/reload`。
- 兜底路径：重启测试实例；重启前记录当前实例 PID，只停止 Runner 自己启动的进程。
- 就绪判定：WebUI 端口可连接、OneBot 心跳正常、插件加载日志出现。
- 安全边界：`reloader.py` 只接受 `test_root` 下的实例，拒绝生产数据根与生产端口。

### 5.8 断言与 LLM 判定

- `contains`：支持 `all` 与 `any` 两种模式，默认 `all`。
- `regex`：使用 Python `re`，按消息逐条匹配。
- `semantic`：按用例启用；调用 OpenAI 兼容接口，提示词要求只返回：

```json
{"pass": true, "reason": "简短理由"}
```

- 未配置 judge 或调用失败时，结果标记为 `SKIPPED` 或 `ERROR`，不得伪装成 `PASSED`。
- 硬断言失败时不再调用 LLM 判定，避免用模型掩盖明确错误。

### 5.9 报告与失败证据

每次运行生成：

```text
tools/astrbot_e2e/reports/<YYYYmmdd-HHMMSS>/<case-name>/
├─ case.json          # 用例副本
├─ summary.json       # 状态、耗时、断言汇总
├─ messages.json      # 发送与收到的消息、时间、发送者、消息 ID
├─ assertions.json    # 每条断言的输入、实际值、结果
├─ judge.json         # LLM 判定原文（如启用）
└─ astrbot.log        # 时间窗口内的测试实例日志
```

控制台输出：用例名、状态（PASSED / FAILED / SKIPPED / ERROR）、耗时、失败原因与证据目录。

退出码：`0` 表示全部通过；`1` 表示硬断言失败；`2` 表示环境或运行错误；`3` 表示仅有跳过项且无失败。首版按此约定实现，为后续 CI 集成留出稳定接口。

## 六、前置技术验证（Spike 0）

### 6.1 目标

验证“同机双开 QQ”是否可行，确认以下四项同时成立：

1. macOS 上能启动第二个 QQ 实例，且与当前实例互不影响。
2. 两个 QQ 实例都能加载 NapCat，且 NapCat 配置目录、登录态、日志互不覆盖。
3. 两个 OneBot 端口能同时监听，并分别登录测试机器人号与测试发送者号。
4. 测试 AstrBot 实例能用独立数据根启动，且不读取、不写入生产 `~/.astrbot`。

### 6.2 重点风险

- `QQ.app` 的 `package.json` 中 `main` 当前硬编码指向默认容器下的 `loadNapCat.js`；第二个实例可能复用同一 NapCat 脚本与配置目录。
- macOS 可能通过单例锁、容器沙箱或 QQ 自身限制阻止双开。
- NapCat 可能按 QQ 数据目录写入配置；若两个实例共享目录，会互相覆盖 `onebot11_<uin>.json`。
- 若必须复制 `QQ.app` 才能隔离 NapCat，只允许复制到独立路径并改写副本的 `package.json`，不得修改当前生产 `QQ.app`。
- macOS App Sandbox 实测：`NAPCAT_WORKDIR` 必须放在容器可写目录（`~/Library/Containers/com.tencent.qq/Data/Library/Application Support/QQ/NapCat-e2e`）；放在 `~/.qq-e2e/NapCat` 会报 `EPERM mkdir`。
- 双开实例会出现 native addon / FFmpeg / PacketBackend 警告；文本双向收发已验证可用，富媒体能力保留为风险。
- 两个测试 QQ 号的登录由用户人工完成；Runner 只验证登录后的 `get_login_info` 与 OneBot 连接状态，不尝试自动扫码或绕过风控。

### 6.3 通过标准

- 两个 QQ 号同时在线；
- 两个 NapCat 各自有独立配置与日志；
- Runner 能分别通过两个 OneBot 端口完成 `get_login_info`；
- 发送者号能在测试群发消息，机器人号能收到并回复；
- 生产实例端口与数据根未被触碰。

Spike 0 已于 2026-10-27 通过，详细账号、端口、证据与残留风险见 `2026-10-27-spike-0-dual-qq-result.md`。

### 6.4 失败回退

若 Spike 0 失败，按以下顺序回退，并写回 `decision-log.md`：

1. Linux 容器/WSL 运行发送方 NapCat（独立 QQ 登录与 OneBot 端口）。
2. 第二台设备人工发送，Runner 只做采集与断言（半自动）。
3. 单账号 + 内部事件注入（仅用于插件逻辑验证，不作为 E2E 验收）。

## 七、MVP 范围与验收标准

### 7.1 本轮 MVP

1. Spike 0 双开验证与结论落盘。
2. Runner 基础能力：配置校验、环境编排、OneBot 发送、事件订阅、日志采集、报告。
3. 探针插件（Probe Plugin）：`/e2e_echo`、`/e2e_sleep`、`/e2e_log` 三个命令，用于 Runner 自检。
4. 首个真实插件用例：`cc_qq /help` 群聊回执。
5. 插件重载：WebUI API 主路径 + 重启兜底。
6. 失败证据与退出码。

### 7.2 验收标准

- `python tools/astrbot_e2e/cli.py doctor` 能明确报告两个账号、测试实例、被测插件是否就绪。
- `python tools/astrbot_e2e/cli.py run tools/astrbot_e2e/cases/probe_echo.json` 稳定通过。
- `python tools/astrbot_e2e/cli.py run tools/astrbot_e2e/cases/cc_qq_help.json --reload` 稳定通过，并产出消息与日志证据。
- 修改插件代码后，`--reload` 能生效并继续通过。
- 故意写错期望时，失败信息能指出“期望什么、实际收到什么”。
- 整个过程中，Runner 未向测试群以外的群发送消息，未触碰生产实例。

## 八、风险清单

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| 同机双开 QQ 不可行 | 主方案阻塞 | 先做 Spike 0；失败按回退顺序切换 |
| NapCat 配置目录冲突 | 两个号互相覆盖配置 | 每个实例独立配置根；Spike 0 验证 |
| OneBot 自身消息不上报 | 观察不到机器人回复 | 优先事件流；失败时用 `get_group_msg_history` 轮询 |
| WebUI 鉴权变化 | 重载失败 | 封装登录与重载；失败时重启实例兜底 |
| 测试实例误连生产 | 污染生产数据 | `doctor` 强制校验数据根与端口；Runner 只管理自己启动的进程 |
| 测试群消息外泄 | 打扰真实群 | 群号白名单硬校验 |
| QQ 风控 | 测试号被限制 | 仅测试群、低频、串行执行 |
| LLM 判定不稳定 | 误判 | 默认硬断言；语义判定仅按用例启用，并保留判定原文 |
| 日志格式变化 | 日志断言失效 | 消息为主、日志为辅；关键字集中在用例中 |

## 九、延期项（Deferred Scope）

| 对象或能力 | 本轮不做的原因 | 后续触发条件或推荐阶段 |
| --- | --- | --- |
| `cc_qq` 长任务（Claude/Codex 实际执行） | 耗时长、涉及会话与工作目录清理，首版先验证闭环 | Runner 稳定后，第二阶段增加 `/new`、`/cc`、`/end` 用例 |
| 审批流程（`/approve`、`/deny`） | 依赖长任务与超时控制 | 长任务用例稳定后单独设计 |
| 多轮对话与上下文断言 | 首版只支持单步 | 用例模型引入 `steps` 后实现 |
| WebUI 页面 | 首版只需 CLI | 有可视化需求时再评估 |
| CI 集成 | 依赖双开环境与人工登录 | 本地稳定后，再评估自托管 Runner |
| 并行用例 | QQ 与测试实例均为单实例，容易互相干扰 | 串行稳定后，再评估多实例池 |
| 全量 LLM 判定矩阵 | 判定不稳定，先按用例可选启用 | 收集一批真实用例后，再评估统一判定策略 |
| 自动扫码登录 | QQ 登录涉及风控与人工确认 | 不承诺自动化；保持人工登录 |
| 图片、文件、引用等消息段 | 首版只验证文本与 @ | 按插件需求逐步扩展 |

延期项不是永久放弃；后续满足触发条件时，进入独立阶段或新 mission。

## 十、后续阶段

1. **Plan**：把本设计拆成可执行计划与任务清单（`plans/`、`spec/tasks.md`）。
2. **Apply**：先执行 Spike 0；通过后再实现 Runner 与两个用例。
3. **Verify**：用真实消息与日志证据验证 MVP 验收标准。
4. **Close**：写 checkpoint，记录延期项与下一阶段入口。

## 十一、审阅记录

- 2026-10-27：用户确认首版范围、实例隔离、双账号、断言渠道与同机双开方向；同意“探针插件 + `cc_qq /help`”与 `tools/astrbot_e2e/` 目录结构。
- 待办：用户书面审阅本设计稿后，进入实施计划（Plan）。
