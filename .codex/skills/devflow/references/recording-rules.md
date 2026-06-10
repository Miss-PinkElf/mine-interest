# 记录规则

记录不是收尾动作，而是主流程的一部分。

## 每轮推进后的最小要求

每轮推进结束后，至少更新：

- `state.md`

如果本轮做了关键取舍，还应更新：

- `decision-log.md`

以下情况还应同步更新：

- `workflow.md`
  - 当前路径变化
  - 当前阶段变化
  - 里程碑或阶段出口条件变化
- `development-overview.md`
  - 当前轮改变了长期目标、阶段划分、关键背景或需求演进理解
  - 用户需要一个“总的记录”来理解项目或需求的完整开发过程

`state.md` 与 `workflow.md` 采用滚动摘要（Rolling Summary）：更新当前事实，删减过时细节，不把每次对话完整追加进去。

## 何时写 `plan`

以下情况写 `plan`：

- Align 完成，准备进入正式提案
- 需要比较方案并保留取舍过程
- 用户要求“先写 plan”
- 轻量路径也需要最小 plan 记录

注意：

- “用户要求先写 plan” 不等于可以跳过 Align
- 先对齐，后写 plan

## 何时写 `decision-log.md`

以下情况写入决策：

- 明确选择方案 A 而放弃方案 B
- 路径从轻量切重型，或从重型降轻量
- 实施中发现需要变更原方向

## 何时更新 `workflow.md`

以下情况必须更新：

- mission 初始化完成
- 路径判断变化
- 阶段切换
- 主要里程碑变化
- 当前阶段出口条件变化

`workflow.md` 记录的是当前 mission 主线，不应该长期停留在过时阶段。

## 何时更新 `development-overview.md`

`development-overview.md` 是总记录（Overall Record），用于帮助人理解完整开发过程。

以下情况更新：

- mission 从单次需求变成长期主题
- 新增或结束一个重要阶段
- 用户确认了影响后续理解的长期目标、范围或边界
- 某次踩坑会改变后续工作方式
- 恢复热路径文件需要瘦身，但历史脉络仍值得保留

注意：

- 它不是默认恢复文件
- 不替代 `state.md`、`workflow.md`、`decision-log.md` 或 checkpoint
- 可以比 `state.md` 更长，但应按阶段整理，不要粘贴原始聊天记录

## 何时写 `bug-log.md`

以下情况必须写：

- 进入 bug 路径
- 触发 `superpowers-systematic-debugging`
- 有根因分析与修复动作需要留档

## 何时写 `checkpoint`

以下情况必须写（触发矩阵）：

- 阶段切换
- 完成重要里程碑
- 做出影响后续实施方向的关键决策
- 准备暂停
- 上下文变重，需要压缩
- 当前轮次准备 Close

每条 checkpoint 至少写清：

- 当前路径与阶段
- 本轮完成内容
- 关键决策
- 风险与阻塞
- 立即下一步
- 相关文件与证据

## 何时写 `handoff`

以下情况写 `handoff`：

- 暂停，准备下次继续
- 跨对话续接
- 上下文过长
- 需要把当前阶段交给下一个 agent

正常完成一个任务时，不强制 handoff；更新 `state.md`、必要时写 `checkpoint` 即可。不要用 handoff 替代日常阶段记录。

## `plan != spec`

始终记住：

- `plan` 记录过程
- `spec` 记录正式结论

不要把 spec 当成过程记录的替代品。

## `checkpoint` 与 `handoff` 的关系

- `checkpoint` 用于阶段内沉淀与近期恢复，回答“做到哪了”
- `handoff` 用于跨会话或跨 agent 交接，回答“下次怎么接”
- 正常阶段收束优先写 `checkpoint`
- 一次暂停通常先写 `checkpoint`，再决定是否需要 `handoff`

## 恢复时的读取顺序

正常恢复当前 mission 时，优先顺序应为：

1. `state.md`
2. `checkpoints.md`
3. 按 `state.md` 或 checkpoint 指针读取 `workflow.md`
4. 按指针读取最新 `handoff`、`development-overview.md`、`plans/` 或 `spec/`

这条路径是恢复热路径（Resume Hot Path），目标是用最少上下文恢复当前工作。

以下情况才读取深度追溯路径（Deep Trace Path）：

- 用户要求理解完整开发过程
- 当前状态与 checkpoint 冲突，需要追溯决策
- 准备跨 agent 交接、归档或复盘
- `state.md` 或 checkpoint 明确要求读取某个 plan、spec、handoff 或 `development-overview.md`

不要在缺少 checkpoint 的情况下只读 handoff；很多正常收尾只会写 checkpoint，不会写 handoff。恢复时如果这些文件已经明确指向某个活跃 mission，后续相关工作默认继续纳入该 mission。

## 文件预算建议

为了避免长期 mission 越做越难恢复，建议控制：

- `state.md`：约 80-120 行，保留当前快照、风险、下一步和关键指针
- `workflow.md`：约 60-100 行，保留当前目标、范围、阶段和里程碑
- `checkpoints.md`：最近 3 条
- `development-overview.md`：可持续增长，但不进入默认恢复热路径

当 `state.md` 或 `workflow.md` 变长时：

- 将历史脉络移入 `development-overview.md`
- 将事件细节移入 `checkpoints.md` 或 `checkpoints-archive.md`
- 将取舍原因移入 `decision-log.md`
- 将跨会话交接细节移入 handoff
