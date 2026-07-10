# 视频情感化转写工作流 State

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-07-10 15:23:33 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：保存当前 mission 的恢复热路径（resume hot path）状态。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-prompt-debug/origin/设想/prompt.md`
- 当前状态（Status）：规格已就绪，等待实施授权（Spec Ready, Awaiting Apply Authorization）
- 文档边界（Scope / Boundary）：本文件是当前 mission 的当前状态真相源（source of truth），不保存完整历史。

## 当前目标

基于 `zzz-prompt-debug/origin/设想/prompt.md`，在用户明确授权后实施个人本地使用的视频/音频“情感化转写（emotion-aware transcription）”MVP。

## 已确认约束

- 输出语言以中文和英文为主。
- 关键术语、模块名、规则名使用中文（English）双语表达。
- 第一版是 React + Vite 浏览器工作台与 Python FastAPI 本地服务，不做 Electron、登录、多用户或云端部署。
- Windows + NVIDIA RTX 3080 / 20GB 显存是正式运行目标；macOS 仅作为后续降级运行目标。
- 本地承担媒体预处理、STT、说话人分离和专用音频/视觉模型；云端 LLM 承担多模态证据解释与融合。
- 人工审核支持片段回放、文本/结论编辑、切分、合并、删除、确认与局部重分析。
- 专用模型优先提供事实证据，LLM 负责有依据的语义解释；冲突应暴露给人工审核。
- OpenSpec（开放规格）已完成，但用户明确要求本轮不进入 Apply（实施）。

## 当前产物

- 计划文档：`plans/2026-06-10-video-emotion-transcript-workflow-plan.md`
- v2 完善计划：`plans/2026-06-10-video-emotion-transcript-v2-doc-plan.md`
- 最终候选路线文档：`zzz-docs/设想/视频情感化转写可行性路线.md`
- 最新 handoff：`handoffs/2026-07-10-002-spec-ready.md`
- 下一会话入口：`NEXT-SESSION-PROMPT-video-emotion-transcript-workflow.md`
- 已确认 MVP 对齐：`plans/2026-07-10-video-emotion-transcript-mvp-align.md`
- 正式实施计划：`plans/2026-07-10-video-emotion-transcript-mvp-implementation-plan.md`
- OpenSpec 提案：`spec/proposal.md`
- OpenSpec 设计：`spec/design.md`
- OpenSpec 任务：`spec/tasks.md`
- 当前延期范围：`deferred/2026-07-10-mvp-deferred-scope.md`

## 验证结果

- 已验证对齐、计划与 OpenSpec artifact 均落盘，且与用户确认的 MVP 边界一致。
- 已验证 Plan 无占位符、路径缺失与格式错误。
- 未执行应用代码、依赖安装、模型下载、真实样本 benchmark 或前后端测试。

## 当前结论

候选路线调研、MVP 对齐、正式 Plan 和 OpenSpec 均已完成。下一步是等待用户明确授权 Apply；授权后从实施计划的 Task 1 开始，先建立可运行的 React + FastAPI 骨架和健康检查，再按 tasks 逐项推进。

## 第一版范围与延期项

- 第一版范围与延期项以 `spec/proposal.md` 和 `deferred/2026-07-10-mvp-deferred-scope.md` 为准；当前不进入延期能力的实现。

## 下次建议

新会话默认先读取 `state.md`、`checkpoints.md`、`spec/tasks.md`。用户授权 Apply 后，读取正式 Plan 的 Task 1，使用 `openspec-apply-change` 和测试驱动开发开始实现；未授权时仅可继续讨论、修订规格或计划。
