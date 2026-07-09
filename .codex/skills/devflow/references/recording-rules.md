# 记录规则

记录不是收尾动作，而是主流程的一部分。

## 分阶段记录策略

记录时机跟随阶段变化，不把所有文档更新都塞进每一次工具调用后。

### Align / Plan

对齐（Align）与计划（Plan）阶段的文档就是阶段交付物，应正常产出：

- `plans/`
- 必要的 `decision-log.md`
- 必要的 `development-overview.md`

### Apply

实施阶段（Apply）默认专注写代码或修改目标文件，不主动更新过程文档，避免实现节奏被打断。

以下情况例外，必须写最小记录：

- Apply 中发生阶段回退
- 出现阻塞或根因不明问题
- 用户暂停或上下文即将压缩
- 当前轮准备进入 Verify / Close

最小记录通常只包括：

- `state.md`
- 必要时写 `checkpoint`

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

## `state.md` 与 `state-history.md`

`state.md` 是当前状态快照（Current State Snapshot），目标是让恢复热路径短而准。

建议保持：

- 30 行内
- 只写当前阶段、当前结论、风险/阻塞、下一步、关键指针
- 不写完整历史，不粘贴长对话

更新 `state.md` 前，如果旧内容仍有追溯价值，先追加到 `state-history.md`，并加上时间戳分隔。

恢复当前工作时默认只读 `state.md`。只有需要追溯状态变化、解释历史判断或处理冲突时，才读取 `state-history.md`。

## 何时写 `origin.md`

`origin.md` 是原始输入索引（Raw Input Source Index），不是一次性冻结文件。

以下情况应追加：

- Mission Init 时记录最早的用户需求来源
- 用户后续追加新的原始提示词、需求草稿或参考文件
- 某个需求来源已经写在 `zzz-prompt-debug/.../prompt-1.md`、`prompt-2.md` 这类文件中，需要建立索引

每条来源至少写清：

- 相对路径
- 时间或序号
- 用途或背景
- 是否已吸收进 `plan`、`spec` 或 `tasks`

不要强制复制全文；如果原始 prompt 已在仓库文件中，优先引用相对路径。

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

## 何时写 `backlog.md` 与 `deferred/`

延期项分两层，避免把所有“以后可能做”混在一起。

| 类型 | 粒度 | 适合内容 | 恢复时机 |
| --- | --- | --- | --- |
| `backlog.md` | 一句话 | 碎片灵感、可做可不做、尚未展开的想法 | handoff 或计划下一轮时扫一眼 |
| `deferred/` | 一个文件一个延期项 | 已讨论过、有一定方案、明确不是本轮做的功能或逻辑 | resume 时按触发条件检查 |

`deferred/` 下的每个文件应写清：

- 暂不做的对象
- 本轮不做的原因
- 当前已有思路
- 后续触发条件
- 推荐进入阶段

禁止把“暂不做”写成永久放弃；如果确定废弃，应写入 `decision-log.md`。

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
- 需要查看原始需求来源时读取 `origin.md`
- 需要追溯旧状态时读取 `state-history.md`
- 需要规划后续延期项时读取 `backlog.md` 或 `deferred/`

不要在缺少 checkpoint 的情况下只读 handoff；很多正常收尾只会写 checkpoint，不会写 handoff。恢复时如果这些文件已经明确指向某个活跃 mission，后续相关工作默认继续纳入该 mission。

## 文件预算建议

为了避免长期 mission 越做越难恢复，建议控制：

- `state.md`：建议 30 行内，保留当前快照、风险、下一步和关键指针
- `workflow.md`：约 60-100 行，保留当前目标、范围、阶段和里程碑
- `checkpoints.md`：最近 3 条
- `development-overview.md`：可持续增长，但不进入默认恢复热路径
- `state-history.md`：可追加旧快照，但不进入默认恢复热路径

当 `state.md` 或 `workflow.md` 变长时：

- 将历史脉络移入 `development-overview.md`
- 将旧状态快照移入 `state-history.md`
- 将事件细节移入 `checkpoints.md` 或 `checkpoints-archive.md`
- 将取舍原因移入 `decision-log.md`
- 将跨会话交接细节移入 handoff
