# 视频情感化转写工作流 Decision Log

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-07-10 16:40:38 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录本 mission 的关键决策与延期项，便于后续追溯。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-prompt-debug/origin/设想/prompt.md`
- 当前状态（Status）：规格已就绪（Spec Ready）
- 文档边界（Scope / Boundary）：本文件是关键决策真相源（source of truth），不代表需求已进入代码实现。

## 决策记录

### 2026-07-10 16:40:38 +08:00 - 保持第一版范围并从 Task 3 红灯恢复

- 决策（Decision）：本轮只完成 Task 1-2，并保留 Task 3 的失败测试作为下次实现入口；不提前实现媒体处理、模型接入、审核工作台或任何已延期能力。
- 原因（Rationale）：用户要求在上下文变长时收尾并于新会话继续，避免未完成的仓储设计与后续范围混合。
- 影响（Impact）：下一会话从 `backend/tests/services/test_job_lifecycle.py` 开始，先完成 SQLite repository（仓储）、Artifact Store（产物存储）和任务恢复，再按 `spec/tasks.md` 顺序推进。

### 2026-07-10 16:08:59 +08:00 - 依赖安装切换为默认源并采用子代理 Apply

- 决策（Decision）：因清华 npm 镜像不可用，后续依赖安装使用各包管理器默认源（default registry）；允许按子代理驱动开发（Subagent-Driven Development）推进 Apply（实施），本轮不执行 `git commit`。
- 原因（Rationale）：用户明确授权切换至默认源并要求使用子代理；前端安装受清华 npm Registry（npm 注册表）HTTP 404 阻塞。
- 影响（Impact）：`frontend/.npmrc` 使用 `https://registry.npmjs.org/`；后续 Python 安装不再强制指定清华 PyPI 镜像。每个计划任务仍需经过实现、规格审查和代码质量审查门禁。

### 2026-07-10 15:54:20 +08:00 - 依赖安装默认使用清华镜像源

- 决策（Decision）：在 Apply（实施）阶段，Python 依赖默认通过 `https://pypi.tuna.tsinghua.edu.cn/simple` 安装；前端 npm 依赖默认使用清华 npm 镜像，并在首次安装前核验镜像可用性。
- 原因（Rationale）：用户明确指定使用清华镜像源（Tsinghua Mirror）作为默认依赖来源。
- 影响（Impact）：该决策已被 2026-07-10 16:08:59 +08:00 的“默认源”授权替代。

### 2026-07-10 15:23:33 +08:00 - 完成 OpenSpec，但不进入 Apply

- 决策（Decision）：将已确认的 MVP 对齐与 Plan 落为 `spec/proposal.md`、`spec/design.md` 和 `spec/tasks.md`，本轮停在规格就绪状态。
- 原因（Rationale）：用户明确要求先完成规格和收尾，在新对话再开始后续步骤，避免长上下文中直接实施。
- 影响（Impact）：下次需要用户明确授权 Apply，才能从 Task 1 开始安装依赖或创建应用代码。

### 2026-07-10 15:05:09 +08:00 - 采用专用模型优先的混合工作台架构

- 决策（Decision）：第一版采用 React + Vite 浏览器工作台、FastAPI 本地服务、SQLite 与本地产物目录；本地专用模型提供事实证据，云端 LLM 负责解释与融合。
- 原因（Rationale）：STT、预处理、人脸/姿态和音频特征具有确定性与隐私要求；反讽、语境和多证据解释更适合云端多模态 LLM。纯 n8n 或纯 LLM Agent 都无法可靠承担媒体处理和审核追溯。
- 影响（Impact）：工具注册表与 Provider Adapter 是核心边界；n8n 延期为后续工作流壳层。

### 2026-07-10 15:05:09 +08:00 - 采用按需预处理与双音轨保留

