# cc-ding 迁移 AstrBot：实施前交接（Session Handoff）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 23:15:47 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：保存本轮需求对齐、计划、规格草稿、实施授权边界与下次恢复步骤。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 对齐文档（Aligned Requirement）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding迁移astrbot需求对齐.md`
- 实施计划（Implementation Plan）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`
- 当前状态（Status）：暂停待下次实施（Paused Before Apply）
- 文档边界（Scope / Boundary）：本文件是恢复与交接记录，不替代 `state.md`、计划或开放规格（OpenSpec）；用户限定本轮只新增本文件与 `NEXT-SESSION-PROMPT-astrbot-claude-bridge.md`，未同步修改其他 mission 文件。

## 当前目标与阶段

目标是把 `cc-ding` 的成熟通用功能迁移为 AstrBot 插件：AstrBot 平台适配器（Platform Adapter）负责 QQ 等平台接入，迁移后的核心负责 Claude Code、Codex、会话、任务、管理与代理间通信（A2A）。

当前完成需求对齐（Align）与计划（Plan）。`spec/proposal.md`、`spec/design.md`、`spec/tasks.md` 已写为待审阅草稿。此前助手误将 T01 标为实施中，用户指出“对齐后直接写计划”不等于本轮实施授权，已撤回标记；**本轮没有进入实施（Apply），没有修改插件代码，也没有执行提交（Commit）**。用户最新指令是“下一个对话再 Apply”；下次对话恢复并核对文件后可按此指令进入实施，不应把本轮已停止的 Apply 误记为完成。

## 本轮完成内容

1. 读取原始需求与本地 `cc-ding/`，核对现有 AstrBot 插件模式及 AstrBot 官方插件事件、插件页面能力。
2. 初始化 `.devflow/astrbot-claude-bridge/`，建立 `workflow.md`、`state.md`、`origin.md`、`decision-log.md`、检查点及归档。
3. 与用户逐项对齐权限、群目录、会话和迁移方式；生成强相关对齐文档和详细实施计划。
4. 根据计划写出开放规格（OpenSpec）提案、设计和 T01–T17 任务草稿；用户尚未要求本轮开始执行这些任务。
5. 阅读仓库根目录 `devflow-handoff.md` 作为收尾指导，未修改该文件。遵照用户本轮限制，只新增本交接与下次会话提示词，不补做其他收尾文件或提交。

## 已确认的关键决策及原因

| 决策 | 原因与约束 |
| --- | --- |
| 采用 devflow 重型路径（Heavy Route） | 迁移涉及平台、两种代理、权限、管理及 A2A，需要 Align → Plan → Spec/Tasks → Apply → Review/Verify/Close。 |
| 迁移 `cc-ding` 通用核心，由 AstrBot 插件替换钉钉平台入口 | 复用成熟的会话、任务和代理能力；AstrBot 已有 QQ 平台接入，不再另造钉钉式平台适配器。原 `DingClaude` 类和多个模块耦合钉钉，不能只替换一个文件。 |
| 本轮仅支持 Claude Code 与 Codex | 这两种代理已在 `cc-ding` 中实现；先完成平台和权限迁移。OpenCode、Pi 后续扩展。 |
| 每个启用 QQ 群固定工作目录，群内共享代理会话 | 保留群协作体验；每条消息仍按真实发送者重新计算权限，不继承上一条消息的写权限。 |
| 私聊按用户独立会话与目录配置 | 私聊权限与群聊分开，避免群会话上下文混入私聊。 |
| 所有用户的代理文件访问限于对应工作目录 | 白名单用户最多读写；非白名单只读。群级只读／可写是上限；有效文件权限取用户与群级的较严格者。 |
| 工具权限单独配置，取用户与群配置允许集交集 | 代理在本次可用工具元数据中自主选择工具；获准工具仍不能绕开文件边界。 |
| 完整迁移包含 Web Console 与 A2A | 用户明确确认两者属于本轮范围；钉钉 Token、工号、Webhook、AI Card、PM2 等协议形式改为 AstrBot 等价交互或逐项说明取消理由。 |
| 不以提示词、Claude Code `plan` 模式或 Codex 完全访问参数充当隔离 | `cc-ding` 目前的问答模式与 Codex 启动参数不足以保证目录边界；真实隔离验证必须先于大规模代码迁移。 |

## 关键文件与恢复顺序

恢复热路径先读：

1. `.devflow/astrbot-claude-bridge/state.md`
2. `.devflow/astrbot-claude-bridge/checkpoints.md`
3. 本交接文件

进入实施前再读：

4. `.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding迁移astrbot需求对齐.md`
5. `.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`
6. `.devflow/astrbot-claude-bridge/spec/proposal.md`
7. `.devflow/astrbot-claude-bridge/spec/design.md`
8. `.devflow/astrbot-claude-bridge/spec/tasks.md`
9. 按任务需要读取 `cc-ding/` 源码；该目录被 `.gitignore` 忽略，只能作为只读参考，最终迁移代码须进入可追踪插件目录并保留 MIT 许可。

根目录 `devflow-handoff.md` 是收尾指导，不是业务真相源，不需修改。`state.md` 和 `checkpoints.md` 的阶段表述以本轮结束时为准；本交接补充了用户最新“下个对话再 Apply”的时间边界。若新会话发现文件与本交接冲突，以当前仓库事实和最新用户指令为准。

## 当前仓库与环境事实

- 目前不存在 `integrations/astrbot/astrbot_plugin_cc_bridge/`，也没有插件代码改动或版本提升。
- `git status --short` 在本轮检查时显示 `.gitignore` 和 `zzz-prompt-debug/接入agent/prompt-01.md` 已修改，另有新建的 `.devflow/astrbot-claude-bridge/` 未追踪；前两项为本轮开始前已有修改，不要覆盖、重置或混入提交。
- 本机可找到 Windows 侧 Claude Code、Codex、OpenCode、Node v24；WSL Ubuntu 存在。初查 WSL 内可找到 Claude Code 和一个指向 Windows npm 路径的 Codex 命令，未找到 `bwrap` 或 WSL 内 Node。仅是环境快照，不能当作隔离能力通过的证据。
- AstrBot Desktop 已有 QQ 的 NapCat／OneBot 接入经验；现有插件源码模式见 `integrations/astrbot/`。任何新插件代码修改都要按根目录 `AGENTS.md` 提升版本，并复制覆盖到本机 AstrBot 对应插件目录。

## 未完成任务、风险与未讨论问题

### 明确延期（Deferred Scope）

- OpenCode、Pi 及其他代理适配：本轮暂不做，因为用户要求先迁移并验收 `cc-ding` 已有的 Claude Code、Codex。触发条件是这两种代理在 AstrBot 的真实 QQ 与目录／工具权限验收通过；之后进入多代理扩展阶段。这是延期，不是永久放弃。对齐文档、计划、`decision-log.md`、`state.md` 和规格草稿均已记录。

### 本轮范围内但尚未细化；不得自行标记延期

- “完整迁移”涵盖 Web Console、A2A、任务、定时、待办、菜单、媒体、命令和配置。本轮尚未写逐命令／逐配置字段功能映射（T01）；哪些能力先作为可运行首版交付、哪些在同一 mission 后续任务完成，需依据 T01 映射和实施依赖安排，不能把 Web Console 或 A2A 悄悄移出已确认范围。
- 私聊默认允许哪些用户、目录如何首次配置；全局与群级白名单的管理入口；工具目录和各代理原生工具元数据如何暴露；钉钉专属命令和远程 Console 管理的 AstrBot 等价形式，均需在 T01／T04／T06 细化并与用户核对实际产品行为。
- 群共享历史与按发送者变更权限会产生上下文及工具结果泄漏风险；实现时须验证读取、写入、恢复会话和后台任务的真实边界。
- T02 真实隔离可行性是硬门禁。若 Shell、Skills、MCP、Hooks、符号链接／联接目录、A2A 等能绕过工作目录，只能回退设计，不能放宽权限继续迁移。
- `cc-ding` 原 A2A 使用默认首个会话和 `a2a-remote` 身份；新实现必须传递可验证来源和目标群授权。原问答模式（QA Mode）和 Codex `danger-full-access` 不能直接复用。

## 立即下一步：下次对话再实施（Apply）

1. 用户下次会话说继续或使用 `NEXT-SESSION-PROMPT-astrbot-claude-bridge.md` 时，先按上面的恢复顺序检查仓库状态与文件；此处的“下一个对话再 Apply”是最新用户指令，本轮不抢先执行。
2. 核对并更新 `workflow.md`、`state.md`、`spec/tasks.md` 中的草稿／待审阅标记，再进入实施；如发现范围冲突，先回到 Align／Plan，而不是直接编码。
3. 先做 T01：逐项功能映射，写 `spec/feature-mapping.md`，包括全部命令、配置、Console、A2A、钉钉专属行为的等价或取消理由。
4. 再做 T02：真实隔离可行性验证，记录可复现命令与证据。T02 未通过不得做 T03 以后代码迁移。
5. 每次插件代码改动按 `AGENTS.md` 使用补丁编辑、提升版本、覆盖 AstrBot 插件目录；不要改 `cc-ding/` 原始克隆；代码修改后先询问是否提交，未经明确允许不提交。
6. 实施完成后只能先报告结果与验证。**完整收尾（Close／归档／必要的正式结束记录）必须等用户在 Apply 之后再次明确允许**；本轮不做完整收尾，也不提交。

## 可从活跃上下文移除的内容

方案比较、逐轮问答与本机初查过程已写入对齐、计划、决策记录和本交接；下次无需重放整段对话。只需按热路径恢复当前阶段，再按计划与任务开始 T01／T02。
