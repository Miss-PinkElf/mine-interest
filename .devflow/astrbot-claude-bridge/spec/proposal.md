# cc-ding 迁移 AstrBot 插件提案（Proposal）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 22:26:33 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：定义本轮完整迁移的动机、范围、非目标和异常边界。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 对齐文档（Aligned Requirement）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding迁移astrbot需求对齐.md`
- 实施计划（Implementation Plan）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`
- 参考实现（Reference Implementation）：`cc-ding/`
- 当前状态（Status）：待修订（Revision Required）
- 文档边界（Scope / Boundary）：本 mission 的提案真相源（source of truth）；与设计、任务一起构成实施依据，单独不触发实施（Apply）。

## 背景

`cc-ding` 已具备 Claude Code、Codex、会话、任务、定时、管理界面和代理间通信（A2A）等成熟能力，但消息接入、身份和回复散落着钉钉协议依赖。本机 AstrBot 已通过 NapCat／OneBot 接入 QQ，插件可处理统一消息事件。用户希望保留 `cc-ding` 的通用能力和插件使用便利性，并按用户及群级配置约束工作目录和工具。

## 目标

1. 以 AstrBot 插件替代钉钉平台接入，使 QQ 群聊、私聊能够使用 Claude Code 与 Codex。
2. 迁移 `cc-ding` 的通用能力，包括 Web Console 管理能力和 A2A；对钉钉专属能力给出明确的 AstrBot 等价映射或取消理由。
3. 群内共享会话、每群固定工作目录；私聊每用户独立会话与目录配置。
4. 白名单用户最多在工作目录内读写，非白名单用户只读；群级策略为上限，工具调用另行配置并取交集。
5. 权限覆盖聊天、后台任务、A2A、管理页及代理扩展入口，使用可验证的隔离边界。
6. 将平台、权限、会话、代理与业务功能拆成单一职责模块，方便后续增加新代理。

## 范围

- 可追踪的 AstrBot 插件源码、Node 核心、插件配置、插件页面、许可、README 和测试。
- Claude Code、Codex 原生能力及会话恢复，Skills、MCP、Hooks 在各代理自身支持范围内加载，工具由代理从本次有效可用列表中自主选择。
- `cc-ding` 的消息与会话、队列中断、任务、Cron、Timer、Todo、Menu、模型、密钥、图片文件、日志、看门狗、Console 和 A2A 功能迁移。
- 本机 AstrBot Desktop 插件覆盖、版本提升、重载及真实 QQ 验收。

## 非目标

- 本轮不接入 OpenCode、Pi 或其他新增代理。原因是先完成已有两种代理的平台和权限重构；在 Claude Code、Codex 的迁移与权限验收完成后进入多代理扩展阶段。
- 不保留钉钉 API、Ding Token、手机号／工号、Webhook、AI Card 或 PM2 控制的原始协议形式；保留其可在 AstrBot 表达的用户功能。
- 不顺带修复无关 TypeScript 报错或执行全局 ESLint；不改动既有其他 AstrBot 插件。

## 边界场景

- 群共享会话中，白名单用户先写入，非白名单用户随后只读提问；恢复会话也不得继承写权限。
- 配置在任务排队或定时等待期间变更；实际执行时必须重新求有效权限。
- A2A 来源无身份、目标群不匹配或请求写权限高于来源权限时拒绝；不沿用原实现默认第一个会话和 `a2a-remote` 身份。
- 符号链接、联接目录、相对路径、Shell、Skills、MCP、Hooks 均不能越过文件边界；隔离验证不通过时回退设计。
- 插件重载、Node 进程退出、CLI 缺失或认证失效时，已保存会话和任务不能静默丢失，用户收到不泄露内部信息的错误反馈。
- 管理页面必须使用 AstrBot 鉴权，并对敏感配置和密钥做脱敏；页面操作不自动获得代理文件权限。

## 开放问题与门禁

- 原生 Windows Codex 目录外拒读方案已在 T02 实测失败；候选替代方案尚未确认。当前提案仍保持完整迁移目标，但不得跳过隔离设计修订进入 T03。
- 权限实现需在最早实施任务中按 Windows／macOS、Claude Code／Codex 和工具组合分别验证。插件运行不依赖 WSL／Ubuntu；原生 Windows 的 Claude Code Shell 沙箱不受官方支持，Shell 等高风险组合验证前默认禁用。macOS 缺少实机时不得以 Windows 结果代替验收。
- AstrBot 对不同平台的图片、文件、引用、提及和流式反馈能力需要逐项验证。QQ 端是本轮真实验收平台，其余平台只要求接入架构不绑定 QQ 专属协议。
- 钉钉专属命令与 Console 字段的逐项映射以 `spec/feature-mapping.md` 为任务产物；不得把未映射项默认为已完成。

## 本轮不做 / 后续阶段（Deferred Scope）

| 对象或能力 | 本轮暂不做的原因 | 后续触发条件或推荐阶段 |
| --- | --- | --- |
| OpenCode、Pi 及其他代理适配 | 先完成 Claude Code、Codex 的平台迁移与权限验证。 | 本轮真实 QQ 与目录权限验收通过后，进入多代理扩展阶段。 |
