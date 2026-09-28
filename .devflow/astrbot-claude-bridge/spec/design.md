# cc-ding 迁移 AstrBot 插件设计（Design）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 22:26:33 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：定义插件、TypeScript 核心、代理执行与权限边界的结构和接口。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 对齐文档（Aligned Requirement）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding迁移astrbot需求对齐.md`
- 实施计划（Implementation Plan）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`
- 当前状态（Status）：待修订（Revision Required）
- 文档边界（Scope / Boundary）：本 mission 的设计真相源（source of truth）；与提案和任务共同约束实施，未通过隔离验证前不宣称权限设计成立。

## 总体思路

AstrBot 插件负责平台边界，迁移后的 `cc-ding` 核心负责业务边界。两者通过插件私有的标准输入／输出（stdio）管道传递消息封套（Message Envelope）和事件；不暴露 Node 进程的控制 HTTP 端口。A2A 网络服务只有显式启用并完成目标群授权后运行。

```text
AstrBot 平台事件
  → Python 事件映射（事件 ID、平台、群／用户、消息段）
  → Node 核心入口（命令或代理消息）
  → 权限决策（每次请求求交，后台执行再求交）
  → 会话／任务队列
  → 隔离运行器（按本次权限创建执行边界）
  → Claude Code 或 Codex
  → Node 核心输出事件 → Python 回复映射 → AstrBot 平台发送
