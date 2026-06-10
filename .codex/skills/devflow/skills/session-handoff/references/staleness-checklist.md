# Staleness Checklist

用于判断某份 handoff 是否已经陈旧。

## 检查项

- [ ] handoff 创建后，仓库是否已有明显新变更
- [ ] handoff 中引用的关键文件是否仍存在
- [ ] handoff 中的“下一步”是否还合理
- [ ] handoff 中的 blocker / 风险是否已变化
- [ ] handoff 中的方案是否已被新决策替代

## 判定建议

### FRESH

满足：

- 关键文件仍存在
- 当前状态与 handoff 基本一致
- 下一步仍然可直接执行

### SLIGHTLY STALE

满足：

- 有一些变化，但不影响主要方向
- 需要补读 `state.md` 与最近记录后继续

### STALE

满足：

- 关键前提已变
- handoff 中多项内容需要重新验证
- 不适合直接照着“下一步”执行

### VERY STALE

满足：

- handoff 已不足以支持安全恢复
- 应先重新探索，再创建新的 handoff
