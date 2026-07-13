# 视频情感化转写工作流 Backlog

## Metadata（元数据）

- 创建时间（Created At）：2026-07-13 14:28:23 +08:00
- 更新时间（Updated At）：2026-07-13 14:28:23 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录一句话轻量后续想法。
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 当前状态（Status）：活跃（Active）
- 文档边界（Scope / Boundary）：轻量 backlog，不是延期真相源。

## 条目

- 先换真实 FFmpeg 质量报告，再换 STT，最后换视觉模型（降低一次集成面）。
- Provider 设置页可增加“测试连接”按钮（调用轻量 chat/completions）。
- 导出后提供浏览器下载，而不仅返回本机路径字符串。
- JobRunner 后台执行管线，前端轮询状态（目前上传后不自动跑全管线）。
