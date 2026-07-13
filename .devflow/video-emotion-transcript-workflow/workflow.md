# 视频情感化转写工作流 Workflow

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-07-13 15:05:44 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：当前流程阶段视图。
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 当前状态（Status）：代码 Apply 完成 → 产品加深（JobRunner）
- 文档边界（Scope / Boundary）：当前快照。

## 路径

- 重型路径 Apply 的 `spec/tasks.md` 已全部完成。
- 下一阶段：**产品主路径加深**（非新开延期范围）。
- 建议新对话：Mini Align → 短 plan（仅 JobRunner/Fake STT）→ Apply。

## 阶段

| 阶段 | 状态 |
| --- | --- |
| Align/Plan/Spec/Tasks 清单 | 完成 |
| V1 适配层与工作台 | 完成 |
| 一键本地启动脚本 | 完成 |
| 上传后自动管线 JobRunner | **未开始（下一优先）** |
| 真 FFmpeg/STT/CUDA | 后续加深 |
| 延期能力 | 延期中 |
