# 片段确认后任务状态同步对齐

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 11:06:01 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：确认手动验收发现的任务状态与页面反馈问题的修复边界。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`.devflow/video-emotion-transcript-workflow/NEXT-SESSION-PROMPT-video-emotion-transcript-workflow.md`
- 关联规格（Related Spec）：`.devflow/video-emotion-transcript-workflow/spec/design.md`、`.devflow/video-emotion-transcript-workflow/spec/tasks.md`
- 当前状态（Status）：已对齐（Aligned）
- 文档边界（Scope / Boundary）：本轮修复的对齐真相源；用户已确认状态规则，但本文件本身不替代实施计划或最终验收。

## 现象与原因

- 现象：片段显示 `confirmed`（已确认）后，任务仍显示「待审核」与 70%；重复点击「确认片段」没有可见反馈。导出后页面也不会立即更新任务状态。
- 原因：确认接口只更新片段；任务的 `confirmed` 状态虽已定义，未接入状态转换。前端确认和导出成功后只刷新片段或显示路径，未刷新任务。

## 已确认方案

- 当某任务的全部片段均已确认且至少有一个片段时，任务由 `review`（待审核）转为 `confirmed`（已确认）。
- 导出成功后任务显示 `exported`（已导出）。
- 首次确认有明确成功反馈；已经确认且内容未改变时，按钮显示已确认状态，避免无意义重复请求。修改已确认片段后允许重新确认。
- 状态变更以本地服务持久化结果为准，页面成功操作后重新查询任务。
- 已有任务也遵守同一规则：查询时若片段非空且全部已确认，而任务仍是待审核，应修复持久状态，使用户刷新即可看到已确认。

## 本轮不做 / 后续阶段

- 真实语音转文字（STT）、播放器媒体源和情绪证据：本轮仅修复演示审核状态，避免扩大手动验收范围；用户决定进入真实媒体能力阶段时重新对齐并计划。既有延期记录见 `.devflow/video-emotion-transcript-workflow/deferred/2026-07-13-v1-adapter-vs-deferred.md`。
