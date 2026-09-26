# 视频情感化转写工作流 Backlog

## Metadata（元数据）

- 创建时间（Created At）：2026-07-13 14:28:23 +08:00
- 更新时间（Updated At）：2026-09-27 01:09:39 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录一句话轻量后续想法。
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 当前状态（Status）：活跃（Active）
- 文档边界（Scope / Boundary）：轻量 backlog，不是延期真相源。

## 条目

- 先换真实 FFmpeg 质量报告，再换 STT，最后换视觉模型（降低一次集成面）。
- Provider 设置页可增加“测试连接”按钮（调用轻量 chat/completions）。
- 导出后提供浏览器下载，而不仅返回本机路径字符串。
- 候选项（Candidate）：在真实证据链路成熟后，评估大语言模型（LLM）基于工具元数据辅助选择分析工具；需先讨论可控范围和可复现性。
