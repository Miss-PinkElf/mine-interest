# cc-ding → AstrBot 逐项功能映射（Feature Mapping）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 23:49:00 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：作为 T01 的逐项迁移清单，区分业务语义、平台替换与钉钉专属行为，并给出验收动作。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 实施计划（Implementation Plan）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`
- 开放规格（OpenSpec）：`.devflow/astrbot-claude-bridge/spec/tasks.md`
- 当前状态（Status）：实施中（In Progress）
- 文档边界（Scope / Boundary）：本文件是 T01 功能范围真相源（source of truth）；映射是待实现验收目标，不表示功能已经迁移或验证通过。

## 分类与验收规则

- **保留**：复用业务语义和尽可能复用纯逻辑，将输入输出替换为插件协议。
- **适配**：保留用户可感知能力，改用 AstrBot 的平台、身份、配置或生命周期能力。
- **取消协议形式**：仅取消钉钉／PM2 专属协议、字段或危险捷径；对应用户能力须在目标项中说明。不得把这一类解释为取消 Web Console 或 A2A。
- 表中“验收”是实施时要执行的动作；当前只完成清单盘点。每项须在 T10–T16 对应任务核验，并将结果回填。
- `C` 指 `runner/src/features/collaboration.ts`，`S` 指 `runner/src/core/session.ts`，`P` 指 `runner/src/policy/evaluate.ts`，`R` 指 `bridge/replies.py`，`W` 指 `bridge/web.py`，`A` 指 `runner/src/a2a/`。群与私聊的命令验收均需覆盖权限差异。

## 命令映射

来源：`cc-ding/src/biz/commands.ts` 的完整 `COMMAND_REGISTRY`、同文件其他 `parse*Command`，以及 `commands-a2a.ts`。命令中的钉钉 ID 参数以 QQ／AstrBot 稳定身份替换。

