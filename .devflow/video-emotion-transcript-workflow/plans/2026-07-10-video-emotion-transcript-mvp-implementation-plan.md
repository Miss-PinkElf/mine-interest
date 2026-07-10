# 视频情感化转写 MVP 实施计划（Implementation Plan）

## Metadata（元数据）

- 创建时间（Created At）：2026-07-10 15:05:09 +08:00
- 更新时间（Updated At）：2026-07-10 15:05:09 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：将已确认的 MVP 对齐设计拆分为可验证、可实施的任务序列。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联对齐（Related Align）：`.devflow/video-emotion-transcript-workflow/plans/2026-07-10-video-emotion-transcript-mvp-align.md`
- 当前状态（Status）：计划中（Planned）
- 文档边界（Scope / Boundary）：本文件是 MVP 实施计划真相源（source of truth），尚未批准 OpenSpec（开放规格）或 Apply（实施），不代表代码已经开始实现。

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers-subagent-driven-development`（推荐）或 `executing-plans`，逐任务实施并保留审查检查点。

**Goal:** 构建仅供个人本地使用的浏览器工作台：本地执行媒体预处理、分段和专用模型分析，云端 LLM（Large Language Model，大语言模型）进行证据解释，并允许逐段审核后导出 JSON / Markdown。

**Architecture:** FastAPI 服务维护 SQLite 任务状态和本地产物目录；确定性工具通过注册表（Tool Registry）运行并生成证据。React + Vite + Ant Design 前端通过本地 API 审核片段；云端模型经 Provider Adapter（提供方适配层）调用，不耦合任一供应商。

**Tech Stack:** Python 3.11、FastAPI、Pydantic、SQLAlchemy、SQLite、FFmpeg、FunASR / SenseVoice、WhisperX、pyannote.audio、MediaPipe、OpenAI-compatible HTTP client、React、TypeScript、Vite、Ant Design、CSS Modules、Vitest、Playwright、pytest。

---

## 文件结构与实施顺序

```text
backend/
  pyproject.toml
  app/
    main.py
    core/{config.py,constants.py,database.py}
    domain/{enums.py,models.py,schemas.py}
    repositories/{jobs.py,segments.py,settings.py}
    services/{artifacts.py,jobs.py,review.py,media.py,preprocess.py,transcription.py}
    services/{tool_registry.py,orchestrator.py,evidence.py,fusion.py}
    integrations/{llm/base.py,llm/openai_compatible.py,vision/mediapipe.py}
    api/routes/{jobs.py,segments.py,settings.py,exports.py}
  tests/...
frontend/
  package.json
  vite.config.ts
  src/
    api/{client.ts,jobs.ts,settings.ts}
    constants/{copy.ts,task.ts}
    features/{jobs,review,settings,exports}/...
    components/{SegmentAudioPlayer,EvidencePanel}/...
    App.tsx
  tests/...
