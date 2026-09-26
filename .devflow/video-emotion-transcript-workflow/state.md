# 视频情感化转写工作流 State

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-09-27 01:09:39 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：保存当前 mission 的恢复热路径状态。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-prompt-debug/origin/设想/prompt.md`
- 当前状态（Status）：演示闭环第一版已实施；本地验证通过，用户手动验收待进行；本轮提交已获授权。
- 文档边界（Scope / Boundary）：当前快照真相源，不保存完整历史。

## 当前目标

个人本地「情感化转写」MVP：可上传、可审核、可导出；专用事实 + LLM 解释 + 人工审核。

## 本轮完成度

- `spec/tasks.md`：既有任务和本轮增量任务全部勾选。
- 显式演示模式（Demo Mode）：上传后应用内任务运行器（JobRunner）自动生成假语音转文字（Fake STT）片段并进入待审核（review）；普通上传维持原行为。
- 演示来源跨重启恢复；前端轮询片段、支持同一标签页刷新恢复；人工修订先保存再确认，Markdown/JSON 导出均包含修订文本和演示声明。
- 验证：后端 pytest 28 passed；前端 vitest 8 passed + build；本地浏览器完成上传、审核、导出和刷新恢复。
- 用户已授权本轮仅提交 mission 相关文件；提交号以仓库最新提交（commit）为准。

## 既有能力与本轮边界

- 既有一键启动脚本和审核适配层仍可用；本轮新增自动演示转写闭环。
- 演示内容不代表上传媒体的真实语音。真实语音转文字（STT）、真实媒体预处理和情绪证据仍待后续阶段对齐。

## 后续阶段

- 真实语音转文字（STT）、真实媒体预处理和情绪证据：本轮为先验证产品交互闭环而暂缓；用户决定进入真实能力阶段时重新对齐并写计划（Plan）。
- Electron、多人云端、n8n、平台下载与训练等：本轮范围外，见 `deferred/`；在用户明确进入相应阶段时重新评估。

## 关键产物

- 最新 handoff：`handoffs/2026-09-27-009-auto-demo-verified.md`
- 恢复提示：`NEXT-SESSION-PROMPT-video-emotion-transcript-workflow.md`
- 边界：`deferred/2026-07-13-v1-adapter-vs-deferred.md`
- 启动：`scripts/start-local-dev.sh`

## 下次建议

1. 用户按 `README.md` 手动验证演示上传、审核、导出与刷新恢复；若发现问题，记录现象并按 bug 路径修复。
2. 验收反馈后，对齐真实语音转文字（STT）和媒体处理的优先顺序，再写计划（Plan）。

## 2026-09-27 当前恢复点

- 对齐：`plans/2026-09-26-upload-auto-demo-transcript-align.md`；计划：`plans/2026-09-26-upload-auto-demo-transcript-plan.md`；增量任务：`spec/tasks.md`。
- 自动演示转写已通过本地浏览器冒烟；用户手动验收待进行。第一版和延期边界见 `deferred/2026-07-13-v1-adapter-vs-deferred.md`。
