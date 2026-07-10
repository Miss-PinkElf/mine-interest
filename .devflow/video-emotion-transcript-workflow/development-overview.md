# 视频情感化转写工作流 Development Overview

## Metadata（元数据）

- 创建时间（Created At）：2026-07-10 15:15:33 +08:00
- 更新时间（Updated At）：2026-07-10 15:15:33 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录 mission 从可行性调研到 MVP 规格就绪的完整阶段脉络。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 当前状态（Status）：规格就绪（Spec Ready）
- 文档边界（Scope / Boundary）：本文件是长期过程概览，不替代 `state.md`、`checkpoints.md`、Plan 或 OpenSpec 真相源。

## 阶段脉络

1. 2026-06-10：完成技术可行性调研，形成候选路线；当时不进入代码实现。
2. 2026-07-10：重新读取原始设想并完成重型 Align（对齐）。目标从“情绪标签 STT”明确为“证据驱动视频理解工作台”。
3. 2026-07-10：确认个人本地浏览器产品形态、Windows + RTX 3080 / 20GB 运行目标、本地专用模型与云端 LLM 的分工、可编辑分段审核和延期范围。
4. 2026-07-10：完成实施计划及 OpenSpec proposal/design/tasks；当前未开始安装依赖、创建应用代码或执行模型 benchmark。

## 稳定结论

- 本地负责媒体处理、可量化专用模型事实和产物存储；云端 LLM 负责引用证据的语义解释。
- 音频预处理必须按质量条件路由并保留原始/轻处理轨，不能为 STT 过度清洗而破坏情绪线索。
- 审核对象是有时间范围的 Segment（片段），人工可以改文本、结论和片段边界；局部变更只重跑受影响片段。
- n8n、自动搜索、自动评论、复杂编辑、多用户与 Electron 均已明确延期，不是永久放弃。
