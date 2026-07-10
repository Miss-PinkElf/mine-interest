# 视频情感化转写 MVP 任务（Tasks）

## Metadata（元数据）

- 创建时间（Created At）：2026-07-10 15:15:33 +08:00
- 更新时间（Updated At）：2026-07-10 15:15:33 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：追踪 MVP 从工程骨架到真实样本验证的可验证实施任务。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联提案与设计（Related Spec）：`.devflow/video-emotion-transcript-workflow/spec/proposal.md`、`.devflow/video-emotion-transcript-workflow/spec/design.md`
- 关联计划（Related Plan）：`.devflow/video-emotion-transcript-workflow/plans/2026-07-10-video-emotion-transcript-mvp-implementation-plan.md`
- 当前状态（Status）：未开始（Not Started）
- 文档边界（Scope / Boundary）：本文件是实施任务追踪真相源；勾选任务前必须获得 Apply（实施）授权。

## 阶段 1：可运行的本地审核纵向链路

- [ ] 初始化 `backend/` 与 `frontend/`，验证 FastAPI 健康检查、React 构建和本地开发代理。
  - 验证：`backend/.venv/bin/python -m pytest tests/test_health.py -v` 与 `frontend` 生产构建通过。
- [ ] 定义 Job、Segment、Evidence、ReviewOperation 和 ExportArtifact 的领域模型与状态枚举。
  - 验证：原始转写不可被人工修订覆盖。
- [ ] 落地 SQLite repository、本地产物目录和可恢复任务状态。
  - 验证：任务失败后既有质量报告等产物仍存在，重启后任务可恢复。
- [ ] 实现媒体文件上传、任务查询、片段查询和导出的本地 API。
  - 验证：API 测试覆盖上传、确认片段和导出。
- [ ] 实现 React 任务页、设置页、状态进度与基础导出入口。
  - 验证：组件测试覆盖上传提交，API Key 不写入浏览器 localStorage。

## 阶段 2：媒体预处理、转写与分段

- [ ] 实现 FFmpeg 媒体信息提取与音频质量报告。
  - 验证：报告覆盖 BGM、噪声、混响、语音占比、响度、削波和重叠说话的可用性/估计结果。
- [ ] 实现条件预处理和 `audio_raw`、`audio_light`、`audio_stt_ready` 双音轨/三产物策略。
  - 验证：干净音频跳过强处理，BGM 重音频创建 STT 就绪轨；原始轨永不覆盖。
- [ ] 实现可替换 STT、VAD 与说话人分离适配器，将结果标准化为可审核 Segment。
  - 验证：fake engine 和最小真实音频均保留时间范围、说话人与原始输出。
- [ ] 实现片段原始音频回放和基于播放器当前位置的切分、相邻合并、删除、文本/角色修改和确认。
  - 验证：受影响片段之外的分析状态保持当前。

## 阶段 3：工具编排与专用模型事实证据

- [ ] 实现 Tool Registry，声明工具 schema、前置条件、运行位置、GPU 需求、产物和失败策略。
  - 验证：无脸帧不会调用人脸工具，工具选择和原因可追溯。
- [ ] 实现确定性 Orchestrator，按质量、多说话人、人脸和证据状态选择工具。
  - 验证：低质量、多人、无脸和失败分支均产生决策日志。
- [ ] 接入关键帧、音频情绪/事件、MediaPipe 人脸/表情候选和姿态工具的标准化输出。
  - 验证：专用事实与 LLM 叙事证据分离；无人脸是“不可用”而非失败。
- [ ] 实现审核工作台的三栏证据视图。
  - 验证：每段可同时看到原始文本、音频、关键帧、客观证据、LLM 解释和审核状态。

## 阶段 4：云端融合、局部重分析与导出

- [ ] 实现 Provider Adapter、Provider 设置和结构化融合协议。
  - 验证：请求不含原媒体路径；输出包含结论、`evidence_ids`、不确定性、冲突与人工审核标记。
- [ ] 实现专用模型优先的证据融合和云端失败重试。
  - 验证：证据冲突标记人工审核；云端失败保留本地产物且仅重试当前片段。
- [ ] 实现局部重分析队列和 JSON / Markdown 导出。
  - 验证：切分/合并/文本修改只重新处理关联片段；导出保留最终内容和可选审计信息。

## 阶段 5：验证、文档与收口

- [ ] 建立真实样本 benchmark 清单，覆盖单人、多人、BGM、噪声/混响、清晰/遮挡/无人脸和疑似反讽。
  - 验证：结果记录 STT、专用证据、LLM 解释、人工结论与失败原因。
- [ ] 运行后端单测、API/集成测试、前端单测/构建和 Playwright 端到端测试。
  - 验证：全部验证命令通过，或在 bug-log 中记录失败现象、原因和解决方案。
- [ ] 更新 README、mission 状态、checkpoint、决策与 deferred 文档，发起代码审查。
  - 验证：文档与实际实现一致，延期能力未被误实现。

## Apply 门禁

- [ ] 用户明确授权开始 Apply（实施）。
- [ ] 执行前重新读取本文件、`spec/design.md` 和正式实施计划。
- [ ] 每个阶段完成后执行聚焦审查与新鲜验证；未经用户明确同意不得执行 `git commit`。
