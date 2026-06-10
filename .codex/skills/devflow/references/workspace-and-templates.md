# 工作区与模板说明

## 工作区结构

```text
.devflow/<mission-slug>/
├── workflow.md
├── state.md
├── decision-log.md
├── plans/
├── spec/
├── bug-log.md
├── learnings.md
├── checkpoints.md
├── checkpoints-archive.md
├── development-overview.md
├── session-tasks.md
└── handoffs/
```

推荐命名：

- `plans/YYYY-MM-DD-<topic>-plan.md`
- `plans/YYYY-MM-DD-<topic>-light-tasks.md`
- `handoffs/YYYY-MM-DD-<seq>-<slug>.md`

## 默认创建与懒创建

### 默认创建

mission 初始化时立即创建：

- `workflow.md`
- `state.md`
- `decision-log.md`

初始化时建议立即填入：

- 当前目标
- 范围
- 成功标准
- 当前路径
- 当前阶段
- 下一步

### mission 已存在时的刷新规则

如果当前 mission 已存在，`Mission Init` 的职责是校验并刷新最小骨架，而不是重建工作区。

应遵循：

- 已有 `workflow.md`、`state.md`、`decision-log.md` 时，不重复覆盖历史内容
- 只补缺失项，不重建整个目录
- 刷新时优先保留最近一次真实推进记录
- 如果当前对话已明确激活某个 mission，后续相关小改动也继续沿用该 mission 的记录体系

### 按阶段懒创建

进入相应阶段时再创建：

- `plans/`
- `spec/`
- `bug-log.md`
- `learnings.md`
- `checkpoints.md`
- `checkpoints-archive.md`
- `session-tasks.md`
- `development-overview.md`
- `handoffs/`

这样既保留长期任务骨架，也避免小任务一开始铺满空文件。

## 模板使用时机

- `workflow-template.md`
  - mission 初始化；路径、阶段或里程碑变化时同步更新
- `state-template.md`
  - mission 初始化，后续持续更新
- `decision-log-template.md`
  - 出现关键取舍后
- `plan-template.md`
  - Align 完成后
- `light-tasks-template.md`
  - 轻量路径进入 Apply 前
- `bug-log-template.md`
  - bug 路径进入调试后
- `checkpoint-template.md`
  - 阶段切换、里程碑、暂停前、Close 前
- `handoff-template.md`
  - 暂停、跨对话、上下文过长、阶段性交接
- `development-overview-template.md`
  - 长期 mission、需求演进、阶段复盘、需要给人理解完整开发过程时

## 上下文预算与读取分层

默认恢复只读取恢复热路径（Resume Hot Path）：

1. `state.md`
2. `checkpoints.md`

按需再读取深度追溯路径（Deep Trace Path）：

- `workflow.md`
- `development-overview.md`
- `decision-log.md`
- `plans/`
- `spec/`
- `handoffs/`
- `checkpoints-archive.md`

判断标准：

- 需要恢复当前工作：读热路径
- 需要理解完整过程：读 `development-overview.md`
- 需要解释为什么这么做：读 `decision-log.md`
- 需要执行计划或核对规格：读 `plans/` 或 `spec/`
- 需要跨会话交接：读最新 handoff

## 文件预算建议

- `state.md`：建议 80-120 行内，写当前状态、风险、下一步、关键指针
- `workflow.md`：建议 60-100 行内，写当前目标、范围、阶段、里程碑
- `checkpoints.md`：只保留最近 3 条
- `development-overview.md`：允许长期增长，但不默认读取

如果 `state.md` 或 `workflow.md` 超过预算，优先把历史内容移动到：

- `development-overview.md`
- `decision-log.md`
- `checkpoints-archive.md`
- `handoffs/`

## Checkpoint 规则

`checkpoints.md` 只保留最近 3 条 checkpoint。

新 checkpoint 写入后，如果超过 3 条：

- 把较旧条目搬到 `checkpoints-archive.md`
- `checkpoints-archive.md` 不主动读取
- 只有追历史时才打开

建议流程：

1. 先把新 checkpoint 追加到 `checkpoints.md`
2. 如果条目数超过 3，搬走最旧条目
3. 在 `state.md` 中记录最新 checkpoint 的主题或时间

## Resume 读取建议

恢复当前 mission 时，建议按以下顺序读取：

1. `state.md`
2. `checkpoints.md`
3. `workflow.md`（仅在阶段或目标不清楚时）
4. 最新 `handoff`（仅在跨会话交接或 state/checkpoint 指向时）
5. `development-overview.md`（仅在需要理解完整开发过程时）
6. `spec/` 或 `plans/`（仅在准备实施或核对正式方案时）

## 轻量 Plan 最小模板

轻量路径或已激活 mission 下的相关小改动，至少应落一个最小 `plan`。推荐模板：

```markdown
# [任务名称]

- 改动文件：`path/a`、`path/b`
- 方案：一句话描述本轮怎么改
- 状态：待实施 / 已完成
```

重点：

- 模板要足够短，确保小改动也愿意先写计划
- 只要任务已纳入某个 mission，就不要因为“改动很小”而跳过这个最小模板

## 总记录最小模板

长期 mission 建议维护 `development-overview.md`。推荐模板：

```markdown
# [Mission 名称] 总记录（Development Overview）

## 定位

本文件用于理解完整开发过程，不是默认恢复热路径。

## 背景

为什么开启这个 mission。

## 已完成阶段

按阶段列出目标、输入、正式改动、验证证据。

## 关键决策

只列影响后续理解的决策，详细原因指向 `decision-log.md`。

## 当前开放问题

仍需观察、讨论或后续实施的事项。

## 推荐读取策略

说明日常恢复读什么，深度追溯读什么。
```

## 进入 Apply 的最小检查示例

在进入 `Apply` 前，可用以下最小检查确认当前记录是否足够：

```markdown
- [ ] 已明确当前 mission 与路径
- [ ] 已有对应 `plan`
- [ ] 重型路径已具备 `proposal.md`、`design.md`、`tasks.md`
- [ ] 轻量路径已具备最小 `tasks`
- [ ] 当前任务目标文件与完成标准清楚
```

## Spec 规则

重型路径固定使用：

- `proposal.md`
- `design.md`
- `tasks.md`

轻量路径不强制三件套，优先使用轻量 `plan + tasks`。
