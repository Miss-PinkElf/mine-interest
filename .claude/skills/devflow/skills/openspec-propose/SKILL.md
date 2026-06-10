---
name: openspec-propose
description: 在 devflow 内用于将已确认且已写成 plan 的方向，正式落成当前 mission 的 proposal.md、design.md 和 tasks.md。没有 plan 时不要直接用它。
---

# OpenSpec Propose（内置版）

把已确认且已计划过的方向转成生命周期 artifact。

在 `devflow` 内，本阶段的默认 artifact 位置不是全局 `openspec/changes/`，而是**当前 mission 工作区下的 `spec/`**：

```text
.devflow/<mission-slug>/spec/
```

除非用户明确要求使用其他位置，否则：

- `proposal.md` 写到 `.devflow/<mission-slug>/spec/proposal.md`
- `design.md` 写到 `.devflow/<mission-slug>/spec/design.md`
- `tasks.md` 写到 `.devflow/<mission-slug>/spec/tasks.md`

它只负责：

```text
将已批准的方向转成 proposal.md / design.md / tasks.md，并判断是否具备进入 Apply 的条件。
```

不要让它重新承担 Align，也不要让它越过 artifact 直接推进实现。

## 输入

- 已确认的 `Align` / `Mini Align` 结论
- 已写好的 `plan`
- 相关代码上下文
- 用户提供的 PRD、设计说明、系统分析或截图说明
- 当前 mission 工作区与 `spec/` 目录位置

## 进入条件

进入本阶段前，应当已经满足：

- 方向已在 Align 中获得确认
- `plan` 已落盘
- 当前任务确实需要正式 artifact，而不是继续探索或继续计划

## 步骤

1. 如果当前没有已落盘 `plan`，先回到 [../superpowers-writing-plans/SKILL.md](../superpowers-writing-plans/SKILL.md)
2. 确认当前子任务名称与产物位置
3. 确认当前 mission 的 `spec/` 目录已存在
   - 在 `devflow` 内，默认是 `.devflow/<mission-slug>/spec/`
   - 不要默认写到全局 `openspec/changes/`
4. 重新读取 `plan`，确认：
   - 目标
   - 范围
   - 风险
   - 下一阶段入口条件
5. 读取模板：
   - [../../assets/templates/proposal-template.md](../../assets/templates/proposal-template.md)
   - [../../assets/templates/design-template.md](../../assets/templates/design-template.md)
   - [../../assets/templates/tasks-template.md](../../assets/templates/tasks-template.md)
6. 如果存在外部规格说明，使用 [../../references/spec-to-artifact-mapping.md](../../references/spec-to-artifact-mapping.md) 做映射
7. 写出：
   - `proposal.md`：做什么、为什么做、范围、非目标、边界场景、开放问题
   - `design.md`：结构、接口、数据流、复用点、风险
   - `tasks.md`：小而可验证的任务与验收点
8. 除非用户已明确授权直接实现，否则请求用户确认 artifact
9. 完成后回到外层主 skill，同步：
   - `state.md`
   - 必要时 `decision-log.md`
   - 一个说明“spec 已就绪”的 `checkpoint`

## 退出条件

只有在以下条件成立时，才算 Propose 完成：

- artifact 已写出
- artifact 与 `plan` 一致
- 用户已批准 artifact，或已明确授权直接进入 Apply

如果这些条件不成立，就仍停留在 Propose。

## 质量标准

- artifact 必须与 `plan` 一致，而不是跳过 `plan` 自行改方向
- artifact 路径必须与当前 mission 一致，不能脱离 `.devflow/<mission>/spec/` 另写一套全局产物
- proposal 覆盖所有重要变更点和异常路径
- design 能解释关键技术路径，而不是空泛描述
- tasks 足够原子、有顺序且可独立验证
- 仍有不确定项时，要显式写出来

## 回退与委派

- 如果实际上尚未达成一致，应返回 `Align`
- 如果 `plan` 暴露为不充分，应返回 `Plan`
- 如果只是在 artifact 质量上拿不准，不要自己发明对齐流程；应回到外层并由相应 `superpowers-*` 负责质量判断

## 约束

- 不要因为任务感觉简单就跳过 `plan` 或 artifact
- 一旦 artifact 已存在，不要继续把聊天历史当最终真相源
- 本阶段不负责重新做 brainstorming
- 本阶段不负责实现代码
