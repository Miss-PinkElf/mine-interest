# 视频情感化转写工作流 Decision Log

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-06-10 15:45:35 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录本 mission 的关键决策与延期项，便于后续追溯。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-docs/设想/prompt.md`
- 当前状态（Status）：已完成（Completed）
- 文档边界（Scope / Boundary）：本文件是关键决策真相源（source of truth），不代表需求已进入代码实现。

## 决策记录

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

- 暂不做对象或能力：不搭建可运行原型，不接入真实模型 API，不写 n8n workflow JSON，不做 UI。
- 本轮暂不做原因：当前任务目标是可行性和路线判断；直接实现会把技术选型、成本、隐私和模型准确率风险提前固化。
- 后续触发条件或推荐阶段：当用户确认候选路线后，进入 PRD（Product Requirements Document，产品需求文档）或 OpenSpec（开放规格）阶段，再拆分 MVP（Minimum Viable Product，最小可行产品）任务。
- 说明：暂不做不等于永久放弃；这些能力应在后续 MVP 或原型阶段继续推进。
