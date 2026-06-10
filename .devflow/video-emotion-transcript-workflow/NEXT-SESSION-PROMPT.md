# 下一会话提示：视频情感化转写工作流

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 15:45:35 +08:00
- 更新时间（Updated At）：2026-06-10 15:45:35 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：为新对话继续推进“视频情感化转写工作流（video emotion transcript workflow）”提供最短恢复入口。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-docs/设想/prompt.md`
- 当前状态（Status）：候选项（Candidate）
- 文档边界（Scope / Boundary）：本文件是下一会话恢复提示，不是已批准实现方案，不直接触发代码实现。

## 给下一位 Agent 的提示

请继续 `video-emotion-transcript-workflow` mission。先读取：

1. `.devflow/video-emotion-transcript-workflow/state.md`
2. `.devflow/video-emotion-transcript-workflow/checkpoints.md`
3. `.devflow/video-emotion-transcript-workflow/handoffs/index.md`
4. `.devflow/video-emotion-transcript-workflow/handoffs/2026-06-10-001-resume-ready.md`
5. `zzz-docs/设想/视频情感化转写可行性路线.md`

当前已完成候选可行性文档 v2，不要直接实现代码。下一步建议先和用户确认第一版 MVP（Minimum Viable Product，最小可行产品）范围，然后进入 PRD（Product Requirements Document，产品需求文档）或 OpenSpec（开放规格）。

第一版建议聚焦：

- 本地视频/音频文件输入。
- 音频质量报告（audio quality report）。
- SenseVoice-Small（FunASR）baseline。
- WhisperX + pyannote.audio baseline。
- 基础抽帧和多模态 LLM 画面描述。
- 低置信度人工审核列表。
- Markdown / JSON 输出。

明确延期：

- 平台自动下载。
- 自动评论抓取。
- 反向搜图。
- n8n workflow。
- 复杂前端 UI。
- 自训练情绪模型。
- 全自动梗理解。
