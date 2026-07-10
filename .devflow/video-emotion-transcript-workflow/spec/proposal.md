# 视频情感化转写 MVP 提案（Proposal）

## Metadata（元数据）

- 创建时间（Created At）：2026-07-10 15:15:33 +08:00
- 更新时间（Updated At）：2026-07-10 15:15:33 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：将已确认的 MVP 范围转为实施前的正式变更提案。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联对齐（Related Align）：`.devflow/video-emotion-transcript-workflow/plans/2026-07-10-video-emotion-transcript-mvp-align.md`
- 关联计划（Related Plan）：`.devflow/video-emotion-transcript-workflow/plans/2026-07-10-video-emotion-transcript-mvp-implementation-plan.md`
- 当前状态（Status）：已提案（Proposed）
- 文档边界（Scope / Boundary）：本文件是 OpenSpec 提案真相源，定义做什么和不做什么；不授权 Apply（实施）。

## 背景

原始设想要求把本地视频或音频转为带时间轴的文字描述，并结合语音、表情、动作、画面与语境解释情绪、语气和潜在反讽。普通 STT（Speech to Text，语音转文字）只能回答“说了什么”，无法可靠回答“为什么这样说、证据是什么”。

此前技术调研已确认：媒体处理、STT、说话人分离和可量化视觉特征应由本地专用模型承担；云端多模态 LLM（Multimodal LLM）适合基于这些证据做语义解释。当前仓库没有可复用应用骨架，因此 MVP 需要从零建立本地浏览器工作台和可恢复的任务模型。

## 目标

构建仅供个人使用的本地浏览器工作台。用户提交一个本地视频或音频任务后，可以获得可播放、可编辑、可审核的时间片段；每个片段保留原始转写、专用模型事实证据、云端解释、置信度和人工修订，确认后导出 JSON / Markdown。

成功标准：

- 单个本地媒体文件可创建为可恢复任务，并保留每个阶段的本地产物。
- 任务生成带时间范围和说话人信息的可审核片段。
- 音频和视觉专用模型结果与 LLM 语义结论分开保存，冲突必须可见。
- 审核者可以播放、编辑、切分、合并、删除、确认片段；变更仅重跑受影响片段。
- 原始媒体默认不上传；云端请求只携带当前片段所需文本、关键帧和证据摘要。

## 范围

- React + Vite 浏览器前端、Python FastAPI 本地服务、SQLite 任务/审核记录和每任务本地产物目录。
- 媒体质量报告、条件预处理、原始/轻处理音轨与 STT 就绪音轨的双音轨策略。
- VAD（Voice Activity Detection，语音活动检测）、STT、说话人分离和时间轴对齐。
- 关键帧、音频情绪/事件、人脸基础事实、表情候选和姿态特征的专用工具接口。
- 工具注册表（Tool Registry）与确定性 Agent 编排（Agent Orchestration），记录工具选择理由。
- 可替换云端模型提供方（LLM Provider Adapter）与“专用模型优先的多模态证据融合”。
- 片段审核、局部重分析、JSON / Markdown 导出和端到端真实样本基准测试。

## 非目标

- Electron、账户、多用户、云端部署、复杂波形/频谱编辑或多轨剪辑。
- 平台自动下载、自动评论抓取、自动网页搜索、自动反向搜图。
- 全量动作识别、自动梗库、全自动梗理解、模型微调、自训练情绪模型和跨视频分析。
- n8n workflow、第三方通知或外部系统分发。

## 关键边界场景

- 原始音频清晰时不得强制人声分离或降噪；处理前后音轨均须保留，防止情绪线索被破坏。
- 无人脸、遮挡人脸、没有姿态或没有语音是正常分析结果，不是任务失败。
- 专用模型与 LLM 判断冲突时，必须保留双方证据并标记人工审核，不能静默选择其中之一。
- 云端模型不可用时，已完成的本地产物和专用模型证据必须保留并可重试。
- 片段切分、合并或文本/角色修订后，只失效相关片段的分析，不重跑完整媒体。

## 开放问题与处理方式

- Windows + CUDA 下各模型的具体版本、Python 依赖组合和显存占用尚未实测：在实施初期通过受控 baseline（基线）和样本 benchmark（基准测试）确认。
- 默认云端模型提供方未固定：以 `base_url`、模型名和 API Key 的本地配置解决，不绑定供应商。
- 最终验收样本集尚未建立：在实施末期建立覆盖多人、BGM、噪声、混响、人脸可见性和疑似反讽的人工复核样本。

## 进入 Apply 的条件

本 proposal、design 与 tasks 已完成。用户本轮明确要求先不 Apply；因此当前只具备规格就绪条件，不具备实施授权。下次会话必须先读取当前 mission 的 `state.md` 和 `checkpoints.md`，再由用户明确授权进入 Apply。
