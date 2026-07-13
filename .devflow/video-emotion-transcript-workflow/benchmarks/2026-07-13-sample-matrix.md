# 真实样本 Benchmark 清单

## Metadata（元数据）

- 创建时间（Created At）：2026-07-13 14:30:00 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：定义 MVP 验证用真实样本矩阵与记录字段。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 当前状态（Status）：计划中（Planned）
- 文档边界（Scope / Boundary）：样本清单真相源；不代表已跑完全部真实模型结果。

## 样本矩阵

| 场景 | 说明 | 期望观察 |
| --- | --- | --- |
| 单人清晰 | 单说话人、低噪声 | STT 稳定，专用证据可用 |
| 多人对话 | 2+ 说话人轮替 | diarization 分段正确 |
| 强 BGM | 背景音乐明显 | 生成 STT 就绪轨，原始轨保留 |
| 噪声/混响 | 环境噪声或混响 | 条件预处理启用 |
| 清晰人脸 | 正面人脸可见 | face_analysis 可选中 |
| 遮挡/侧脸 | 人脸不完整 | 证据降级而非硬失败 |
| 无人脸 | 纯音频或无人物画面 | face 标记 unavailable |
| 疑似反讽 | 字面与语气可能冲突 | 融合标记 requires_human_review |

## 记录字段

- sample_id
- stt_result_summary
- specialized_evidence_summary
- llm_interpretation
- human_final_label
- failure_reason
