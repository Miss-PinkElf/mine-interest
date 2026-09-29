# cc-ding 原生 Python 迁移为 QQ 插件需求对齐（Align）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:23:07 +08:00
- 更新时间（Updated At）：2026-09-29 10:32:01 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：固定本次完整迁移的目标、技术路线、能力范围和分阶段验收边界。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 参考源码（Reference Source）：`cc-ding/`
- 历史参考（Historical Reference）：`.devflow/astrbot-claude-bridge/spec/feature-mapping.md`、`.devflow/astrbot-claude-bridge/spec/permission-matrix.md`
- 当前状态（Status）：用户已确认（Approved）
- 文档边界（Scope / Boundary）：本 mission 的需求与设计对齐真相源（source of truth）；代表已口头确认的方向，不是实施计划（Plan）或开放规格（OpenSpec），不单独触发实施（Apply）。历史 mission 仅提供线索，不继承其验收要求。

## 目标与成功标准

以 `cc-ding/` 为原理和功能参考，在 `integrations/astrbot/` 新建原生 Python AstrBot 插件，使已配置的 QQ 群聊和私聊能够调用本机 Claude Code 与 Codex，并逐阶段补齐 `cc-ding` 的通用用户能力。最终插件由 AstrBot 安装、配置、启动和重载；业务逻辑按消息、身份、会话、代理、任务、管理和 A2A 边界拆分，不继续依赖钉钉 SDK、钉钉身份字段或一个巨型入口类。

成功标准：

1. 逐项建立原命令、配置字段、管理页面、CLI 辅助命令、消息形态及 A2A 能力的映射与验收清单；最终每项都有“已实现并验证／已映射为 AstrBot 等价行为／经用户确认的例外”之一的记录，不静默遗漏。
2. QQ 群聊与私聊可进行两种代理的多轮对话，能恢复、结束、中断、排队和接收结果；身份与命令权限按原项目可感知语义工作。
3. 任务、定时、待办、通知、媒体、模型与密钥、管理控制台（Web Console）、跨实例管理和代理间通信（A2A）均纳入同一 mission 的后续阶段，直到功能清单收口才宣称完整。
4. 插件源码、配置说明、部署版本与本机 AstrBot 插件副本一致；每次插件代码变更均提升版本并覆盖本机对应插件目录。代码提交需用户明确允许。

## 原项目的运行原理

`cc-ding/src/biz/cc-ding-cli.ts` 通过钉钉流客户端接收消息，完成鉴权、去重、内容转换和命令路由，再把普通消息交给会话逻辑。`cc-ding/src/biz/claude-process.ts` 与 `cc-ding/src/biz/codex-agent.ts` 启动本机 Claude Code／Codex CLI，读取流式输出，保存代理会话 ID，并通过 `cc-ding/src/biz/messaging.ts` 调用钉钉接口回复。代理自己选择并执行其工具；项目外围负责会话、任务、定时、权限准入、管理控制台和 A2A。

因此新插件直接实现同一工作链：AstrBot 接收 QQ 事件 → 插件统一消息与身份 → 会话和权限层 → Python 代理进程适配器 → AstrBot 回复。技术路线不保留 TypeScript 核心进程；`cc-ding/` 只作为行为对照，避免把原巨型钉钉入口复制到新插件。

## 模块与数据边界

| 模块 | 职责与接口边界 |
| --- | --- |
| AstrBot 入口（AstrBot Entry） | 注册消息、命令、页面与生命周期；启动和关闭内部服务，不承载完整业务流程。 |
| 平台消息适配（Platform Message Adapter） | 从 QQ／AstrBot 事件提取稳定平台、群、用户和消息 ID，归一文本、图片、文件、引用、提及；把回复事件送回 AstrBot。 |
| 身份与权限（Identity and Permission） | 处理 owner、管理员、白名单、群配置、自由模式、问答模式和管理命令准入；与代理进程权限分开表示。 |
| 会话与存储（Session and Storage） | 管理群聊／私聊会话键、代理会话 ID、历史、恢复、队列、去重、审计与插件数据目录；工作目录按会话配置。 |
| 代理进程（Agent Runner） | Claude Code 与 Codex 各有独立适配器；使用 Python 异步子进程管理启动、流事件、中断、超时和退出。 |
| 命令与工具（Commands and Tools） | 显式斜杠命令走集中注册表；普通自然语言交给选定代理。插件可调用能力通过工具元数据集中声明，由代理自行选择，不靠散落关键词硬编码意图。 |
| 任务与调度（Tasks and Scheduling） | 消息队列、任务队列、Cron、Timer、待办、菜单、通知与恢复策略；后台执行仍使用当前配置与会话身份。 |
| 管理控制台（Web Console） | 基于 AstrBot 插件页面和受保护的插件接口，提供状态、会话、配置、模型、密钥、日志和跨实例管理。前端可借鉴原项目的 Ant Design（Antd）界面，但业务后端由 Python 插件负责。 |
| 代理间通信（A2A） | 保留 Agent Card、Hub、注册心跳、任务发送／查询／取消与协作命令；路由使用 QQ／AstrBot 会话身份。 |

