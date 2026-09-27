# 视频情感化转写工作流 Workflow

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-09-27 12:26:52 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：当前流程阶段视图。
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 当前状态（Status）：演示闭环第一版已完成本地验证，用户手动验收待进行
- 文档边界（Scope / Boundary）：当前快照。

## 路径

- 既有重型路径与本轮增量 `spec/tasks.md` 均已完成。
- 本轮 Mini Align（最小对齐）→ Plan（计划）→ OpenSpec（开放规格）→ Apply（实施）→ Verify（验证）已执行。
- Windows PowerShell 一键启动增量已完成轻量计划（Light Plan）、实施（Apply）与验证（Verify）；下一步是用户手动验收。真实语音转文字（STT）和媒体处理进入下一阶段前需重新对齐范围。

## 阶段

| 阶段 | 状态 |
| --- | --- |
| Align/Plan/Spec/Tasks 清单 | 完成 |
| V1 适配层与工作台 | 完成 |
| 一键本地启动脚本 | 完成 |
| 上传后自动演示管线 JobRunner | 第一版完成，通过测试及本地浏览器冒烟；用户手动验收待进行 |
| 真 FFmpeg/STT/CUDA | 后续加深 |
| 延期能力 | 延期中 |
