---
description: 对话收尾：回顾工作、更新 devflow 文档、生成下次对话提示词
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Skill
---

你是 devflow 交接助手。用户即将结束当前对话，请执行以下收尾流程。

本提示词保持单一交接流程，不拆分多种模式；但必须遵循当前 `devflow` 技能（DevFlow skill）的上下文预算（Context Budget）规则：

- `state.md` 与 `workflow.md` 使用滚动摘要（Rolling Summary），只保留当前快照，不追加完整聊天历史。
- `checkpoints.md` 只保留最近 3 条 checkpoint，旧内容归档到 `checkpoints-archive.md`。
- `development-overview.md` 是总记录（Overall Record），用于理解完整开发过程；只有本次对话改变长期目标、阶段脉络或关键背景时才更新。
- 下一次对话默认恢复热路径（Resume Hot Path）是 `state.md` + `checkpoints.md`；需要理解完整过程时再读 `development-overview.md`。

## 第一步：回顾本次对话

1. 梳理本次对话中完成的工作、做出的决定、遇到的问题。
2. 检查是否有未完成的任务或未讨论完的议题。

## 第二步：更新 devflow 文档

使用 `devflow` skill 的 handoff 子流程，对以下文档**逐项判断是否需要更新**，不需要的跳过，不要默认全部补充：

1. **状态（state.md）**：更新当前进度、阶段、下一步（几乎每次都需要）；保持短当前态，不写成长历史
2. **工作流（workflow.md）**：本次对话是否有路径变化、阶段切换、里程碑变化？如有则更新；保持当前流程视图，不保留过时阶段
3. **问题清单（bug-log）**：本次对话中是否发现了 bug？如有则写入，需包含：问题现象、原因、解决方案（或待解决标记）
4. **计划（plans）**：是否有新增或更新的 plan？已有 plan 是否与本次决定冲突？如有则修正
5. **经验（learnings）**：本次是否有值得沉淀的踩坑记录或技术决策？
6. **决策文档（decision-log）**：本次是否做了关键取舍（选方案、变路径、变方向）？
7. **检查点（checkpoint）**：本次是否完成了阶段、修复了重要 bug、或准备暂停？
8. **检查点（checkpoint-archive）**：本次是否完成了checkpoint的归档，只保留最新的三条
9. **总记录（development-overview.md）**：本次是否改变了完整开发过程的理解？如有则更新；否则不要为了收尾而改
10. **spec**：本次是否涉及 proposal/design/tasks 内容的变更？
11. **交接文档（handoff）**：生成本次对话的 handoff 交接记录

## 第三步：生成下一次对话的提示词

在写到 `.devflow/<mission>/` 对应目录下创建或更新 `NEXT-SESSION-PROMPT-{mission名称}.md`，内容包括但不限于：

- 当前进度概述
- 未完成的任务清单
- 未讨论完的议题
- 需要注意的上下文信息
- 建议下次对话优先处理的事项
- 恢复读取建议：默认先读 `state.md` 与 `checkpoints.md`；需要理解完整开发过程时再读 `development-overview.md`

> mission 名称从当前 devflow 的 mission 目录名中获取。文件直接写好内容，用户可以直接复制使用。

## 注意事项

- 所有文档使用简体中文。
- devflow 相关文档写到 `.devflow/<mission>/` 对应目录下。
- 不需要用户额外确认，直接执行以上流程并汇报结果。
