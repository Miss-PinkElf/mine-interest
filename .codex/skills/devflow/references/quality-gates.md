# 质量门禁

## 对齐门禁

- 没有完成 `Mission Init` 不进入 `Align`
- 重型路径必须完整 Align
- 轻量路径也必须至少做一次 Mini Align
- 不允许跳过对齐直接进入 Plan
- 不允许跳过对齐直接进入 Apply

## 初始化门禁

- 首次进入 mission 时必须完成 `Mission Init`
- `workflow.md`、`state.md`、`decision-log.md` 未建立前，不进入正式阶段流转
- 恢复旧 mission 时先校验并刷新最小骨架，不要盲目覆盖已有记录

## 计划门禁

- 重型路径必须有 `plan`
- 轻量路径也必须有最小 plan
- 没有 plan，不进入 `Propose`
- 没有 plan，不进入正式实施

## 实施门禁

- Apply 前必须具备任务定义
- 重型路径依赖 `spec/tasks.md`
- 轻量路径依赖轻量 `tasks`
- Apply 前应重新读取 `plan`
- 如果实施中暴露设计缺陷，停止并回退

## 调试门禁

- bug 必须先进 `superpowers-systematic-debugging`
- 根因未知时不允许猜改
- 连续 3 次修复失败后，必须质疑设计或方案

## 审查门禁

- 有意义的里程碑后要做 review
- review 不是只在最后做；任务阶段也可以做
- 若 review 涉及设计变化，回退到 Propose

## 验证门禁

- 完成前必须进入 `superpowers-verification-before-completion`
- 必须运行实际验证
- 必须用新鲜证据支撑完成结论

## Checkpoint 门禁

- 阶段切换时要决定是否写 `checkpoint`
- 重要里程碑、暂停前、当前轮次 Close 前必须写 `checkpoint`
- `checkpoints.md` 超过 3 条时，要把旧条目搬到 `checkpoints-archive.md`

## Resume 门禁

- Resume 时必须读取最近一次 `checkpoint`
- 最新 `handoff` 仅在存在时作为补充，不应替代 checkpoint
- 如果恢复记录与当前仓库事实冲突，以当前事实为准，再回写记录