```

每一阶段都必须保留上一阶段可运行的端到端路径；不得先接入全部真实模型再补任务、产物和审核模型。所有业务文案、状态 key、阈值、模型能力描述和提示词必须放入具名常量或配置真相源，不散落在函数体或 JSX 中。

### Task 1：初始化可运行的本地双端工程

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/tests/test_health.py`
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/App.module.scss`
- Create: `frontend/src/index.css`

- [ ] **Step 1: 编写健康检查失败测试**

```python
def test_health_returns_service_status(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
```

- [ ] **Step 2: 执行失败测试并确认 API 尚未存在**

Run: `cd backend && .venv/bin/python -m pytest tests/test_health.py -v`

Expected: FAIL，提示 `app.main` 或 `/api/health` 尚不存在。

- [ ] **Step 3: 创建 FastAPI 健康检查、CORS 本地开发配置和 Vite React 入口**

```python
app = FastAPI()

@app.get('/api/health')
def get_health() -> dict[str, str]:
    return {'status': 'ok'}
```

前端入口仅渲染 `App`，`App` 使用 Ant Design `Layout` 作为工作台骨架；样式写入 `App.module.scss`，不使用行内样式。

- [ ] **Step 4: 执行后端单测和前端构建**

Run: `cd backend && .venv/bin/python -m pytest tests/test_health.py -v`

Expected: PASS。

Run: `cd frontend && npm run build`

Expected: Vite 生产构建成功。

### Task 2：定义任务、片段、证据与审核的领域模型

**Files:**
- Create: `backend/app/core/constants.py`
- Create: `backend/app/domain/enums.py`
- Create: `backend/app/domain/models.py`
- Create: `backend/app/domain/schemas.py`
- Create: `backend/tests/domain/test_segment_models.py`

- [ ] **Step 1: 编写片段原始结果不可覆盖的测试**

```python
def test_reviewed_segment_preserves_raw_text():
    segment = Segment.create(raw_text='原始识别')
    segment.apply_text_edit('人工修订')
    assert segment.raw_text == '原始识别'
    assert segment.edited_text == '人工修订'
    assert segment.final_text == '人工修订'
```

- [ ] **Step 2: 执行领域测试并确认失败**

Run: `cd backend && .venv/bin/python -m pytest tests/domain/test_segment_models.py -v`

Expected: FAIL，提示 `Segment` 尚不存在。

- [ ] **Step 3: 实现枚举、Pydantic 请求/响应模式与领域实体**

定义 `JobStatus`、`SegmentReviewStatus`、`EvidenceSource`、`AnalysisStatus` 等枚举。`Segment` 包含 `start`、`end`、说话人、`raw_text`、`edited_text`、`final_text`、证据列表、审核操作和重分析状态；所有状态和默认文案引用 `constants.py` 中的具名常量。

- [ ] **Step 4: 验证领域不变量**

Run: `cd backend && .venv/bin/python -m pytest tests/domain/test_segment_models.py -v`

Expected: PASS。

### Task 3：实现 SQLite、本地产物目录与可恢复任务状态

**Files:**
- Create: `backend/app/core/database.py`
- Create: `backend/app/repositories/jobs.py`
- Create: `backend/app/repositories/segments.py`
- Create: `backend/app/services/artifacts.py`
- Create: `backend/app/services/jobs.py`
- Create: `backend/tests/services/test_job_lifecycle.py`

- [ ] **Step 1: 编写任务产物隔离与失败恢复测试**

```python
def test_failed_job_keeps_completed_artifacts(job_service, artifact_store):
    job = job_service.create(source_media_path='sample.mp4')
    artifact_store.write_text(job.id, 'quality/report.json', '{}')
    job_service.mark_failed(job.id, stage='transcription', error_code='MODEL_UNAVAILABLE')
    assert artifact_store.exists(job.id, 'quality/report.json')
    assert job_service.get(job.id).status == JobStatus.FAILED
```

- [ ] **Step 2: 执行失败测试**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_job_lifecycle.py -v`

Expected: FAIL，提示任务服务尚不存在。

- [ ] **Step 3: 实现 SQLite repository 与每任务独立产物目录**

实现 `JobRepository`、`SegmentRepository` 和 `ArtifactStore`。任务状态至少覆盖等待、处理中、待审核、已确认、已导出和失败；失败记录阶段、错误码、可重试标记和时间。应用启动时将中断中的任务转为可恢复状态，不删除产物。

- [ ] **Step 4: 验证生命周期与迁移初始化**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_job_lifecycle.py -v`

Expected: PASS。

### Task 4：实现媒体质量报告、条件预处理与双音轨产物

**Files:**
- Create: `backend/app/services/media.py`
- Create: `backend/app/services/preprocess.py`
- Create: `backend/tests/services/test_preprocess_routing.py`
- Create: `backend/tests/fixtures/media/clean.wav`
- Create: `backend/tests/fixtures/media/bgm_heavy.wav`

- [ ] **Step 1: 编写预处理条件路由测试**

```python
def test_clean_audio_skips_separation_and_denoise(router):
    plan = router.build(AudioQualityReport(is_clean=True))
    assert plan.steps == [PreprocessStep.NORMALIZE_LOUDNESS]

def test_bgm_heavy_audio_creates_stt_ready_track(router):
    plan = router.build(AudioQualityReport(has_strong_bgm=True))
    assert PreprocessStep.SEPARATE_VOCALS in plan.steps
    assert plan.outputs.stt_ready_track == 'audio_stt_ready.wav'
```

- [ ] **Step 2: 执行失败测试**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_preprocess_routing.py -v`

Expected: FAIL，提示音频质量报告和路由器不存在。

- [ ] **Step 3: 实现 FFmpeg 适配、质量报告和双音轨路由**

`MediaService` 负责抽取音频并读取媒体信息；`PreprocessRouter` 依据质量报告构建处理计划；`PreprocessService` 保存 `audio_raw`、`audio_light` 与 `audio_stt_ready`。人声分离、去混响和降噪均是可替换工具，不得覆盖原始轨。响度配置、工具命令、文件名和处理原因均从具名配置读取。

- [ ] **Step 4: 在 fixture 上验证路由与产物清单**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_preprocess_routing.py -v`

Expected: PASS。

### Task 5：实现工具注册表与可观测编排器

**Files:**
- Create: `backend/app/services/tool_registry.py`
- Create: `backend/app/services/orchestrator.py`
- Create: `backend/tests/services/test_tool_registry.py`
- Create: `backend/tests/services/test_orchestrator.py`

- [ ] **Step 1: 编写工具前置条件与调用记录测试**

```python
def test_orchestrator_only_calls_face_tool_when_face_frames_exist(registry):
    result = run_pipeline(registry, frame_manifest=FrameManifest(has_face=False))
    assert 'face_analysis' not in result.called_tools
    assert result.decision_log[0].reason == 'NO_FACE_FRAME'
```

- [ ] **Step 2: 执行失败测试**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_tool_registry.py tests/services/test_orchestrator.py -v`

Expected: FAIL，提示工具元数据和编排器不存在。

- [ ] **Step 3: 实现工具元数据与确定性条件路由**

工具元数据必须包含工具名、输入/输出 schema、前置条件、运行位置、本地 GPU 需求、产物路径和失败策略。编排器对每次工具选择生成决策日志；仅在需要语义解释时调用云端融合，不让 LLM 决定文件处理或绕过前置条件。

- [ ] **Step 4: 验证无脸、多人、低质量等分支**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_tool_registry.py tests/services/test_orchestrator.py -v`

Expected: PASS。

### Task 6：接入转写、VAD 分段、说话人分离与时间轴对齐

**Files:**
- Create: `backend/app/services/transcription.py`
- Create: `backend/tests/services/test_transcription_segments.py`
- Create: `backend/tests/fakes/transcription.py`

- [ ] **Step 1: 编写转写片段保留时间范围与说话人测试**

```python
def test_transcription_result_becomes_reviewable_segments(service):
    segments = service.to_segments(fake_transcription_result())
    assert [(item.start, item.end, item.speaker_id) for item in segments] == [
        (0.0, 2.4, 'speaker_0'),
        (2.4, 5.1, 'speaker_1'),
    ]
```

- [ ] **Step 2: 执行失败测试**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_transcription_segments.py -v`

Expected: FAIL，提示转写服务不存在。

- [ ] **Step 3: 定义可替换转写引擎并实现初始基线**

定义 `TranscriptionEngine` 协议，适配 SenseVoice 和 WhisperX + pyannote 的输出。将 VAD、词级时间戳和 diarization 结果标准化为 `Segment`，保留原始引擎输出作为产物；模型加载、设备和超时只由配置控制。

- [ ] **Step 4: 验证 fake engine 与最小真实音频冒烟路径**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_transcription_segments.py -v`

Expected: PASS。

### Task 7：接入专用视觉与音频证据工具

**Files:**
- Create: `backend/app/integrations/vision/mediapipe.py`
- Create: `backend/app/services/evidence.py`
- Create: `backend/tests/services/test_evidence_collection.py`
- Create: `backend/tests/fakes/vision.py`

- [ ] **Step 1: 编写事实证据与语义解释分离测试**

```python
def test_evidence_store_keeps_specialized_facts_separate_from_narrative(store):
    store.add_face_fact(segment_id='seg-1', blendshape='mouthSmileLeft', confidence=0.9)
    store.add_narrative(segment_id='seg-1', text='可能带调侃', confidence=0.6)
    evidence = store.list_for_segment('seg-1')
    assert {item.source for item in evidence} == {EvidenceSource.SPECIALIZED_MODEL, EvidenceSource.LLM}
```

- [ ] **Step 2: 执行失败测试**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_evidence_collection.py -v`

Expected: FAIL，提示证据收集服务不存在。

- [ ] **Step 3: 实现关键帧、MediaPipe 和音频证据标准化**

按片段边界抽取开始、中间、结束附近关键帧，并保留固定间隔抽帧作为补充。MediaPipe 适配输出人脸存在、关键点、Blendshape、头部方向和姿态；音频适配输出情绪候选、事件、能量、音高、语速和停顿。没有人脸或姿态时写入“不可用”证据，不抛出任务失败。

- [ ] **Step 4: 验证证据来源、置信度和无脸分支**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_evidence_collection.py -v`

Expected: PASS。

### Task 8：实现云端 Provider Adapter 与证据融合协议

**Files:**
- Create: `backend/app/integrations/llm/base.py`
- Create: `backend/app/integrations/llm/openai_compatible.py`
- Create: `backend/app/services/fusion.py`
- Create: `backend/tests/services/test_fusion.py`
- Create: `backend/tests/fakes/llm.py`

- [ ] **Step 1: 编写融合请求最小化与冲突标记测试**

```python
def test_fusion_request_excludes_raw_media_and_marks_conflict(fake_provider):
    result = FusionService(fake_provider).analyze(conflicting_segment())
    assert 'raw_media_path' not in fake_provider.last_request
    assert result.requires_human_review is True
    assert result.evidence_ids
```

- [ ] **Step 2: 执行失败测试**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_fusion.py -v`

Expected: FAIL，提示 Provider Adapter 或融合服务不存在。

- [ ] **Step 3: 实现结构化提示、适配器和失败策略**

定义 provider 协议，读取 `base_url`、模型名和 API Key 的本地配置。融合提示集中在模块常量中，要求输出结论、证据引用、不确定性、冲突说明和人工审核标记。请求只含文本、筛选帧引用/内容和结构化证据，不含原媒体。网络失败写入可重试错误，不覆盖本地证据。

- [ ] **Step 4: 验证 OpenAI-compatible fake、冲突和网络失败场景**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_fusion.py -v`

Expected: PASS。

### Task 9：实现审核操作、局部失效与导出服务

**Files:**
- Create: `backend/app/services/review.py`
- Create: `backend/app/services/exports.py`
- Create: `backend/tests/services/test_review_operations.py`
- Create: `backend/tests/services/test_exports.py`

- [ ] **Step 1: 编写切分/合并仅失效受影响片段测试**

```python
def test_split_marks_only_new_segments_for_reanalysis(review_service):
    result = review_service.split(segment_id='seg-2', at_seconds=12.5)
    assert result.reanalysis_segment_ids == {'seg-2a', 'seg-2b'}
    assert review_service.get('seg-1').analysis_status == AnalysisStatus.CURRENT
```

- [ ] **Step 2: 执行失败测试**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_review_operations.py tests/services/test_exports.py -v`

Expected: FAIL，提示审核或导出服务不存在。

- [ ] **Step 3: 实现审核操作与双格式导出**

实现文本/角色/结论修订、切分、相邻合并、删除与确认。每次操作写入审核日志；局部失效仅进入受影响片段队列。JSON 导出保存机器原始字段、人工字段、证据和最终字段；Markdown 导出按时间轴生成可读报告。

- [ ] **Step 4: 验证审核审计与导出内容**

Run: `cd backend && .venv/bin/python -m pytest tests/services/test_review_operations.py tests/services/test_exports.py -v`

Expected: PASS。

### Task 10：暴露本地 API 与任务执行入口

**Files:**
- Create: `backend/app/api/routes/jobs.py`
- Create: `backend/app/api/routes/segments.py`
- Create: `backend/app/api/routes/settings.py`
- Create: `backend/app/api/routes/exports.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/api/test_jobs.py`
- Create: `backend/tests/api/test_segments.py`

- [ ] **Step 1: 编写上传、审核和导出 API 测试**

```python
def test_confirmed_segment_can_be_exported(client, prepared_job):
    client.post(f'/api/segments/{prepared_job.segment_id}/confirm')
    response = client.post(f'/api/jobs/{prepared_job.id}/exports', json={'format': 'markdown'})
    assert response.status_code == 201
    assert response.json()['artifact_type'] == 'markdown'
```

- [ ] **Step 2: 执行失败测试**

Run: `cd backend && .venv/bin/python -m pytest tests/api/test_jobs.py tests/api/test_segments.py -v`

Expected: FAIL，提示路由不存在。

- [ ] **Step 3: 实现上传、状态、片段、审核、重试、设置和导出路由**

路由只做 schema 校验、服务调用和错误映射。上传流式写入任务目录；任务执行交给 `JobRunner`；所有 API 返回可用于前端渲染的稳定 schema。不得在路由中执行模型推理或嵌入业务文案。

- [ ] **Step 4: 执行 API 测试与 OpenAPI 检查**

Run: `cd backend && .venv/bin/python -m pytest tests/api/test_jobs.py tests/api/test_segments.py -v`

Expected: PASS。

### Task 11：构建 React 任务、设置和 API 数据层

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/jobs.ts`
- Create: `frontend/src/api/settings.ts`
- Create: `frontend/src/constants/copy.ts`
- Create: `frontend/src/constants/task.ts`
- Create: `frontend/src/features/jobs/UploadTaskForm.tsx`
- Create: `frontend/src/features/jobs/TaskProgress.tsx`
- Create: `frontend/src/features/settings/ProviderSettingsForm.tsx`
- Create: `frontend/src/features/jobs/index.module.scss`
- Create: `frontend/src/features/settings/index.module.scss`
- Create: `frontend/src/features/jobs/UploadTaskForm.test.tsx`

- [ ] **Step 1: 编写上传提交状态测试**

```tsx
it('submits a selected local media file', async () => {
  render(<UploadTaskForm createJob={createJob} />)
  await userEvent.upload(screen.getByLabelText(UPLOAD_MEDIA_LABEL), new File(['x'], 'sample.mp4'))
  await userEvent.click(screen.getByRole('button', { name: START_TASK_LABEL }))
  expect(createJob).toHaveBeenCalled()
})
```

- [ ] **Step 2: 执行失败测试**

Run: `cd frontend && npm run test -- UploadTaskForm.test.tsx`

Expected: FAIL，提示组件或常量不存在。

- [ ] **Step 3: 实现 API Client、任务表单、状态展示和 Provider 设置**

使用 Ant Design `Upload`、`Form`、`Progress` 和 `Alert`。文案、轮询间隔、任务状态映射和 API 路径集中到 constants/API 文件；API Key 仅提交本地 FastAPI 设置接口，前端不得写入 localStorage。

- [ ] **Step 4: 验证组件测试与 TypeScript 构建**

Run: `cd frontend && npm run test -- UploadTaskForm.test.tsx && npm run build`

Expected: 测试和构建均通过。

### Task 12：构建片段审核工作台与证据面板

**Files:**
- Create: `frontend/src/features/review/ReviewWorkspace.tsx`
- Create: `frontend/src/features/review/SegmentList.tsx`
- Create: `frontend/src/features/review/SegmentEditor.tsx`
- Create: `frontend/src/components/SegmentAudioPlayer/index.tsx`
- Create: `frontend/src/components/EvidencePanel/index.tsx`
- Create: `frontend/src/features/review/index.module.scss`
- Create: `frontend/src/features/review/ReviewWorkspace.test.tsx`

- [ ] **Step 1: 编写切分和证据冲突可见性测试**

```tsx
it('shows conflicting evidence and sends a split request', async () => {
  render(<ReviewWorkspace job={conflictingJob} />)
  expect(screen.getByText(CONFLICT_REVIEW_COPY)).toBeVisible()
  await userEvent.click(screen.getByRole('button', { name: SPLIT_SEGMENT_LABEL }))
  expect(splitSegment).toHaveBeenCalledWith('seg-2', expect.any(Number))
})
```

- [ ] **Step 2: 执行失败测试**

Run: `cd frontend && npm run test -- ReviewWorkspace.test.tsx`

Expected: FAIL，提示审核组件或常量不存在。

- [ ] **Step 3: 实现分段回放、编辑和审核交互**

审核页使用稳定三栏布局：片段列表、文本/审核编辑区、证据面板。每段显示时间范围、说话人、原始与修订文本、原始音频播放、视频/关键帧、专用模型事实、LLM 解释、不确定性和确认状态。切分位置取播放器当前时间；合并仅允许相邻片段；无脸等不可用证据显示为状态而非错误。

- [ ] **Step 4: 验证审核组件与浏览器布局**

Run: `cd frontend && npm run test -- ReviewWorkspace.test.tsx && npm run build`

Expected: 测试和构建均通过。

### Task 13：实现导出体验、端到端验证与本地运行说明

**Files:**
- Create: `frontend/src/features/exports/ExportPanel.tsx`
- Create: `frontend/src/features/exports/ExportPanel.test.tsx`
- Create: `frontend/e2e/review-workflow.spec.ts`
- Create: `README.md`
- Create: `backend/tests/integration/test_local_pipeline.py`

- [ ] **Step 1: 编写本地端到端审核与导出测试**

```ts
test('uploads a job, confirms a segment, and downloads markdown', async ({ page }) => {
  await page.goto('/')
  await page.setInputFiles('input[type=file]', 'e2e/fixtures/sample.mp4')
  await page.getByRole('button', { name: START_TASK_LABEL }).click()
  await page.getByRole('button', { name: CONFIRM_SEGMENT_LABEL }).click()
  await expect(page.getByRole('button', { name: EXPORT_MARKDOWN_LABEL })).toBeEnabled()
})
```

- [ ] **Step 2: 执行失败测试**

Run: `cd frontend && npx playwright test e2e/review-workflow.spec.ts`

Expected: FAIL，提示导出面板或工作流尚未完成。

- [ ] **Step 3: 实现导出下载、集成测试 fixture 和运行说明**

导出面板仅允许导出已确认片段，并显式告知是否附带原始模型与审核记录。README 说明 Windows + CUDA 前提、本地服务启动、模型下载/配置、云端数据边界、样本验收方式和 macOS 的降级说明；不记录真实密钥。

- [ ] **Step 4: 执行完整验证矩阵**

Run: `cd backend && .venv/bin/python -m pytest`

Expected: 后端单元、API 与集成测试通过。

Run: `cd frontend && npm run test && npm run build && npx playwright test`

Expected: 前端单测、构建与端到端测试通过。

### Task 14：模型基准测试、审查与提交门禁

**Files:**
- Create: `zzz-prompt-debug/origin/设想/video-emotion-transcript-benchmark.md`
- Create: `backend/app/benchmark/run.py`
- Create: `backend/tests/fixtures/benchmark_manifest.json`
- Modify: `.devflow/video-emotion-transcript-workflow/state.md`
- Modify: `.devflow/video-emotion-transcript-workflow/checkpoints.md`

- [ ] **Step 1: 建立人工审核样本和结果记录格式**

测试样本覆盖单人、多人、强 BGM、噪声/混响、清晰人脸、遮挡人脸、无人脸和疑似反讽片段。记录 STT、说话人、专用模型事实、LLM 解释、人工确认和失败原因；不在文档中包含未授权原始媒体。

- [ ] **Step 2: 执行基准测试并记录实际结果**

Run: `cd backend && .venv/bin/python -m app.benchmark.run --manifest tests/fixtures/benchmark_manifest.json`

Expected: 生成按样本和工具分组的 JSON 结果与人工复核入口。

- [ ] **Step 3: 对照 MVP 验收标准进行代码审查**

检查：原始媒体未上传云端；专用模型事实与 LLM 推断分离；冲突进入审核；切分/合并只失效受影响片段；密钥不进入日志或导出；所有延期项仍未被误实现。

- [ ] **Step 4: 更新状态并在用户明确同意后提交**

先回写 mission 的验证证据、未解决风险与后续延期项。只有用户明确要求提交时才执行：

```bash
git add backend frontend README.md .devflow/video-emotion-transcript-workflow zzz-prompt-debug/origin/设想/video-emotion-transcript-benchmark.md
git commit -m "实现视频情感化转写MVP"
```

Expected: 未得到用户明确许可时，不执行 `git commit`。

## 计划自查

- 覆盖性：每项已确认能力均对应任务，包含预处理双音轨、专用模型优先证据、云端融合、片段审核、局部重分析、隐私和导出。
- 范围：延期项未进入任何实现任务；n8n、自动搜索、Electron 和复杂编辑均保持延期。
- 一致性：所有任务围绕 `ProjectJob -> Segment -> Evidence -> Review -> Export` 数据路径；模型调用均位于工具/适配器层。
- 验证：每个行为任务先定义失败测试，最终有后端、前端、端到端和真实样本基准验证。
