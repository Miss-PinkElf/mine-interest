# QQ 多代理 AstrBot 接入决策日志（Decision Log）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 21:43:08 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录经对齐确认的架构与范围取舍。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：设计回退中（Propose Revision）
- 文档边界（Scope / Boundary）：决策记录真相源（source of truth）；记录已确认方向和候选细节，不触发实施。

## 已确认

- 2026-09-28：按用户要求采用 devflow 重型路径（Heavy Route）。
- 2026-09-28：文件访问权限与工具调用权限分开配置；非白名单用户只能读取指定工作目录，不能读取其他目录或编辑文件。具体隔离机制仍待设计确认。
- 2026-09-28：白名单用户也只能访问指定工作目录，但可在该目录内读写。
- 2026-09-28：每个启用的 QQ 群对应一个固定工作目录。
- 2026-09-28：确认以 `cc-ding` 通用核心为迁移基础，由 AstrBot 插件替换钉钉消息与身份适配；不是重新实现独立业务服务，也不是原样复制钉钉入口。
- 2026-09-28：本轮支持 Claude Code 和 Codex；同一 QQ 群内共享代理会话，私聊独立控制权限；群级可配置只读和工具权限；代码需按模块职责拆分，降低耦合。
- 2026-09-28：群级权限为上限，每条消息按发送者身份与群级配置取更严格的文件权限；工具调用也取双方配置交集，私聊独立配置。
- 2026-09-28：“完整迁移”包含 `cc-ding` 的 Web Console 管理能力与代理间通信（A2A）；钉钉专属字段和交互需映射到 AstrBot，而不是照搬协议。
- 2026-09-28：用户明确要求对齐文档写完后直接编写计划；对齐与实施顺序分别落在 `plans/2026-09-28-cc-ding迁移astrbot需求对齐.md`、`plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`，未越过规格与任务门禁。
- 2026-09-28：用户指出仅要求对齐后直接写计划，不等于批准进入实施。已把开放规格（OpenSpec）三件套标记为待审阅草稿，撤回 T01 的实施中标记；插件代码未改。

## 本轮不做 / 后续阶段（Deferred Scope）

- 对象或能力：OpenCode、Pi 及其他代理适配。
- 本轮暂不做的原因：用户要求先完整迁移 `cc-ding` 已支持的 Claude Code 与 Codex，避免同时扩大代理适配和平台迁移范围。
- 后续触发条件或推荐阶段：Claude Code、Codex 的 AstrBot 迁移及权限边界完成验证后，进入多代理扩展阶段；届时沿本轮抽出的代理接口增加适配器。

## 待确认

- 计划采用插件管理的 Node 运行进程与标准输入／输出通信；具体协议和隔离方式仍需开放规格（OpenSpec）及可行性验证。

## 2026-09-28 23:58:41 +08:00｜运行平台与权限机制修正

- 用户明确插件最终运行于 Windows 或 macOS，不以 Ubuntu／WSL 为前置条件。之前先在 WSL 安装 `bubblewrap` 的探索仅是验证候选方案，不构成产品架构决策；插件代码尚未开始。
- 非白名单只读优先使用 Claude Code、Codex 的原生权限能力，文件权限与工具权限仍分开配置；但“不能读取工作目录外用户文件”仍需按代理和工具组合实测，不能仅由 `plan`／`read-only` 模式名称推断。
- Claude Code 官方 Shell 沙箱支持 macOS，不支持原生 Windows；原生 Windows 的 Shell、MCP、Hooks 等未验证组合默认禁用。Codex 官方权限配置支持原生 Windows 和 macOS，可定义目录外拒读的自定义配置，仍需本机验证。
- T02 改为平台／代理／工具组合矩阵。只对全部越权样本通过的组合开放功能；未通过的组合回退设计。macOS 无实机时明确记为未验证，不作为已验收能力。Web Console 与 A2A 仍属本轮迁移范围。
- 钉钉专属命令、AI Card、用户工号、Webhook 等在 AstrBot 的逐项功能映射与验收标准。

## 2026-09-29 00:10:27 +08:00｜Codex 原生 Windows 权限门禁失败

- 用户已允许初始化 Codex elevated Windows 沙箱。实测内置 `:read-only` 仍可读取工作目录外文件；自定义 `:root = deny` 在普通后端要求 elevated，在 elevated 后端被 `requires effective ':root' read access` 拒绝。
- 这些结果与“所有用户均不得读取工作目录外文件”冲突。保持该要求，不将只读写入限制冒充目录外拒读；按 devflow 从实施（Apply）回退提案（Propose），T03 及后续插件代码迁移暂缓。
- 下一轮方案必须在 Windows／macOS 原生运行，具有真实进程级目录边界，并覆盖代理启动、会话恢复、子进程、符号链接／联接目录及工具权限。该方案目前是候选项（Candidate），未获实测或批准。

## 2026-09-29 00:20:00 +08:00｜交接与范围记录

- 用户要求本轮交接并提交当前 mission 相关文件，下一对话继续；这是阶段暂停，不代表实施（Apply）或正式关闭（Close）完成。
- 首版交付边界尚未与用户逐项讨论；Web Console、A2A、任务、调度、媒体、命令等仍属于已确认的完整迁移目标，不能因尚未实现就自行归为延期。
- OpenCode、Pi 已明确延期，详见 `deferred/agent-expansion.md`；其他问题列为待讨论项（Open Questions），不是已批准延期。