| 原命令 | 分类与目标 | 验收动作 |
| --- | --- | --- |
| `/help` | 保留；`C` 命令注册表输出按当前权限过滤的帮助。 | 群普通用户、管理员和私聊输出可用命令；无越权入口。 |
| `/info` | 保留；`C` 与 `S` 输出群、会话、任务和代理状态，敏感配置脱敏。 | 分别执行 `robot`、`session`、`task`，核对无密钥。 |
| `/log` | 保留；`S` 读取当前会话日志，受本次身份限制。 | 群共享历史可见范围符合群规则，私聊互相不可见。 |
| `/new` | 保留；`S` 开新会话并可继续初始消息。 | 两种代理新建后旧会话 ID 不再使用。 |
| `/resume` | 保留；`S` 按会话 ID 或最近记录恢复，执行时重算权限。 | 跨群 ID 拒绝，白名单创建后非白名单恢复仍只读。 |
| `/end` | 保留；`S` 结束当前会话。 | 结束后同群再次发送不复用已结束进程。 |
| `/goon` | 保留；`S` 重启并恢复本次授权的代理执行。 | 权限降级后执行不得继承旧写权限。 |
| `/cc` | 保留；`C` 直接透传代理文本，仍经过 `P`。 | 原生斜杠命令可发送，不能绕开工具白名单。 |
| `/task` | 保留；`runner/src/features/tasks.ts`。 | 入队、执行、取消、重试时身份与权限均正确。 |
| `/mq` | 保留；`runner/src/core/queue.ts`。 | 列表、前移、删单项／范围／全部及数量上限逐项验证。 |
| `/cron` | 保留；`runner/src/features/scheduler.ts`。 | 自然语言／表达式创建、列表、暂停、恢复、删除；触发时重验权限。 |
| `/timer` | 保留；调度器（Scheduler）。 | 创建、列表、取消、到期执行；权限变化后禁止越权。 |
| `/ls` | 保留；`C` 在授权工作目录内列树。 | 相对路径、目录外绝对路径及符号链接逃逸测试。 |
| `/claude.md` | 适配；`C` 读取当前工作目录中的代理说明文件，针对 Codex 明确显示 `AGENTS.md`。 | 两种代理各读取对应文件，目录外路径拒绝。 |
| `/version` | 适配；插件元信息（Metadata）和 `C` 返回插件／核心版本。 | QQ 显示版本与仓库、本机插件副本一致。 |
| `/open` | 适配；仅向管理员返回 AstrBot 插件页面入口。取消从 QQ 启动本机文件管理器、Shell、VS Code 的形式。 | `/open console` 能定位页面；其他变体明确说明替代方式。 |
| `/clean` | 适配；`S`／`W` 清理插件数据区中的会话、任务、媒体缓存，不删除项目工作目录。 | 管理员确认目标后清理；普通用户拒绝；项目文件保留。 |
| `/reset-apikeycfg` | 保留；密钥管理（Key Management）重置可用状态。 | 管理员执行后状态正确，QQ 不回显密钥。 |
| `/cfg` | 适配；AstrBot 配置与 `W` 管理群／私聊、目录、白名单、工具、模型和代理。钉钉 Token 等参数取消。 | 逐字段更新后即时重算权限；旧参数给明确替代提示。 |
| `/bash` | 适配；管理员执行也必须经过 `P` 与已验证的平台权限运行器（Permission Runner），工具权限单独配置。原生 Windows 上 Claude Code 的 Shell 沙箱未获官方支持，验证前禁用该组合。 | 非管理员、只读群、禁用 Shell 时拒绝；允许组合的目录外访问拒绝。 |
| `/auth` | 适配；`P`／`W` 以 QQ／AstrBot 用户 ID 管理白名单、管理员、申请审批。 | 增删、列表、批准／拒绝及权限降级逐项验证。 |
| `/recorder` | 适配；录制到插件数据区，并限定管理员／私聊权限。 | 开启、退出、文件访问边界及保留策略核验。 |
| `/todo` | 适配；`C` 保留增、完成、删、列表、提醒；`@` 人改为 AstrBot 平台用户 ID，取消 `staffId|dingtalkId` 模式参数。 | 所有子命令与 QQ 提及、提醒分别验证。 |
| `/menu` | 保留；`C` 管理用户／群快捷命令。 | 添加、删除、列表、触发词、群菜单及权限重验。 |
| `/!`、`/！`、`!`、`！` | 保留；`runner/src/core/queue.ts` 中断本会话当前任务。 | 不影响其他群或私聊；中断后队列可继续。 |
| `/reboot` | 适配；改为 AstrBot 插件重载与核心进程重启，取消 PM2、在线更新包操作。 | 管理员可重载；普通用户拒绝；旧参数有说明。 |
| `/destroy` | 适配；解绑群配置并清理插件专属数据，工作目录删除须单独明确授权。 | 不能跨群执行；配置移除后群消息不再进入代理。 |
| `/freedom` | 适配；改为“群内非白名单可对话但只读”的明确群策略，不能跳过文件权限。 | 开关前后非白名单始终无法写入。 |
| `/qa` | 适配；改为真实只读隔离策略；`gitRepos`／`docs` 输入仍须受目录与网络工具策略约束，`autoPull` 不得在只读模式写项目。 | 只读模式下 Shell／MCP／Hooks 与仓库拉取均无法写入。 |
| `/model` | 保留；`C` 管理当前会话模型和可用列表。 | 查询、切换、增删；两代理模型选项分别校验。 |
| `/a2a` | 适配；`A` 保留 `list`、`info`、`send`、`status`、`cancel`、`discover`；`send` 显式指定目标群。 | 六种子命令、来源身份、目标群与权限上限逐项验证。 |

`/cfg` 的参数级映射以“配置字段映射”表为准；`/open shell|code|folder`、`/reboot --update` 等危险或本机桌面专属行为只取消原协议形式，不取消管理页与插件重载能力。

## 配置字段映射

来源：`cc-ding/src/biz/types.ts` 的 `IConfig`、`IConversation`、`IQaCfg`、`IClaudeSetting`，以及 `console.ts` 的管理配置。同行列出的每个字段使用同一目标、分类与验收动作；实施时仍须逐字段测试。

