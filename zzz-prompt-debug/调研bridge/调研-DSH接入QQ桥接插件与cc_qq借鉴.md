# DSH 接入 QQ 桥接插件调研与 cc_qq 借鉴报告

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 14:30:51 +08:00
- 更新时间（Updated At）：2026-10-27 14:30:51 +08:00
- 作者（Author）：Claude（AI 助手）
- 目的（Purpose）：调研 6 个 DSH 接入 QQ 的开源桥接/插件，厘清其接入原理，并对照本地 `cc_qq` 与借鉴来源 `cc-ding`，提炼可落地的借鉴点与优先级。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`（相关，但不属于该 mission 已批准计划）
- 原始需求（Raw Requirement）：`zzz-prompt-debug/调研bridge/prompt-01.md`
- 调研代码目录（Research Code Path）：`zzz-prompt-debug/调研bridge/dsh-qq-plugins/`（已加入 `.gitignore`，不提交）
- 当前状态（Status）：调研完成（Research Completed）
- 文档边界（Scope / Boundary）：本文是调研结论（Research），不是当前状态真相源（source of truth），不代表已批准方案（Plan），不触发实现（Apply）。所有结论仅基于代码与文档研读，未在真实 DSH/QQ 环境运行验证。

---

## 0. 一句话结论

这 6 个仓库不是同一类东西，大致分成三族：

| 族 | 仓库 | 本质 |
|---|---|---|
| 独立桥接进程（Web API 适配） | `qq-bridge`、`dsh-qq`、`DSH-Fatwhale-QQ` | 桥接进程通过 DSH Web API 或 `dsh` CLI 驱动 Agent，再与 QQ 后端通信 |
| DSH 原生 Cordis 插件 | `dsh-qq-bridge`、`dsh-qq-plugin`、`dsh-dfy-qq` | 直接运行在 DSH 宿主内，注入 `agents`/`sessions`/`tools`/`systemPrompt` 等服务 |
| 本地对照基线 | `cc-ding`、`cc_qq` | 通过 CLI 子进程驱动 Claude Code / Codex，不依赖 DSH 宿主 |

对 `cc_qq` 最有价值的借鉴，不在“照搬 DSH API”，而在这些设计模式：

1. **权限与审批**：`dsh-qq` 的 L0–L3 分级、确认码 + TOTP、编号审批 `#n`、超时自动拒绝、自动回落、哈希链审计。
2. **会话体验**：`dsh-qq-plugin` 的 `/new`、`/list`、`/switch`、`/current`、`/cancel`，以及“一个 QQ 聊天 ↔ 多个 DSH 会话”的两级会话列表。
3. **消息可靠性**：`dsh-qq-bridge` 的轮询水位、消息去重、合并窗口、singleflight、图片原图回发、语音转写。
4. **行为层**：`dsh-dfy-qq` 的“让模型判断要不要接话 / 挑哪个人格”，比硬编码关键词更符合 Agent 化方向。
5. **产品化与安全边界**：`DSH-Fatwhale-QQ` 的“无工具聊天内核”和 `dsh-qq` 的“双重工具边界”，都能补强 `cc_qq` 的群聊隔离。

同时必须强调：`cc_qq` 当前的安全模型已经不弱，甚至强于多数外部插件。**不要为了追功能而引入 `bypassPermissions`、默认 `danger-full-access`、无鉴权控制台等反模式。**

---

## 1. 调研范围与方法

### 1.1 仓库清单

