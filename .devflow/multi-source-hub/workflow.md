# Metadata（元数据）

- 更新时间（Updated At）：2026-09-23 16:52:08 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：记录当前工作路径与下一次验收入口。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38 行。
- 当前状态（Status）：需求 4 Verify 暂停，等待真实运行验收。
- 文档边界（Scope / Boundary）：本任务记录；诊断插件不代表完整信息中心已获准实施。

# 当前工作流（Workflow）

- 主线：需求 4 的 Align → Plan → Spec → Apply 已走完；代码提交 `2fae5a6`；Verify 仅剩真实新消息与远端推送。
- 恢复：先读 `state.md`、`checkpoints.md`，再读最新 008 交接；必要时读 `spec/2026-09-23-需求4/tasks.md`。
- 运行验收：启动 AstrBot、重载检查器 0.5.5 和 B 站 0.2.5，发 QQ/B 站样本，检查 Vault 与私有 `data-hub` 的 Markdown 允许清单。
- 边界：Cookie、快照、数据库及媒体不外传；新增需求 5 另走 Align，外层 14 项不因本轮自动开工。
- 测试：`PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -v`；无需全局 ESLint。
