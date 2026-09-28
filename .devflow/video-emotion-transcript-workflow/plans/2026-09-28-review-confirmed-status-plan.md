# 片段确认后任务状态同步实施计划

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 11:06:01 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：按已确认的状态规则修复后端持久化与前端即时反馈。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联对齐（Related Align）：`.devflow/video-emotion-transcript-workflow/plans/2026-09-28-review-confirmed-status-align.md`
- 关联规格（Related Spec）：`.devflow/video-emotion-transcript-workflow/spec/design.md`、`.devflow/video-emotion-transcript-workflow/spec/tasks.md`
- 当前状态（Status）：已完成（Completed）；自动验证与用户手动验收通过，提交待用户决定。
- 文档边界（Scope / Boundary）：本轮实施顺序真相源；不授权下一阶段真实媒体能力实施。

**目标（Goal）：** 全部片段确认后任务持久化为已确认，导出后页面立即显示已导出，并让确认操作有可见结果。

**架构（Architecture）：** 在现有片段审核服务（ReviewService）同一数据库事务中确认片段并统计任务片段；任务状态由任务仓储（JobRepository）持久化。前端成功操作后重新查询任务；片段编辑器依照持久片段状态和本地修改显示按钮。

**技术栈（Tech Stack）：** FastAPI、SQLAlchemy、React、Ant Design、pytest、Vitest。

## 文件职责

- `backend/app/domain/models.py`：任务状态转换方法。
- `backend/app/services/jobs.py`：读取旧任务时修复已确认片段与任务状态不一致的记录。
- `backend/app/services/review.py`：确认片段后判定全部已确认；修订已确认片段时回到待审核。
- `backend/tests/api/test_segments.py`：状态转移的接口回归。
- `frontend/src/App.tsx`、`frontend/src/features/review/ReviewWorkspace.tsx`、`frontend/src/features/review/SegmentEditor.tsx`、`frontend/src/features/exports/ExportPanel.tsx`：刷新任务并给出确认反馈。
- `frontend/src/App.test.tsx`、`frontend/src/features/review/ReviewWorkspace.test.tsx`：交互回归。
- `.devflow/video-emotion-transcript-workflow/bug-log.md`、`spec/design.md`、`spec/tasks.md`：问题与验收记录。

## 任务 1：后端状态转移

- [x] 增加失败先行的接口测试：单片段确认后任务为 `confirmed`；多片段只确认一段仍为 `review`，全部确认后转为 `confirmed`；修改已确认文本后回到 `review`；导出后为 `exported`。
- [x] 运行 `cd backend && .venv/bin/python -m pytest tests/api/test_segments.py -q`，新增三个断言先失败。
- [x] 在片段审核服务（ReviewService）同一事务内保存片段并更新任务；空片段不能被判为全部确认。
- [x] 重跑聚焦测试，3 passed。
- [x] 增加旧数据回归：片段全部已确认但任务仍为 `review` 时，查询任务修复并持久化为 `confirmed`；只确认部分片段时不修复；新增断言先失败，再通过。

## 任务 2：前端状态与反馈

- [x] 增加页面测试：确认成功刷新任务并显示「已确认」；导出成功刷新任务并显示「已导出」；未改动的已确认片段不再重复确认；改动后可重新确认。
- [x] 运行 `cd frontend && npm run test -- src/App.test.tsx src/features/review/ReviewWorkspace.test.tsx`，新增三个断言先失败。
- [x] 将确认与导出成功后的任务重新查询集中在页面操作回调；确认按钮按持久状态和本地编辑状态显示。
- [x] 重跑聚焦测试，10 passed。

## 任务 3：记录与验证

- [x] 更新问题日志（Bug Log）的现象、原因、方案，补齐规格任务状态。
- [x] 运行 `cd backend && .venv/bin/python -m pytest -q`：32 passed；`cd frontend && npm run test && npm run build`：11 passed，构建通过。
- [x] 检查变更范围和工作区状态；不执行提交（commit），待用户另行明确授权。

## 本轮不做 / 后续阶段

- 真实 STT（语音转文字）、媒体播放和情绪证据不属于本次状态修复；用户选择进入真实媒体阶段时重新对齐，详见关联对齐文档与现有延期记录。
