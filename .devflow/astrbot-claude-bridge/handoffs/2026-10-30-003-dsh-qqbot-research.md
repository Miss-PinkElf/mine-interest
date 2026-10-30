# 官方 dsh-qqbot 对比调研交接（Session Handoff）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-30 14:40:00 +08:00
- 作者（Author）：Claude
- 目的（Purpose）：交接本轮官方插件调研结论、T02 选型候选项、未讨论事项与下一步，供新对话直接恢复。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 调研产出（Research Output）：`.devflow/astrbot-claude-bridge/spec/2026-10-30-腾讯dsh-qqbot对比调研.md`
- 前一份交接（Previous Handoff）：`.devflow/astrbot-claude-bridge/handoffs/2026-09-29-002-t02-design-revision.md`
- 当前状态（Status）：交接暂停，待设计选型（Handoff / Awaiting Decision）
- 文档边界（Scope / Boundary）：恢复用交接记录，不替代 `state.md`、`spec/` 与实测证据；未完成实施（Apply）或正式关闭（Close）。

## 当前目标与阶段

目标不变：复用并模块化迁移 `cc-ding` 通用核心，由 AstrBot 插件替换钉钉平台适配；本轮只支持 Claude Code、Codex；QQ 群每群一个固定工作目录并共享会话，私聊独立；**所有用户均不能读取工作目录外文件**，白名单用户在目录内可读写，非白名单用户在目录内只读；群级与用户级权限取交集。插件须在 Windows／macOS 原生运行。

当前仍在提案修订（Propose Revision）阶段：T01 已完成，T02（原生 Windows 目录隔离实测）未通过，T03 及后续代码迁移未开始。

## 本轮完成内容

1. 克隆腾讯官方 `@tencent-connect/dsh-qqbot`（0.5.4，HEAD `70371b3`）到 `tmp/refs/dsh-qqbot`（已被 `.gitignore` 忽略，不入库）。
2. 从其源码做三个维度的调研：权限与审批模型、会话与消息链路、宿主耦合度；同时调研本仓库 `cc-qq` 插件架构，形成三方对照。
3. 产出 `spec/2026-10-30-腾讯dsh-qqbot对比调研.md`，状态为候选项（Candidate），不是真相源、不代表批准方案、不触发实施。
4. 更新 `state.md`、`decision-log.md`、`backlog.md`、`checkpoints.md`、`workflow.md`、`origin.md`、`handoffs/index.md`，旧状态归档到 `state-history.md`、旧 checkpoint 归档到 `checkpoints-archive.md`。
5. 未修改任何插件代码，未升版本，未覆盖本机 AstrBot 插件目录。

## 关键结论

1. **两者解决的不是同一问题**：dsh-qqbot 是"DSH 自家 agent 接 QQ"的渠道插件，本 mission 是"外部 CLI 接 QQ"的代理桥。
2. **官方实现没有解决 T02 的问题，而是绕开**：无只读档、无工具级白/黑名单、无进程级目录外拒读；靠「白名单准入 + 独立 workspace + 审批卡片」兜底。
3. **它消息工程强、权限隔离弱**：流式双轨、被动回复三级兜底、审批 nonce、交付物投递值得借鉴；单 workspace 全局共享、无审计、无审批超时不可照搬。
4. **它自带的两个边界缺陷不要学**：`qqbot_describe_image` 绕过路径白名单；`qqbot_send_file` 的 `target` 不校验归属。
5. **附带查实 `cc-qq` 三条缺口**（跨 mission 观察，未登记）：群级与用户级未取交集（群规则可把 guest 提升到 full）、`allowed_work_dirs` 不约束群规则初始 `work_dir`、Codex 无逐次审批。

## T02 候选项（均未批准）

| 候选项 | 做法 | 代价 |
| --- | --- | --- |
| A. 需求降级（参照官方） | 非白名单用户不服务，"只读"降为可选体验档 | 改变已对齐的需求边界，但可立即解开 T02 |
| B. 维持需求，缩小可开放面 | Windows 不开放 Codex；Claude Code 只开已实测的基础文件工具；macOS 用官方沙箱单独实测 | 与"本轮支持 Codex"冲突，需重新谈范围 |
| C. 引入外部隔离 | 容器 / 沙箱进程 / WSL | 与"Windows／macOS 原生运行"冲突（WSL 已被用户否决） |

判断：A 与 B 是同一事实的两面——T02 的根因不是"配置没调对"，而是"Codex 在原生 Windows 上不提供该边界"。**选型未定前不得修改设计、计划或代码。**

## 未讨论 / 待决定事项

- T02 走 A 还是 B（阻塞项，优先级最高）。
- 首版（First Version）交付边界：哪些命令、媒体、任务、Console、A2A 能力进入第一版。
- 调研中 8 项可借鉴设计，逐项判定"进本 mission 首版 / 进 `cc-qq` 排期 / 仅记录"。
- 图片理解与视觉能力是否要做、如何做（官方实现的路径校验有缺陷）。
- `cc-qq` 三条缺口是否登记进 `.devflow/cc-qq-full-migration/backlog.md`（本 mission 未擅自修改另一 mission 真相源）。
- macOS 仍无任何实机证据，不得宣称通过。

以上除 OpenCode／Pi 外，均属未讨论项，**不是已批准延期**。详见 `backlog.md`。

## 阻塞

- T02 阻塞未解除：尚无经实测满足"工作目录外拒读"的 Codex 原生 Windows 方案。本次调研确认业界官方实现也未解决该问题，只能作为需求取舍先例，不能当作技术方案。
- 工具边界：Claude Code 原生 Windows 无官方 Shell 沙箱；Shell、Skills、MCP、Hooks、后台恢复均未验证，保持关闭。

## 当前仓库边界

- 未修改 `integrations/astrbot/` 下插件代码，未改变插件版本或部署本机副本。
- 本轮只提交 `.devflow/astrbot-claude-bridge/` 下的文档；`.devflow/astrbot-plugin-e2e/`、`zzz-prompt-debug/接入agent/prompt-01.md`、`.gitignore`、`config.ts`、`tsconfig.json` 的既有改动与本次对话无关，未纳入提交。
- `tmp/refs/dsh-qqbot` 是被忽略的本地克隆，不随仓库交付；新环境复现需重新克隆。

## 立即下一步

1. 先读 `state.md`、`checkpoints.md`、本文件与 `spec/2026-10-30-腾讯dsh-qqbot对比调研.md`。
2. 与用户确认 T02 选型 A 或 B。
3. 按选型修订需求对齐、计划与开放规格（OpenSpec），更新 `spec/permission-matrix.md` 的结论，重跑 T02 全矩阵。
4. T02 全部越权样本通过后，才恢复 T03 插件骨架与后续迁移；每次插件代码变更须提升版本并覆盖本机 AstrBot 对应位置。

## 恢复指引

- 默认恢复热路径：`state.md` + `checkpoints.md`。
- 需要完整过程：`development-overview.md`（若存在）、`state-history.md`、`checkpoints-archive.md`。
- 需要原始输入与延期项：`origin.md`、`backlog.md`、`deferred/agent-expansion.md`。
- 以最新仓库事实与用户指令为准。
