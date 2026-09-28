# QQ 多代理 AstrBot 接入当前状态（Current State）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 21:43:08 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：提供本 mission 的短当前快照。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：交接暂停，待设计修订（Handoff / Propose Revision）
- 文档边界（Scope / Boundary）：当前状态真相源（source of truth）；用户已授权实施，但 T02 暴露设计缺陷，按 devflow 门禁回退开放规格（OpenSpec）。

## 当前快照

- 用户指定重型路径（Heavy Route）；本轮只迁移 Claude Code 与 Codex，OpenCode、Pi 留待后续阶段。
- 群成员均可对话；所有用户的文件访问均限制在指定工作目录。白名单用户可读写，非白名单用户只可读取；工具调用权限单独配置。
- 本地参考项目为 `cc-ding/`，仓库现有 AstrBot 插件位于 `integrations/astrbot/`。
- 当前阶段：T01 逐功能映射清单已完成；T02 原生 Windows 实测发现 Codex `:read-only` 可读取目录外文件，`:root = deny` 在普通及 elevated 沙箱均不能启动。现回退提案（Propose）修正执行边界，交接到下一对话；尚未修改插件代码。
- 每个启用的 QQ 群配置一个固定工作目录，群内成员共享代理会话；私聊权限单独控制，群级还可配置只读与工具权限。
- 已确认方向：迁移 `cc-ding` 的通用业务核心；AstrBot 插件承接统一平台消息，替换钉钉输入输出与身份适配。
- 已确认权限叠加：群级配置是上限；每条消息按发送者身份与群级配置取更严格权限，工具调用也按两层配置交集决定；私聊使用独立配置。
- 已确认完整迁移范围包含 Web Console 管理能力与代理间通信（A2A）；钉钉专属交互改映射到 AstrBot 能力。
- 用户补充插件最终在 Windows／macOS 原生运行，不依赖 WSL／Ubuntu；非白名单优先使用 CLI 原生只读权限，Shell、MCP、Hooks 等未验证工具组合默认禁用。macOS 未实测不得宣称通过。
- 对齐文档：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding迁移astrbot需求对齐.md`。
- 实施计划：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`。
- 下一步：确认原生 Windows／macOS 可满足工作目录外拒读的 Codex 执行边界，修订设计和计划，重新验证 T02；通过前不进入 T03 代码迁移。
- 最新交接：`handoffs/2026-09-29-002-t02-design-revision.md`；下次提示词：`NEXT-SESSION-PROMPT-astrbot-claude-bridge.md`。

## 本轮不做 / 后续阶段（Deferred Scope）

- OpenCode、Pi 及其他代理适配：本轮先完整迁移 Claude Code、Codex 相关能力；完成迁移与权限验收后，再进入多代理扩展阶段。
- 首版与完整迁移的阶段划分尚未确认；Web Console、A2A 等仍在本轮完整目标内，待重新进入实施前与用户核对阶段边界，不能自动延期。
