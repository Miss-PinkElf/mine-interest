# 视频情感化转写工作流 Workflow

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-09-28 11:42:20 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：当前流程阶段视图。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 当前状态（Status）：第一版演示闭环与状态修复已通过用户手动验收；跨会话交接就绪。
- 文档边界（Scope / Boundary）：当前流程快照，不替代规格、计划或下一阶段授权。

## 当前路径

- 本轮状态问题按 Mini Align（最小对齐）→Plan（计划）→OpenSpec（开放规格）→Apply（实施）→Verify（验证）处理；代码与用户手动验收均通过，进入 Close（收尾）。
- 真实 STT（语音转文字）、媒体处理和证据链路尚未完成下一阶段 Align（对齐），不得从候选项或旧规格直接进入实施。

## 阶段状态

| 阶段 | 当前状态 |
| --- | --- |
| V1 适配层与显式演示闭环 | 第一版完成，用户 Mac mini 手动验收通过 |
| 片段确认与任务状态同步 | 修复完成，自动测试与用户手动验收通过 |
| 本轮交接与提交 | 用户明确授权，仅提交本 mission 相关文件 |
| 真实 FFmpeg / STT / 片段回放 / 情绪证据 | 后续阶段，待样本与范围对齐 |
| 其他延期能力 | 见 `deferred/`，非永久放弃 |
