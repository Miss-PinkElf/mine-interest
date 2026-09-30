# cc-ding 完整迁移为 cc-qq 工作流（Workflow）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:10:32 +08:00
- 更新时间（Updated At）：2026-09-30 15:35:00 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录本次完整迁移的阶段与门禁。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：第一阶段待运行验收（Stage 1 Runtime Verification Pending）
- 文档边界（Scope / Boundary）：本 mission 的流程真相源（source of truth）；对齐、计划和第一阶段开放规格已落盘，不代表第一阶段已验收。

## 目标与路径

- 目标：理解 `cc-ding/` 的完整能力，借鉴其运行链路，用原生 Python 实现基于 AstrBot 的 QQ 插件并分阶段补齐功能，保持模块化。
- 路径：重型路径（Heavy Route），依次进行对齐（Align）→ 计划（Plan）→ 开放规格（OpenSpec）→ 实施（Apply）→ 审查与验证（Review / Verify）→ 收尾（Close）。
- 当前阶段：三项运行缺陷已按计划实施到 `0.1.14`，单元测试通过。第一阶段真实 QQ 验收仍未完成，运行中的 AstrBot 仍是 `0.1.12`。

## 阶段门禁

- 先与用户讨论候选方案并取得对齐确认，再写对齐文档与计划。
- 计划落盘后才创建 `spec/proposal.md`、`spec/design.md`、`spec/tasks.md`。
- 三件套齐备后才修改插件代码；插件代码变更须同步到 AstrBot 对应位置并更新版本。
- 完成声明前取得新的验证证据；代码提交须经用户明确允许。

## 下一步

用户上传 `integrations/astrbot/astrbot_plugin_cc_qq-v0.1.14-upload.zip`。其后验证过期消息、私聊空白、代理早退，以及 Claude Code、双代理模型和恢复／中断。
