# 示例：创建 handoff

## 场景

当前 mission 已完成需求梳理与 proposal，准备暂停，后续在新对话中继续实施。

## 动作

1. 读取当前 `state.md`、`workflow.md`、`spec/proposal.md`
2. 用模板创建新 handoff
3. 在 `handoffs/index.md` 中登记为最新 handoff
4. 在 `state.md` 中写入最新 handoff 与下一步

## 结果

下次恢复时，不必重新翻整个聊天记录，只需读取 mission 记录与最新 handoff。
