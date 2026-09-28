# 下次对话提示词：cc-ding 迁移 AstrBot 插件

## Metadata（元数据）

- 更新时间（Updated At）：2026-09-29 00:21:05 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：供下一次对话直接复制，恢复 T02 设计回退后的工作。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 实施计划（Implementation Plan）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`
- 最新交接（Latest Handoff）：`.devflow/astrbot-claude-bridge/handoffs/2026-09-29-002-t02-design-revision.md`
- 当前状态（Status）：待下次修订设计（Propose Revision Next Session）
- 文档边界（Scope / Boundary）：恢复提示词，不替代当前仓库事实、`state.md`、计划或开放规格（OpenSpec）；不代表实施完成。

## 可直接复制到新对话的提示词

请继续 `mine-interest` 仓库的 `.devflow/astrbot-claude-bridge/` mission，使用 devflow 重型路径（Heavy Route）。先读 `.devflow/astrbot-claude-bridge/state.md` 与 `checkpoints.md`，再读 `handoffs/index.md` 和最新 `handoffs/2026-09-29-002-t02-design-revision.md`。根据该交接按需读 `spec/permission-matrix.md`、`bug-log.md`、`backlog.md`、计划和开放规格（OpenSpec）。先核对 Git 状态和实际文件，不要沿用旧的“从 T01 开始”提示词。

当前进度：T01 `spec/feature-mapping.md` 已完成；T02 原生 Windows 权限验证未通过，按 devflow 从实施（Apply）回退提案修订（Propose Revision）。Codex CLI 0.158.0 的 `:read-only` 成功读取工作目录外哨兵；自定义 `:root = deny` 在普通沙箱要求 elevated，在 elevated 沙箱被启动前校验拒绝。用户已允许 elevated 测试，但没有同意降低权限要求。Claude Code 基础文件工具仅有部分 Windows 样本，Shell、MCP、Hooks、Skills、会话恢复及 macOS 均未完整验证。`spec/permission-matrix.md` 写了命令、结果和限制。没有修改 AstrBot 插件代码，没有版本提升或本机覆盖；T03 及后续代码任务未开始。

任务目标：复用并模块化迁移 `cc-ding` 通用核心，由 AstrBot 插件替换钉钉平台适配。本轮支持 Claude Code、Codex；QQ 群每群一个固定工作目录并共享会话，私聊独立；所有用户均不能读取工作目录外文件，白名单用户最多在目录内读写，非白名单只读；群级与用户级文件／工具权限取交集，工具调用单独配置并让代理从允许列表自主选择。完整迁移目标仍包括 Web Console 和代理间通信（A2A）。最终插件原生运行于 Windows／macOS，不要求 WSL／Ubuntu。

立即下一步：调查并与用户对齐可真实执行“工作目录外拒读”的 Windows／macOS 原生隔离候选，修订需求对齐／计划／OpenSpec 后重跑 T02。T02 未通过不得进入 T03，也不要把 Codex 内置只读或根目录可读配置当成合格方案。与用户另外核对首个可运行版本（First Version）的阶段边界；Web Console、A2A 等属于完整迁移目标，尚未被批准延期。`backlog.md` 记录未讨论项；`deferred/agent-expansion.md` 只记录已明确延期的 OpenCode、Pi 等新代理，延期不是永久放弃。

提交与环境：本轮交接时用户明确授权提交当前 mission 相关文件，提交信息须用中文。`.gitignore` 和 `zzz-prompt-debug/接入agent/prompt-01.md` 在本轮开始前已有改动且未纳入 mission 文档提交；默认不提交 `config.ts`、`tsconfig.json`。`cc-ding/` 只作只读参考。未来每次修改插件代码要使用补丁编辑、提升插件版本并覆盖本机 AstrBot 插件目录。根目录 `devflow-handoff.md` 是只读收尾指导，不修改。

当前对话只做交接暂停，没有完成实施（Apply）或正式关闭（Close）。新对话可以从设计修订继续；不要把这份交接当成安全验收通过。
