# 下一会话提示：视频情感化转写工作流

## Metadata（元数据）

- 更新时间（Updated At）：2026-09-27 01:09:39 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：供新对话直接恢复本 mission，并从用户手动验收反馈继续。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-prompt-debug/origin/设想/prompt.md`
- 关联计划（Related Plan）：`.devflow/video-emotion-transcript-workflow/plans/2026-09-26-upload-auto-demo-transcript-plan.md`
- 当前状态（Status）：演示闭环第一版完成，本地验证通过；用户手动验收待进行。
- 文档边界（Scope / Boundary）：恢复提示，不是新需求的实施授权或最终产品验收结论。

请继续 mission：`video-emotion-transcript-workflow`。

## 默认先读

1. `.devflow/video-emotion-transcript-workflow/state.md`
2. `.devflow/video-emotion-transcript-workflow/checkpoints.md`
3. `.devflow/video-emotion-transcript-workflow/handoffs/2026-09-27-009-auto-demo-verified.md`

## 当前进度

- `spec/tasks.md` 中既有任务和本轮演示增量任务均已完成。
- 显式演示模式（Demo Mode）已打通上传→任务运行器（JobRunner）→假语音转文字（Fake STT）片段→人工修订/确认→Markdown/JSON 导出；来源标记跨重启保留，页面刷新能恢复任务。
- 后端 28 项测试、前端 8 项测试与构建通过；本地浏览器已冒烟，但用户表示稍后自行手动验证。
- 演示片段**不代表上传媒体的真实语音**。真实 STT、媒体预处理、音视频情绪证据及真实云端 LLM 调用仍待后续阶段对齐。
- 一键启动：`./scripts/start-local-dev.sh`；具体操作见 `README.md`。

## 未完成事项与未讨论议题

1. 用户手动验收尚未完成。优先收集其实际结果；若发现问题，按现象→原因→方案更新 `bug-log.md` 并修复。
2. 真实语音转文字（STT）、真实媒体处理及情绪证据的顺序与验收样本尚未对齐。演示模式完成不代表真实转写完成。
3. 大语言模型（LLM）辅助意图识别、基于工具元数据选择分析工具只是候选项（Candidate），未批准进入计划（Plan）或实施（Apply）。持久任务队列与自动重试也按需求触发再评估。
4. Electron、n8n、平台下载、训练等延期项见 `.devflow/video-emotion-transcript-workflow/deferred/`，均非永久放弃。

## 建议下次优先处理

先围绕用户的手动验收反馈推进。若验收通过，再对齐下一阶段真实 STT 与媒体处理范围，按 devflow 的 Align→Plan→Spec/Tasks→Apply 门禁推进；不要直接把候选想法当成已批准任务。

## 启动与恢复

```bash
./scripts/start-local-dev.sh
# 前端 http://127.0.0.1:5173
```

## 注意

- 后端使用 `backend/.venv`；仓库内使用相对路径；文档术语按中文+英文双语表达。
- 默认只读 `state.md` 与 `checkpoints.md`；需要完整过程时读 `development-overview.md`；需要追溯输入、旧状态与延期时读 `origin.md`、`state-history.md`、`backlog.md` 或 `deferred/`。
- 本地运行数据在 `backend/data/`，不得提交；本轮提交只包括 mission 相关文件。下一阶段提交仍需按用户当时授权判断。
