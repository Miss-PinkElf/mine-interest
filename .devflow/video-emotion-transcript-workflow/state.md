# 视频情感化转写工作流 State

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-09-28 11:42:20 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：保存当前 mission 的恢复热路径状态。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-prompt-debug/origin/设想/prompt.md`
- 当前状态（Status）：演示闭环与状态修复已通过用户手动验收；本轮按用户授权提交并跨会话交接。
- 文档边界（Scope / Boundary）：当前快照真相源；不代表真实媒体能力已实现或下一阶段已获实施授权。

## 当前目标与进度

- 长期目标：个人本地视频/音频情感化转写与人工审核工作台。
- 当前第一版：显式演示模式（Demo Mode）上传→应用内任务运行器（JobRunner）→假语音转文字（Fake STT）片段→人工修订/确认→Markdown/JSON 导出，数据持久化到本机。
- 用户 Mac mini 手动验收：修订文本与片段 `confirmed`（已确认）可见，已确认按钮禁用，任务显示「已导出 100%」；用户回复“可以了”。
- 状态修复：全部片段确认后任务进入已确认，导出后页面即时显示已导出；旧任务查询可修复历史不一致状态。后端 32 项、前端 11 项测试及构建通过。
- 本轮用户明确授权收尾时提交 mission 相关代码和文档；`.vscode/controlled-explorer.json` 等无关改动不纳入。

## 能力边界与后续

- 演示文本不代表媒体真实语音；播放器尚无真实媒体源，证据面板无真实情绪数据；导出文件保存在后端本机目录，浏览器暂无下载入口。
- 真实 STT（语音转文字）、真实媒体处理/回放、情绪证据与云端 LLM（大语言模型）调用是后续加深；待用户选择真实能力阶段并准备验收样本时重新对齐。TTS（文字转语音）与 LLM 自主选工具均未获实施批准，具体边界见 `deferred/2026-07-13-v1-adapter-vs-deferred.md`。

## 恢复与下一步

1. 先读 `checkpoints.md`，必要时读最新 `handoffs/2026-09-28-010-macmini-demo-accepted.md`；使用说明见仓库根目录 `README.md`。
2. 如用户要继续产品能力，先讨论真实 STT、媒体处理与片段播放的顺序、代表性样本和验收标准，再按 Align（对齐）→Plan（计划）→Spec/Tasks（规格/任务）→Apply（实施）推进。
3. 提交与工作区范围以 `git log -1`、`git status --short` 为准；本轮收尾不纳入无关 `.vscode/controlled-explorer.json`。
