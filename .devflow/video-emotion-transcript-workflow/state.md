# 视频情感化转写工作流 State

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-06-10 15:45:35 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：保存当前 mission 的恢复热路径（resume hot path）状态。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-docs/设想/prompt.md`
- 当前状态（Status）：已完成（Completed）
- 文档边界（Scope / Boundary）：本文件是当前 mission 的当前状态真相源（source of truth），不保存完整历史。

## 当前目标

基于 `zzz-docs/设想/prompt.md` 的设想，完成视频/音频“情感化转写（emotion-aware transcription）”技术可行性调研，并输出候选路线文档。

## 已确认约束

- 输出语言以中文和英文为主。
- 关键术语、模块名、规则名使用中文（English）双语表达。
- 本轮只做调研和候选文档，不写业务代码，不搭建原型。
- 文档必须标注候选项（Candidate），不能伪装为已批准计划（Plan）。

## 当前产物

- 计划文档：`plans/2026-06-10-video-emotion-transcript-workflow-plan.md`
- v2 完善计划：`plans/2026-06-10-video-emotion-transcript-v2-doc-plan.md`
- 最终候选路线文档：`zzz-docs/设想/视频情感化转写可行性路线.md`
- 最新 handoff：`handoffs/2026-06-10-001-resume-ready.md`
- 下一会话入口：`NEXT-SESSION-PROMPT.md`

## 验证结果

- 已验证文件全部落盘。
- 已验证候选路线文档覆盖可行性、技术栈、Agent / n8n workflow 路线、大致实施思路。
- 已验证候选路线文档包含 Metadata（元数据）、候选项（Candidate）状态和延期项（Deferred Scope）。

## 当前结论

候选路线文档已完成 v2 完善：补入 SenseVoice-Small（FunASR）、audio-separator、emotion2vec+、LangGraph、音频预处理细化方案、工程实施路线和资源估算口径。后续如果继续推进，应先确认 MVP（Minimum Viable Product，最小可行产品）范围，再进入 PRD（Product Requirements Document，产品需求文档）或 OpenSpec（开放规格）阶段。

## 第一版范围与延期项

- 第一版建议聚焦：本地文件输入、音频质量报告（audio quality report）、SenseVoice-Small baseline、WhisperX + pyannote.audio baseline、基础抽帧、多模态 LLM 画面描述、低置信度人工审核列表、Markdown / JSON 输出。
- 第一版可选：人声分离（vocal separation）、表情识别（facial expression recognition）。
- 明确延期：平台自动下载、自动评论抓取、反向搜图、n8n workflow、复杂前端 UI、自训练情绪模型、全自动梗理解。
- 延期原因：这些能力依赖合规边界、成本预算、样本验证和核心 worker 稳定性；当前不是永久放弃，只是不进入第一版 MVP。

## 下次建议

新对话先读取 `NEXT-SESSION-PROMPT.md`、`state.md`、`checkpoints.md` 和最新 handoff。下一步建议围绕 MVP 范围写 PRD（Product Requirements Document，产品需求文档）或 OpenSpec（开放规格），不要直接实现。