| 仓库 | 版本 | 分支 | 形态 | 本地路径 |
|---|---:|---|---|---|
| [Derpyu520/qq-bridge](https://github.com/Derpyu520/qq-bridge) | `0.2.1-r1` | `main` | 独立 Node 桥接 | `zzz-prompt-debug/调研bridge/dsh-qq-plugins/qq-bridge/` |
| [Yuuyuko-uu/dsh-qq-bridge](https://github.com/Yuuyuko-uu/dsh-qq-bridge) | `1.0.8` | `main` | DSH 原生插件 | `zzz-prompt-debug/调研bridge/dsh-qq-plugins/dsh-qq-bridge/` |
| [h-D-ACE/dsh-qq](https://github.com/h-D-ACE/dsh-qq) | `1.1.0` | `main` | 独立桥接（qq-bridge 增强分叉） | `zzz-prompt-debug/调研bridge/dsh-qq-plugins/dsh-qq/` |
| [xcisxc29/dsh-qq-plugin](https://github.com/xcisxc29/dsh-qq-plugin) | `1.0.5` | `main` | DSH 原生插件 | `zzz-prompt-debug/调研bridge/dsh-qq-plugins/dsh-qq-plugin/` |
| [beiheng127/dsh-dfy-qq](https://github.com/beiheng127/dsh-dfy-qq) | `0.5.5` | `master` | DSH 原生插件（行为层） | `zzz-prompt-debug/调研bridge/dsh-qq-plugins/dsh-dfy-qq/` |
| [miku05231/DSH-Fatwhale-QQ](https://github.com/miku05231/DSH-Fatwhale-QQ) | `3.1.3` | `main` | 独立桥接 + 桌面应用 | `zzz-prompt-debug/调研bridge/dsh-qq-plugins/DSH-Fatwhale-QQ/` |

### 1.2 方法

1. 全部仓库使用 `git clone --depth 1` 浅克隆，只用于研读，不提交。
2. 先读 README 建立功能地图，再读入口文件、核心模块、配置与测试。
3. 对 README 宣传与代码实现不一致的地方单独标注。
4. 所有结论带源码路径与行号；无法从代码确认的内容标注“未确认”。
5. 未在真实 DSH/QQ 环境运行，因此不对“实际能否工作”做保证。

### 1.3 重要前提

这些外部仓库面向 **DeepSeek Harness（DSH）**，而 `cc_qq` 面向 **Claude Code / Codex CLI**。两者的宿主能力不同：

- DSH 插件可以直接拿到 `sessionController`、`assistant-stream`、`approval/request`、`user-questions/request`、`tools/pre-execute` 等宿主事件。
- `cc_qq` 是 AstrBot 插件，每次回合启动一个独立 CLI 子进程，通过 `stream-json` / `--json` 解析结果，必须自己实现会话、权限、审批、队列、审计。

因此，外部仓库的**模式**可以借鉴，**API 不能直接照搬**。

---

## 2. 先厘清概念：DSH 是什么，QQ 怎么接

### 2.1 DSH（DeepSeek Harness）

DSH 是一个本地 Agent 宿主，类似“DeepSeek 版的 Claude Code / Codex 桌面端”。从这些仓库可以确认它有这些关键机制：

| 机制 | 作用 | 相关仓库 |
|---|---|---|
| Profile / `cordis.patch.yml` | 插件与运行时配置的挂载点 | 三个 DSH 插件、`dsh-qq` |
| Agent Preset | 预设 Agent 的工具面、人格、权限 | `qq-bridge`、`dsh-qq` |
| Permission Preset | 沙箱模式 + 审批策略（`read-only` / `workspace-write` / `danger-full-access`，`ask` / `never`） | `dsh-qq` |
| `/api/<namespace>/<method>` | 斜杠 RPC | `qq-bridge`、`dsh-qq` |
| `/api/remote.mux` + `session/follow` | 事件流与会话跟踪 | `qq-bridge`、`dsh-qq` |
| `session/control` / `session/projections` | 会话状态、待处理队列 | `qq-bridge`、`dsh-qq` |
| `sessionController` / `agents` | 宿主内创建、恢复、驱动 Agent | 三个 DSH 插件 |
| `assistant/message` / `assistant-stream` | 流式输出 | 三个 DSH 插件 |
| `approval/request` / `user-questions/request` | 工具审批与结构化提问 | `dsh-qq-plugin` |
| `tools.guard` / `tools.restrict` | 执行期拒绝、注册期隐藏 | `qq-bridge`、`dsh-qq`、`DSH-Fatwhale-QQ` |
| `systemPrompt.context` | 注入人格、记忆、群友档案等上下文 | `dsh-dfy-qq` |
| MCP | 把 QQ 操作暴露成 Agent 工具 | `qq-bridge`、`dsh-qq` |
| `dsh --profile ... --json` | 无头 CLI + NDJSON 事件 | `DSH-Fatwhale-QQ` |
| `@deepseek-ai/dsh-app-boot` / companion | 桌面宿主内驱动会话 | `DSH-Fatwhale-QQ` |

### 2.2 QQ 侧的两种接入路线

| 路线 | 原理 | 代表 | 特点 |
|---|---|---|---|
| OneBot 11 + SnowLuma / NapCat | 本机 QQ 后端暴露 WebSocket / HTTP，桥接按 OneBot 协议收发 | `qq-bridge`、`dsh-qq`、`dsh-qq-bridge`、`dsh-dfy-qq`、`DSH-Fatwhale-QQ` | 支持群聊、@、引用、合并转发、图片、语音；需要用户自己安装并登录 QQ 后端 |
| 腾讯官方 QQ 机器人平台 | 通过官方 SDK 连接 `api.bot.qq.com`，扫码创建机器人 | `dsh-qq-plugin` | 无需公网 IP、无反代；但当前代码只做 1:1 私聊（`c2c`），不支持群聊 |

### 2.3 三种 DSH 接入形态

```
┌──────────────────────────────────────────────────────────────┐
│ A. 独立桥接进程（DSH Web API）                               │
│ QQ 后端 ── OneBot WS/HTTP ──► 桥接进程 ── /api RPC ──► DSH    │
│                                    ◄── remote.mux 事件流 ────│
│ 代表：qq-bridge、dsh-qq                                       │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ B. DSH 原生 Cordis 插件                                      │
│ QQ 后端 ── OneBot/官方 SDK ──► 插件(host 半) ── 宿主服务 ──► Agent │
│ 设置页 ◄── HTTP ──► 插件(client 半)                          │
│ 代表：dsh-qq-bridge、dsh-qq-plugin、dsh-dfy-qq               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ C. CLI / 桌面宿主 / Companion                                │
│ QQ 后端 ──► 桥接 ── `dsh --json` 子进程 ──► Agent            │
│               或 ── @deepseek-ai/dsh-app-boot 桌面宿主       │
│               或 ── companion 插件 HTTP                      │
│ 代表：DSH-Fatwhale-QQ                                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. 六个仓库逐个解剖

### 3.1 `qq-bridge`（Derpyu520，上游基线）

#### 定位

把 QQ 好友/群消息接入 DSH Agent：QQ 消息变成 DSH 会话里的用户消息，Agent 的回复、提问、工具审批发回 QQ。

#### 架构

```
QQ 消息 ──► SnowLuma（OneBot v11 WS）──► qq-bridge ──► DSH Web API
                                              ▲                │
                                              └── 回复/提问/审批 ┘
```

- 入口：`qq-bridge/src/bridge.js`
- 独立 Node ESM 进程，无托盘；Windows 用 `start.bat` 循环重启
- 自带本地 Web 控制台（默认 `127.0.0.1:3100`）

#### QQ 侧

- 使用 `@snowluma/sdk` 的 `SnowLumaWebSocketClient`
- 私聊/群消息、`notify` 拍一拍、心跳、`bot_status`
- 支持文本、`at`、`reply`、图片、`face`/`mface`、合并转发
- 语音/视频不作为模型输入，只落占位文本
- 断线自动重连；token/端点可从 OneBot 配置中发现并写回
- HTTP API 作为发送与读取兜底

关键位置：`qq-bridge/src/bridge.js:11815-11998`、`src/snowluma-conn.js`、`src/mcp-snowluma-safe.js`

#### DSH 侧

- 鉴权：用 `~/.dsh/.credentials.yaml` 里的持久化签名密钥**离线铸造 Cookie**，不依赖进程启动 token；launch token 仅作兜底，且限制只发回环地址
- RPC：点号方法名转斜杠端点 `/api/<namespace>/<method>`
- 事件流：`/api/remote.mux` + `session/follow`，跨重连保留 `_desiredFollows` 并重放
- 会话创建：`workspace.create` → `sessions.create` → `events.follow`
- Preset：`qq-chat` / `qq-chat-v2`，由 `plugins/qq-agent-presets/` 提供
- MCP：挂三个 server
  - `snowluma`：QQ 动作安全子集
  - `snowluma-host`：只读探活
  - `web-search-safe`：只读搜索，带 SSRF 防护
- 工具面双重防线：`tools.restrict` 注册期隐藏 + `tools.guard` 执行期白名单

关键位置：`qq-bridge/src/dsh-client.js:97-145`、`:667-760`；`src/bridge.js:8148-8170`；`plugins/qq-agent-presets/qq-tool-restrict.mjs:265-330`

#### 消息链路

**入站（QQ → DSH）**

1. SDK 收到消息，排除自己发的
2. `handleIncoming` 做白名单/模式判断
3. 解析 `at`、引用原文、媒体元数据
4. 处理挂起提问/审批
5. 处理静默、管理员控制词、`/reset` 等桥接硬命令
6. 二代仿真模式消息进入未读流，按唤醒配置决定是否唤醒
7. 普通模式拼 prompt，必要时按会话入队，DSH 恢复后补投
8. `ensureSession` 后调用 `api.sessions.prompt({ mode: 'queue' })`

**出站（DSH → QQ）**

1. `pumpMux` 收到 `session/event`，按映射找 QQ 会话
2. `turn/start` 建 collector，`turn/end` 收尾
3. 回合结束后检查本回合是否已成功调用 MCP 发送工具，成功则跳过自动转发
4. 敏感信息审计，命中整条拦截
5. 普通模式 `sendToQQ`；社交模式按时间线分条
6. Markdown 转纯文本、`splitForQQ` 分段、`escapeCqText` 防 CQ 注入
7. 审批/提问转发到 QQ，管理员回复后回执

关键位置：`qq-bridge/src/bridge.js:10817-11160`、`:11341-11810`、`:7223-7244`、`:7993-8030`

#### 会话模型

- 每个 QQ 私聊/群对应一个 DSH 会话
- key：`private:<QQ>` / `group:<群号>`
- 映射持久化：`state/sessions.json`
- 所有 QQ 会话统一归组到「QQ 聊天」workspace
- 模式/preset 变化时旧会话退役

#### 权限/安全

- 白名单：`allow.private` / `allow.groups`，`deny` 优先，空白名单默认拒绝
- 四种模式：`chat` / `closed-agent` / `reserved` / `reserved2`
- 群聊 Agent 无本地工具：preset 不挂 bash/read/write/subagent
- 发送目标强制白名单；语音只能从语音库目录取
- 出站敏感信息审计
- 控制台需要 `consoleToken`，绑定回环地址，写操作检查 Origin

#### 特色能力

- 四模式切换
- 一代/二代仿真（观望、活跃、试探、退场、潜水、分条）
- 黑话学习
- 表情包收藏与发送
- 语音发送（只发语音库，无 TTS）
- Token 账本与费用折算
- 10 页 Web 控制台

#### README 与代码差异

- README 说“每 4 秒轮询”是 `dsh-qq-bridge` 的问题，不在本仓库
- README 自述接收语音/视频只占位、AI 发语音只发语音库
- `RULES.md` 明确 DSH 设置页没有 `qq-mode` 卡片，因为插件只有 host 半
- 控制台令牌 README 说“打印在启动日志”，实际只打印前 6 位

#### 评价

这是整条产品线的“上游基线”，功能极全，但复杂度高、配置多、代码体量大。适合作为“能力地图”，不适合整体照搬。

---

### 3.2 `dsh-qq`（h-D-ACE，qq-bridge 增强分叉）

#### 定位

基于 `qq-bridge v0.2.0-r3` 的二次开发版，新增多系统、接口平台、控制中心、owner 管理通道、L0–L3 权限、审计、定时任务等。**这是对 `cc_qq` 参考价值最高的仓库。**

#### 架构

```
QQ 后端（SnowLuma / NapCat）
   │ OneBot v11
   ▼
接口平台（可选，3120）──► 桥接进程 ──► DSH Web API
                              │
                              ├── 控制中心（3099）
                              ├── owner 私聊管理通道
                              └── 审批/审计
```

#### 比上游新增的关键能力

| 能力 | 说明 | 关键位置 |
|---|---|---|
| 接口平台 | 统一 SnowLuma / NapCat，预留微信/Discord/KOOK | `interface-platform/README.md` |
| 控制中心 | 启停桥接、接口平台、QQ 后端；NapCat 扫码；版本检查 | `src/launcher/control-center.mjs` |
| 跨群认人 | 只认 QQ 号，同名不同号不合并 | `src/social/people.js` |
| 分层人物记忆 | 群内 / 私聊 / 全局，注入时过滤可见性 | `src/social/memory-policy.js` |
| 入群感知 | 新人、熟人进新群、退群回归 | `src/social/group-events.js` |
| owner 管理通道 | 私聊 `/mode agent L1~L3` + 确认码 + TOTP | `src/admin/mode-control.js`、`src/admin/totp.js` |
| L0–L3 权限 | 群友 / 只读 / 工作区 / 完全访问但每次审批 | `src/admin/dsh-permission.js` |
| 审批增强 | 编号 `#n`、真实参数、并发不覆盖、超时拒绝 | `src/admin/approvals.js` |
| 自动回落与审计 | 高权限闲置回落；哈希链审计 | `src/admin/audit-log.js` |
| 切换不失忆 | 休眠会话 + owner 交接，回落后续接 | `src/mode-handover.js` |
| 定时任务 | 一次/每天/每周/工作日/每月/随机/cron | `src/scheduler/engine.js` |
| 定时静默 | 按时间段停止唤醒省 token | `src/silence-schedule.js` |

#### 权限模型（最值得借鉴）

`dsh-qq/src/admin/dsh-permission.js` 里写清了 DSH 0.2.0-rc.2 的关键事实：

- 权限预设 = 沙箱模式 + 审批策略
- `dsh-base` 默认表：
  - `read-only` + `ask`
  - `workspace-write` + `ask`
  - `danger-full-access` + **`never`**
- 单个会话的权限只能通过 `commands/execute(sessionId, "/permission <name>")` 设置
- 桥接**禁止**映射到内置 `danger-full-access`（审批策略 `never` = 不弹审批直接执行）

它的级别映射：

| 级别 | 适用 | DSH 权限预设 | Agent preset | 额外闸门 |
|---|---|---|---|---|
| L0 | 群聊/仿真 | `qq-chat*` | 无本地工具 | 无 |
| L1 | closed-agent 只读 | `read-only` | `qq-agent-readonly` | 工具白名单 |
| L2 | closed-agent 工作区 | `workspace-write` | `qq-agent-workspace` | `qq-approval-gate` |
| L3 | closed-agent 完全访问 | 自定义 `qq-full-ask`（`danger-full-access` + `ask`） | `qq-agent-full` | `qq-approval-gate` |

**最关键的一条经验**：在 DSH rc.2 里，`danger-full-access + ask` 并不等于“每次审批”，因为审批只在“越过当前沙箱”时触发；完全访问没有边界可越过，所以永远不会弹审批。`dsh-qq` 因此用 `tools/pre-execute` 瀑布主动返回 `{ kind: 'ask' }`，自己造审批闸门。

这与 `cc_qq` 的实测结论高度一致：`bypassPermissions` 不执行 deny 规则，所以 `cc_qq` 改用 `dontAsk + guard hook`。**两者都在说明同一件事：权限模式本身不可靠，必须在工具执行前加一道确定性的闸门。**

关键位置：`dsh-qq/src/admin/dsh-permission.js:1-110`、`plugins/qq-agent-presets/qq-approval-gate.mjs:1-80`、`docs/guides/ADMIN_CHANNEL.md`

#### 审批设计

- owner 私聊里回复“通过 #n / 拒绝 #n”
- 编号全局唯一，跨重启不复用
- 展示工具名、理由、真实命令参数（脱敏、截断）
- 多个挂起时，裸回复会要求带编号
- 超时自动拒绝并通知
- AI 没有审批决定工具，只有 owner 的真实 QQ 消息能消费
- 审计写入 `state/admin/audit.jsonl`，JSONL + SHA-256 哈希链

#### README 与代码差异

- 接口平台是 M1，不是完整交付；临时消息、文件段、消息历史、媒体上传、持久化游标未统一
- macOS + NapCat 未在真实环境验收
- L2/L3 审批闸门需要在部署机运行 `npm run probe:permission` 实测
- 跨群协作只提供 presence/activity，不返回聊天内容
- 定时任务农历未做
- Linux 桌面版 DSH 随机端口发现未实现

#### 评价

安全与运维设计最完整，适合作为 `cc_qq` 的“权限/审批/审计”参考。但系统复杂、依赖多，且部分能力是 Beta。

---

### 3.3 `DSH-Fatwhale-QQ`（miku05231，产品化桌面应用）

#### 定位

不是 DSH 插件，而是一个完整的桌面桥接产品：NapCat + 桥接 + 控制台 + 托盘 + 更新 + Docker。

#### 架构

```
手机/电脑 QQ ←→ 腾讯服务器
                  ↕
             NapCatQQ（本机登录）
                  ↕ OneBot v11 WS
        ┌──────────────────────┐
        │  桥接 src/index.js   │  白名单 → 串行队列 → 分段回发
        │  dsh --profile ...   │
        └──────────────────────┘
                  ↕
        Windows 托盘 / Web 控制台 / Docker
```

#### DSH 接入（与其他仓库不同）

- **不接 DSH Web API**
- 三种方式：
  1. `dsh --profile headless --patch ... --json` 子进程，解析 NDJSON 的 `session`、`text`、`final`、`error`
  2. `@deepseek-ai/dsh-app-boot` 加载 desktop profile，用 `sessionController.create/prompt` 驱动
  3. `qq-bridge-companion` 插件跑在 DSH Desktop 宿主内，桥接通过本地 HTTP `/prompt`、`/cancel`、`/attach` 调用

#### 普通成员与管理员隔离（最值得借鉴）

- 普通成员固定走 `runChatOnlyDsh`，加载一个**无工具 DSH 内核**
- `installChatOnlyPolicy` 强制：
  - `tools.guard(() => CHAT_ONLY_DENIAL)` 拒绝一切工具
  - `tools.schemas()` 必须为空
  - 每轮再检查 `schemas(agent).length === 0`，否则报错
- 管理员才走完整 DSH profile / headless，使用 `dsh.permissionMode`

关键位置：`DSH-Fatwhale-QQ/src/chat-only.js:110-145`、`src/chat-only-host.js:90-112`、`src/agent-runner.js:65-140`

#### 会话模型

- key：`p:<QQ>:u:<QQ>:<scope>:v1` / `g:<群号>:u:<QQ>:<scope>:v1`
- 也就是说：**群聊不是“一个群一个会话”，而是“群内每个发言人一个会话”**
- `scope = admin:<permissionMode>` 或 `chat`
- 管理员和普通成员即使在同一群，也使用不同会话和不同权限域
- 固定 180 分钟窗口，从首次对话计时

这个设计对 `cc_qq` 很有启发：`cc_qq` 目前是“一个群一个会话”，所有角色共享上下文，只有权限档按发言者变化。理论上 guest 可能从共享上下文里推断 owner 之前说过/做过什么。是否构成安全问题，需要产品确认，但至少值得评估。

#### 安全与产品化

优点：

- 零第三方依赖
- 自研 OneBot v11 WS 客户端
- 无工具聊天内核 fail-closed
- 管理员/普通成员双轨
- 托盘、控制台、更新、Docker、记忆、人格、表情库、TTS、B站自动化

问题：

- 控制台普通管理 API **没有登录令牌**，只依赖回环地址
- 没有 DSH 审批转发到 QQ 的通道
- 管理员出站不转义 CQ 码
- 入站只解析 `text` / `at`，不解析引用、图片、语音
- 自动回复不带引用、不带 @
- 群成员事件、拍一拍、撤回全部忽略

#### 评价

产品化程度最高，适合借鉴“部署形态、托盘、更新、无工具内核、每用户会话隔离”。但它的安全细节不如 `dsh-qq`，不要整体照搬。

---

### 3.4 `dsh-qq-bridge`（Yuuyuko-uu，轻量双向桥）

#### 定位

让 DSH 里已有的 AI 会话和 QQ 双向互通。它**不创建会话**，只把 QQ 聊天绑定到已经活着的 DSH 会话。

#### 插件结构

- Host 半：`lib/host.js`，`main` 指向它
- Client 半：`lib/client.js`，注册 `settings.section`，标题「通到 QQ」
- 两半只通过 HTTP 通信：`/dsh-qq-bridge/state|save|test-send|update|asr-*`
- 依赖注入：`agents, sessions, sessionTitle, webServer, timer, workspaceRegistry, attachments, tools`

#### QQ 侧

- **只走 OneBot 11 HTTP**，不连 WebSocket
- 轮询 `get_friend_msg_history` / `get_group_msg_history`
- 默认轮询间隔 **2000ms**（README 写 4 秒，已滞后）
- 支持 `send_private_msg` / `send_group_msg`
- 后端可以是 SnowLuma 或 NapCat

#### DSH 侧

- 不创建会话，只 `ctx.agents.get(id)` 找活着的 Agent
- 入站：`agent.followup({ role: 'user', ... })`
- 出站：监听 `session/event`，只处理 `assistant/message` 与 `turn/end`
- 不注册 system prompt，把群署名、门槛提示写进 user 文案
- 只给开了回复门槛的群会话动态注册 `qq_reply_gate` 工具

#### 消息可靠性设计（很值得借鉴）

| 设计 | 作用 |
|---|---|
| 轮询水位 `上次时间` | 每个聊天独立记录已处理到哪 |
| 已转消息 Set | 消息 id 去重，超过 300 只保留最近 300 |
| 10 分钟过期 | 太旧的消息不补投 |
| 合并窗口 | 同一个人连续消息攒成一批，默认 1 秒，最多 20 秒 |
| singleflight | 轮询任务重叠时返回同一个 Promise |
| 超时 | 读历史 8s / 5s 超时 |

#### 富媒体

- 图片：URL / `file://` / `base64://` / 本地路径；落盘到 `~/.dsh/qq-bridge-inbox/`；单张 5MB，最多 4 张
- 语音：`get_record` → 下载/解码 → ffmpeg 转 16k 单声道 → 用户配置的转写命令
- 分享卡片：B 站卡片会抽 BV 号
- 合并转发：最多展开 2 层
- 出站：文字 + 图片；正文里的 markdown 图也会被抠出来发

#### 回复门槛

- 模型调用 `qq_reply_gate` 判断“这条是不是在跟我说话”
- `@` 或引用自己直接放行
- 默认只掐出站、不真停轮；开启 `门槛真停轮` 才 `agent.cancel`

这是“LLM 介入判断”的典型例子，比关键词硬编码更自然。

#### 局限

- 不创建会话、不做审批、不做模型切换
- 只发文字与图片，不发文件/语音/视频
- 没有审批转发，危险操作不受此插件约束

#### README 与代码差异

- 轮询间隔：README 4 秒，代码 2000ms
- 回复门槛：README 说“当场停轮”，默认只掐出站，需手动开
- 出站最多 4 张图是硬编码，设置页没写

#### 评价

最适合借鉴“消息可靠性 + 富媒体 + LLM 回复门槛”。它的“依附已有会话”思路也很适合 AstrBot 场景。

---

### 3.5 `dsh-qq-plugin`（xcisxc29，官方 QQ 机器人遥控器）

#### 定位

通过腾讯官方 QQ 机器人平台，把手机 QQ 变成 DSH 的远程控制器。扫码绑定，无需公网 IP、无反代。

#### 插件结构

- Host 半：`index.js`，`main`
- Client 半：`client.js`，注册 `settings.section`，标题「QQ」
- 依赖注入：`sessionController, sessions`，可选 `workspaceRegistry, webServer, permissionPresets, credentials`
- 事件：
  - `agent/assistant-stream`（全局）
  - `approval/request`（全局、prepend）
  - `user-questions/request`（全局、prepend）
- 工具：`qq_session_control`、`send_to_qq`、`notify_qq`
- 路由前缀：`/.dsh-qq-plugin`

#### QQ 侧

- 腾讯官方 SDK `@tencent-connect/qqbot-nodejs`
- WebSocket 网关 + RESUME
- 扫码绑定：`@tencent-connect/qqbot-connector` 的 `startQrConnect`
- AppSecret 存 DSH 凭据服务，状态文件只留 AppID
- **只做 1:1 私聊 `c2c`**，非 `c2c` 直接忽略
- 被动回复优先，超过限额降级为主动推送

#### 会话管理（最值得借鉴）

- `/new`、`/list`、`/list all`、`/switch <编号|短 id|标题>`、`/current`、`/cancel`
- 会话列表分“会话文件夹”和“会话”两级
- 编号跨屏连续，每屏 10 条
- 引用列表消息可以冻结编号
- 归档或磁盘消失的会话自动换绑并通知
- 会话索引直接读 `$DSH_HOME/sessions` 与 `storages/session_projcache/sessions`

#### 模型与审批

- `/model` 列出模型与推理等级
- `/model 2` 或 `/model 等级 high` 切换，下一步生效
- `approval/request`：发“🔐 需要你确认…回复允许或拒绝”
- `user-questions/request`：发带编号选项的问题，数字回复
- 只为绑定到 QQ 的会话认领审批/提问，未绑定委托桌面端

#### 主动推送

- `notify_qq`：任意会话可以主动给绑定对话发消息
- 发送失败进待发队列，下次用户说话先补发
- `send_to_qq`：发送文件/图片/视频
- 长回复超过 4000 字转为 `.md` 文件发送

#### 安全

- 默认权限预设 `danger-full-access`，**这是风险点**
- 没有插件级白名单，依赖“未认证机器人仅管理员可用”
- `allowCrossSessionNotify` 默认开启
- AppSecret 存凭据服务，这是好实践

#### README 与代码差异

- 按钮/交互消息/流式：未实现，README 自己标注
- 审批可回“数字选项”：审批只认允许/拒绝；数字选项属于提问
- 图片/文件/语音“交给 Agent”：实际是下载后以文本路径 + 描述交给 Agent，不是原生视觉输入
- “notify_qq 实测连发十条”：代码有队列，但实测无法验证

#### 评价

会话管理、审批/提问转发、主动推送、长回复转文件，是 `cc_qq` 最值得直接借鉴的一组能力。但它的默认权限太宽，且只支持私聊。

---

### 3.6 `dsh-dfy-qq`（beiheng127，QQ 对话行为层）

#### 定位

给 DSH 加一个 QQ 对话行为层：人设、认人、表情包、主动接话、子人格、群聊短期记忆。

#### 插件结构

- Host 半：`index.js`，注入 `tools, systemPrompt, webServer`
- Client 半：`client.js`，注册 `settings.section`，标题「肥鱼·QQ」
- 内置 OneBot 11 **反向 WebSocket 服务端**，默认 `ws://127.0.0.1:6700/onebot/v11/ws`
- 也支持 OneBot 11 HTTP 上报

#### 行为层能力

| 能力 | 实现 |
|---|---|
| 人设装载 | 读 md/txt 或直接文本，拼成 system prompt |
| 认人 | 群友档案注入 + `peopleSeen` 自动记录 + `dfy_people_upsert` |
| 子人格 | 扫 `personas/`，模型按语境挑 0–2 个，调 `dfy_persona_read` 读全文 |
| 群友子人格 | 攒群友原话，蒸馏成 `personas/群友/<昵称>-<账号>.md` |
| 表情包 | 扫目录、建索引、概率 + 大保底 + 最近没发过 + 用途匹配 |
| 主动接话 | `shouldSpeak()`：关键词 / 概率 / 冷却 / @ |
| 群聊记忆 | 每个会话保留最近 N 条 |
| 回复长度 | prompt 指令 + 通道切段 |

#### LLM 介入设计

- `personaAuto`：让模型按语境决定要不要切换子人格
- `dfy_persona_read`：模型需要全文时主动读
- `qq_reply_gate`（在 `dsh-qq-bridge` 里）：模型判断是否接话
- `JEV`（在 Fatwhale 里）：用模型判定群聊是否该接话

这比“关键词列表 + 概率硬编码”更符合 Agent 化方向，也符合“让 Agent 自己选择工具”的思路。

#### 风险与偏差

- 人设、记忆、表情包注入使用宿主级 `systemPrompt.context`，**没有按 QQ 会话过滤**，可能影响同一 DSH 里的所有会话（宿主是否按会话隔离未确认）
- 群聊记忆注入用全局 `lastChatKey`，多群时可能串记忆
- 群友子人格的原话采集**不受开关控制**，关着也在记
- 配置明文存 OneBot token
- `qqNapcatBat` 会被 `spawn` 执行，属于高权限面
- 没有审批/提问转发
- 没有会话切换

#### README 与代码差异

- `sessionId` 前缀：README 写 `dfyqq-`，实际 `onebot-`
- `.dfyqq/config.json` 覆盖顺序在 0.5.4 已改，README 前后矛盾
- “回复长度硬约束”只是 prompt 指令 + 切段，不是强制截断
- “主动接话给通道层 shouldSpeak”内置通道用自己的 `speakGate`，没有调用 service

#### 评价

如果 `cc_qq` 未来要做“群聊陪伴/人格化”，这是最好的行为层参考。但它的宿主级注入和记忆隔离问题必须避免。

---

## 4. 横向对比

### 4.1 能力矩阵

| 维度 | qq-bridge | dsh-qq | Fatwhale | dsh-qq-bridge | dsh-qq-plugin | dsh-dfy-qq | cc_qq |
|---|---|---|---|---|---|---|---|
| 形态 | 独立桥接 | 独立桥接 | 桌面应用 | DSH 插件 | DSH 插件 | DSH 插件 | AstrBot 插件 |
| QQ 协议 | OneBot WS | OneBot WS/接口平台 | OneBot WS | OneBot HTTP 轮询 | 官方 QQ Bot | OneBot 反向 WS | aiocqhttp |
| 群聊 | ✅ | ✅ | ✅ | ✅ | ❌ 仅私聊 | ✅ | ✅ |
| 会话创建 | ✅ | ✅ | ✅ | ❌ 依附已有 | ✅ | ✅ | ✅ |
| 多会话切换 | 控制台改映射 | 控制台 | ❌ | ❌ | ✅ `/new` `/list` `/switch` | ❌ | 部分 `/new` `/resume` |
| 审批转发 | ✅ | ✅ 编号 | ❌ | ❌ | ✅ | ❌ | ✅ |
| 结构化提问 | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| 主动推送 | 回合结束自动 | 回合结束自动 | 回合结束自动 | 回合结束自动 | ✅ `notify_qq` | 仅定时任务 | 仅审批卡片 |
| 图片入站 | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ 占位 | ❌ |
| 图片出站 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| 文件/语音 | 部分 | 部分 | TTS | 语音转写 | ✅ | ❌ | ❌ |
| 引用解析 | ✅ | ✅ | ❌ | 部分 | ✅ | ❌ | ❌ |
| 合并转发 | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| 人设/记忆 | 角色卡 | 人物库/记忆 | 记忆/人格 | ❌ | ❌ | ✅ | `/initbase` 模板 |
| 权限分级 | 模式 | L0–L3 | 双轨 | ❌ | 权限预设 | ❌ | guest/member/owner |
| 审计 | 部分 | 哈希链 | 部分 | ❌ | 日志 | ❌ | `permission_audit` |
| 控制台 | ✅ | ✅ + 控制中心 | ✅ + 托盘 | 设置页 | 设置页 | 设置页 | AstrBot 配置页 |
| 默认安全姿态 | 白名单 + 无工具群聊 | 高权限需确认 + TOTP | 普通成员无工具 | 总开关关、试运行开 | **默认完全访问** | 通道关、白名单空 | 分档 + 审批 |

### 4.2 README 与代码差异汇总

| 仓库 | README 宣传 | 代码事实 |
|---|---|---|
| `dsh-qq-bridge` | 每 4 秒轮询 | 默认 2000ms |
| `dsh-qq-bridge` | 门槛“当场停轮” | 默认只掐出站，需手动开 |
| `dsh-qq-bridge` | 合并转发 2 层 | 外层 + 2 层嵌套，口径需确认 |
| `dsh-qq-plugin` | 按钮/流式 | 未实现，README 自述 |
| `dsh-qq-plugin` | 审批可回数字选项 | 审批只认允许/拒绝 |
| `dsh-qq-plugin` | 图片/文件/语音交给 Agent | 实际是文本路径 + 描述，非原生视觉输入 |
| `dsh-qq-plugin` | notify 十条实测 | 代码有队列，实测无法验证 |
| `dsh-dfy-qq` | `dfyqq-` 前缀 | 实际 `onebot-` |
| `dsh-dfy-qq` | 子人格开关控制采集 | 原话采集不受开关控制 |
| `dsh-dfy-qq` | 每会话记忆 | 注入用全局 `lastChatKey`，可能串记忆 |
| `dsh-dfy-qq` | 回复长度硬约束 | 只是 prompt 指令 + 切段 |
| `dsh-qq` | 接口平台统一接入 | M1，未完整交付 |
| `dsh-qq` | L2/L3 审批闸门 | 需部署机实测 `probe:permission` |
| `qq-bridge` | 控制台令牌打印在日志 | 只打印前 6 位 |
| `Fatwhale` | 真实 QQ 投递已验证 | README 自己标注多项未完全验收 |

### 4.3 各仓库最值得学 / 最不该学

| 仓库 | 最值得学 | 最不该学 |
|---|---|---|
| `qq-bridge` | DSH Web API 鉴权、remote.mux、工具双重防线 | 体量过大、配置过多 |
| `dsh-qq` | L0–L3、确认码 + TOTP、编号审批、哈希链审计、切换不失忆 | 系统复杂、接口平台 M1、Beta 依赖 |
| `Fatwhale` | 无工具聊天内核、每用户会话隔离、托盘/更新/Docker | 控制台无鉴权、无审批转发、CQ 不转义 |
| `dsh-qq-bridge` | 水位/去重/合并/singleflight、富媒体、LLM 回复门槛 | 不建会话、不做审批、只发文字图片 |
| `dsh-qq-plugin` | 会话管理、审批/提问转发、notify 队列、长回复转文件 | 默认 `danger-full-access`、只支持私聊 |
| `dsh-dfy-qq` | 人设/认人/子人格/表情/主动接话的 LLM 化 | 宿主级 prompt 注入、记忆不隔离、明文 token |

---

## 5. 这几个 DSH 接入原理大致是什么

### 5.1 Web API 路线（`qq-bridge` / `dsh-qq`）

```
桥接进程
  ├─ 读取 ~/.dsh/.credentials.yaml
  │    └─ 用持久化签名密钥离线铸造会话 Cookie
  ├─ POST /api/<namespace>/<method>
  │    ├─ workspace.create
  │    ├─ sessions.create
  │    ├─ sessions.prompt({ mode: 'queue' })
  │    ├─ session.selectModel
  │    └─ commands/execute("/permission <name>")
  └─ GET /api/remote.mux
       ├─ $events
       ├─ session/follow
       ├─ session/event
       ├─ question/requested
       └─ approval/requested
```

关键点：

1. **鉴权不靠启动 token**：DSH 0.1.7 起启动 token 只在内存，桥接改用 `~/.dsh/.credentials.yaml` 的持久化签名密钥离线铸造 Cookie。
2. **事件流跨重连重放**：`_desiredFollows` 记住要 follow 的会话，断线重连后重新 follow。
3. **会话由桥接创建并映射**：每个 QQ 聊天一个 DSH 会话，映射持久化。
4. **审批/提问走事件流**：`approval/requested` 转发到 QQ，回执写回 `$events/result`。
5. **工具面靠 preset + guard**：群聊 preset 不挂本地工具，MCP 只暴露安全子集。

### 5.2 Cordis 插件路线（三个 DSH 插件）

```
插件 host 半
  ├─ 声明 inject：agents / sessions / sessionController / tools /
  │               systemPrompt / webServer / timer / workspaceRegistry
  ├─ 监听：
  │    ├─ session/event（assistant/message、turn/end）
  │    ├─ agent/assistant-stream
  │    ├─ approval/request
  │    ├─ user-questions/request
  │    └─ tools/pre-execute
  ├─ 调用：
  │    ├─ agent.followup(...)
  │    ├─ sessionController.prompt/cancel/create/selectModel
  │    ├─ tools.register(...)
  │    └─ systemPrompt.context(...)
  └─ 注册 HTTP 路由，供 client 半调用
```

关键点：

1. **插件活宿主内**，天然能拿到会话、流、审批、工具、提示词等能力。
2. **Host 半 + Client 半**：Host 半是 Node 侧逻辑，Client 半是设置页 UI，两半通过 HTTP 路由通信。
3. **`cordis.patch.yml` 负责挂载**，`package.json` 的 `dsh.bundle` / `dsh.client` 负责声明。
4. **审批/提问是全局 waterfall**：插件只认领自己绑定的会话，未绑定就 `next()` 委托给桌面端。
5. **工具可以动态注册**：`qq_reply_gate`、`send_to_qq`、`notify_qq`、`dfy_*` 都是这样暴露给 Agent 的。

### 5.3 CLI / 桌面宿主路线（`DSH-Fatwhale-QQ`）

```
桥接
  ├─ dsh --profile headless --patch ... --json [--session-id] <text>
  │    └─ 解析 NDJSON：session / text / final / error
  ├─ 或 @deepseek-ai/dsh-app-boot 加载 desktop profile
  │    └─ sessionController.create/prompt
  └─ 或 companion 插件（DSH Desktop 宿主内）
       └─ 本地 HTTP /health /prompt /cancel /attach
```

关键点：

1. **不碰 DSH Web API**，只把 `dsh` 当 CLI 用。
2. **headless 模式最通用**，但拿不到审批事件、流式 token、工具调用细节。
3. **desktop host / companion 模式能让会话出现在 DSH 桌面端**，体验更好，但依赖宿主 API。
4. **无工具内核**：普通成员单独起一个 DSH 内核，`tools.schemas()` 必须为空。

### 5.4 QQ 侧路线

| 路线 | 收消息 | 发消息 | 群聊 | 媒体 | 登录 |
|---|---|---|---|---|---|
| OneBot WS | 事件推送 | WS action | ✅ | ✅ | SnowLuma/NapCat 自己登录 |
| OneBot HTTP 轮询 | 定时拉历史 | HTTP action | ✅ | ✅ | 同上 |
| 官方 QQ Bot | WebSocket 网关 | 官方 SDK | ❌ 当前只 c2c | ✅ | 手机扫码创建机器人 |

---

## 6. 对 `cc_qq` 的借鉴清单

### 6.1 先明确 `cc_qq` 的定位与边界

`cc_qq` 当前形态：

- AstrBot Star 插件，Python 进程内运行
- 只处理 `aiocqhttp` 平台
- 每次回合启动 `claude` / `codex` CLI 子进程
- 自己管理 SQLite 会话、工作目录、权限档、审批 broker、审计表
- 已有能力：
  - guest 只读、member 工作区、owner/admin 完全权限
  - Claude：`dontAsk + --tools` / `acceptEdits + 沙箱 + PreToolUse hook` / `dontAsk + guard hook`
  - Codex：`ccqq-readonly` / `ccqq-workspace` / `danger-full-access`
  - 审批 broker + `/approve` `/deny` + `permission_audit`
  - `/new` `/resume` `/end` `/goon` `/cc` `/!` `/pwd` `/cd` `/initbase`
  - 私聊去重、过期消息、SQLite 消息回执

不可照搬：

- DSH 的 `sessionController`、`assistant-stream`、`approval/request`、`tools/pre-execute` 等宿主 API
- `cordis.patch.yml` 插件机制
- DSH 的 agent preset / permission preset 体系

必须保留：

- 三档权限 + hook + broker + 审计的 fail-closed 安全模型
- `bypassPermissions` 不使用的结论
- 工作区路径边界与危险命令识别

### 6.2 借鉴优先级总表

| 优先级 | 借鉴点 | 来源 | 对 `cc_qq` 的价值 | 难度 | 风险 |
|---|---|---|---|---|---|
| P0 | 语义化长文本分段 + 段间延迟 | `cc-ding`、`dsh-qq-bridge` | 现在 1500 字硬切，体验差 | 低 | 低 |
| P0 | 处理中 ACK / 回执 | `cc-ding` | 用户长时间无反馈 | 低 | 低 |
| P0 | 群聊 prompt 标注发送人 | `cc-ding` | 多人群聊 Agent 分不清谁说的 | 低 | 低 |
| P0 | 入站去重/水位增强 | `cc-ding`、`dsh-qq-bridge` | 现在只有私聊 10 秒正文去重 + 180 秒过期 | 低 | 低 |
| P0 | 审批编号 `#n` + 多挂起 + 超时 | `dsh-qq` | 现在审批号是 6 位 hex，多挂起体验弱 | 低-中 | 低 |
| P0 | `/list` `/switch` `/current` `/cancel` | `dsh-qq-plugin` | 现在只有 `/new` `/resume` `/end` | 中 | 低 |
| P1 | 有界消息队列 + `/mq` | `cc-ding` | 现在只有锁等待，无队列管理 | 中 | 低 |
| P1 | 错误分类与自动恢复 | `cc-ding` | 429 / 上下文超长 / 会话丢失 / 认证失效 | 中 | 中 |
| P1 | Watchdog 无活动检测 | `cc-ding` | 现在只有 1800 秒单行读取超时 | 中 | 中 |
| P1 | 引用消息解析 | `dsh-qq-bridge`、`dsh-qq` | 现在不解析引用 | 中 | 中 |
| P1 | 图片/文件入站 | `dsh-qq-bridge`、`cc-ding` | 现在非文本直接拒绝 | 中 | 中 |
| P1 | 主动推送 `notify` + 待发队列 | `dsh-qq-plugin` | 现在只用于审批卡片 | 中 | 中 |
| P1 | 长回复转 `.md` 文件 | `dsh-qq-plugin` | 避免截断 | 中 | 需确认 AstrBot 文件发送能力 |
| P1 | 管理员提权确认码 + TOTP + 自动回落 | `dsh-qq` | 现在只有静态角色，无提权流程 | 中-高 | 中 |
| P1 | 群内每用户会话隔离 | `DSH-Fatwhale-QQ` | 现在群内共享上下文，guest 可能看到 owner 历史 | 中-高 | 需产品确认 |
| P2 | 人格/认人/子人格/表情包/主动接话 | `dsh-dfy-qq` | 若要做群聊陪伴 | 高 | 高（需隔离） |
| P2 | 定时任务/定时静默 | `dsh-qq`、`Fatwhale` | 省 token、定时提醒 | 中-高 | 中 |
| P2 | 控制台/Token 账本/托盘/更新 | `qq-bridge`、`Fatwhale` | 产品化 | 高 | 低 |
| P2 | 接口平台（多 QQ 后端抽象） | `dsh-qq` | 同时接 SnowLuma/NapCat | 高 | 中 |

### 6.3 P0：低难度、高收益、先做

#### 1. 语义化分段

现状：`cc_qq/platform/replies.py` 按 1500 字符硬切，可能把一句话/代码块切断。

建议：

- 优先按换行、句号、问号、感叹号、空格切
- 多段带 `[i/n]` 头（可选）
- 段间 300–500ms 延迟
- 代码块尽量不拆，超长再硬切

参考：`cc-ding/src/biz/messaging.ts:250-279`、`:371-424`；`dsh-qq-bridge/lib/host.js` 的“长回复按空行拆段 + 450ms 间隔”。

#### 2. 处理中 ACK

现状：用户发消息后，Agent 跑几十秒，QQ 里没有任何反馈。

建议：

- 收到消息后立即回一句“收到，处理中…”（可配置开关）
- 或使用 QQ 表情回执（需确认 AstrBot/OneBot 支持）
- 长任务完成后再发结果

参考：`cc-ding` 的 ACK 机制。

#### 3. 群聊 prompt 标注发送人

现状：`cc_qq` 群聊 prompt 不包含发送者信息，Agent 不知道是谁在说话。

建议：

- prompt 末尾追加 `消息来自: 昵称(QQ号)`
- 引用消息追加 `引用 <昵称>: <原文>`
- 群名片与 QQ 号不一致时，以 QQ 号为主键

参考：`cc-ding/src/biz/claude-process.ts:935-945`；`dsh-qq-bridge` 的群署名。

#### 4. 入站去重/水位增强

现状：

- 私聊同正文 10 秒去重
- 180 秒过期
- SQLite 主键 `(platform_id, message_id)`

建议：

- 增加“会话水位”：记录每个会话已处理的最大消息时间/ID，防止乱序旧消息
- 增加“处理中/排队中”状态水位，防止同一消息在重启/重放时重复进入
- 群聊也加入去重，不只私聊

参考：`cc-ding/src/biz/dedup.ts:152-275`；`dsh-qq-bridge/lib/host.js` 的 `上次时间` + `已转消息`。

#### 5. 审批编号 `#n` + 多挂起 + 超时

现状：

- 审批号是 6 位 hex
- 同一会话/发送者/工具/摘要的并发请求复用同一 future
- 没有全局编号、没有“多个挂起时要求带编号”

建议：

- 全局自增编号 `#1`、`#2`，跨重启不复用（持久化）
- 审批卡片展示：工具名、真实命令参数（脱敏、截断）、发起会话、过期时间
- 多个挂起时，裸回复“通过/拒绝”要求带编号
- 超时自动拒绝并通知
- 审批结果写入审计表

参考：`dsh-qq/src/admin/approvals.js`、`src/bridge.js:13185-13200`。

#### 6. `/list` `/switch` `/current` `/cancel`

现状：只有 `/new` `/resume` `/end` `/goon`，没有会话列表和切换。

建议：

- `/list`：列出当前会话的最近 N 个历史会话（编号、标题、时间、状态）
- `/switch <编号|会话ID>`：切换当前会话
- `/current`：显示当前会话
- `/cancel`：取消当前回合（如果 CLI 支持中断）
- 列表编号跨屏连续，引用列表消息可冻结编号（进阶）

参考：`dsh-qq-plugin/lib/router.js:351-518`、`:1308-1362`。

### 6.4 P1：中等难度、明显提升

#### 7. 有界消息队列 + `/mq`

现状：每会话 `asyncio.Lock` 串行，没有队列容量、过期、查看、删除。

建议：

- 每会话有界队列（例如 20 条）
- 入队消息 10 分钟过期
- `/mq` 查看/删除/置顶
- 重启后从 SQLite 恢复 queued 消息（已有基础）

参考：`cc-ding/src/biz/session.ts:997-1095`。

#### 8. 错误分类与自动恢复

现状：统一 `AgentProcessError`，没有重试/compact/reset。

建议：

- 429/TPM 限流：退避重试，发送“继续”
- 上下文超长：自动 `/compact` 后继续
- “conversation not found”：清除会话 ID 后重开
- 401 认证失败：通知用户
- Codex 认证失效：触发 `codex login --device-auth`，把 URL/一次性代码发到 QQ

参考：`cc-ding/src/biz/claude-process.ts:96-173`、`:1100-1354`；`src/biz/codex-agent.ts:333-408`。

#### 9. Watchdog 无活动检测

现状：只有 1800 秒单行读取超时。

建议：

- 无活动 N 分钟（可配置，默认 5）→ kill 子进程 + 通知 + 允许 `/goon` 恢复
- 最多自动恢复 2 次，避免死循环

参考：`cc-ding/src/biz/watchdog.ts:22-110`。

#### 10. 引用消息解析

现状：不解析 `reply` 段。

建议：

- 入站解析被引用消息的发送者与原文
- 注入 prompt：`[引用 昵称：原文] 回复内容`
- 引用机器人自己时视为必回（如果做群聊主动回复）
- 需要确认 AstrBot `aiocqhttp` 的引用字段形态

参考：`dsh-qq-bridge/lib/host.js:1880-1943`、`dsh-qq/src/bridge.js` 的引用解析。

#### 11. 图片/文件入站

现状：非 `Plain/At` 段直接提示“暂不支持文本以外消息”。

建议：

- 图片：下载到工作目录，注入本地路径 + 尺寸/格式
- 文件：下载到工作目录，注入路径 + 文件名
- OCR/语音转写可选
- 需要确认 AstrBot 的图片/文件下载 API 与 OneBot 段格式

参考：`dsh-qq-bridge/lib/host.js:1503-1571`、`:452-486`；`cc-ding/src/biz/image.ts`。

#### 12. 主动推送 `notify` + 待发队列

现状：主动消息只用于审批卡片。

建议：

- 增加 `notify` 工具/命令，允许 Agent 或定时任务主动发消息
- 发送失败入队，下次用户说话先补发
- 需要确认 AstrBot 主动消息 API 与 QQ 平台限制

参考：`dsh-qq-plugin/lib/send-tools.js:89-126`、`lib/pending.js:32-136`。

#### 13. 长回复转 `.md` 文件

现状：1500 字硬切。

建议：

- 超过阈值（例如 4000 字）先发摘要，再把全文写成 `.md` 文件发送
- 需要确认 AstrBot 文件发送能力

参考：`dsh-qq-plugin/lib/reply-limit.js:25-48`。

#### 14. 管理员提权确认码 + TOTP + 自动回落

现状：owner/admin 是静态配置，没有“临时提权”流程。

建议：

- owner 私聊 `/mode agent L1|L2|L3` → 确认码 →（L3 再加 TOTP）→ 切换
- 高权限闲置 30 分钟或达到时限自动回落
- 重启不继承高权限
- `/panic` 一键回落到 guest/只读
- 每次变更写审计并通知 owner

参考：`dsh-qq/src/admin/mode-control.js`、`src/admin/totp.js`、`docs/guides/ADMIN_CHANNEL.md`。

注意：`cc_qq` 已经有角色档，提权流程不是“从零做权限”，而是“给高权限加临时性和二次确认”。

#### 15. 群内每用户会话隔离

现状：一个群一个会话，所有角色共享上下文，只有权限档按发言者变化。

风险：guest 可能从共享上下文里推断 owner 之前说过/做过什么；不同成员的对话会互相污染。

建议（二选一）：

- **方案 A（强隔离）**：群内每个发言人一个 Agent 会话，key 类似 `group:<群号>:user:<QQ>`；群级共享记忆单独存，注入时过滤
- **方案 B（弱隔离）**：仍用一个会话，但每轮按角色过滤历史上下文；guest 只看到群级公共内容，不看 owner 私聊/高权限操作

参考：`DSH-Fatwhale-QQ/src/computer-access.js:31-37` 的 `g:<群号>:u:<QQ>:<scope>`。

需要产品确认：`cc_qq` 是“群共享助理”还是“每人一个助理”。这会影响产品形态，不能暗猜。

### 6.5 P2：行为层与产品化

#### 16. 人格/认人/子人格/表情包/主动接话

如果 `cc_qq` 未来要做“群聊陪伴/人格化”，可参考 `dsh-dfy-qq`：

- 人设文件 → system prompt
- 群友档案 → 按 QQ 号认人
- 子人格 → 模型按语境挑，调工具读全文
- 表情包 → 概率 + 大保底 + 最近没发过 + 用途匹配
- 主动接话 → LLM 判断，而不是关键词硬编码
- 群聊记忆 → 最近 N 条

但必须避免它的两个坑：

- 不要用宿主级全局 prompt 注入，要按 QQ 会话隔离
- 不要让记忆跨群串线

#### 17. 定时任务 / 定时静默

参考 `dsh-qq`：

- 定时任务：一次/每天/每周/工作日/每月/随机/cron
- 定时静默：按时间段停止唤醒省 token，消息照记，结束后补唤醒
- AI 只能登记任务，发群需要 owner 确认

#### 18. 控制台 / Token 账本 / 托盘 / 更新

参考 `qq-bridge` 与 `Fatwhale`：

- Web 控制台：状态、日志、会话、审批、人格、Token 花费
- Token 账本：按群/好友/轮次统计，峰谷价折算
- 托盘/后台服务/Docker/自动更新

这些是产品化能力，优先级低于消息体验和会话管理。

#### 19. 多 QQ 后端抽象

参考 `dsh-qq/interface-platform`：

- 统一 SnowLuma / NapCat
- 预留微信/Discord/KOOK
- 数据令牌与管理令牌分离

对 `cc_qq` 来说，AstrBot 已经抽象了平台，短期不需要自建接口平台。

### 6.6 明确不建议借鉴

| 反模式 | 来源 | 原因 |
|---|---|---|
| 默认 `bypassPermissions` | `cc-ding` | 实测不执行 deny 规则，等于没有边界 |
| 默认 `danger-full-access` | `dsh-qq-plugin` | 审批默认 `never`，高权限直接执行 |
| `/bash` 直接执行宿主机命令 | `cc-ding` | 绕过 Agent 工具面与审批 |
| `freedomMode` 跳过白名单 | `cc-ding` | 破坏准入边界 |
| 控制台无鉴权 | `Fatwhale` | 本机任意进程可调管理 API |
| 明文存 token/凭据 | `dsh-qq-bridge`、`dsh-dfy-qq` | 应走凭据服务或至少文件权限 0600 |
| 宿主级全局 prompt 注入 | `dsh-dfy-qq` | 会污染所有会话 |
| 无入站去重 | `dsh-dfy-qq` | 重复消息会重复回复 |
| 不转义 CQ 码 | `Fatwhale` | 模型输出可能被解释成 CQ 码 |

---

## 7. LLM 介入与“让 Agent 自己选工具”的具体建议

用户此前明确过两个方向：

1. 多考虑 LLM 介入或辅助判断，不要什么都硬编码。
2. 把工具列表给 Agent，让 Agent 自己选择调用，类似 Codex 把 skills 元数据给模型。

结合本次调研，可以落成下面几条：

### 7.1 用 LLM 做“要不要接话”的判断

参考：

- `dsh-qq-bridge` 的 `qq_reply_gate` 工具：模型判断这条消息是否在跟自己说话。
- `Fatwhale` 的 JEV：群聊未 @ 时，用模型判定是否接话。
- `dsh-dfy-qq` 的 `shouldSpeak()`：关键词/概率/冷却，作为降级方案。

`cc_qq` 现在的群聊规则是“未 @ 当前机器人直接静默”，这是硬编码。可以改成：

- 默认仍只响应 @，避免噪音和成本
- 可选开启“LLM 判断是否接话”模式：群消息先进入一个轻量判断（用便宜模型或主模型），判断为“在跟我说话/值得接”才启动 Agent
- 判断结果与理由写入日志，便于调参
- 保留 `@` / 引用自己 / 关键词作为快速放行路径

### 7.2 用 LLM 做人格/子人格选择

参考 `dsh-dfy-qq`：

- `personaAuto`：模型按语境判断要不要切换子人格
- `dfy_persona_read`：模型需要全文时主动读
- `dfy_persona_list` / `dfy_persona_show`：把人格清单作为工具暴露

`cc_qq` 如果要做群聊人格，建议：

- 只把人格摘要注入 system prompt
- 全文通过工具按需读取
- 不要把所有子人格全文塞进 prompt

### 7.3 把 QQ 操作暴露成工具，让 Agent 自己决定

参考 `dsh-qq-plugin`：

- `send_to_qq`：发文件/图片/视频
- `notify_qq`：主动推送
- `qq_session_control`：新建/切换/列出会话

参考 `dsh-dfy-qq`：

- `dfy_people_upsert`：写群友档案
- `dfy_emoji_draw`：抽表情包
- `dfy_persona_read` / `dfy_persona_list`：读人格

对 `cc_qq` 的落地方式：

- 如果继续用 Claude Code / Codex CLI，可以通过 **MCP server** 或 **skill/工具清单** 把这些能力暴露给 Agent。
- 不要把“切会话”“发通知”“抽表情”全部做成聊天命令硬路由；聊天命令只保留确定性操作（`/approve`、`/deny`、`/cd`、`/panic`），其余交给 Agent 判断。
- **硬边界仍由确定性代码执行**：权限、路径、危险命令、审批，不能交给模型。

一句话：**LLM 负责“想做什么”，确定性代码负责“能不能做”。**

### 7.4 用 LLM 做意图识别而不是关键词表

可借鉴的模式：

- 入站消息先分类：`chat` / `command` / `approval` / `question` / `ignore`
- 分类结果决定走哪条链路
- 分类失败或低置信度时，走安全默认（例如只回 @、不主动接话）
- 分类器与主 Agent 分离，避免主 Agent 被群聊噪音干扰

这比维护一长串关键词/正则更可扩展，也符合“不要硬编码”的要求。但要有成本控制：只在群聊未 @、且开关开启时才调用。

---

## 8. 建议的落地路线（候选，不是已批准 Plan）

> 以下是调研后的候选路线，用于后续 Align/Plan 讨论。未经用户确认，不进入实现。

### Phase A：消息体验与会话管理（P0）

1. 语义化分段 + 段间延迟
2. 处理中 ACK
3. 群聊 prompt 标注发送人
4. 入站去重/水位增强
5. 审批编号 `#n` + 多挂起 + 超时
6. `/list` `/switch` `/current` `/cancel`

验收标准：

- 长回复不再从句子/代码块中间硬切
- 用户发消息后 1 秒内看到“处理中”反馈
- 群聊 Agent 能正确识别发送者
- 重复/乱序消息不重复触发
- 多个审批并存时，回复带编号能准确命中
- 会话列表与切换可用

### Phase B：可靠性与富媒体（P1）

1. 有界消息队列 + `/mq`
2. 错误分类与自动恢复
3. Watchdog 无活动检测
4. 引用消息解析
5. 图片/文件入站
6. 主动推送 `notify` + 待发队列
7. 长回复转 `.md`
8. 管理员提权确认码 + TOTP + 自动回落
9. 群内会话隔离方案（需产品确认）

验收标准：

- 限流/上下文超长/会话丢失能自动恢复或给出明确提示
- 卡死的 CLI 能被 watchdog 终止并恢复
- 引用消息能带上下文
- 图片/文件能被 Agent 读取
- Agent 能主动推送且失败可补发
- 高权限有临时性、可回落、可审计
- 群内不同角色上下文隔离符合产品预期

### Phase C：行为层与产品化（P2）

1. 人格/认人/子人格/表情包/主动接话
2. 定时任务/定时静默
3. 控制台/Token 账本/托盘/更新
4. 多 QQ 后端抽象（如需要）

验收标准：

- 人格与记忆按会话隔离，不污染其他会话
- 主动接话由 LLM 判断，有成本控制
- 定时任务/静默可配置、可审计
- 控制台有鉴权，Token 统计准确

### 不建议进入路线

- `bypassPermissions`
- `/bash`
- `freedomMode`
- 默认 `danger-full-access`
- 无鉴权控制台
- 明文凭据

---

## 9. 需要确认的问题与未确认项

### 9.1 产品决策

1. `cc_qq` 的群聊定位：**群共享助理** 还是 **每人一个助理**？
   - 这决定是否要做群内会话隔离。
2. 是否需要“主动接话/群聊陪伴”能力？
   - 如果只是远程遥控编码助手，行为层优先级可以降低。
3. 是否允许 Agent 主动发 QQ 消息（`notify`）？
   - 需要评估打扰与平台限制。
4. 是否需要多模型/多 Agent 切换（`/model`）？
5. 高权限是否需要 TOTP/确认码，还是保持静态 owner/admin？

### 9.2 技术未确认

1. AstrBot `aiocqhttp` 是否支持：
   - 主动消息
   - 引用回复
   - 图片/文件发送与下载
   - 消息撤回
   - 表情回执
   - 流式/AI Card
2. AstrBot 的 `message_obj.self_id`、`At.qq`、`raw_message.time` 在不同适配器版本中是否始终存在。
3. Claude Code `dontAsk + PreToolUse hook` 的行为，依赖此前 2.1.202 实测；升级后需回归。
4. Codex 权限档案语法（`default_permissions`、`:workspace_roots`、`:tmpdir`）依赖 `codex-cli 0.162.1`；升级后需回归。
5. `cc_qq` 的 SQLite 同步访问在高并发下对 AstrBot 事件循环的影响，未做基准测试。
6. `permission_audit` 只记录审批事件，不是完整工具调用审计；是否满足未来审计需求需产品确认。
7. 群内共享上下文的安全影响，未做正式评估。
8. 外部 6 个仓库的 README 声明均未在本地真实 DSH/QQ 环境复测。

### 9.3 外部仓库未确认项

- `dsh-qq` 的 L2/L3 审批闸门在真实 DSH 上是否每次触发、是否正确回执。
- `dsh-qq` 的 macOS + NapCat 真实链路。
- `dsh-qq-plugin` 的 `workspaceRegistry.archivedSessionIds` 在 QQ 宿主上是否可用。
- `dsh-qq-plugin` 的“扫码当场创建机器人”与“notify 十条实测”。
- `dsh-dfy-qq` 的 `systemPrompt.context` 是否对所有 DSH 会话生效。
- `dsh-dfy-qq` 的 `onebot-` 前缀是否能接上旧会话。
- `dsh-qq-bridge` 的 `agent.cancel` 在所有 DSH 版本是否可用。
- `SnowLuma` 是否完整实现 `get_friend_msg_history` / `get_group_msg_history` / `get_forward_msg` / `get_record`。
- `Fatwhale` 的 `read-only` / `workspace-write` 下 DSH `ask` 审批的实际行为。
- `Fatwhale` 与 `qq-bridge` 是否存在代码血缘（无 NOTICE，代码结构差异大）。

---

## 10. 附录

### 10.1 克隆命令（复现用）

```bash
cd zzz-prompt-debug/调研bridge
mkdir -p dsh-qq-plugins
cd dsh-qq-plugins
git clone --depth 1 https://github.com/Derpyu520/qq-bridge.git qq-bridge
git clone --depth 1 https://github.com/Yuuyuko-uu/dsh-qq-bridge.git dsh-qq-bridge
git clone --depth 1 https://github.com/h-D-ACE/dsh-qq.git dsh-qq
git clone --depth 1 https://github.com/xcisxc29/dsh-qq-plugin.git dsh-qq-plugin
git clone --depth 1 https://github.com/beiheng127/dsh-dfy-qq.git dsh-dfy-qq
git clone --depth 1 https://github.com/miku05231/DSH-Fatwhale-QQ.git DSH-Fatwhale-QQ
```

`.gitignore` 已加入：

```gitignore
# ===== 调研用外部仓库（不提交） =====
zzz-prompt-debug/调研bridge/dsh-qq-plugins/
```

### 10.2 关键源码索引

| 主题 | 仓库 | 路径 |
|---|---|---|
| DSH Cookie 鉴权 | `qq-bridge` | `src/dsh-client.js:97-145` |
| remote.mux 事件流 | `qq-bridge` | `src/dsh-client.js:667-760` |
| 会话映射 | `qq-bridge` | `src/bridge.js:1219-1223`、`:1369-1383` |
| 工具双重防线 | `qq-bridge` | `plugins/qq-agent-presets/qq-tool-restrict.mjs:265-330` |
| L0–L3 权限 | `dsh-qq` | `src/admin/dsh-permission.js:1-110` |
| 审批闸门 | `dsh-qq` | `plugins/qq-agent-presets/qq-approval-gate.mjs:1-80` |
| 编号审批 | `dsh-qq` | `src/admin/approvals.js` |
| 管理通道 | `dsh-qq` | `src/admin/mode-control.js`、`src/admin/totp.js` |
| 无工具聊天内核 | `Fatwhale` | `src/chat-only.js:110-145`、`src/chat-only-host.js:90-112` |
| 每用户会话 key | `Fatwhale` | `src/computer-access.js:31-37` |
| 轮询/去重/合并 | `dsh-qq-bridge` | `lib/host.js:626-657`、`:1945-2071` |
| 回复门槛 | `dsh-qq-bridge` | `lib/host.js:1649-1742` |
| 会话路由 | `dsh-qq-plugin` | `lib/router.js:351-518`、`:1308-1362` |
| 审批/提问转发 | `dsh-qq-plugin` | `lib/runtime.js:2173-2231` |
| 主动推送 | `dsh-qq-plugin` | `lib/send-tools.js:89-126`、`lib/pending.js:32-136` |
| 行为层 prompt | `dsh-dfy-qq` | `index.js:640-775` |
| 群友子人格 | `dsh-dfy-qq` | `index.js:504-643` |
| cc_qq 权限 | `cc_qq` | `permissions.py:44-173` |
| cc_qq 审批 | `cc_qq` | `approval.py:107-233` |
| cc_qq CLI 参数 | `cc_qq` | `agents/profiles.py:27-241` |
| cc_qq 回复分段 | `cc_qq` | `platform/replies.py:11-31` |
| cc_qq 事件解析 | `cc_qq` | `platform/qq_events.py:81-118` |
| cc-ding 分段 | `cc-ding` | `src/biz/messaging.ts:250-279` |
| cc-ding 去重 | `cc-ding` | `src/biz/dedup.ts:10-275` |
| cc-ding Watchdog | `cc-ding` | `src/biz/watchdog.ts:22-110` |
| cc-ding 引用 | `cc-ding` | `src/biz/quote.ts:75-343` |

### 10.3 术语表（中英双语）

| 中文 | English | 说明 |
|---|---|---|
| 深度求索 Agent 宿主 | DeepSeek Harness（DSH） | 本地 Agent 运行时 |
| OneBot 11 | OneBot v11 | QQ 机器人协议标准 |
| 权限预设 | Permission Preset | 沙箱模式 + 审批策略 |
| 代理预设 | Agent Preset | Agent 的工具面/人格/权限组合 |
| 事件流 | Event Stream | DSH `remote.mux` / `session/follow` |
| 工具守卫 | Tool Guard | 执行期拒绝工具调用 |
| 工具限制 | Tool Restrict | 注册期隐藏工具 |
| 审批闸门 | Approval Gate | 在工具执行前主动要求审批 |
| 回复门槛 | Reply Gate | 判断是否接话 |
| 无工具内核 | Chat-only Kernel | 普通成员使用的零工具 Agent |
| 会话水位 | Session Watermark | 记录已处理到哪，防重复/乱序 |
| 单飞 | Singleflight | 并发请求合并为同一个执行 |
| 哈希链审计 | Hash-chain Audit | 每条审计记录带前一条哈希 |
| 子人格 | Sub-persona | 可切换的语气/风格人格 |
| 群友档案 | People Profile | 按 QQ 号记录群成员信息 |

---

## 11. 文档结论

1. 这 6 个仓库的“接入原理”可以归为三类：DSH Web API 适配、DSH Cordis 宿主插件、CLI/桌面宿主适配；QQ 侧则是 OneBot 11 与腾讯官方机器人两条路线。
2. 对 `cc_qq` 最有价值的不是某一项酷炫功能，而是三类设计：
   - **权限/审批的确定性闸门**（`dsh-qq`）
   - **会话与消息的可靠性**（`dsh-qq-plugin`、`dsh-qq-bridge`、`cc-ding`）
   - **LLM 化的行为判断与工具暴露**（`dsh-dfy-qq`、`dsh-qq-plugin`）
3. `cc_qq` 的安全模型已经强于多数外部插件，后续迭代应保持“LLM 决定意图、确定性代码守住边界”的分工，不要为了功能牺牲权限边界。
4. 下一阶段建议先做 P0（分段、ACK、发送人标注、去重、审批编号、会话列表/切换），再根据产品定位决定是否进入 P1/P2。
5. 本文只是调研结论，不代替 Align、Plan 或任何已批准方案；进入实现前仍需按仓库规范完成讨论与计划。
