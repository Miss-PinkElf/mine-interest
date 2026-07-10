# 下一会话提示：视频情感化转写工作流

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 15:45:35 +08:00
- 更新时间（Updated At）：2026-07-10 15:23:33 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：为新对话提供当前 mission 的最短恢复入口。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联规格（Related Spec）：`.devflow/video-emotion-transcript-workflow/spec/`
- 当前状态（Status）：规格已就绪（Spec Ready）
- 文档边界（Scope / Boundary）：本文件是恢复提示，不是实施授权；不直接触发 Apply（实施）。

当前 mission 已完成可行性调研、MVP 对齐、实施计划和 OpenSpec（proposal/design/tasks），但用户明确要求本轮不开始 Apply。

恢复顺序：

1. `.devflow/video-emotion-transcript-workflow/state.md`
2. `.devflow/video-emotion-transcript-workflow/checkpoints.md`
3. `.devflow/video-emotion-transcript-workflow/spec/tasks.md`
4. `.devflow/video-emotion-transcript-workflow/handoffs/2026-07-10-002-spec-ready.md`
5. 需要完整实现细节时读 `plans/2026-07-10-video-emotion-transcript-mvp-implementation-plan.md` 与 `spec/design.md`。

若用户明确授权实施：从 Plan 的 Task 1 开始，调用 `openspec-apply-change`，使用 `backend/.venv`，先写失败测试再实现。不要实现 `deferred/2026-07-10-mvp-deferred-scope.md` 中的能力。

若用户继续讨论：以 `spec/proposal.md`、`spec/design.md` 和 `deferred/2026-07-10-mvp-deferred-scope.md` 为真相源更新范围；不要把未确认候选方向当成 Apply 任务。
