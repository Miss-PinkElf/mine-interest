# Resume Checklist

从 handoff 恢复时，按此清单核验，避免盲目续接。

## 恢复前核验

- [ ] 当前目录确实是目标项目
- [ ] 能确认当前 mission 是正确的
- [ ] 已读取 `state.md`
- [ ] 已读取最近一次 checkpoint
- [ ] 已查看 handoff 创建时间，知道上下文新旧程度
- [ ] 如存在 handoff，已完整读取 handoff 文档

## 上下文核验

- [ ] 已理解 handoff 中的关键背景
- [ ] 已检查 handoff 中的假设现在是否仍成立
- [ ] 已确认 blocker 是否仍然存在
- [ ] 已查看关键文件与产物

## 状态核验

- [ ] 已读取 `workflow.md`
- [ ] 已读取必要的 `spec/` artifact
- [ ] handoff 中提到的关键文件当前仍存在

## 开始恢复

- [ ] 从“立即下一步”第 1 条开始
- [ ] 如果 handoff 信息不足，先补探索再行动
- [ ] 如果 handoff 与当前事实冲突，先修正记录

## 红旗信号

遇到这些情况，应暂停并先核验：

1. handoff 提到的文件不存在
2. 当前代码状态与 handoff 描述明显不一致
3. 原先假设已经失效
4. blocker 已变化，但 handoff 没反映
5. 设计或架构已被别的改动改变
