# 视频情感化转写 MVP 设计（Design）

## Metadata（元数据）

- 创建时间（Created At）：2026-07-10 15:15:33 +08:00
- 更新时间（Updated At）：2026-07-10 15:15:33 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：定义视频情感化转写 MVP 的模块边界、数据流、接口和风险控制。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联提案（Related Proposal）：`.devflow/video-emotion-transcript-workflow/spec/proposal.md`
- 关联计划（Related Plan）：`.devflow/video-emotion-transcript-workflow/plans/2026-07-10-video-emotion-transcript-mvp-implementation-plan.md`
- 当前状态（Status）：已设计（Designed）
- 文档边界（Scope / Boundary）：本文件是 OpenSpec 技术设计真相源，解释如何实现；不授权 Apply（实施）。

## 总体思路

系统使用“本地确定性工具 + 本地状态存储 + 云端证据解释”的混合架构。媒体处理、结构化识别和审核数据由本地服务控制；云端 LLM 只能解释提交给它的片段证据，不能绕过工具直接决定媒体处理步骤。

```text
React 工作台
  -> FastAPI 本地 API
     -> JobRunner（任务执行器）
        -> Media / Preprocess / Transcription 工具
        -> Specialized Evidence 工具
        -> Tool Registry + Orchestrator
        -> LLM Provider Adapter + Fusion
     -> SQLite + Artifact Store
  -> 片段审核与 JSON / Markdown 导出
```

## 结构与边界

### 前端（frontend）

- 任务页：选择本地媒体、启动任务、显示阶段状态和失败摘要。
- 审核工作台：稳定三栏布局，包含片段列表、编辑/播放区和证据面板。
- 设置页：保存本地服务所需 Provider 配置；浏览器不把密钥写入 localStorage。
- 导出页：仅导出已确认片段，可选择是否包含模型原始结果和审核记录。

React 组件按 `features/jobs`、`features/review`、`features/settings`、`features/exports` 分离，通用音频播放与证据展示组件单独放在 `components`。使用 Ant Design（Antd）和 CSS Modules，业务文案、状态键和阈值集中在常量模块。

### 后端（backend）

- `domain`：定义 Job、Segment、Evidence、ReviewOperation、ExportArtifact 的不变量和 API schema。
- `repositories`：SQLite 持久化任务、片段和本地 Provider 设置。
- `artifacts`：为每个 Job 分配独立目录，保存输入媒体引用、音轨、帧、引擎原始输出、质量报告和导出文件。
- `media` / `preprocess`：抽取音频、生成质量报告，按条件执行人声分离、去混响、保守降噪和响度标准化。
- `transcription`：将不同 STT / diarization 引擎统一为时间片段。
- `evidence`：写入专用模型的客观事实证据。
- `tool_registry` / `orchestrator`：声明工具输入输出与前置条件，生成可追溯的条件路由决策。
- `fusion`：构造受限的云端证据请求，解析结构化解释并处理冲突与重试。
- `review` / `exports`：维护人工修改、局部失效和最终导出。

## 核心数据模型

```text
ProjectJob
  id, source_media, status, failure, artifact_root
  -> Segments[]
       id, start, end, speaker
       raw_text, edited_text, final_text
       analysis_status, review_status
       -> Evidence[]
            source, kind, payload, confidence, availability
       -> ReviewOperations[]
  -> ExportArtifacts[]
```

- `raw_text` 是模型原始转写，永不覆盖。
- `edited_text` 保存人工修订，`final_text` 为已确认输出文本。
- `Evidence.source` 区分专用模型、音频分析、OCR、LLM 和人工审核；`availability` 区分可用、不可用与失败。
- 每个修改记录操作人、时间、前后状态和受影响片段；个人本地模式下操作人固定为本地用户标识。

## 数据流与接口

### 任务管线

```text
上传媒体
-> 创建 Job 与本地产物目录
-> 媒体信息 / 音频质量报告
-> 生成 audio_raw、audio_light、audio_stt_ready
-> VAD / STT / diarization 形成 Segments
-> 抽帧和专用音频/视觉证据
-> 云端融合生成有依据的解释
-> 待人工审核
-> 确认 / 局部重分析
-> JSON / Markdown
```

API 只承担 schema 校验、服务调用和错误映射：

- `POST /api/jobs`：上传本地媒体并创建任务。
- `GET /api/jobs/{job_id}`：读取任务、阶段、失败信息和产物摘要。
- `GET /api/jobs/{job_id}/segments`：读取审核片段与证据摘要。
- `POST /api/segments/{segment_id}/split`、`/merge`、`/delete`、`/confirm`：执行审核操作。
- `POST /api/segments/{segment_id}/reanalyze`：只重跑失效片段。
- `POST /api/jobs/{job_id}/exports`：生成 JSON 或 Markdown。
- `GET` / `PUT /api/settings/provider`：读取或保存本机 Provider 配置，响应中不回显完整密钥。

## 预处理与双音轨

预处理借鉴训练数据处理材料的“先判断、再处理”原则，但不为获得干声而破坏情绪信息。

- `audio_raw`：原始提取音轨，始终保存。
- `audio_light`：仅做必要的轻量响度处理，供人工回听与情绪判断。
- `audio_stt_ready`：根据 BGM、噪声、混响和语音占比条件处理，供 STT 和说话人分离。

质量报告决定工具是否调用。原音清晰时跳过人声分离与强降噪；检测到明显 BGM 时才调用分离工具。每次工具调用写入原因、输入/输出产物和失败信息。所有阈值由命名配置定义，不在业务逻辑中硬编码。

## 专用模型优先的证据融合

专用模型先提供可量化事实：人脸有无、面部关键点/Blendshapes、头部方向、姿态关键点、基础表情候选、音频情绪/事件、能量、音高、语速和停顿。LLM 再结合转写、关键帧、OCR 和这些事实给出“可能反讽/调侃/尴尬”等语义结论。

融合不能使用固定百分比权重。LLM 结果必须返回：结论、置信度、不确定性、引用的 `evidence_ids`、冲突说明和 `requires_human_review`。专用模型与语义结论冲突时，系统保留全部证据并进入审核队列。

关键帧按固定间隔补充采样，同时按每个片段的开始、中间和结束取帧，避免表情与相邻语句错位。无人脸/无姿态只产生“不可用”证据，不中断任务。

## 失败恢复与隐私

- 每个 Job 的中间产物独立保存；失败只标记当前阶段，不清除上游产物。
- 云端请求失败仅重试片段融合步骤；本地任务重新启动时将中断状态转为可恢复状态。
- 任一专用工具失败时，其他可用证据仍可进入审核；前端展示可恢复操作。
- 原始视频、音频、完整关键帧和审核记录只保存在本机。
- 云端调用只发送当前片段必须的文本、筛选帧和证据摘要；记录请求包含的证据标识，不记录 API Key。

## 风险与权衡

- Windows + CUDA 的模型兼容与显存占用是实施风险：使用工具接口、串行重 GPU 阶段和真实样本 benchmark 控制风险。
- 表情/姿态模型只反映有限视觉特征，不等同复杂情绪：结果作为证据，不作为单一结论。
- 云端模型质量、成本和隐私边界随 Provider 改变：适配器隔离供应商，并在前端显示调用阶段与错误状态。
- 复杂音频编辑会扩张为剪辑器：MVP 仅支持片段切分、相邻合并、删除和文本/结论修订。
