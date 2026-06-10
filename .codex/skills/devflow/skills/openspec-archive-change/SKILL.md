---
name: openspec-archive-change
description: 在 devflow 内用于在审查与验证都通过后，归档或正式关闭当前 mission 下的一个已完成子变更。
---

# OpenSpec Archive（内置版）

只有在变更真正完成后，才关闭生命周期。

它只负责：

```text
确认当前 change 是否满足关闭条件，并执行归档或等价的关闭记录。
```

它不负责自行判断“验证是否成立”；验证质量结论应来自 `superpowers-verification-before-completion`。

## 前置条件

- `plan` 承诺的当前阶段内容已经兑现，或有明确弃置说明
- proposal 中承诺的内容已经实现
- tasks 已完成，或有明确处置结论
- 已有验证证据
- review 发现已解决或已明确接受

## 进入条件

只有在以下条件成立时才进入 Archive：

- Apply 已完成当前 change
- Review / Verify 已完成
- 当前问题已经从“继续实现”变成“是否允许关闭生命周期”

## 步骤

1. 确认当前归档的是哪个子变更
2. 重新检查 artifact 与任务完成状态
3. 判断是否需要把 delta spec 同步回主规格集合
4. 写一个收尾 `checkpoint`，说明：
   - 本轮完成内容
   - 证据
   - 未完成项与后续方向
5. 在当前较轻量的 mission 工作流中记录关闭状态，或执行项目所需的归档动作
6. 总结本次交付内容、通过的证据，以及同步了什么
7. 回到外层主 skill 更新状态、决策与经验记录

## 退出条件

只有在关闭状态已经写入、必要同步已经完成后，Archive 才算结束。

## 约束

- 不要从“看起来实现完了”直接归档
- 如果验证失败，回到 Apply
- 如果 review 反馈意味着设计或范围变化，回到 Propose
- 本阶段不负责补做实现
- 本阶段不负责替代 verification 或 review