- 决策（Decision）：保留 `audio_raw` / `audio_light` 与 `audio_stt_ready`，仅在质量报告显示必要时启用人声分离、去混响或降噪。
- 原因（Rationale）：训练数据清洗经验不能直接用于情绪理解；过度处理会破坏气声、停顿、能量与尾音等语气证据。
- 影响（Impact）：审核界面可回放不同轨道，STT 与情绪分析不会被迫使用同一处理结果。

### 2026-06-10 15:45:35 +08:00 - 明确第一版范围与延期项

- 决策（Decision）：在候选路线文档中新增“第一版范围与明确延期矩阵（MVP Scope and Deferred Scope Matrix）”。
- 原因（Rationale）：用户提醒后续会新开对话继续讨论，必须把“第一版做什么”和“后续明确延期什么”落盘，避免恢复时把候选增强能力误认为 MVP 必达项。
- 影响（Impact）：下一轮可以直接围绕 MVP（Minimum Viable Product，最小可行产品）范围进入 PRD（Product Requirements Document，产品需求文档）或 OpenSpec（开放规格），不需要重新从全部设想开始。

### 2026-06-10 15:34:26 +08:00 - 完善候选路线文档 v2

- 决策（Decision）：吸收 `STT-情感视频理解-可行性分析.md` 和 `数据集处理.md` 的可借鉴内容，更新 `zzz-docs/设想/视频情感化转写可行性路线.md`。
- 原因（Rationale）：原 v1 文档偏稳健架构与风险边界，缺少 SenseVoice-Small（FunASR）、audio-separator、LangGraph、工程排期、成本/GPU 口径以及细化音频预处理经验。
- 影响（Impact）：v2 文档更接近后续 MVP（Minimum Viable Product，最小可行产品）设计输入，但仍保持候选项（Candidate）状态，不直接触发实现。
- 口径（Position）：对补充材料中的“唯一”“最强”“固定价格”等时效性或强断言统一降级为候选判断，并要求实施阶段用样本集实测。

### 2026-06-10 11:43:30 +08:00 - 采用“调研 + 候选路线文档”轻量路径

- 决策（Decision）：本轮不进入代码实现，先完成技术可行性评估（feasibility assessment）和候选路线（candidate roadmap）。
- 原因（Rationale）：原始需求仍处于设想阶段，涉及语音识别（STT）、说话人分离（speaker diarization）、视觉理解（vision understanding）、表情识别（facial expression recognition）、外部搜索（external search）和 Agent 编排（agent orchestration）多个模块，直接实现风险过高。
- 影响（Impact）：产出文档将作为后续 PRD（Product Requirements Document，产品需求文档）或 OpenSpec（开放规格）的输入。

### 2026-06-10 11:43:30 +08:00 - 推荐先做 Agent/Python 核心，再接 n8n

- 决策（Decision）：候选路线优先推荐 Python pipeline + Agent tool layer，n8n workflow 作为编排壳层或演示层。
- 原因（Rationale）：媒体处理、抽帧、模型推理、缓存、长任务队列和错误恢复更适合代码化；n8n 适合连接 API、人工审核和自动化流程，不适合承载全部重计算逻辑。
- 影响（Impact）：后续如实现，应先设计稳定的本地/服务端核心能力，再暴露给 n8n 节点调用。

## 本轮不做 / 后续阶段（Deferred Scope）

当前明确延期项、原因和触发条件统一记录在 `deferred/2026-07-10-mvp-deferred-scope.md`。这些能力不是永久放弃；仅在本 MVP 的单视频审核闭环完成真实样本验证前不进入 Apply。

## 2026-07-13 14:12:10 +08:00 - 中断任务恢复策略

- 决策：应用重启时，将状态为 `processing` 的任务标记为 `failed`，错误码 `JOB_INTERRUPTED`，`retryable=true`，且不删除任何产物。
- 备选：直接回退为 `pending`；或新增独立 `interrupted` 状态。
- 原因：现有枚举无 interrupted；失败 + 可重试既能暴露中断事实，又支持后续人工/管线重入，并与“失败不清理上游产物”一致。

