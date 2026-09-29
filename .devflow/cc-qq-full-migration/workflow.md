# cc-ding 完整迁移为 cc-qq 工作流（Workflow）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:10:32 +08:00
- 更新时间（Updated At）：2026-09-29 11:00:28 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录本次完整迁移的阶段与门禁。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：第一阶段实施暂停（Stage 1 Apply Paused）
- 文档边界（Scope / Boundary）：本 mission 的流程真相源（source of truth）；对齐、计划和第一阶段开放规格已落盘，不代表第一阶段已验收。

## 目标与路径

- 目标：理解 `cc-ding/` 的完整能力，借鉴其运行链路，用原生 Python 实现基于 AstrBot 的 QQ 插件并分阶段补齐功能，保持模块化。
- 路径：重型路径（Heavy Route），依次进行对齐（Align）→ 计划（Plan）→ 开放规格（OpenSpec）→ 实施（Apply）→ 审查与验证（Review / Verify）→ 收尾（Close）。
- 当前阶段：原始对齐（Align）已获用户确认，总体与第一阶段计划（Plan）、开放规格（OpenSpec）三件套已落盘；第一阶段实施（Apply）在交接点暂停。T00 已完成，T01–T03 有未核验代码，T04 尚未接通。新增群聊 @ 门禁须先走 Mini Align → Plan → Spec/Tasks，更新当前阶段范围后才实施。

## 阶段门禁

- 先与用户讨论候选方案并取得对齐确认，再写对齐文档与计划。
- 计划落盘后才创建 `spec/proposal.md`、`spec/design.md`、`spec/tasks.md`。
- 三件套齐备后才修改插件代码；插件代码变更须同步到 AstrBot 对应位置并更新版本。
- 完成声明前取得新的验证证据；代码提交须经用户明确允许。

## 下一步

下一次先读 `state.md`、`checkpoints.md` 和最新 handoff；确认群号白名单与 @ 门禁的第一版语义，再依 `spec/tasks.md` 继续 T01–T04。每次插件代码变更同步版本和本机 AstrBot 副本；用户本次明确要求先写收尾文档、暂不提交。
