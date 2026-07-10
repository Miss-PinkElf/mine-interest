# 视频情感化转写工作流 Workflow

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-07-10 15:23:33 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录“视频/音频情感化转写工作流（video emotion transcript workflow）”调研任务的 devflow 阶段。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-prompt-debug/origin/设想/prompt.md`
- 当前状态（Status）：规格已就绪，等待实施授权（Spec Ready, Awaiting Apply Authorization）
- 文档边界（Scope / Boundary）：本文件是当前 mission 的流程真相源（source of truth），只记录阶段和门禁，不代表最终批准实现方案。

## 当前路径

重型路径（Heavy Path）：Align -> Plan -> OpenSpec -> Apply -> Review -> Verify -> Close。

## 阶段状态

- Classify（分类）：已完成。任务由“技术调研”升级为跨前后端、模型与审核体验的 MVP 构建，采用重型路径。
- Mission Init（任务初始化）：已完成。已建立 devflow 工作区。
- Align（对齐）：已完成并获用户确认。对齐真相源为 `plans/2026-07-10-video-emotion-transcript-mvp-align.md`。
- Plan（计划）：已完成。计划真相源为 `plans/2026-07-10-video-emotion-transcript-mvp-implementation-plan.md`，已完成覆盖性、占位符和路径自查。
- OpenSpec（开放规格）：已完成。`spec/proposal.md`、`spec/design.md` 与 `spec/tasks.md` 已落盘并与 Plan 一致。
- Apply（实施）：未开始。用户明确要求本轮不进入 Apply；下次必须重新获得实施授权后，使用 `openspec-apply-change` 从 Task 1 开始。
