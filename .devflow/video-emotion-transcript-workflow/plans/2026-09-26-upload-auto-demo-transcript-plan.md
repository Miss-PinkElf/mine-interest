# 上传后自动演示转写实施计划（Implementation Plan）

> 执行入口：按下列任务顺序实施，使用 `openspec-apply-change` 逐项验证；未经用户确认不提交代码。

**Goal（目标）：** 用户显式选择演示模式后，上传媒体自动产生标明来源的审核片段，并可确认、导出 Markdown/JSON。

**Architecture（架构）：** FastAPI 上传路由创建任务并安排应用内后台 JobRunner；运行模式以任务产物元数据持久保存，避免修改既有 SQLite 表结构。JobRunner 串联当前本地适配层和 Fake STT，状态经 SQLite 持久化；React 轮询状态并刷新片段。

**Tech Stack（技术栈）：** FastAPI、SQLAlchemy/SQLite、React/TypeScript、Ant Design、pytest、Vitest。

## Metadata（元数据）

- 创建时间（Created At）：2026-09-26 23:28:12 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：将已确认的自动演示转写对齐结果转为可执行、可验证的顺序任务。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联对齐（Related Align）：`.devflow/video-emotion-transcript-workflow/plans/2026-09-26-upload-auto-demo-transcript-align.md`
- 关联规格（Related Spec）：`.devflow/video-emotion-transcript-workflow/spec/`
- 当前状态（Status）：已完成（Completed）；2026-09-27 通过测试与本地浏览器验收
- 文档边界（Scope / Boundary）：本轮实施顺序真相源；不替代 OpenSpec（开放规格）任务与验证证据。

## 文件职责与顺序

### Task 1：任务来源持久化与导出标识

- 修改 `backend/app/core/constants.py`：集中管理演示模式键、元数据路径和演示提示文案。
- 修改 `backend/app/domain/models.py`、`backend/app/domain/schemas.py`、`backend/app/services/jobs.py`：任务暴露 `is_demo`；上传时写演示元数据；重新读取任务时恢复标识。旧任务缺元数据时视为普通任务。
- 修改 `backend/app/services/exports.py`：演示任务的 Markdown/JSON 产物带来源声明；保留普通任务现有格式。
- 测试 `backend/tests/services/test_demo_job.py`：上传、重建服务后查询、两种导出格式均保留标识；旧任务保持非演示。
- 验证：`backend/.venv/Scripts/python.exe -m pytest tests/services/test_demo_job.py -q`（在 `backend/` 中运行）通过。

### Task 2：自动执行管线与 API

- 新建 `backend/app/services/demo_transcription.py`：实现只产演示文本的 `TranscriptionEngine`（转写引擎）适配器，文本与时间范围集中常量管理。
- 新建 `backend/app/services/job_runner.py`：从 pending 进入 processing，生成质量报告及预处理占位产物，运行 Fake STT，持久化片段，只有至少一个片段时进入 review；失败记录稳定阶段/错误码并保留产物。
- 修改 `backend/app/services/jobs.py`：提供 `mark_review`；启动恢复覆盖 processing 和尚未调度的 pending 演示任务，普通 pending 保持原状。
- 修改 `backend/app/api/runtime.py`、`backend/app/api/routes/jobs.py`：构建 JobRunner；上传请求中显式 `demo_mode=true` 时安排 FastAPI BackgroundTasks。普通上传仍维持 pending 兼容旧 API。
- 测试 `backend/tests/services/test_job_runner.py` 与 `backend/tests/api/test_jobs.py`：成功、空片段、引擎错误、显式模式及旧接口兼容；TestClient 中后台任务在响应结束前执行，因此 POST 返回体以创建时 pending 快照为准，GET 检查最终 review。
- 验证：`backend/.venv/Scripts/python.exe -m pytest tests/services/test_job_runner.py tests/api/test_jobs.py -q` 通过。

### Task 3：前端显式演示模式与状态刷新

- 修改 `frontend/src/constants/copy.ts`、`frontend/src/constants/task.ts`：演示文案、模式键和已有具名轮询间隔。
- 修改 `frontend/src/api/jobs.ts`、`frontend/src/features/jobs/UploadTaskForm.tsx`：上传必须勾选演示模式，表单向 API 发送模式字段。
- 修改 `frontend/src/App.tsx`：对 pending/processing 轮询 `getJob`；到 review/failed 停止轮询并刷新片段；会话内保存任务 ID，浏览器刷新后重新查询任务和演示来源。写入异步结果前比对当前任务 ID，避免旧响应覆盖新上传任务。确认片段前先持久化人工修订。
- 必要时局部修改 `frontend/src/features/review/ReviewWorkspace.tsx`：让异步片段更新进入审核列表，不进行无关重构。
- 修改 `frontend/src/features/jobs/UploadTaskForm.test.tsx` 并新增聚焦页面测试：未选择模式不能提交，选择后请求正确；异步进入 review 后片段出现。
- 验证：在 `frontend/` 运行 `npm run test` 与 `npm run build`。

### Task 4：闭环验证与记录

- 扩充后端 API/集成测试：上传演示媒体，不手工写片段，GET 片段、确认、导出 Markdown/JSON，检查演示声明。
- 验证：后端 `backend/.venv/Scripts/python.exe -m pytest -q`，前端 `npm run test`、`npm run build`；若本地浏览器可用，再进行页面级上传与审核验收。
- 审查本轮 diff，只保留可追溯改动；更新 `spec/tasks.md`、`state.md`、`checkpoints.md` 和必要的 `decision-log.md`。代码修改完成后询问用户是否需要提交；没有明确允许不执行 commit。

## 本轮不做 / 后续阶段（Deferred Scope）

- 真实 FFmpeg/STT/说话人分离：演示闭环稳定后立即进入真实样本阶段；本轮占位适配层不得称为真实分析。
- LLM（Large Language Model，大语言模型）工具选择及证据融合：真实 STT 与可信媒体证据可用后再对齐；任务状态不交给 LLM 决定。
- 持久队列、并发调度、自动重试入口：应用内后台执行不能满足长时或多进程任务时再引入。
