---
name: devflow
description: |
  长期开发任务主入口。只要任务会分阶段推进、预计跨多轮继续、需要先讨论再写 plan、需要记录决策/bug/checkpoint/handoff，或用户说“先梳理”“先讨论”“先写 plan”“保存进度”“继续上次”，都应优先使用它。
  额外触发条件：当工作区内已存在 `.devflow/<mission>/` 且当前对话已读取该 mission 的 `state.md`、`checkpoints.md`、`handoff`、`NEXT-SESSION-PROMPT` 或其他工作区文件时，后续与该 mission 相关的改动默认继续纳入 devflow，而不是按普通即时任务处理；当当前请求明显属于某个活跃 mission 的续作、小改动、恢复或收口时，即使用户没有显式提到 `devflow`，也应继续使用它。
  不要把 devflow 当成收尾记录器；它必须在第一次真正推进前介入，并强制执行 Align -> Plan -> Spec/Tasks -> Apply -> Verify/Close。
author: Codex
version: 0.2.0
date: 2026-04-15
---

# DevFlow

## 核心定位

`devflow` 是长期开发任务与中大型开发任务的主入口。

它负责：

1. 判断当前任务应该走哪条路径
2. 把记录系统建立为主线，而不是收尾附属品
3. 把阶段推进委托给 OpenSpec 子技能
4. 把质量门禁委托给 Superpowers 子技能
5. 在暂停、续接、上下文压缩时协调 handoff
6. 控制恢复时的上下文预算（Context Budget），避免长期 mission 越做越难恢复

一句话：

**OpenSpec 管阶段推进，Superpowers 管思考质量，DevFlow 管主线记录、路径调度与恢复。**

## 不可跳过的铁律

以下规则是 `devflow` 的硬门禁，不是建议：

1. `Align` 先于一切实现路径
   - 用户说“直接做”“先写 plan”“先出 tasks”都不构成跳过对齐的许可
   - 轻量任务也至少做 `Mini Align`
2. `Plan` 先于 `Propose` 与 `Apply`
   - `plan != spec`
   - `plan` 回答“做什么、顺序怎么排”
   - `spec` 回答“为什么这样做、怎么实现、任务如何追踪”
   - 没有落盘的 `plan`，不得进入正式 spec，也不得开始实现
3. 没有任务定义，不进入 `Apply`
   - 重型路径依赖 `spec/tasks.md`
   - 轻量路径依赖轻量 `tasks`
   - 进入 `Apply` 前必须重新检查当前路径所需 artifact 是否齐备；缺失则回退补齐
4. 重要阶段切换、里程碑、暂停与收尾都要写 `checkpoint`
   - 至少包括：阶段切换、重要里程碑、影响后续方向的关键决策、暂停前或 Close 前
   - `checkpoints.md` 只保留最近 3 条
   - 更旧内容搬到 `checkpoints-archive.md`
5. 恢复热路径（Resume Hot Path）必须保持短
   - 默认只读 `state.md` 与 `checkpoints.md`
   - 只有 `state.md`、`checkpoint` 或用户请求明确指向时，才继续读取 `workflow.md`、最新 `handoff`、`development-overview.md`、`plans/` 或 `spec/`
   - 不得因为“可能有用”而默认全量读取整个 mission 工作区
6. 没有新鲜验证证据，不得宣称完成
7. 首次进入 mission 时，必须先完成 `Mission Init`
   - 至少创建并初始化 `workflow.md`、`state.md`、`decision-log.md`
   - 没有初始化工作区，不进入 `Align`

如果当前工作违反了这些规则，优先回退阶段，而不是继续往前冲。

## 适用场景

优先用于以下场景：

- 中大型功能开发
- 预计跨多轮推进的长任务
- 需要边讨论边记录过程和决策的任务
- 需要先 plan 再 spec 再实施的任务
- 需要保留 bug 调试过程的任务
- 暂停后下次继续、或跨对话续接的任务

