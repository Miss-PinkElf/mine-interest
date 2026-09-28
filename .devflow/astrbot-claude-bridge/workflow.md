# QQ 多代理 AstrBot 接入工作流（Workflow）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 21:43:08 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录本 mission 的路径、阶段与门禁。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：交接暂停，待设计修订（Handoff / Propose Revision）
- 文档边界（Scope / Boundary）：当前工作流真相源（source of truth）；用户已于 2026-09-28 明确授权实施。

## 路径与阶段

- 路径：重型路径（Heavy Route）。
- 当前阶段：提案修订（Propose Revision）并交接暂停；T01 已完成，T02 因 Codex 原生 Windows 严格拒读配置无法启动而回退。
- 顺序：需求对齐（Align）→ 计划（Plan）→ 开放规格（OpenSpec）提案、设计、任务 → 实施（Apply）→ 审查（Review）→ 验证（Verify）→ 收尾（Close）。
- 门禁：用户确认设计后才写计划；计划落盘后才写规格与任务；规格与任务齐备后才修改插件代码。

## 本轮目标

完成 `cc-ding` 通用核心向 AstrBot 插件的迁移。本轮优先修复两种代理在 Windows／macOS 的工作目录隔离设计，再恢复代码实施。

## 下一步

下次先读 `state.md`、`checkpoints.md` 与最新交接；修订 Codex 原生 Windows 执行隔离设计，重新验证 T02；通过前不进入 T03。
