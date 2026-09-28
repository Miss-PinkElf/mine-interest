# cc-ding 完整迁移 AstrBot 插件实施计划（Implementation Plan）

> **面向执行者（For agentic workers）：**进入实施（Apply）前，必须先完成本 mission 的开放规格（OpenSpec）提案、设计与任务；执行任务时使用 `openspec-apply-change`，按需要使用 `superpowers-subagent-driven-development` 或 `executing-plans`。所有提交（Commit）须先取得用户明确允许，提交信息使用中文。

**目标（Goal）：**把 `cc-ding` 的 Claude Code、Codex 及通用功能迁移为由 AstrBot 管理的插件，在 QQ 群聊和私聊中提供可验证的工作目录与工具权限。

**架构（Architecture）：**AstrBot 插件归一化平台消息并管理本地 Node 核心进程；核心复用并拆分 `cc-ding` 的会话、任务、代理与管理能力，通过标准输入／输出协议（stdio IPC）与插件通信。每次代理执行由统一权限决策与隔离运行器约束，群共享会话但不共享上一次请求的权限。

**技术栈（Tech Stack）：**AstrBot 插件 Python、TypeScript／Node.js 24、Claude Code CLI、Codex CLI、AstrBot 插件页面（Plugin Page）、Windows／macOS 原生权限能力、Python `unittest` 与 Node 测试。

