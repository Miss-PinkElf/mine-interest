# QQ 多代理 AstrBot 接入当前状态（Current State）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 21:43:08 +08:00
- 更新时间（Updated At）：2026-10-30 14:40:00 +08:00
- 作者（Author）：Codex / Claude
- 目的（Purpose）：提供本 mission 的短当前快照。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：交接暂停，待设计选型（Handoff / Awaiting Decision）
- 文档边界（Scope / Boundary）：当前状态真相源（source of truth）；不代表实施（Apply）完成，也不代表 T02 已通过。

## 当前快照

- 用户指定重型路径（Heavy Route）；本轮只迁移 Claude Code 与 Codex，OpenCode、Pi 留待后续阶段。
- 群成员均可对话；所有用户的文件访问均限制在指定工作目录。白名单用户可读写，非白名单用户只可读取；工具调用权限单独配置。群级权限为上限，与用户级取更严格者；私聊独立配置。
- 本地参考项目为 `cc-ding/`，仓库现有 AstrBot 插件位于 `integrations/astrbot/`。
- 当前阶段：T01 逐功能映射清单已完成；T02 原生 Windows 实测未通过（Codex `:read-only` 可读取目录外文件，`:root = deny` 在普通及 elevated 沙箱均不能启动），已从实施（Apply）回退提案修订（Propose）。尚未修改插件代码。
- **2026-10-30 新增：完成腾讯官方 `@tencent-connect/dsh-qqbot` 0.5.4 源码级对比调研**，产出 `spec/2026-10-30-腾讯dsh-qqbot对比调研.md`（候选项，非批准方案）。调研结论：官方实现无只读档、无工具级白/黑名单、无进程级目录外拒读，采用「白名单准入 + 独立 workspace + 审批卡片」，因此**不能为 T02 提供技术方案**，只能提供需求取舍先例。
- **T02 现有三个候选项，均未获批准**：A 需求降级（非白名单不服务）、B 维持需求但缩小可开放面（Windows 不开 Codex 等）、C 引入外部隔离（与原生运行要求冲突）。未选型前不进入 T03。
- 未讨论项（首版边界、借鉴项分级、cc-qq 交叉缺口）已记入 `backlog.md`，不视为已批准延期。
- 已明确延期项仍仅 OpenCode / Pi，见 `deferred/agent-expansion.md`。
- 对齐文档：`plans/2026-09-28-cc-ding迁移astrbot需求对齐.md`；实施计划：`plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`（均待修订）。
- 最新交接：`handoffs/2026-10-30-003-dsh-qqbot-research.md`；下次提示词：`NEXT-SESSION-PROMPT-astrbot-claude-bridge.md`。

## 下一步

1. 由用户拍板 T02 走 A 还是 B（C 与"Windows／macOS 原生运行"冲突，仅作对照）。
2. 依据选型修订需求对齐、计划与开放规格（OpenSpec），重跑 T02 全矩阵。
3. T02 通过前不进入 T03 插件代码迁移；不得启用 Codex 代理执行，不得开放未验证的 Shell／MCP／Hooks 组合。

## 本轮不做 / 后续阶段（Deferred Scope）

- OpenCode、Pi 及其他代理适配：先完成 Claude Code、Codex 的迁移与权限验收；触发条件见 `deferred/agent-expansion.md`。延期不是永久放弃。
- 首版与完整迁移的阶段划分：仍未与用户确认；Web Console、A2A 等仍属已确认目标，见 `backlog.md`，不得自行归为延期。
- `cc-qq` 的三条交叉缺口（群级未取交集、`allowed_work_dirs` 不约束群规则初始目录、Codex 无逐次审批）：属另一 mission，本文只作观察，**尚未登记进 `.devflow/cc-qq-full-migration/backlog.md`**，需用户决定。