```

## 结构与边界

### AstrBot 插件

- `main.py` 只负责注册事件、配置变更和生命周期回调。
- `bridge/events.py` 把 AstrBot 消息转为 `IncomingMessage`，保留稳定的平台 ID、群 ID、QQ 用户 ID、消息 ID、群聊／私聊类型和文本／图片／文件／引用／提及段。
- `bridge/process.py` 管理 Node 进程的启动握手、请求编号、响应关联、取消、超时、重启和标准错误日志。父进程终止时清理子进程；子进程重启后从插件数据区恢复会话。
- `bridge/replies.py` 把核心输出映射回 AstrBot 消息接口。平台不支持的消息形态使用可理解的文本降级，并记录原因。
- `bridge/web.py` 注册插件页面 API，使用 AstrBot 已登录的后台身份作第一层鉴权，管理操作在 Node 核心继续校验管理员角色。

### TypeScript 通用核心

- `contracts.ts` 定义 `IncomingMessage`、`ReplyEvent`、`ExecutionContext`、`EffectivePolicy`、`AgentRunRequest` 和错误码；类型中不保留钉钉工号、Webhook 或 Token。
- `policy/evaluate.ts` 计算角色和群／私聊策略。有效文件级别是用户上限与会话配置上限的较严格者；有效工具集是用户、会话与代理支持集的交集。未配置群、未知身份、无效目录或无法识别的工具配置均拒绝执行。
- `core/session.ts` 使用 `platform_id + group_id + agent_type` 作为群会话键，使用 `platform_id + user_id + agent_type` 作为私聊键。群共享历史，代理类型之间保持独立的原生会话 ID。
- `core/queue.ts` 保留 `cc-ding` 的排队、中断与去重语义；入队记录原始发送者，出队重新求权限。中断只作用于目标会话当前任务。
- `features/` 拆分任务、调度、协作命令、模型与密钥等功能；消息发送通过平台输出接口，不直接调用 AstrBot 或钉钉 API。
- `a2a/` 保留协议和 Hub 能力，调用目标会话时必须带可验证的来源、目标群和权限上限；缺失来源时默认拒绝，不能使用伪造 QQ 身份。

### 代理与隔离运行器

- Claude Code、Codex 适配器只负责命令参数、输入输出事件、会话恢复和代理能力元数据；不判断 QQ 白名单。
- 权限运行器接收 `AgentRunRequest` 中的规范化目录、只读／读写级别和可用工具集，按宿主平台与代理选择已验证配置；任何未验证组合失败关闭。Claude Code 原生 Windows 以只读模式、无头拒绝模式、目录外读取限制及工具允许集组合验证。**Codex 的 Windows 原生沙箱加自定义根目录拒读配置已实测失败，本条执行边界尚无可实施方案；T02 通过前不得据此开发代理启动器。**macOS 分别验证两种代理的原生隔离。仅模式名称本身不构成通过证据。
- 对同一群共享会话的连续请求，代理进程可重新启动并恢复原生会话，但每次调用必须重新装载本次发送者的权限配置；禁止把白名单用户的运行进程直接交给非白名单用户续用。
- 工作目录与插件数据区分离：项目文件映射给隔离环境；会话、审计、凭据与配置留在受信任的插件数据区。代理运行所需的 Skills、MCP、Hooks 与认证资源由受控启动器加载；文件工具能否被限制在工作目录内必须用真实进程验证。
- 插件入口与 Node 核心在 Windows／macOS 原生运行，不要求 WSL／Ubuntu。Claude Code 官方内置 Shell 沙箱不支持原生 Windows；在缺少其他经验证的宿主边界时，该平台禁用 Claude Code 的 Shell 及可间接执行文件操作的未验证工具。macOS 使用官方内置沙箱作为候选，必须关闭非沙箱重试并验证读取、写入和子进程边界。Codex 的平台权限配置也须实测；macOS 未实测前只标为待验证。

## 数据流与接口

### 标准输入／输出协议（stdio IPC）

每行一个 JSON 对象，采用显式 `protocol_version`、`request_id`、`kind` 和 `payload`。`kind` 包括 `hello`、`message`、`reply`、`progress`、`cancel`、`status`、`error`。插件只接收自己启动的子进程输出；核心只接收插件管道输入。协议版本不符立即停止执行并报告配置错误。

### 身份与授权

1. Python 插件从 AstrBot 事件提取真实平台、群和用户标识，拒绝从用户文本读取身份字段。
2. TypeScript 核心读取配置和白名单，形成 `ExecutionContext`；群权限取用户与群策略交集，私聊使用用户与私聊策略交集。
3. 命令、代理工具、任务创建、任务执行、A2A 及管理操作均使用同一 `EffectivePolicy` 计算入口；调度或队列延迟执行时重新计算。
4. 不把拒绝理由中的绝对目录、密钥、令牌或内部调用栈发送到 QQ 群。

### 功能映射

- `cc-ding` 的会话、任务、命令解析、模型、密钥轮换、图片处理、看门狗与 A2A 是复用来源；迁移时把钉钉发消息回调替换为 `ReplyEvent`。
- 原 Web Console 的配置、会话、模型、密钥和状态页面映射到 AstrBot 插件页面（Plugin Page）；页面不直接读写核心数据文件，而是调用受保护 API。
- 钉钉手机号／工号、Ding Token、Webhook、AI Card、表情回执及 PM2 进程命令没有协议级复用价值；逐项映射为 QQ／AstrBot 身份、配置、回复与插件重载，或在功能映射表中说明取消理由。
- 逐命令和逐字段迁移状态记录于 `spec/feature-mapping.md`，每一项必须有验证证据，才能计入“完整迁移”。

## 风险与权衡

| 风险 | 处理方式 |
| --- | --- |
| `cc-ding` 的 `DingClaude` 巨型类与平台耦合 | 先定义平台无关契约，再逐模块抽取；不整份重写成 Python。 |
| 群共享历史与用户权限不同 | 每次请求重新求权限，重新创建隔离进程，后台任务保留创建者。 |
| CLI、Shell、MCP、Hooks 能访问目录外文件 | 按平台／代理／工具组合验证；未通过或未验证组合默认禁用，不把只读模式直接当作目录隔离。 |
| A2A 原实现默认第一个会话并使用 `a2a-remote` 身份 | 明确目标群与可验证来源，拒绝无身份和越权调用。 |
| 被忽略的本地 `cc-ding/` 无法随插件交付 | 将需要的源代码复制到可追踪插件目录，保留 MIT 许可。 |
| Node 子进程或 AstrBot 重载造成消息丢失 | 请求编号、持久化队列、重启恢复和幂等去重。 |
| 插件页面替换原 Console 后功能遗漏 | 逐功能映射表与页面验收清单。 |

## 本轮不做 / 后续阶段（Deferred Scope）

| 对象或能力 | 本轮暂不做的原因 | 后续触发条件或推荐阶段 |
| --- | --- | --- |
| OpenCode、Pi 及其他代理适配 | 本轮先完成已有 Claude Code、Codex 的完整迁移与安全边界。 | 真实 QQ 与权限验收通过后，沿代理适配接口进入多代理扩展阶段。 |