---

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 22:23:59 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：给出从隔离验证到功能迁移、平台联调和收尾的实施顺序、文件职责与验收门禁。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 对齐文档（Aligned Requirement）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding迁移astrbot需求对齐.md`
- 参考实现（Reference Implementation）：`cc-ding/`
- 当前状态（Status）：待隔离方案修订（Revision Required）
- 文档边界（Scope / Boundary）：本 mission 的计划真相源（source of truth）；规定顺序与验收，不代替开放规格（OpenSpec）任务，也不单独授权实施（Apply）。

## 实施前门禁

> 2026-09-29 T02 实测回退：Codex CLI 0.158.0 在原生 Windows 的内置 `:read-only` 可读取工作目录外文件；自定义 `:root = deny` 在普通和 elevated 沙箱均无法启动。当前隔离方案不满足第 3 条门禁。下次须先修订方案并获得可复现验证证据，T03 及后续插件代码任务仍未开始；完整记录见 `spec/permission-matrix.md`。

1. 已完成需求对齐（Align），用户明确要求对齐文档落盘后直接写本计划。
2. 本计划完成后，依次生成 `.devflow/astrbot-claude-bridge/spec/proposal.md`、`design.md`、`tasks.md`，逐任务关联本计划阶段；三件套齐备且一致后才能修改插件代码。
3. 权限可行性验证是最早的实施任务。按 Windows／macOS、Claude Code／Codex、只读／读写和工具组合建立能力矩阵。只有实测满足“只能读取指定目录、只读不能写、读写只能在指定目录写”的组合才可启用；未验证组合默认禁用并回退设计，不以提示词、单独的 `plan` 模式或 `danger-full-access` 代替。插件本体不得依赖 WSL／Ubuntu。
4. `cc-ding/` 当前在 `.gitignore` 中，视为只读参考。迁移产物必须进入仓库内可追踪的插件目录，保留 MIT 许可与必要版权声明。

## 文件结构与职责

下列是目标文件位置；开放规格（OpenSpec）可在不改变职责边界的前提下细化名称。不得把迁移代码重新合并成一个大型 `main.py` 或 `cc-ding-cli.ts`。

| 目标文件 | 单一职责 | 来源或依据 |
| --- | --- | --- |
| `integrations/astrbot/astrbot_plugin_cc_bridge/main.py` | AstrBot 生命周期、消息入口、命令注册 | 现有 AstrBot 插件模式 |
| `integrations/astrbot/astrbot_plugin_cc_bridge/bridge/events.py` | 平台消息封套与 QQ 身份映射 | `cc-ding/src/biz/cc-ding-cli.ts` 接收入口 |
| `integrations/astrbot/astrbot_plugin_cc_bridge/bridge/process.py` | Node 子进程和标准输入／输出协议（stdio IPC） | 新增边界 |
| `integrations/astrbot/astrbot_plugin_cc_bridge/bridge/replies.py` | 文本、图片、文件、引用、提及与状态回复 | `cc-ding/src/biz/messaging.ts` 的平台无关语义 |
| `integrations/astrbot/astrbot_plugin_cc_bridge/bridge/web.py` | 插件页面后端接口及管理员鉴权 | `cc-ding/src/biz/console.ts` |
| `integrations/astrbot/astrbot_plugin_cc_bridge/_conf_schema.json` | 群目录、白名单、私聊、工具、代理和后台配置 | AstrBot 插件配置 |
| `integrations/astrbot/astrbot_plugin_cc_bridge/metadata.yaml` | 插件元信息和可感知版本号 | AstrBot 插件规范 |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/src/contracts.ts` | 平台无关消息、身份、权限、请求与回复类型 | `cc-ding/src/biz/types.ts` 抽取 |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/src/transport/stdio.ts` | 带请求编号的进程通信与错误协议 | 新增边界 |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/src/policy/evaluate.ts` | 用户、群、私聊和工具权限求交与审计决策 | `cc-ding/src/biz/session.ts` 鉴权重构 |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/src/runtime/isolation.ts` | 按代理与宿主平台选择经验证的权限配置，拒绝未验证工具组合 | 新增安全边界 |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/src/agents/claude.ts` | Claude Code 命令、事件、恢复与能力映射 | `cc-ding/src/biz/claude-agent.ts`、`claude-process.ts` |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/src/agents/codex.ts` | Codex 命令、JSON 事件、恢复与能力映射 | `cc-ding/src/biz/codex-agent.ts` |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/src/core/session.ts` | 群共享与私聊独立会话、恢复和持久化 | `cc-ding/src/biz/session.ts` |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/src/core/queue.ts` | 排队、去重、中断、出队重验权限 | `cc-ding/src/biz/session.ts`、`dedup.ts` |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/src/features/tasks.ts` | 任务队列与重试 | `cc-ding/src/biz/task.ts`、`task-runner.ts` |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/src/features/scheduler.ts` | Cron、Timer 和权限续验 | `cc-ding/src/biz/cron.ts`、`timer.ts` |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/src/features/collaboration.ts` | 待办、菜单、模型、日志及命令路由 | `cc-ding/src/biz/todo.ts`、`menu.ts`、`model.ts`、`commands.ts` |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/src/a2a/` | A2A 协议、目标群路由和来源授权 | `cc-ding/src/biz/a2a/` |
| `integrations/astrbot/astrbot_plugin_cc_bridge/pages/console/` | AstrBot 插件页面中的状态和配置管理 | `cc-ding/src/biz/console.ts` 功能映射 |
| `integrations/astrbot/astrbot_plugin_cc_bridge/runner/LICENSE.cc-ding` | 上游 MIT 许可与版权声明 | `cc-ding/LICENSE` |
| `tests/astrbot_cc_bridge/`、`integrations/astrbot/astrbot_plugin_cc_bridge/runner/test/` | Python 适配与 TypeScript 核心验证 | 新增测试 |

## 阶段 1：盘点与隔离可行性

**目标：**先建立逐功能迁移清单和真实隔离证据，避免后续大规模迁移建立在错误权限假设上。

- [ ] 列出 `cc-ding/src/biz/commands.ts` 每个命令、`types.ts` 每个配置字段、Console 页面能力及 A2A 入口，逐项标记“保留通用语义／改用 AstrBot 等价能力／钉钉专属取消”，写入 `.devflow/astrbot-claude-bridge/spec/feature-mapping.md`；每项有验收方式。
- [ ] 对 `cc-ding/src/biz/cc-ding-cli.ts`、`session.ts`、`messaging.ts`、`claude-process.ts`、`codex-agent.ts` 画依赖边界，确认需抽出的业务接口和平台字段。
- [ ] 在规格任务中定义最小隔离验证样本：群目录内读取；目录外读取；目录内写入；只读写入；符号链接／联接目录逃逸；Shell、Skills、MCP、Hooks 的文件访问；代理恢复后权限降级。
- [ ] 先在本机原生 Windows 验证两种 CLI 的权限能力；macOS 作为正式目标平台建立独立验收矩阵，不能把 Windows 结果直接视为 macOS 已通过。Claude Code 的 `plan`／`dontAsk`、目录外读取限制和工具允许集需组合验证；Codex 的原生 Windows 沙箱与自定义权限配置需验证。
- [ ] 以自动化证据证明**拟开放的工具组合**中白名单可在目录内读写、非白名单只能读、两者均不能访问目录外用户文件。Shell、Skills、MCP、Hooks 等未验证组合先禁用，不阻塞已通过的安全组合进入阶段 2；需要这些组合的功能在其验证通过前不得启用或宣称完成。

**验证门禁：**每个拟开放组合的测试可重复运行并记录命令、退出码、文件前后状态；越权样本全部被拒绝。macOS 无测试环境时明确记录“未验证”，不得宣称 macOS 安全验收完成。

## 阶段 2：抽取通用核心与通信契约

**目标：**让迁移核心不再直接依赖钉钉 Stream 回调、Webhook、工号或 `DingClaude` 巨型入口类。

- [ ] 建立目标插件目录、Node 包与 MIT 许可文件；首版 `metadata.yaml`、`_conf_schema.json` 和 `README.md` 明确 Node 版本、代理命令及隔离先决条件。
- [ ] 在 `runner/src/contracts.ts` 定义消息封套、回复、发送者、群／私聊路由、工具允许集、工作目录、会话标识及错误码；在 Python `bridge/events.py` 实现同一协议的转换。
- [ ] 用标准输入／输出（stdio）连接 Python 插件和 Node 核心；定义启动握手、请求／响应／事件、取消、超时、进程退出和恢复。协议只允许插件创建的进程访问，不暴露网络控制端口。
- [ ] 将会话、任务、配置、审计数据写到插件专属数据区；工作目录保留项目文件。迁移旧 `cc-ding` 数据时先保留原始文件与路径映射，不在首次加载时破坏旧数据。
- [ ] 把 `cc-ding` 的直接 `sendDingMessage`、`queryDingUser` 等调用替换为平台无关接口；逐模块迁移并保持原有纯逻辑测试通过。

**验证门禁：**使用伪造平台事件和伪造 Node 进程完成消息往返、取消、崩溃重启和会话恢复；核心模块中无钉钉 API 或钉钉身份类型依赖。

## 阶段 3：统一权限与两种代理

**目标：**将权限决策固定在所有执行入口之前，同时恢复 Claude Code 和 Codex 的原生交互能力。

- [ ] 实现用户角色、群级上限、私聊配置和工具允许集的交集计算；只读用户始终不能升级为可写，配置缺失时失败关闭。
- [ ] 每次排队入队与出队、会话恢复、定时任务触发、A2A 接收和管理页代理操作均调用同一权限决策层；审计记录包含请求来源、目标群、有效角色、目录及结果，不记录密钥。
- [ ] Claude Code 适配保留会话恢复、流式事件、Skills、MCP、Hooks 的原生加载；Codex 适配保留线程恢复、JSON 事件和其原生扩展能力。工具列表以本次允许集提供给代理，由代理选择；不可用的工具不暴露。
- [ ] 代理进程均通过统一权限运行器启动，按本次权限使用已验证的平台／代理配置；不支持的工具组合失败关闭，禁止沿用 `cc-ding` 中的 `bypassPermissions` 或 Codex `danger-full-access` 参数。
- [ ] 验证同一群共享会话内“白名单写入 → 非白名单只读提问 → 白名单继续写入”的权限切换，确保第二次请求不能借恢复会话写文件。

**验证门禁：**Claude Code、Codex 的真实 CLI 与伪造 CLI 测试均通过；工作目录外读取、只读写入、工具越权和恢复后提权测试均失败关闭。

## 阶段 4：AstrBot 消息与通用功能迁移

**目标：**在 QQ 群和私聊中恢复 `cc-ding` 的日常使用能力。

- [ ] 插件只处理已配置群及允许的私聊，识别 QQ 用户、群、消息 ID 与消息段；群会话键按群配置，私聊会话键按用户配置。
- [ ] 迁移 `/help`、`/info`、`/new`、`/resume`、`/end`、`/goon`、`/cc`、`/task`、`/mq`、`/cron`、`/timer`、`/todo`、`/menu`、`/model`、`/log`、`/ls`、授权及中断等仍有意义的命令；以阶段 1 的逐命令清单核对完整性。
- [ ] 迁移图片、文件、引用、提及与回复映射；对 AstrBot 平台不支持的消息形态返回明确降级说明，避免静默丢内容。
- [ ] 迁移任务排队、定时与一次性提醒、待办、快捷菜单、超时看门狗、去重、日志、密钥轮换与失败恢复；所有后台任务保留创建者身份并在执行时重验权限。
- [ ] 逐配置项替换钉钉 Token、手机号／工号、Webhook、AI Card 和 PM2 专属操作；保留功能语义，取消无等价意义的协议字段，并在 README 中说明迁移结果。

**验证门禁：**逐命令映射表无遗漏；QQ 群、私聊和后台任务的权限组合测试通过，断线／超时后的会话仍可恢复。

## 阶段 5：管理页面与代理间通信

**目标：**把原 Web Console 与 A2A 纳入插件管理和统一权限链。

- [ ] 用 AstrBot 插件页面（Plugin Page）实现群／私聊配置、代理状态、会话管理、模型与密钥管理、任务和日志查看；页面通过 `bridge/web.py` 的受保护接口调用核心，不直接暴露 Node 管理端口。
- [ ] 迁移 A2A Hub、任务状态与跨代理调用；显式选择目标群，验证调用者与目标群授权，不沿用原实现中“默认首个会话＋`a2a-remote` 身份”的执行方式。
- [ ] A2A 发起、接收、重试和回调结果均保留来源身份与权限上限；不能通过 A2A 把只读请求转为写入请求，也不能访问其他群工作目录。
- [ ] 验证管理页面登录态、越权配置修改、密钥脱敏与 A2A 目标群隔离；关闭管理页面或 A2A 时不影响基础 QQ 对话。

**验证门禁：**管理页面和 A2A 的功能清单逐项通过；从只读用户到后台入口的提权尝试全部拒绝。

## 阶段 6：真实验收、部署与收尾

**目标：**把代码、文档、版本和本机 AstrBot 运行状态收束到可 review、可恢复的状态。

- [ ] 运行 Node 核心测试与构建、`backend/.venv` 中的 Python 适配器测试、隔离越权测试及 AstrBot 插件加载测试；不做无关的全局 ESLint 或无关 TypeScript 错误修复。
- [ ] 在本机 AstrBot Desktop 上覆盖插件到对应插件目录、提升 `metadata.yaml` 和插件内部版本、重载插件；记录部署版本和加载日志。每次后续插件代码变更重复版本提升与覆盖流程。
- [ ] 用真实 QQ 群的白名单与非白名单账号、私聊、Claude Code、Codex、图片／文件、任务／定时、管理页面和 A2A 完成端到端验收；记录实际证据及未通过项，不把离线模拟视为真实验收。
- [ ] 更新插件 README、配置示例、逐命令迁移表、权限与隔离操作说明，回写 `.devflow/astrbot-claude-bridge/state.md`、`checkpoints.md` 与必要决策。
- [ ] 进行聚焦代码审查（Code Review）和新鲜验证（Fresh Verification）；所有必需门禁通过后才宣称本轮完成。代码修改完成后先询问用户是否提交，未经明确允许不执行 Git Commit。

**验证门禁：**实际插件版本与仓库版本一致，真实 QQ 验收和安全测试有记录，关键功能无未分类缺口。

## 本轮不做 / 后续阶段（Deferred Scope）

| 对象或能力 | 本轮暂不做的原因 | 后续触发条件或推荐阶段 |
| --- | --- | --- |
| OpenCode、Pi 及其他代理适配 | 本轮优先完成 `cc-ding` 已支持的 Claude Code、Codex 迁移与权限体系。 | Claude Code、Codex 的 AstrBot 迁移及目录／工具权限验收完成后，沿 `runner/src/agents/` 的统一接口进入多代理扩展阶段。 |

## 计划自检

- 对齐成功标准 1：阶段 2 的会话契约、阶段 4 的群与私聊路由、阶段 6 的真实 QQ 验收。
- 对齐成功标准 2、5：阶段 1 的隔离可行性、阶段 3 的权限执行、阶段 5 的后台入口验证。
- 对齐成功标准 3：阶段 3 的 Claude Code／Codex 适配，阶段 4 的会话与中断。
- 对齐成功标准 4：阶段 1 的逐功能清单，阶段 4 的通用能力，阶段 5 的 Web Console 与 A2A。
- 对齐成功标准 6：目标文件职责表和阶段 2 的核心抽取门禁。