| 原字段 | 分类、目标与原因 | 验收动作 |
| --- | --- | --- |
| `clientName`, `model` | 保留；插件显示名与默认模型，进入插件配置。 | 修改后群默认值生效。 |
| `whiteUserList`, `owner`, `adminUserList` | 适配；从手机号／工号改为平台稳定用户 ID；`P` 计算角色。 | QQ ID 识别、角色变更与只读降级。 |
| `clientSecret`, `dingSecret`, `defaultDingToken` | 取消钉钉 Stream／Webhook 协议字段；由 AstrBot 平台适配器管理平台认证。 | 新配置不包含字段；消息收发使用 AstrBot。 |
| `ownerConversationId`, `enableMsgToUser` | 适配；管理员通知目标与私聊开关由 AstrBot 路由管理。 | 通知与私聊启停，不能给非目标用户发消息。 |
| `conversations` | 适配；群／私聊路由配置集合。 | 未配置群拒绝，已配置群与私聊隔离。 |
| `taskQueueSize`, `taskHandlerCount`, `sessionMaxConcurrency` | 保留；任务队列与并发配置。 | 边界数量、出队顺序及权限重验。 |
| `includeThinking`, `resultOnly` | 保留；回复展示选项，敏感推理内容须按代理能力审查。 | 两种代理输出模式可切换。 |
| `apiKeyCfg.resetTime`, `apiKeyCfg.modelSettings`, `apiKeyCfg.retryLogs` | 保留；受保护的密钥池、轮换与错误重试规则。 | 密钥脱敏、轮换、重试、不可用恢复。 |
| `debug` | 保留；插件日志级别，不向 QQ 泄露敏感配置。 | 开关日志且脱敏。 |
| `preBash` | 适配；如保留预执行命令，必须独立配置为可用 Shell 工具且在隔离环境内运行。 | 禁用 Shell／只读时不得写入或越界。 |
| `recorderCfg.dist` | 适配；插件专属数据区的录制路径。 | 不写入工作目录或越界。 |
| `maxTurnTimeMins`, `maxAutoRecovery` | 保留；看门狗（Watchdog）阈值和恢复次数。 | 可控制超时触发与停止重试。 |
| `cardTemplateId`, `cardTemplateKey` | 取消钉钉 AI Card 协议字段；对应流式体验由 AstrBot 回复能力实现。 | QQ 进度／最终回复可见，不需要卡片模板。 |
| `envs` | 适配；受控代理环境变量，不允许通过变量绕开目录或泄露凭据。 | 两代理接收允许变量，敏感值不回显。 |
| `retryCfg.maxDurationSecs`, `retryCfg.maxCount`, `retryCfg.minCountForDuration`, `retryCfg.retryCooldownSecs` | 保留；重试风暴检测与密钥冷却。 | 阈值边界和停止条件。 |
| `a2aCfg.hubUrl`, `a2aCfg.apiKey`, `a2aCfg.remoteAgents` | 适配；`A` 的 Hub 地址、认证与远端列表。 | 连接、认证失败、目标群授权及禁用 A2A。 |
| `a2aCfg.remoteAgents[].id`, `name`, `baseUrl`, `apiKey`, `defaultSkill` | 保留语义；远端代理元数据与技能配置，受 `A` 权限约束。 | 逐字段读写脱敏、发现与任务调用。 |
| `conversationId`, `conversationType`, `conversationTitle` | 适配；分别改为平台群／用户稳定 ID、群／私聊枚举和显示名。 | 同名不同 ID 不串会话；平台重启后稳定。 |
| `linkConversationId` | 适配；显式会话共享关系，默认不跨群共享目录。 | 未授权跨群链接拒绝。 |
| `workDir` | 保留；按群／私聊配置，必须规范化并由各平台代理的已验证权限配置实际限制。 | 目录内读写、目录外拒绝和符号链接逃逸。 |
| `dingToken`, `mobile` | 取消钉钉 Webhook／手机号字段；改用 AstrBot 平台路由与用户 ID。 | 新配置无字段，QQ 消息正常路由。 |
| `whiteUserList`, `agent`, `model`（会话级） | 保留语义；群／私聊白名单与代理、模型覆盖配置。 | 会话级优先级及两代理切换。 |
| `useLocalOcr` | 保留语义；图片识别降级能力。 | 不支持视觉的模型收到受控 OCR 文字。 |
| `atSender` | 适配；AstrBot 提及发送者。 | QQ 群提及目标正确，私聊不误用。 |
| `receiveReply`, `receiveReplyMode`, `ackReaction` | 适配；确认回复与平台可用的文本／表情能力。 | 平台不支持表情时有文本降级。 |
| `preBash`, `permissionMode`, `freedomMode`（会话级） | 适配；分别进入隔离 Shell、有效文件权限、群内只读对话策略；禁止 `bypassPermissions` 与以 `plan` 假装只读。 | 群级上限和工具交集测试，旧危险值拒绝。 |
| `sessionCfg`, `taskCfg.skill` | 保留语义；会话与任务使用的技能元数据。 | 任务只可选择当前允许技能。 |
| `qaMode`, `qaCfg` | 适配；真实只读策略和受控外部参考。 | 只读期间无法写项目、无法读目录外文件。 |
| `qaCfg.gitRepos`, `qaCfg.docs`, `qaCfg.autoPull` | 适配；参考资料输入和拉取行为必须经过工具／目录权限。 | 不允许的网络工具或只读写入被拒。 |
| `maxTurnTimeMins`, `streaming`, `ensureAt`（会话级） | 适配；超时与平台回复能力。 | 群级覆盖全局，QQ 不支持时有明确降级。 |
| `envs`, `teamAgents`（会话级） | 适配；受控变量与 A2A 可见代理列表。 | 变量脱敏，跨群调用经过目标授权。 |
| `IClaudeSetting.isValid`, `apiKey`, `baseUrl`, `model`, `smallModel`, `memo` | 保留语义；密钥管理（Key Management）页面及运行器配置。 | 每字段 CRUD、密钥脱敏、禁用后不被选用。 |
| `console.port`, `console.host`, `console.authUsers`, `console.remoteConsoles`, `updatePkgUrl` | 适配／取消协议形式；页面使用 AstrBot 后台鉴权，取消独立 Console 监听、局域网扫描、远端更新包；跨实例管理若需要须另设受信任接入，不以旧地址透传。 | 页面只对后台管理员开放；无独立公开端口、默认密码或任意 URL 代理。 |

