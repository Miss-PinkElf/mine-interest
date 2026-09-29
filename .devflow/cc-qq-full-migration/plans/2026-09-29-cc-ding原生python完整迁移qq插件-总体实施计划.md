# cc-ding 原生 Python 完整迁移 QQ 插件实施计划（Implementation Plan）

> 执行者（Agentic Worker）：当前为 devflow 重型路径（Heavy Route）；实施前先生成开放规格（OpenSpec）的 `proposal.md`、`design.md`、`tasks.md`，按任务逐项推进。任务使用 `- [ ]` 跟踪；代码提交仅在用户明确允许后进行。

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:27:00 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：定义 `cc-ding` 通用能力迁移到原生 Python AstrBot 插件的文件边界、阶段顺序、任务和验收门禁。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 已确认对齐（Aligned Design）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-ding原生python迁移qq插件-需求对齐.md`
- 参考源码（Reference Source）：`cc-ding/`
- 当前状态（Status）：计划中（Planned）
- 文档边界（Scope / Boundary）：本 mission 的总体实施顺序真相源（source of truth）；已对齐目标，但本文件不代替各阶段的详细任务或开放规格（OpenSpec），不单独触发实施（Apply）。

**目标（Goal）：**在 `integrations/astrbot/astrbot_plugin_cc_qq/` 建立由 AstrBot 管理的原生 Python QQ 插件，逐项完成 `cc-ding` 的 Claude Code、Codex、会话、业务命令、管理和 A2A 能力。

**架构（Architecture）：**AstrBot 入口将 QQ 事件归一为平台无关消息；身份、会话和命令服务调度独立的 Claude Code／Codex 异步进程适配器；回复由 AstrBot 发送。插件数据存于 AstrBot 插件数据目录，管理页面和 A2A 使用相同的身份与会话服务。`cc-ding/` 只作为行为参考，业务核心不保留 Node 侧车进程。

**技术栈（Tech Stack）：**Python、AstrBot 插件 API、Python 标准库 `asyncio`／`sqlite3`、Claude Code CLI、Codex CLI；管理页面沿用仓库偏好的 React、TypeScript、Ant Design（Antd）与 CSS Module。插件外部依赖只有在现有 AstrBot 能力不足时才新增。

---

## 适用边界与阶段原则

- 本计划覆盖完整目标，但阶段 1、2、3 是可独立验收的交付切片；只有阶段 4 的差异清单收口后才可宣称完整迁移。
- 每个后续阶段开始前，按本计划写该阶段的细化计划（Detailed Plan），刷新当前 `spec/` 的提案、设计和任务，再进入实施；不因“以后再做”把阶段 2、3、4 从 mission 删除。
- 普通代理会话保持源代码实际默认权限：Claude Code `bypassPermissions`，Codex `danger-full-access`。问答模式 `/qa` 单独实现两种代理可验证的只读行为。QQ 用户白名单不等于操作系统文件隔离。
- 显式命令走注册表，普通自然语言由代理处理；插件工具以名称、描述、参数和权限元数据集中注册，交给代理选择，避免散落的硬编码意图分支。
- 新插件每次代码变更都在 `metadata.yaml` 和 Python 版本常量中提升版本，并覆盖到 AstrBot 用户数据目录的 `data/plugins/astrbot_plugin_cc_qq/`。仓库文本编辑优先用补丁；不自动提交。

## 文件地图（File Map）

以下是目标文件和单一职责；每个阶段只创建所需文件，避免先铺空壳。后续细化计划若调整路径，先更新本地图和开放规格（OpenSpec）。

| 路径 | 职责 | 阶段 |
| --- | --- | --- |
| `integrations/astrbot/astrbot_plugin_cc_qq/main.py` | AstrBot 注册、事件入口与生命周期 | 1 |
| `integrations/astrbot/astrbot_plugin_cc_qq/metadata.yaml` | 插件身份和可感知版本 | 1–4 |
| `integrations/astrbot/astrbot_plugin_cc_qq/_conf_schema.json` | 群、私聊、owner、白名单、代理和工作目录配置 | 1–3 |
| `integrations/astrbot/astrbot_plugin_cc_qq/constants.py` | 版本、默认值、状态键和提示词入口 | 1–4 |
| `integrations/astrbot/astrbot_plugin_cc_qq/contracts.py` | 消息、身份、授权、会话和代理事件数据契约 | 1 |
| `integrations/astrbot/astrbot_plugin_cc_qq/platform/qq_events.py` | AstrBot／QQ 输入转换 | 1–2 |
| `integrations/astrbot/astrbot_plugin_cc_qq/platform/replies.py` | QQ 回复与主动通知 | 1–2 |
| `integrations/astrbot/astrbot_plugin_cc_qq/policy.py` | owner、管理员、白名单、群策略与命令准入 | 1–3 |
| `integrations/astrbot/astrbot_plugin_cc_qq/storage.py` | 插件数据目录和原子／事务存储入口 | 1 |
| `integrations/astrbot/astrbot_plugin_cc_qq/sessions.py` | 会话状态、恢复与消息队列 | 1–2 |
| `integrations/astrbot/astrbot_plugin_cc_qq/agents/base.py` | 代理统一接口、事件与取消语义 | 1 |
| `integrations/astrbot/astrbot_plugin_cc_qq/agents/claude.py` | Claude CLI 参数与流事件解析 | 1–2 |
| `integrations/astrbot/astrbot_plugin_cc_qq/agents/codex.py` | Codex CLI 参数与 JSON 事件解析 | 1–2 |
| `integrations/astrbot/astrbot_plugin_cc_qq/agents/process.py` | 异步子进程、超时、中断与退出处理 | 1–2 |
| `integrations/astrbot/astrbot_plugin_cc_qq/service.py` | 消息准入、命令、会话、代理和回复编排 | 1–2 |
| `integrations/astrbot/astrbot_plugin_cc_qq/commands/registry.py` | 显式命令表和帮助元数据 | 1–2 |
| `integrations/astrbot/astrbot_plugin_cc_qq/commands/session.py` | `/new`、`/resume`、`/end`、`/goon`、`/!`、`/cc` | 1 |
| `integrations/astrbot/astrbot_plugin_cc_qq/commands/admin.py` | `/auth`、`/cfg`、`/freedom`、`/qa` 等管理命令 | 2 |
| `integrations/astrbot/astrbot_plugin_cc_qq/features/` | 任务、调度、待办、菜单、模型、密钥、录制和通知的聚焦模块 | 2 |
| `integrations/astrbot/astrbot_plugin_cc_qq/media/` | 图片、文件、引用、提及与 OCR | 2 |
| `integrations/astrbot/astrbot_plugin_cc_qq/tools/` | 可供代理选择的插件工具元数据和调用边界 | 2–3 |
| `integrations/astrbot/astrbot_plugin_cc_qq/admin/` | 插件页面后端、配置与跨实例管理接口 | 3 |
| `integrations/astrbot/astrbot_plugin_cc_qq/pages/` | 管理页面静态资源 | 3 |
| `integrations/astrbot/astrbot_plugin_cc_qq/a2a/` | Agent Card、Hub、Client、任务协议及持久化 | 3 |
| `integrations/astrbot/astrbot_plugin_cc_qq/README.md` | 安装、QQ 配置、权限和功能说明 | 1–4 |
| `.devflow/cc-qq-full-migration/spec/feature-mapping.md` | 原命令、字段、Console、A2A、CLI 和消息能力的逐项迁移清单 | 1–4 |

## 跨模块契约（Contracts）

- 输入事件（Incoming Event）包含 `platform_id`、`conversation_kind`、`conversation_id`、`sender_id`、`message_id`、`segments` 与可用的引用／提及信息；会话键同时包含平台实例和群／私聊范围，防止不同 QQ 账号或同号 ID 串会话。
- 授权结果（Authorization Decision）明确角色、可否进入会话、可否执行管理命令，以及本次 `/qa` 模式；每次后台任务执行前重新读取最新配置。普通模式的 CLI 权限与消息准入分别记录。
- 代理事件（Agent Event）统一为会话已启动、文本增量、工具调用、完成、错误和取消；适配器保存 Claude 会话 ID 或 Codex 线程 ID，服务层不解析代理原生 JSON。
- 输出事件（Reply Event）由平台模块发送，记录发送结果；后台任务、A2A 和 CLI 辅助入口共用这一接口，不能直连 QQ 协议 URL。
- 提示词（Prompt）、工具元数据（Tool Metadata）、默认文案（Default Copy）、状态键（State Key）和阈值（Threshold）集中在 `constants.py` 或所属模块顶部；跨模块复用时抽为专门文件。

## 阶段 0：功能清单和真实行为基线

### T00 — 逐项映射原项目

**文件：**`cc-ding/src/biz/commands.ts`、`types.ts`、`console.ts`、`a2a/`、`bin/cc-ding.ts`、`README.md`（只读）；创建 `.devflow/cc-qq-full-migration/spec/feature-mapping.md`。

- [ ] 从原命令注册表、配置类型、Console 路由、CLI 子命令、消息处理和 A2A 协议逐项列出能力，记录源文件、目标模块、目标 QQ 行为和验收动作。
- [ ] 将钉钉协议字段、PM2／npm 操作标为“平台替换”，列出可观察的 AstrBot 等价行为；确无等价实现的条目先向用户确认，不将其默默删掉。
- [ ] 记录源码与说明不一致的行为：Claude 默认权限以 `claude-process.ts` 的 `bypassPermissions` 为准；Codex 以 `codex-agent.ts` 的 `danger-full-access` 为准；`/qa` 是明确修正项。

**门禁：**命令、配置、Console、CLI、A2A 和媒体六类均有完整条目；原功能清单的空白项不得被算作通过。

## 阶段 1：QQ 与双代理基础链路

### T01 — 插件骨架、配置与数据契约

**文件：**`main.py`、`metadata.yaml`、`_conf_schema.json`、`constants.py`、`contracts.py`、`storage.py`、`README.md`。

- [ ] 创建可被 AstrBot 加载的插件，配置已启用群／私聊、owner、管理员、白名单、代理类型、模型和工作目录；首次启用前不默认响应全部群。
- [ ] 使用插件数据目录保存会话与审计状态；以 Python 标准库 `sqlite3` 管理持久状态，按消息 ID 和会话键建唯一约束，避免重载后重复执行。
- [ ] 定义输入、授权、会话与代理事件结构，入口只依赖这些契约；在 README 写明 CLI 安装和普通模式完整访问权限。

**门禁：**插件可加载、配置可读、空配置不会启动代理，数据不写入源码目录。

### T02 — QQ 消息、身份与回复适配

**文件：**`platform/qq_events.py`、`platform/replies.py`、`policy.py`、`main.py`。

- [ ] 从 AstrBot 事件提取平台实例、群／私聊、发送者和消息 ID；文本请求、管理员命令与 QQ 发送接口不带钉钉字段。
- [ ] 实现 owner、管理员、全局／群白名单和未配置会话拒绝；统一使用 QQ 稳定用户 ID，不保留手机号或工号解析。
- [ ] 把文本、错误和确认事件经 AstrBot 回复；发送失败保留状态供重试，不在日志和聊天中输出密钥。

**门禁：**同一 QQ 号的不同群、不同 QQ 平台实例和私聊不会串会话；未授权请求不会启动 CLI。

### T03 — 两种 CLI 进程适配

**文件：**`agents/base.py`、`agents/process.py`、`agents/claude.py`、`agents/codex.py`、`constants.py`。

- [ ] 用异步子进程启动 Claude Code 与 Codex；参数数组传递，不经 Shell 拼接用户文本；分别解析 `stream-json` 与 JSON Lines，产生统一代理事件。
- [ ] 保留源代码普通模式的权限默认值和显式模型覆盖；保存 Claude 会话 ID／Codex 线程 ID，用原生恢复命令继续多轮。
- [ ] 在进程异常、超时、取消和 CLI 缺失时生成明确事件，清理子进程及资源；代理自行使用原生工具能力，不在插件中硬编码工具选择。

**门禁：**两种 CLI 的新会话和恢复行为有可观察结果；中断后不产生幽灵回复。

### T04 — 会话编排与基础命令

**文件：**`sessions.py`、`service.py`、`commands/registry.py`、`commands/session.py`、`main.py`。

- [ ] 会话服务串行化同一会话请求，支持入队、去重、进程重启后的恢复；不同群或私聊可独立推进。
- [ ] 迁移 `/help`、`/new`、`/resume`、`/end`、`/goon`、`/cc`、`/!` 和基本 `/info`；显式命令只在准入后执行，普通文本交给代理。
- [ ] 处理插件重载时的取消与状态保存；工作目录、代理类型和会话 ID 由本次会话配置确定。

**门禁：**两种代理在真实 QQ 群和私聊中完成多轮、结束、中断、继续和重载恢复；阶段 1 清单逐项打勾。

## 阶段 2：业务、媒体与工具

### T05 — 任务与调度

**文件：**`features/queue.py`、`features/tasks.py`、`features/cron.py`、`features/timer.py`、`commands/tasks.py`、`sessions.py`。

- [ ] 迁移 `/task`、`/mq`、`/cron`、`/timer`，保存排队、取消、重试和触发状态；定时自然语言解释交给代理辅助，表达式和权限检查由业务模块确定执行。
- [ ] 保留并发、队列大小、超时与重试配置；后台执行前重算角色和会话状态，避免旧配置残留。

**门禁：**任务与定时事件执行一次、可取消、可恢复，出错状态可查询。

### T06 — 协作、管理命令和 CLI 辅助能力

**文件：**`features/todo.py`、`features/menu.py`、`features/models.py`、`features/keys.py`、`features/recorder.py`、`features/notify.py`、`commands/admin.py`、`commands/collaboration.py`、`tools/`。

- [ ] 迁移 `/auth`、`/cfg`、`/freedom`、`/qa`、`/model`、`/todo`、`/menu`、`/recorder`、`/bash`、`/ls`、`/log`、`/clean`、`/destroy`、`/open`、`/reboot`、`/version`、`/reset-apikeycfg` 等剩余原命令，按 T00 映射结果逐项归档。
- [ ] 保留模型切换、API Key 轮换／冷却、看门狗、后台通知与原 CLI 的任务／推送入口所代表的能力；通过插件服务接口实现 QQ 等价入口。
- [ ] 插件工具目录集中声明名称、描述、参数和准入要求；代理根据这些元数据选择插件能力，不引入关键词路由。
- [ ] `/qa` 对 Claude Code 与 Codex 使用可验证的只读执行配置；若某 CLI 组合无法证明不可写，回退设计，不把提示词当作通过证据。

**门禁：**原命令与 CLI 辅助能力逐项有 QQ 等价行为；普通模式和问答模式的权限表现分别记录。

### T07 — 媒体与回复体验

**文件：**`media/images.py`、`media/files.py`、`media/quotes.py`、`media/ocr.py`、`platform/qq_events.py`、`platform/replies.py`。

- [ ] 迁移图片、文件、引用、提及、富文本和录制输入；附件保存于插件数据目录，向代理提供可用路径或内容。
- [ ] 保留长消息分段、进度／确认、群内提及和主动通知；QQ／AstrBot 无法直接表达的钉钉卡片能力给出明确降级文本。

**门禁：**每种原输入与输出形态都有 QQ 示例和结果记录，无法支持的形态不静默丢失。

## 阶段 3：管理控制台与 A2A

### T08 — 本地管理控制台

**文件：**`admin/api.py`、`admin/config.py`、`admin/status.py`、`pages/`、`_conf_schema.json`。

- [ ] 在 AstrBot 插件页面实现原 Console 的状态、会话、配置、密钥、辅助文件和 A2A 监控能力；前端使用组件化 React／TypeScript 与 Ant Design（Antd），业务操作经过受保护的 Python 接口。
- [ ] 管理员身份、密钥脱敏、配置校验和重载生效统一到插件权限接口；PM2 状态与重启映射为插件生命周期和进程状态。

**门禁：**T00 中每个本地 Console 操作都有页面入口或明确等价管理方式；非管理员不可读写。

### T09 — 跨实例管理与代理间通信

**文件：**`admin/remote.py`、`a2a/types.py`、`a2a/server.py`、`a2a/client.py`、`a2a/hub.py`、`a2a/store.py`、`commands/a2a.py`。

- [ ] 迁移已配置远端实例的状态、会话和配置管理，使用明确身份与认证；原任意 URL 扫描／远程更新操作需给出可验收的 AstrBot 等价管理流程。
- [ ] 迁移 Agent Card、Hub 注册和心跳、任务发送／查询／取消、直连与 Hub 路由、`/a2a` 命令；调用始终携带目标 QQ 会话和来源身份。

**门禁：**跨实例读写与 A2A 请求有成功和拒绝记录；断连、重试、重复任务不会造成跨群误路由。

## 阶段 4：差异收口、文档与部署

### T10 — 完整功能对照与插件交付

**文件：**`.devflow/cc-qq-full-migration/spec/feature-mapping.md`、`integrations/astrbot/astrbot_plugin_cc_qq/README.md`、`metadata.yaml`、`constants.py`、`_conf_schema.json`。

- [ ] 逐项核对 T00 清单：命令、配置、媒体、CLI 辅助、Web Console、远端管理和 A2A；记录实际行为、证据与经用户确认的例外，不用“已规划”代替“已实现”。
- [ ] 更新插件安装、QQ 账号与群配置、代理 CLI 准备、权限默认值、`/qa`、管理页面、A2A、故障恢复和版本说明。
- [ ] 将仓库插件副本覆盖到 AstrBot 用户数据目录的对应插件目录，核对版本、加载状态和实际 QQ 使用结果；发生插件代码追加改动时再次提升版本并覆盖。
- [ ] 按 devflow 审查（Review）和验证（Verify）门禁复核证据，更新 `state.md`、`checkpoints.md`、`decision-log.md`；仅在用户明确允许后提交代码。

**门禁：**清单无未分类缺口，仓库与 AstrBot 插件版本一致，关键功能有新鲜运行证据，才能将 mission 标记完成。

## 本轮不做 / 后续阶段（Deferred Scope）

| 暂不做的对象 | 本阶段原因 | 后续触发条件 |
| --- | --- | --- |
| T05–T07 的任务、协作、媒体 | 阶段 1 先稳定 QQ 消息和双代理会话链路。 | T01–T04 的阶段验收完成，进入阶段 2 的详细计划和开放规格。 |
| T08–T09 的管理页面、跨实例与 A2A | 依赖身份、会话、配置和任务接口。 | 阶段 2 接口稳定，进入阶段 3 的详细计划和开放规格。 |
| T10 的完整性收口 | 需要前三阶段的实际产物。 | 阶段 3 验收完成，进入阶段 4；此前不得声称完整迁移。 |

这些项目都属于本 mission 的必做后续阶段，不是永久放弃。OpenCode、Pi 不在本次原始需求或 `cc-ding` 已有代理清单中，本计划不引入额外代理。