如果只是一次性小修且不需要留下过程记录，可以不触发本 skill。

## 工作区与真相源

工作区固定为：

```text
.devflow/<mission-slug>/
```

进入 mission 后，以工作区内文件为真相源，聊天记录只用于辅助理解。

优先信任：

- `state.md`
- `checkpoints.md`
- `workflow.md`
- `decision-log.md`
- `development-overview.md`
- `plans/`
- `spec/`
- `bug-log.md`
- 最新 `handoff`

恢复时的默认读取顺序不同于“可信度列表”：

```text
state.md -> checkpoints.md -> 按指针读取 workflow / handoff / development-overview / plans / spec
```

`state.md` 与 `workflow.md` 应是当前快照（Current Snapshot），不要承担完整历史；完整脉络写入 `development-overview.md`、`decision-log.md`、`checkpoints-archive.md` 或 handoff。

默认创建：

- `workflow.md`
- `state.md`
- `decision-log.md`

按阶段懒创建：

- `plans/`
- `spec/`
- `bug-log.md`
- `learnings.md`
- `checkpoints.md`
- `checkpoints-archive.md`
- `session-tasks.md`
- `development-overview.md`
- `handoffs/`

只要 `devflow` 已经介入，**工作区文件比对话更可信**。  
如果对话与工作区记录冲突，以当前仓库事实为准，再把差异回写记录。

## 活跃 Mission 自动关联

当以下任一信号出现时，默认认为对应 mission 已被激活：

- 当前对话已读取 `.devflow/<mission>/` 下的 `state.md`、`workflow.md`、`checkpoints.md`、`handoff`
- 当前对话已读取与该 mission 明确相关的 `NEXT-SESSION-PROMPT`
- 用户当前请求明显属于该 mission 的续作、小改动、恢复或收口

一旦 mission 已激活，后续相关请求默认继续纳入该 mission，而不是重新按“普通即时任务”处理。只有在以下情况才中断自动关联：

- 用户明确切换到另一个 mission
- 用户明确说明当前请求与已激活 mission 无关
- 仓库事实表明当前请求属于完全独立的新任务

## 职责边界

`devflow` 负责：

- 判断路径与阶段
- 建立并维护 mission 工作区
- 规定记录、checkpoint、handoff、resume 的主线规则
- 决定何时进入哪个子 skill

`devflow` 不负责：

- 重新定义 `openspec-*` 的生命周期内部规则
- 重新定义 `superpowers-*` 的思考与质量方法论
- 在外层重复书写子 skill 已经负责的细节

## 路径分类规则

采用：**系统先判断 + 用户可覆盖**

规则如下：

1. 用户显式指定轻量、重型、bug 或 resume 路径时，优先按用户指定执行
2. 用户未指定时，先判断路径，再用一两句话说明判断理由
3. 如果当前对话已激活某个 mission，则后续相关请求默认继续纳入该 mission
4. 在进入 `Plan` 或 `Apply` 前，允许用户切换路径
5. 实施中发现复杂度判断错误时，可以升级或降级路径，但必须回写记录

### 轻量路径

适用于：

- 目标足够明确
- 改动影响面有限
- 不需要完整 proposal/design/tasks 三件套

流程：

```text
Mini Align -> Light Plan -> Light Tasks -> Apply -> Verify -> Close
```

### 重型路径

适用于：

- 需求存在歧义
- 影响多个模块、页面或阶段
- 需要正式 spec 管理与阶段回退

流程：

```text
Align -> Plan -> proposal/design/tasks -> Apply -> Review -> Verify -> Close
```

### bug 路径

适用于：

- 测试失败
- 异常行为
- 根因未知
- 修复尝试已开始失控

流程：

```text
Classify -> Debugging -> bug-log -> Verify -> Close
```

### resume 路径

适用于：

- 跨对话续接
- 暂停后恢复
- 上下文恢复

流程：

```text
Read state -> Read latest checkpoint -> Read latest handoff(if any) -> Reconfirm route -> Align/Plan/Apply
```