新字段必须包括群级 `file_access`、群级 `allowed_tools`、用户级 `file_access`、用户级 `allowed_tools`、私聊目录／权限与 A2A 来源身份；有效权限取交集，空配置失败关闭。字段最终命名在 T04／T06 的协议实现中统一，不把示意名散落在模块里。

## Web Console 管理能力映射

来源：`cc-ding/src/biz/console.ts` 的 HTTP 路由。同行列出的每个路由独立保留验收项；目标统一是 AstrBot 插件页面（Plugin Page）与受保护后端（`W`），不原样公开 HTTP 接口。

| 原接口／能力 | 分类与目标 | 验收动作 |
| --- | --- | --- |
| `/api/login`, `/api/change-password` | 适配；改用 AstrBot 后台登录态，取消独立默认管理员密码。 | 未登录／非管理员拒绝；后台管理员可进入。 |
| `/api/status`, `/api/clients`, `/api/clients/:id/config`, `/api/clients/:id/config/raw`, `/api/clients/:id/config/reload` | 适配；状态、插件实例、配置查看／编辑／生效。 | 每项读写、权限重算、敏感字段脱敏。 |
| `/api/clients/:id/conversations`, `/api/clients/:id/conversations/:convId` | 适配；群／私聊的增删改查。 | 配置变更后路由、目录和会话隔离。 |
| `/api/clients/:id/start`, `/api/clients/:id/stop`, `/api/clients/:id/pm2`, `/api/clients/:id/pm2/restart` | 适配；改为插件核心状态和受保护的重启；取消 PM2 控制。 | 后台管理员可查询／重启，未授权拒绝。 |
| `/api/clients/:id/apikeys`, `/api/clients/:id/apikeys/:index`, `/api/global/apikeys`, `/api/global/apikeys/:index`, `/api/global/apikeys/reorder` | 保留密钥池 CRUD、排序与脱敏语义；由 `W` 管理。 | 增、查、改、删、排序；旧密钥永不回显。 |
| `/api/global/retrylogs`, `/api/global/config`, `/api/global/settings-tpl`, `/api/global/raw-config` | 适配；插件配置、重试规则、设置模板与原始配置查看／编辑。 | 管理员变更后校验 schema；不暴露密钥。 |
| `/api/clients/:id/files` | 适配；仅列允许的插件配置文件与会话数据，不成为任意文件读写通道。 | 路径穿越、符号链接和非管理员访问拒绝。 |
| `/api/a2a/stats`, `/api/a2a/agents`, `/api/a2a/tasks` | 保留 A2A 统计、代理列表、任务记录语义。 | 页面逐项查询且按目标群授权过滤。 |
| `/api/ping`, `/api/remote/status`, `/api/remote/scan`, `/api/remote/clients`, `/api/remote/global/*` | 取消独立 Console 的公开探测、局域网扫描与任意远端代理形式；本机页面能力与显式 A2A 远端替代。 | 无公开探测端口和任意 URL 代理；A2A 显式远端可用。 |
| `/api/global/update-pkg-url`, `/api/update`, `/api/remote/update`, `/api/batch/update` | 取消 npm／PM2 远端更新形式；插件升级走 AstrBot 插件管理。 | 页面提供升级说明，不能从聊天触发系统安装。 |
| `/api/batch/restart`, `/api/batch/reload-config`, `/api/machine/restart`, `/api/machine/reload-config`, `/api/console/restart`, `/api/remote/console/restart`, `/api/batch/console-restart` | 适配／取消远端形式；本机插件重载与配置热更新，远端实例须显式受信任。 | 本机重载后会话恢复，远端旧 URL 不可直接操作。 |

原 Console 前端位于 `cc-ding/console-web/`；迁移时按上述用户能力重建页面，不照搬原 HTTP 认证、PM2 或远端代理。页面的任务、日志和会话视图在 T13 中逐项落实，不能因为旧 `console.ts` 未提供单独路由就遗漏。

