# 视频情感化转写工作流 Workflow

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-07-13 14:28:23 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录当前 mission 的流程阶段视图（当前快照）。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-prompt-debug/origin/设想/prompt.md`
- 当前状态（Status）：MVP 代码任务完成，准备真实模型加深（Code Complete / Next Real Models）
- 文档边界（Scope / Boundary）：当前流程视图，不保存完整聊天历史。

## 路径

- 类型：重型路径（Heavy Path）
- 生命周期：Align → Plan → Spec/Tasks → Apply → Verify → Close（代码任务）
- 当前：`spec/tasks.md` 全部勾选；**代码 Apply 收口**；下一阶段是「真实模型/样本加深」，可新开 mission 或在本 mission 继续加深任务。

## 阶段视图

| 阶段 | 状态 |
| --- | --- |
| Align / Plan / Spec | 已完成 |
| Apply Task 1-5 + 阶段2-5 | 已完成并提交 |
| 真实模型加深 / CUDA 实测 | 未开始（明确为后续，非 tasks 漏做） |
| 延期能力（Electron/n8n/…） | 延期中 |

## 本会话里程碑

1. 恢复 context，从 Task 3 红灯实现到全 tasks 完成。
2. 用户授权：每完成 task 自动 commit。
3. 会话收尾：区分第一版适配层 vs 明确延期，生成新会话提示。