### 纯探索分支

当任务仍处于“先聊清楚，不承诺方向，不开始实现”的状态时：

```text
Classify -> Explore -> Align
```

`Explore` 不是偷跑实现的通道，只是把纯讨论和正式对齐区分开。

## 主线流程

DevFlow 主线为：

```text
Classify -> Mission Init -> Align -> Plan -> Propose/Tasks -> Apply -> Review/Verify -> Close
```

关键约束：

- `Align` 不能跳过，轻量任务也至少要做 Mini Align
- `Plan` 不能静默省略
- `plan != spec`
- 阶段切换前应执行显式检查，而不是只看原则声明
- 没有任务定义不进入 `Apply`
- 每轮推进后至少更新 `state.md`
- 每次重要阶段切换都应决定是否写 `checkpoint`
- `Close` 不等于 mission 结束，它只表示当前轮次收束

重型路径固定三件套：

- 当前 mission 的 `spec/proposal.md`
- 当前 mission 的 `spec/design.md`
- 当前 mission 的 `spec/tasks.md`

轻量路径至少要求：

- 轻量 `plan`
- 轻量 `tasks`

## 阶段执行顺序

| 阶段 | 外层职责 | 进入的子 skill |
| --- | --- | --- |
| `Classify` | 判断当前请求属于哪条路径与哪类阶段 | 无 |
| `Mission Init` | 建立或校验最小工作区骨架 | 无 |
| `Align` | 把任务送入正式对齐 | `superpowers-brainstorming` |
| `Plan` | 把方向落成 plan | `superpowers-writing-plans` |
| `Propose / Tasks` | 产出或更新 lifecycle artifacts | `openspec-propose` |
| `Apply` | 按任务推进生命周期 | `openspec-apply-change` |
| `Review / Verify` | 调用质量门禁子 skill 完成审查与验证 | `superpowers-requesting-code-review` / `superpowers-receiving-code-review` / `superpowers-verification-before-completion` |
| `Close` | 更新状态，写 checkpoint，并决定是否 handoff | 无 |

阶段内部细节由对应子 skill 负责；`devflow` 外层只负责调度、记录和恢复。

## 阶段门禁

### 对齐门禁

- 没有完成 `Mission Init` 不进入 `Align`
- 不允许跳过 Align 直接进入 Apply
- 用户要求“先写 plan”时，也必须先做 Align
- 对齐结束后必须把结论转入 `Plan`

### 计划门禁

- 重型路径必须写入 `plans/`
- 轻量路径也必须有最小 plan 记录
- `plan` 负责说明做什么与实施顺序，不替代正式 spec
- plan 写完前，不得创建正式 artifact
- 在 `devflow` 内，重型路径 artifact 默认落到当前 mission 的 `spec/`
- 重型路径只有 `plan` 没有 `proposal/design/tasks` 时，不得进入 `Apply`
- 没有 plan，不进入正式实施

### 实施门禁

- 没有任务定义不进入 `Apply`
- 重型路径进入 `Apply` 前必须确认 `proposal.md`、`design.md`、`tasks.md` 已存在且与 `plan` 一致
- 轻量路径进入 `Apply` 前必须至少具备最小 `plan` 与最小 `tasks`
- 如果前置条件缺失，先回退补齐，再继续实施
- 如果暴露设计缺陷，停止实施并回退

### 调试门禁

- bug 必须先进 `superpowers-systematic-debugging`
- 不允许直接猜改
- 修复过程必须回写 `bug-log.md`

### 完成门禁

- 宣称完成前必须进入 `superpowers-verification-before-completion`
- 没有新鲜证据，不允许宣称完成
- 阶段收尾前必须决定是否写 `checkpoint`
- 暂停、上下文压缩、跨会话续接时才强制写 `handoff`

## 回退规则

