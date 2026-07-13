# 视频情感化转写工作流 Origin

## Metadata（元数据）

- 创建时间（Created At）：2026-07-10 15:15:33 +08:00
- 更新时间（Updated At）：2026-07-13 15:05:44 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：维护当前 mission 的原始输入索引（Raw Input Source Index）和吸收状态。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 当前状态（Status）：持续维护（Active）
- 文档边界（Scope / Boundary）：本文件是原始需求与输入来源索引，不替代对齐、计划或 OpenSpec 真相源，不直接触发实施。

## 输入索引

| 时间 | 原始输入 | 用途 | 吸收状态 |
| --- | --- | --- | --- |
| 2026-06-10 | `zzz-prompt-debug/origin/设想/prompt.md` | 说明“带情感、表情、梗和语境解释”的视频/音频转写目标。 | 已吸收至 Align、Plan 与 OpenSpec。 |
| 2026-06-10 | `zzz-prompt-debug/origin/设想/STT-情感视频理解-可行性分析.md` | 提供候选模型、Agent / n8n 架构与路线调研。 | 已吸收为候选技术输入，具体模型须 benchmark 确认。 |
| 2026-06-10 | `zzz-prompt-debug/origin/设想/数据集处理.md` | 提供人声分离、去混响、谨慎降噪和切片经验。 | 已吸收为“按需预处理 + 双音轨保留”原则。 |
| 2026-07-10 | 本次对话中的用户确认 | 确认浏览器本地工作台、Windows + RTX 3080 / 20GB、云端 LLM、多模型证据融合、片段审核和延期边界。 | 已吸收至 `.devflow/video-emotion-transcript-workflow/spec/`。 |
| 2026-07-10 | 本次恢复会话中的用户约束 | 依赖安装默认使用清华镜像源（Tsinghua Mirror）；Python 使用清华 PyPI 镜像，npm 在首次安装前核验清华 npm 镜像的可用性。 | 已吸收至决策记录，待 Apply（实施）时执行。 |
| 2026-07-10 | 本次 Apply 会话中的用户授权 | 清华 npm 镜像不可用后，允许依赖安装改用默认源（default registry）；同时授权使用子代理（subagent）推进 Apply，不执行提交。 | 已吸收至决策记录与任务执行方式。 |

## 2026-07-13 14:28:23 +08:00 - 本会话用户原始指令索引

| 相对路径/来源 | 用途 | 吸收状态 |
| --- | --- | --- |
| 用户消息：恢复 `NEXT-SESSION-PROMPT-video-emotion-transcript-workflow.md` | 恢复 Apply 上下文 | 已吸收，从 Task 3 继续 |
| 用户消息：选 A 继续 Task 3 | 授权实现持久化 | 已完成并提交 |
| 用户消息：先提交再 Task 4；每 task 提交；做完全部 tasks | 授权批量 Apply + 自动 commit | 已完成 |
| 用户消息：上下文太长，新开对话；区分第一版与延期；读 `devflow-handoff.md` 收尾 | 会话收尾与交接 | 本 handoff 007 吸收中 |

## 2026-07-13 15:05:44 +08:00 - 会话后半段用户输入索引

| 来源 | 用途 | 吸收状态 |
| --- | --- | --- |
| 如何在 Mac 启动、能测什么 | 使用说明与能力边界 | 已吸收到 state/README/脚本 |
| 预处理/STT 原理与技术栈讲解 | 认知对齐 | 已对齐；无新 spec |
| 完成度与「task 是干啥的」 | 预期校准 | 已写入 learnings/decision |
| 下一步该做什么 | 优先 JobRunner | 已写入 state/backlog/handoff |
| 二次 devflow-handoff 收尾 + 提交 | 本 handoff 008 | 进行中 |

