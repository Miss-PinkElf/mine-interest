# Metadata（元数据）

- 更新时间（Updated At）：2026-09-28 18:55:00 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：记录当前工作路径与下一次验收入口。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38、50–58 行。
- 当前状态（Status）：需求 7 迁移已做，扫码页和邮件待验收；需求 4 Verify 待续。
- 文档边界（Scope / Boundary）：本任务记录；诊断插件不代表完整信息中心已获准实施。

# 当前工作流（Workflow）

- 主线：需求 4 的 Align → Plan → Spec → Apply 已走完；代码提交 `2fae5a6`。Verify 已证实本机插件运行与 Markdown 真实推送，但 T7 尚缺稳定采集和新 QQ 样本验收。
- 恢复：先读 `state.md`、`checkpoints.md`，再读最新 011 交接。
- 下一步：打开 `0.3.1` 插件页，确认登录状态和仓库校验都显示出来。邮件要等用户打开「包含我自己的更新」后再推一轮。直连 DNS、发布闸门和 `BV1aVjMzeE96` 本轮暂缓。
- 边界：用户本轮明确暂缓远端媒体上传与 Git LFS；现有 Markdown 发布行为不变。原需求 5 已被需求 7 吸收；外层 14 项不因本轮自动开工。
- 新分支：需求 7 已完成 Align → 两份 Plan → `spec/2026-09-28-需求7/` → 首版 Apply/独立审查；114 项测试通过。当前暂停在真实迁移与告警端到端 Verify，具体状态见 `tasks.md` 和 `deferred/需求7首版边界与真实验收.md`。不得影响需求 4 尚未完成的 Verify。
- 测试：`PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -v`；无需全局 ESLint。