原项目源码和本仓库现有插件仅作参考；新插件及其文档必须位于可追踪的 `integrations/astrbot/` 子目录。插件配置由 AstrBot 管理，会话、队列、媒体和审计数据存入插件专属数据目录，不与仓库源码混放。

## 功能范围与阶段顺序

| 阶段 | 必须交付的能力 | 阶段验收 |
| --- | --- | --- |
| 1. QQ 与双代理基础链路 | 群聊／私聊、身份与准入、Claude Code／Codex、会话新建／继续／结束／中断、文本回复、去重、恢复与基本配置。 | 已配置 QQ 会话可完成两种代理的多轮对话；重载后按原代理会话 ID 恢复；未授权消息不会启动代理。 |
| 2. 日常业务与媒体 | 原有显式命令、消息与任务队列、Cron、Timer、待办、菜单、模型和密钥、看门狗、重试、审计、录制、通知、图片、文件、引用、提及、OCR 与回复体验。 | 原命令和配置字段逐项映射；QQ 群／私聊的输入输出和后台任务可检查。 |
| 3. 管理与协作 | Web Console 的状态、群／私聊配置、会话、密钥、辅助文件和进程管理；跨实例管理；A2A 的 Hub、Client、Agent Card、任务路由与监控。 | 页面与 A2A 的读写、鉴权、重连、任务状态和取消逐项检查；远端能力不被静默省略。 |
| 4. 完整性收口 | 逐功能差异复核、插件文档与配置说明、部署副本与版本一致性、真实 QQ 使用检查。 | 完整映射清单无未分类缺口，插件副本与仓库版本一致。 |

阶段 1 只是可运行的垂直切片，不代表完整迁移已经完成。后续阶段均属于本 mission 的承诺范围；如原能力在 AstrBot 中没有直接等价形式，先设计可观察的替代行为并与用户确认，再调整清单。

## 平台替换与权限语义

- 钉钉 ClientId、Secret、机器人 Token、Stream 回调、Webhook、手机号／工号及 AI Card 换成 AstrBot 已有的平台认证、QQ 稳定 ID、消息段与回复能力。原命令的用户可感知结果保留，平台专属参数逐项记录替代方式。
- 原 PM2 启停、npm 更新和本地打开文件管理器等操作改由 AstrBot 插件生命周期、插件管理或显式本机管理入口承接。跨实例管理仍在阶段 3 范围；不能仅因平台不同而从清单删除。
- 用户确认普通会话完全沿用 `cc-ding` 的代理默认执行权限。源码中 Claude Code 默认 `bypassPermissions`，Codex 默认 `danger-full-access`；QQ 白名单控制请求准入，并非文件系统隔离。历史 mission 的严格工作目录拒读、白名单只读分层与 Windows／macOS 双平台验收不自动进入本 mission。
- `/qa` 问答模式是已确认的定向修正：普通会话默认值不变，但问答模式对 Claude Code 与 Codex 都要达到可验证的只读行为。原项目的提示词和 Claude `plan` 模式不能单独作为只读证据。
- 群／私聊身份、管理员、自由模式和问答模式的可用对象按原功能语义重新映射到 QQ，不能沿用钉钉手机号或工号判断。

## 错误处理与验收证据

- 代理命令缺失、认证失败、超时、进程异常、插件重载、QQ 发送失败与 A2A 断连时，记录明确状态并尽可能保留可恢复会话；日志和群消息不得泄露密钥。
- 核对证据以本 mission 的逐项映射表、插件加载与 QQ 交互结果、代理进程行为、管理页和 A2A 操作结果为准。某阶段未完成的项目必须明确标记并保留到下一阶段。
- `cc-ding/README.md` 对 Claude 默认权限的描述与 `cc-ding/src/biz/claude-process.ts` 实际回退值不完全一致；迁移默认行为以运行代码为准，在新插件说明中写清楚。

## 本轮不做 / 后续阶段（Deferred Scope）

| 后续对象或能力 | 当前阶段暂不做的原因 | 触发条件与推荐阶段 |
| --- | --- | --- |
| 任务、定时、媒体和大部分辅助命令 | 先建立可运行的 QQ 与双代理会话链路，避免在入口未稳定前叠加后台行为。 | 阶段 1 的双代理与恢复通过后，进入阶段 2；这些能力仍须完成。 |
| Web Console、跨实例管理与 A2A | 依赖统一身份、会话和数据接口；先固定这些接口。 | 阶段 2 的基础业务和数据接口稳定后进入阶段 3；仍属完整迁移范围。 |
| 最终功能清单收口与部署验收 | 需要前三阶段的实际实现与运行结果。 | 阶段 3 完成后进入阶段 4，不把阶段性交付误称为完整迁移。 |

当前没有决定永久放弃的 `cc-ding` 通用能力，也未自动沿用历史 mission 的 OpenCode、Pi 等额外代理延期项；本次原始目标仅要求迁移 `cc-ding` 已有的 Claude Code 与 Codex。
