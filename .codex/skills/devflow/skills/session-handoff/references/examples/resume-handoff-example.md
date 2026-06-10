# 示例：从 handoff 恢复

## 场景

用户说：“继续上次那个 skill 改造任务。”

## 动作

1. 读取当前 mission 的 `state.md`
2. 读取最近一次 checkpoint
3. 找到对应 `.devflow/<mission>/handoffs/index.md`
4. 如果存在 handoff，读取最新 handoff
5. 参考 `resume-checklist.md` 核验当前状态
6. 必要时补读上一份 handoff 与 `spec/` artifact
7. 从 checkpoint 或 handoff 中的“立即下一步”继续

## 结果

AI 可以快速恢复到正确阶段，而不是重新猜测当前应该做什么。
