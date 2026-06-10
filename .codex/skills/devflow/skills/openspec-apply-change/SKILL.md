---
name: openspec-apply-change
description: 在 devflow 内用于按当前 mission 的 tasks.md 实现已批准任务，并严格执行调试、审查与验证门禁。
---

# OpenSpec Apply（内置版）

根据 `tasks.md` 推进 Apply 生命周期。

它只负责：

```text
按任务推进实现、维护任务状态、在失败时暂停并回退到正确阶段。
```

它不负责自己发明调试方法论、验证哲学或代码审查标准；这些质量动作应委派给对应 `superpowers-*`。

## 输入

- 已批准的 `plan`
- 已批准的 `proposal.md`
- 已批准的 `design.md`
- 已批准的 `tasks.md`

## 进入条件

进入 Apply 前，应当已经满足：

- `plan` 已批准
- `proposal.md`、`design.md`、`tasks.md` 已存在
- 至少当前批次任务的含义清楚

## 步骤

1. 编码前重新读取：
   - `plan`
   - 当前 artifact
   - 最新 `state.md`
2. 选择执行模式：
   - 顺序模式：适合耦合任务
   - 并行模式：适合独立任务
   - 子代理模式：适合更大、更隔离的单元
3. 对每个任务：
   - 先标记为 `in_progress`
   - 只实现该任务范围
   - 按验收标准自检
   - 只有拿到证据后才标记完成
4. 如果出现失败，立即转到 [../superpowers-systematic-debugging/SKILL.md](../superpowers-systematic-debugging/SKILL.md)
5. 如果任务属于纯逻辑或纯变换单元，可选用 [../superpowers-test-driven-development/SKILL.md](../superpowers-test-driven-development/SKILL.md)
6. 如果任务之间明显独立，可考虑 [../superpowers-dispatching-parallel-agents/SKILL.md](../superpowers-dispatching-parallel-agents/SKILL.md)
7. 如果工作量大且适合隔离实现/审查循环，可考虑 [../superpowers-subagent-driven-development/SKILL.md](../superpowers-subagent-driven-development/SKILL.md)
8. 每完成一个有意义的里程碑，评估是否需要：
   - [../superpowers-requesting-code-review/SKILL.md](../superpowers-requesting-code-review/SKILL.md)
   - [../superpowers-verification-before-completion/SKILL.md](../superpowers-verification-before-completion/SKILL.md)
   - 写 `checkpoint`
9. 完成当前 Apply 阶段后，回到外层主 skill 更新 `state.md`、`decision-log.md`、`learnings.md`

## 生命周期输出

Apply 阶段的主要输出是：

- 已更新的任务状态
- 已实现的代码变更
- 必要时的回退决定
- 当前是否可进入 Review / Verify 的判断

## 停止条件

出现以下情况时，暂停 Apply 并回到 Propose：

- 暴露出设计缺陷
- 任务边界拆错
- 新用户约束使当前设计失效
- 发现 `plan` 本身不成立

出现以下情况时，暂停当前任务但不一定回退阶段：

- 当前任务意义不清，需要澄清
- 出现 bug 或失败，需要转 [../superpowers-systematic-debugging/SKILL.md](../superpowers-systematic-debugging/SKILL.md)
- 需要先完成 review / verify 才能决定是否继续

## 约束

- 不要在没有 `plan` 的情况下直接按 `tasks.md` 开工
- 不要凭记忆实现，要按 artifact 实现
- 不要把无关修复塞进同一个任务
- 多次失败后不要继续猜修
- 本阶段不负责自行定义“什么叫验证通过”，应交给 verification skill
- 本阶段不负责自行定义“review 是否通过”，应交给 review skills