## A2A、消息与内部能力映射

| 来源 | 分类与目标 | 验收动作 |
| --- | --- | --- |
| `a2a/server.ts` Agent Card、健康探测、JSON-RPC `tasks/send`、`tasks/sendSubscribe`、`tasks/get`、`tasks/cancel` | 保留协议语义；`A` 要求显式目标群、来源身份和权限上限。 | 每个方法正常与越权样本、任务状态与取消。 |
| `a2a/hub.ts` 注册、心跳、代理／客户端／统计／任务查询 | 保留 Hub 语义；认证、目标群路由与失败关闭。 | 注册、断连、过期、查询、重连测试。 |
| `a2a/client.ts` 直连与 Hub 路由；`a2a/auth.ts` 鉴权；`a2a/session-mapper.ts` 状态 | 保留业务语义；去除默认首个会话和 `a2a-remote` 伪身份。 | 无来源、错误群、只读来源写入、重试重复任务均拒绝。 |
| `messaging.ts` 文本／Markdown、分段、提及、确认表情、群／私聊发送 | 适配到 `R` 的 AstrBot 消息链。 | 文本、长文、提及、回复、失败重试；不使用 Ding Webhook。 |
| `image.ts` 与 `messaging.ts` 图片／文件发送和下载、`quote.ts` 引用、富文本段 | 适配到 `bridge/events.py` 与 `R`。 | QQ 图片、文件、引用、富文本样本；不支持形态有文本降级。 |
| `session.ts` 会话、恢复、日志、队列；`dedup.ts` 去重；`send-queue.ts` 发送队列 | 保留业务语义，拆成 `S`／队列（Queue），数据放插件专属区。 | 群共享、私聊独立、重启恢复、重复消息、权限降级。 |
| `task.ts`／`task-runner.ts`，`cron.ts`，`timer.ts`，`todo.ts`，`menu.ts` | 保留任务、调度、待办、菜单；后台任务执行时重验权限。 | 各功能 CRUD、定时触发、权限变更和幂等性。 |
| `model.ts`、`api-key-manager.ts`、`secrets.ts`、`watchdog.ts`、`streaming.ts`、`recorder.ts` | 保留模型、密钥、看门狗、进度和录制语义；输出改走平台接口。 | 模型切换、密钥轮换、超时恢复、流式降级、录制访问。 |
| `claude-process.ts`、`claude-agent.ts`、`codex-agent.ts` | 保留两种 CLI 的流式／JSON 解析、恢复和取消；由平台权限运行器启动，未验证组合默认禁用。 | 两种真实 CLI 多轮与降权恢复测试。 |

## 依赖边界与迁移顺序

1. `cc-ding-cli.ts` 的 `DingClaude` 同时拥有钉钉 Stream 回调、命令路由、任务、管理和 A2A，是平台耦合点；新 `main.py` 只做 AstrBot 生命周期和事件入口，Node 核心只接收平台无关消息封套（Message Envelope）。
2. `session.ts` 的 `DingClaude` 类型、`conversationId`、`senderStaffId`、`sessionWebhook` 与 `messaging.ts` 直接发送耦合；新会话层改用平台／会话／用户稳定 ID 与回复事件（Reply Event），权限在入队、出队及恢复时重算。
3. `claude-process.ts` 和 `codex-agent.ts` 直接导入钉钉发送方法及巨型类；先抽代理事件接口，再让它们只依赖隔离运行器与输出接口。不能复制现有 `bypassPermissions`、Codex `danger-full-access`。
4. `console.ts` 直接读写独立客户端和系统进程；管理页经 AstrBot 鉴权与核心权限决策后操作插件数据。A2A 同样经过统一权限链。
5. 先验证 T02 真实隔离，再建立 T03–T08 的核心边界，最后迁移 T09–T14 用户能力。没有 T02 通过证据不能开始代码迁移。

## 待实施时逐项裁决的问题

- 私聊默认开放对象、初次目录配置及管理员通知方式；需要在 T04／T06 形成可验证配置语义。
- 工具允许集如何映射到两种 CLI 的原生工具、Skills、MCP、Hooks；T02 必须先证明拟开放的平台／代理／工具组合有效，未验证组合默认禁用。插件运行不依赖 WSL／Ubuntu。
- 页面是否保留跨机器实例管理：旧任意 URL 代理不符合当前权限模型；如要保留用户能力，须设计显式受信任的实例注册和鉴权。

这些问题属于本轮范围内的待细化项，不是延期项（Deferred Scope）。OpenCode、Pi 的明确延期及触发条件见对齐文档与计划。
