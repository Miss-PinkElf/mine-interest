---
name: openspec-explore
description: 在 devflow 内用于纯讨论、需求探索、方案比较或代码调查，但暂不开始实现时使用。
---

# OpenSpec Explore（内置版）

这是 `devflow` 生命周期中的纯探索分支。

它只负责回答一件事：

```text
当前是否仍处于 Explore 阶段，还是已经足够进入 Align。
```

不要让它承担 `superpowers-brainstorming` 的完整对齐职责，也不要让它偷跑到 Propose 或 Apply。

## 适用场景

- 用户想先讨论思路
- 需求仍然模糊
- 需要做方案比较、权衡分析或代码调查
- 当前还不应该开始实现
- 当前还没有形成已确认方向

## 工作姿态

- 只探索，不实现
- 可以自由读取代码和文档
- 提问要帮助暴露约束与边界
- 图表、表格能帮助理解时可以使用
- 可以把结论整理成后续可进入 Align 的摘要，但不要强推实现

## 生命周期职责

Explore 阶段只关心：

1. 现在还缺哪些关键信息
2. 是否需要继续探索
3. 是否已经足够退出 Explore，回到 `devflow` 主线进入 Align

Explore 阶段不负责：

- 拿用户最终确认
- 写正式 `plan`
- 写 `proposal/design/tasks`
- 开始实现

## 输出目标

探索结束时，最好留下以下之一：

- 更清晰的需求定义
- 方案比较及推荐
- 已识别的风险与未知项
- 是否进入 `Align` 的明确建议

## 退出条件

满足以下任一条件时，应退出 Explore：

- 已经形成候选方向，需要正式对齐
- 用户要求开始收敛方案
- 已经拿到足够信息，不继续探索也能进入 Align

退出 Explore 后，回到 `devflow` 主线，由外层决定是否进入 `Align`。

## 约束

- 本模式下不要写实现代码
- 如果讨论已经收敛到明确方向，回到 `devflow` 主线先进入 `Align`
- `Explore` 不能代替 `Align`、`Plan` 或 `Apply`
- 如果问题本质上是 bug 排查，转到 [../superpowers-systematic-debugging/SKILL.md](../superpowers-systematic-debugging/SKILL.md)
- 如果探索结论会影响后续行动，回到外层主 skill 更新 `state.md`、`decision-log.md` 或 `learnings.md`
