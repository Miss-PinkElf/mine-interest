# cc-ding 到 cc-qq 逐项功能映射（Feature Mapping）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:37:00 +08:00
- 更新时间（Updated At）：2026-09-29 17:00:00 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：逐项追踪原项目能力在原生 Python AstrBot 插件中的 QQ 等价行为、阶段和验收结果。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 总体计划（Master Plan）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-ding原生python完整迁移qq插件-总体实施计划.md`
- 当前开放规格（OpenSpec）：`.devflow/cc-qq-full-migration/spec/tasks.md`
- 当前状态（Status）：第一阶段代码已接通、运行验收待做（Stage 1 Code Connected / Runtime Pending）
- 文档边界（Scope / Boundary）：本 mission 的功能覆盖清单真相源（source of truth）；目标行为是待实施事项，不代表功能已通过。后续阶段持续回填实际证据和经用户确认的例外。

## 分类与状态规则

- **保留（Preserve）**：保留用户可感知的业务行为，用 Python 重写，输入输出改由 AstrBot 承接。
- **平台替换（Platform Adapt）**：钉钉／PM2／npm 专属机制改为 QQ／AstrBot 等价入口，原用户目标仍需可观察。
- **定向修正（Targeted Fix）**：只有已获用户确认的 `/qa` 两代理真实只读行为可偏离原源码。
- 阶段数字对应总体计划的 1–4；“代码已接通，待实测”表示已有实现但该项的真实 QQ／双 CLI 验收证据未齐，“待实现”表示目标阶段仍未编码。旧版 `0.1.12` 已有 Codex 群聊及私聊回复，不能据此推定 Claude Code 或新版 `0.1.13` 的模型选择已通过。每项完成时记录具体文件、实际 QQ 或管理操作结果和日期。
- 本清单以 `cc-ding/src/biz/commands.ts`、`types.ts`、`console.ts`、`bin/cc-ding.ts`、`a2a/`、`messaging.ts`、`image.ts`、`quote.ts`、`session.ts`、`task.ts` 等源码为准；历史 mission 映射仅供交叉核对。

## 显式命令映射

| 原命令 | 目标 QQ／AstrBot 行为 | 阶段 | 验收动作 | 状态 |
| --- | --- | --- | --- | --- |
| `/help` | 展示当前基础命令和用法；管理员专属命令及角色展示在阶段 2。 | 1–2 | 普通成员／管理员在群和私聊查看。 | 阶段 1 代码已接通，待实测 |
| `/info` | 展示当前会话；插件和任务状态在阶段 2 补齐。 | 1–2 | 查询 `robot`、`session`、`task`。 | 阶段 1 代码已接通，待实测；其余待阶段 2 |
| `/log` | 读取当前会话日志尾部。 | 2 | 群和私聊分别读取且不串会话。 | 待实现 |
| `/new` | 新建代理会话，可带首轮消息。 | 1 | Claude／Codex 各开新会话。 | 代码已接通，待实测 |
| `/resume` | 恢复当前会话范围的历史代理 ID。 | 1 | 默认最近和指定 ID；跨群拒绝。 | 代码已接通，待实测 |
| `/end` | 结束当前会话并关闭活跃执行。 | 1 | 结束后不复用旧进程。 | 代码已接通，待实测 |
| `/goon` | 中断／重启并按原代理会话继续。 | 1 | 两代理恢复且不重复旧回复。 | 代码已接通，待实测 |
| `/cc` | 原样透传代理文本，包括代理斜杠内容。 | 1 | 透传 `/compact` 等文本。 | 代码已接通，待实测 |
| `/task` | 排队、查询、取消代理任务。 | 2 | 正常、取消、失败和重试。 | 待实现 |
| `/mq` | 展示、前移和删改当前消息队列。 | 2 | 顺序、范围删除与数量限制。 | 待实现 |
| `/cron` | 表达式或自然语言创建、暂停、继续和删除定时任务。 | 2 | 模型辅助解析、到期执行和重载恢复。 | 待实现 |
| `/timer` | 创建、列出和取消一次性延时任务。 | 2 | 到期仅执行一次。 | 待实现 |
| `/ls` | 列出当前工作目录结构。 | 2 | 相对路径和异常路径说明。 | 待实现 |
| `/claude.md` | 查看当前目录代理说明；Codex 对应 `AGENTS.md`。 | 2 | 两代理各返回正确说明。 | 待实现 |
| `/version` | 展示仓库、本机插件与核心版本。 | 2 | QQ 返回与 `metadata.yaml` 一致。 | 待实现 |
| `/open` | 给管理员管理页入口；本地目录／终端／编辑器操作使用 AstrBot 主机管理入口。 | 2–3 | `console` 与旧参数各有明确反馈。 | 待实现 |
| `/clean` | 清理会话缓存、任务与媒体缓存；保护项目工作目录。 | 2 | 管理员确认后清理，普通用户拒绝。 | 待实现 |
| `/reset-apikeycfg` | 重置密钥可用状态。 | 2 | 状态变更且 QQ 不回显密钥。 | 待实现 |
| `/cfg` | 查看和更新 QQ 群／私聊配置；钉钉参数给等价字段说明。 | 2 | 变更身份、目录、模型和代理后生效。 | 待实现 |
| `/bash` | 保留管理员工作目录命令能力和审计；普通模式沿用原高权限默认值。 | 2 | 管理员执行及审计，普通用户拒绝。 | 待实现 |
| `/auth` | 用 QQ 稳定 ID 管理白名单、管理员和申请审批。 | 2 | 增删、申请、批准、拒绝。 | 待实现 |
| `/recorder` | 管理员私聊记录消息到插件数据目录。 | 2 | 开关、文本／媒体和访问范围。 | 待实现 |
| `/todo` | 待办增删改查与提醒；`@` 对象改为 QQ ID。 | 2 | 创建、完成、删除、到期提醒。 | 待实现 |
| `/menu` | 用户／群快捷菜单与数字选择。 | 2 | 添加、删除、触发和群菜单。 | 待实现 |
| `/!`、`/！`、`!`、`！` | 中断本会话当前代理任务。 | 1 | 不影响其他会话并继续队列。 | 代码已接通，待实测 |
| `/reboot` | 插件服务与管理页重载；PM2／npm 参数映射到 AstrBot 生命周期。 | 2–3 | 管理员重载、普通用户拒绝、旧参数说明。 | 待实现 |
| `/destroy` | 解绑当前 QQ 群／私聊并按确认范围清理插件数据。 | 2 | 不跨群，工作目录删除另行确认。 | 待实现 |
| `/freedom` | 群成员开放对话，仍保留管理员命令控制。 | 2 | 开关前后普通成员准入。 | 待实现 |
| `/qa` | 两代理可验证只读问答，配置资料源与自动拉取。 | 2 | Claude／Codex 写入尝试均失败，普通模式不变。 | 待实现 |
| `/model` | 查询、切换和维护代理模型选项。 | 2 | 两代理分别查询和切换。 | 待实现 |
| `/a2a` | 列出、发现、发送、查询和取消协作任务。 | 3 | 各子命令及目标会话路由。 | 待实现 |

## 配置字段映射

| 原字段（全部来自 `types.ts`） | QQ／插件目标 | 阶段 | 验收动作 | 状态 |
| --- | --- | --- | --- | --- |
| `clientName`、`model` | 插件显示名、Claude Code／Codex 独立默认模型；动态切换留待阶段 2。 | 1–2 | 两代理默认模型独立生效，旧共享值不生效；阶段 2 验证动态切换。 | 独立默认模型代码已接通，待安装实测；动态切换待实现 |
| `whiteUserList`、`owner`、`adminUserList` | QQ ID 的全局白名单、owner 与管理员。 | 1 | 准入、角色、私聊与群差异。 | 代码已接通，待实测 |
| `clientSecret`、`dingSecret`、`defaultDingToken` | 平台认证由 AstrBot 的 QQ 适配器管理；插件不保存钉钉密钥。 | 1 | 新配置无需钉钉凭据即可收发。 | 待实现 |
| `ownerConversationId`、`enableMsgToUser` | 管理员通知目标与 QQ 私聊开关。 | 1–2 | 通知仅送目标，私聊可开关。 | 待实现 |
| `conversations` | 已配置 QQ 群／私聊列表。 | 1 | 未配置拒绝、已配置路由。 | 代码已接通，待实测 |
| `taskQueueSize`、`taskHandlerCount`、`sessionMaxConcurrency` | 任务队列和并发上限。 | 2 | 上限与并发行为。 | 待实现 |
| `includeThinking`、`resultOnly`、`debug` | 回复展示与脱敏日志开关。 | 2 | 展示模式和日志输出。 | 待实现 |
| `apiKeyCfg.resetTime`、`modelSettings`、`retryLogs` | 密钥池、轮换和错误匹配。 | 2 | 密钥状态、轮换、冷却和脱敏。 | 待实现 |
| `preBash`、`envs` | 代理前置命令与环境变量。 | 2 | 群／全局覆盖和审计。 | 待实现 |
| `recorderCfg.dist` | 录制数据位置。 | 2 | 数据区写入与配置生效。 | 待实现 |
| `maxTurnTimeMins`、`maxAutoRecovery` | 超时与恢复阈值。 | 2 | 超时中断和次数限制。 | 待实现 |
| `cardTemplateId`、`cardTemplateKey` | QQ 进度与最终回复；无需钉钉 AI Card 模板。 | 2 | QQ 可见确认、进度、结果。 | 待实现 |
| `retryCfg.maxDurationSecs`、`maxCount`、`minCountForDuration`、`retryCooldownSecs` | 重试风暴和密钥冷却规则。 | 2 | 阈值、停止条件与状态查询。 | 待实现 |
| `a2aCfg.hubUrl`、`apiKey`、`remoteAgents` 及远端 `id`、`name`、`baseUrl`、`apiKey`、`defaultSkill` | A2A Hub、认证、远端代理列表。 | 3 | 连接、认证、远端 CRUD。 | 待实现 |
| `conversationId`、`conversationType`、`conversationTitle` | QQ 群／私聊稳定 ID、类型和显示名。 | 1 | 同名不同 ID 不串会话。 | 待实现 |
| `linkConversationId`、`workDir` | 显式共享关系及会话工作目录。 | 1–2 | 目录配置、共享与独立。 | 待实现 |
| `dingToken`、`mobile` | 群发送和私聊身份交给 AstrBot／QQ ID。 | 1 | 不使用钉钉字段，群私聊仍可收发。 | 待实现 |
| 群级 `whiteUserList`、`agent`、`model` | 群级准入、代理与模型覆盖。 | 1 | 群间配置差异。 | 代码已接通，待实测 |
| `useLocalOcr`、`atSender`、`receiveReply`、`receiveReplyMode`、`ackReaction` | OCR 与 QQ 提及／确认回复。 | 2 | 图片和确认行为。 | 待实现 |
| 群级 `preBash`、`permissionMode`、`envs` | 群级代理执行选项。 | 2 | 覆盖优先级和实际 CLI 参数。 | 待实现 |
| `freedomMode`、`qaMode`、`qaCfg.gitRepos`、`docs`、`autoPull` | 群成员准入和问答资料。 | 2 | 模式开关、只读、资料刷新。 | 待实现 |
| `sessionCfg`、`taskCfg.skill` | 会话与任务技能配置。 | 2 | 任务调用目标技能。 | 待实现 |
| 群级 `maxTurnTimeMins`、`streaming`、`ensureAt`、`teamAgents` | 群级超时、进度、提及与协作代理。 | 2–3 | 覆盖值与 A2A 路由。 | 待实现 |

## 管理控制台（Web Console）映射

| 原接口或页面能力（`console.ts`、`console-web/`） | 插件页面等价行为 | 阶段 | 验收动作 | 状态 |
| --- | --- | --- | --- | --- |
| `/api/login`、`/api/change-password` | 使用 AstrBot 后台认证与插件页面会话。 | 3 | 未登录与非管理员拒绝。 | 待实现 |
| `/api/status`、`/api/clients`、`/api/clients/:id/config`、`/config/raw`、`/config/reload` | 插件状态、实例配置、原始配置和热重载。 | 3 | 各项读取、编辑、生效和脱敏。 | 待实现 |
| `/api/clients/:id/conversations`、`/:convId` | QQ 群／私聊配置 CRUD。 | 3 | 新增、编辑、删除、路由变化。 | 待实现 |
| `/api/clients/:id/start`、`/stop`、`/pm2`、`/pm2/restart` | AstrBot 插件／代理进程状态和重载。 | 3 | 状态、停止、重启和恢复。 | 待实现 |
| `/api/clients/:id/apikeys`、`/:index`、`/api/global/apikeys`、`/:index`、`/reorder` | 群级／全局密钥池 CRUD、排序、脱敏。 | 3 | 增删改查、排序、不回显旧密钥。 | 待实现 |
| `/api/global/retrylogs`、`/config`、`/settings-tpl`、`/raw-config` | 重试规则、全局配置和模板编辑。 | 3 | 校验、保存、重载与回滚。 | 待实现 |
| `/api/clients/:id/files` | 受保护的菜单／模型／Cron／待办／会话辅助数据编辑。 | 3 | 仅允许列出的配置文件。 | 待实现 |
| `/api/a2a/stats`、`/agents`、`/tasks` | A2A 状态、代理与任务监控。 | 3 | 列表、状态及权限。 | 待实现 |
| `/api/ping`、`/api/remote/status`、`/scan`、`/clients`、`/global/*` | 跨实例发现、状态、客户端和配置管理。 | 3 | 已配置远端成功／失败与鉴权。 | 待实现 |
| `/api/global/update-pkg-url`、`/api/update`、`/api/remote/update`、`/api/batch/update` | 本机／远端 AstrBot 插件升级管理流程。 | 3 | 页面有等价操作或经用户确认的例外。 | 待实现 |
| `/api/batch/restart`、`/reload-config`、`/machine/restart`、`/machine/reload-config`、`/console/restart`、`/remote/console/restart`、`/batch/console-restart` | 本机和已配置远端实例的重启、重载与状态反馈。 | 3 | 单实例／批量操作和授权。 | 待实现 |

## CLI 辅助入口映射

| 原 `cc-ding` CLI 子命令 | QQ 插件目标 | 阶段 | 验收动作 | 状态 |
| --- | --- | --- | --- | --- |
| `init` | AstrBot 插件配置与首次群／私聊设置。 | 1–2 | 无钉钉参数完成初始化。 | 待实现 |
| `run` | AstrBot 插件生命周期管理。 | 1 | 加载、重载和停止。 | 待实现 |
| `doctor` | 插件诊断状态和 CLI 可用性。 | 2 | 缺失 CLI／配置给明确结果。 | 待实现 |
| `notify` | 插件服务的主动 QQ 通知。 | 2 | 指定群／私聊成功与失败统计。 | 待实现 |
| `push` | 插件服务推送图片／文件。 | 2 | 文件、图片和说明。 | 待实现 |
| `task` | 插件任务服务的后台命令及完成通知。 | 2 | 后台执行、状态和通知。 | 待实现 |
| `console` | AstrBot 插件管理页面。 | 3 | 管理员打开与非管理员拒绝。 | 待实现 |
| `a2a-server` | 插件 A2A Hub 服务。 | 3 | 启停、认证与注册。 | 待实现 |

## A2A 与消息能力映射

| 来源能力 | QQ 插件目标 | 阶段 | 验收动作 | 状态 |
| --- | --- | --- | --- | --- |
| Agent Card、健康探测、JSON-RPC `tasks/send`、`tasks/sendSubscribe`、`tasks/get`、`tasks/cancel` | 同协议语义，目标为 QQ 会话与代理。 | 3 | 每个方法及取消状态。 | 待实现 |
| Hub 注册、心跳、已连接 Client、Agent、统计与任务查询 | 代理注册、状态、任务监控。 | 3 | 断连／重连和状态一致。 | 待实现 |
| 直连、Hub 路由、远端列表、API Key 鉴权、任务持久化 | 已配置远端的协作调用。 | 3 | 认证失败、重复任务、错误目标。 | 待实现 |
| 钉钉文本／Markdown、长消息分段、确认表情、群／私聊和主动发送 | AstrBot QQ 文本、分段、确认和主动通知。 | 1–2 | 长文本、群私聊、确认、发送失败。 | 待实现 |
| 图片、文件、富文本、引用、提及、OCR 与录制 | QQ 消息段、附件保存、引用上下文和 OCR。 | 2 | 每类输入各有示例结果。 | 待实现 |
| 会话持久化、消息去重、队列、中断、重启恢复 | 插件数据区的群／私聊独立会话。 | 1–2 | 多轮、重复消息、并发和重载。 | 阶段 1 代码已接通，待实测；高级队列操作待阶段 2 |
| 看门狗、API Key 轮换、流式显示、通知队列 | Python 业务模块与 AstrBot 回复。 | 2 | 超时、失败恢复、密钥脱敏和进度。 | 待实现 |

## 本阶段不做 / 后续阶段（Deferred Scope）

- 阶段 1 只验收 QQ 文本、准入、双代理与基础会话命令；阶段 2 的任务、媒体、密钥与 `/qa` 等条目等待阶段 1 链路通过后继续，原因是它们依赖稳定会话接口。
- 阶段 3 的 Web Console、跨实例与 A2A 等待阶段 2 数据与身份接口稳定后继续；阶段 4 收口等待前三阶段全部实现。表中“待实现”必须随阶段推进逐项更新，不可因阶段切换永久忽略。