| 当前阶段 | 触发情况 | 回退到 |
| --- | --- | --- |
| Align | 用户补充大量新约束 | 继续 Align |
| Plan | 理解目标有偏差 | Align |
| Propose | 用户推翻方案 | Align |
| Apply | 暴露设计缺陷 | Propose |
| Apply | 连续 3 次修复失败 | 先 Debugging，必要时 Propose |
| Review | 审查反馈涉及设计变更 | Propose |
| Verify | 验证失败但设计仍成立 | Apply |
| Verify | 验证失败且暴露设计问题 | Propose |
| Close | 当前阶段结束但 mission 未结束 | 保留工作区并写 checkpoint 或 handoff |

## 记录规则

始终遵循：

- mission 建立或恢复后，先校验 `workflow.md`、`state.md`、`decision-log.md`
- 每轮推进后至少更新 `state.md`
- 路径变化、阶段变化、里程碑调整后更新 `workflow.md`
- 重要历史脉络、阶段总览、需求演进写入 `development-overview.md`，不要塞进 `state.md`
- 做出关键选择后更新 `decision-log.md`
- 对齐确认后必须写 `plan`
- 遇到 bug 时写 `bug-log.md`
- 阶段切换、重要里程碑、暂停前、正式完成当前轮次时写 `checkpoint`
- `checkpoints.md` 只保留最近 3 条，超出内容搬入 `checkpoints-archive.md`
- `checkpoint` 回答“做到哪了”，`handoff` 回答“下次怎么接”
- `development-overview.md` 回答“为什么这样演进、整体做过什么”，只在人类理解完整过程或深度恢复时读取
- `state.md` 与 `workflow.md` 采用滚动摘要（Rolling Summary），更新时优先改写当前状态，不追加长历史
- 正常阶段收束优先写 `checkpoint`；只有跨会话、跨 agent、上下文过长时才强制写 `handoff`
- 暂停、跨对话、上下文过长、阶段性交接时才生成 `handoff`

不要把 `spec` 当成过程记录，不要把 `handoff` 当成 `state.md` 的替代品，也不要把“聊天里说过”当成已经落盘。

## 上下文预算

长期 mission 的记录要分成两类：

- 恢复热路径（Resume Hot Path）：`state.md`、`checkpoints.md`
- 深度追溯路径（Deep Trace Path）：`development-overview.md`、`decision-log.md`、`checkpoints-archive.md`、`plans/`、`spec/`、`handoffs/`

默认恢复只读取热路径。只有以下情况才进入深度追溯路径：

- 用户要求理解完整开发过程
- 当前状态或 checkpoint 明确指向某个 plan、spec、handoff 或总记录
- 出现冲突，需要追溯历史决策
- 准备做跨 agent 交接或归档

建议保持：

- `state.md`：短当前态，避免超过约 120 行
- `workflow.md`：短流程视图，避免超过约 100 行
- `checkpoints.md`：最近 3 条
- `development-overview.md`：可增长，但不默认读取

## 读取地图

- 路径判断与阶段说明：`references/routing-and-stages.md`
- brainstorm 与 plan 的关系：`references/brainstorming-guide.md`
- 工作区结构与模板：`references/workspace-and-templates.md`
- 记录规则：`references/recording-rules.md`
- 质量门禁：`references/quality-gates.md`
- 示例：`references/examples/`

进入具体动作时，按需读取：

- 探索：`skills/openspec-explore/SKILL.md`
- 计划：`skills/superpowers-writing-plans/SKILL.md`
- 提案：`skills/openspec-propose/SKILL.md`
- 实施：`skills/openspec-apply-change/SKILL.md`
- 归档：`skills/openspec-archive-change/SKILL.md`
- 对齐：`skills/superpowers-brainstorming/SKILL.md`
- 调试：`skills/superpowers-systematic-debugging/SKILL.md`
- 审查：`skills/superpowers-requesting-code-review/SKILL.md`
- 接收审查：`skills/superpowers-receiving-code-review/SKILL.md`
- 验证：`skills/superpowers-verification-before-completion/SKILL.md`
- 交接：`skills/session-handoff/SKILL.md`
