# Metadata（元数据）

- 创建时间（Created At）：2026-05-18 16:47:01 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：说明 Codex CLI `/goal` 命令的用途、启用方式、配置文件、常用命令、实验性边界，以及在本桌宠项目中的推荐使用方式。
- 关联仓库或项目（Related Repository / Project）：agent-desktop-pet
- 关联 mission（Related Mission）：`.devflow/codex-goal-command-guide`
- 关联计划（Related Plan）：`.devflow/codex-goal-command-guide/plans/2026-05-18-codex-goal-command-guide-plan.md`
- 当前状态（Status）：已完成（Completed）
- 文档边界（Scope / Boundary）：本文是项目内使用指南，不是 OpenAI 官方文档；官方行为以 OpenAI Codex 文档为准。本文不会自动触发任何实现（Apply）或配置修改。

# Codex CLI `/goal` 命令实验功能使用指南

## 1. 简短结论

`/goal` 是 Codex CLI 的目标命令（Goal Command），用于给当前 Codex 会话设置一个持续目标（persistent target）。它适合长期任务（long-running task）、复杂调试（debugging）和多轮开发（multi-turn development），帮助 Codex 在上下文变长、任务分支变多时仍然记住“本轮到底要完成什么”。

截至 2026-05-18，OpenAI 官方文档将目标功能（Goals）列为实验性功能（Experimental Feature）。这意味着它可能变化、调整或被移除，不建议把它作为唯一真相源（single source of truth）。

在本项目中，推荐定位是：

```text
/goal = 当前 Codex 会话的短期目标锚点（session-level objective anchor）
.devflow/<mission>/plans/ = 长期任务计划真相源（source of truth plan）
.devflow/<mission>/decision-log.md = 关键决策记录（decision log）
.devflow/<mission>/handoffs/ = 跨会话交接（handoff）
```

## 2. 官方来源

本文参考以下 OpenAI 官方文档：

- Codex CLI 斜杠命令（Slash Commands）：<https://developers.openai.com/codex/cli/slash-commands>
- Codex 配置（Configuration）：<https://developers.openai.com/codex/config-basic>
- Codex 功能成熟度（Feature Maturity）：<https://developers.openai.com/codex/feature-maturity>

## 3. `/goal` 有什么用

`/goal` 的核心价值是给当前会话提供一个明确、可持续引用的任务目标。

它适合这些场景：

- 长期开发：例如一个 mission 要跨多轮完成，容易被临时问题打断。
- 调试收口：例如“只修复当前崩溃，不顺手改无关 TypeScript 报错”。
- 防止跑偏：例如任务中途发现很多可优化点，但本轮只做最小闭环（minimum viable loop）。
- 上下文压缩前后保持方向：压缩上下文（context compaction）后，目标仍能帮助 Codex 维持任务边界。

它不适合替代这些东西：

- 计划（Plan）
- OpenSpec（开放规格）
- devflow mission
- 决策日志（Decision Log）
- 交接文档（Handoff）
- 测试与验证记录（verification evidence）

原因很简单：`/goal` 是会话级提醒，而不是项目级真相源。

## 4. 启用条件

`/goal` 不是默认稳定功能，需要启用目标功能（Goals）。

### 方式一：使用 `/experimental`

在 Codex CLI 中输入：

```text
/experimental
```

然后在实验功能（experimental features）里打开 Goals。如果 Codex 提示需要重启，就重启当前 Codex 会话。

### 方式二：修改配置文件

在 Codex 配置文件（configuration file）中启用：

```toml
[features]
goals = true
```

常见配置文件位置：

```text
~/.codex/config.toml
```

如果只想让本仓库启用，可以使用项目配置（project config）：

```text
.codex/config.toml
```

注意：项目配置需要 Codex 信任当前项目后才会加载。Codex 配置优先级通常是命令行参数（CLI flags）高于配置档案（profile），再高于项目配置，最后是用户配置（user config）。

## 5. 当前仓库环境观察

本次检查到当前 Codex CLI 版本：

```text
codex-cli 0.130.0
```

当前仓库已有：

```text
.codex/AGENTS.md
```

当前仓库没有项目级 Codex 配置：

```text
.codex/config.toml
```

本机用户级配置中已有 `[features]` 表，但未看到 `goals = true`。因此，按当前观察，`/goal` 大概率尚未启用。

本文只记录使用指南，没有实际修改 `~/.codex/config.toml`，也没有新增 `.codex/config.toml`。

## 6. 常用命令

设置目标：

```text
/goal 完成桌宠记忆系统阶段一，并保持现有验证通过
```

查看当前目标：

```text
/goal
```

暂停目标：

```text
/goal pause
```

恢复目标：

```text
/goal resume
```

清除目标：

```text
/goal clear
```

## 7. 推荐写法

好的目标应该包含四类信息：

- 目标对象：这轮要完成哪个模块、能力或问题。
- 完成边界：做到哪里算完成。
- 约束条件：哪些事情本轮不要做。
- 验证口径：如何证明完成。

推荐示例：

```text
/goal 完成桌宠记忆质量验证的最小闭环：只改后端日志与验证脚本，不碰前端 UI；完成后跑 backend/.venv 下的相关测试，并更新当前 mission 的计划与问题记录
```

```text
/goal 收口电脑控制 Agent 候选层协议第一版：补齐后端事件结构、前端展示入口和最小验证；延期浏览器自动操作能力，并写入 decision-log
```

```text
/goal 修复当前回归问题：只处理启动失败根因，不顺手修复无关 TypeScript 报错；验证 npm run dev 能启动到预期端口
```

不推荐写法：

```text
/goal 优化项目
```

```text
/goal 修所有问题
```

这些目标太泛，会让 Codex 难以判断优先级和边界。

## 8. 与 devflow 的关系

本项目默认使用 devflow 管理长期开发。`/goal` 和 devflow 的职责不同。

| 对象 | 定位 | 适合内容 | 是否是真相源（source of truth） |
| --- | --- | --- | --- |
| `/goal` | 会话级目标锚点（session-level objective anchor） | 当前这一轮 Codex 工作的目标和边界 | 否 |
| `plans/` | 计划（Plan） | 做什么、顺序怎么排、本轮不做什么 | 是 |
| `decision-log.md` | 决策日志（Decision Log） | 关键取舍、延期项、为什么这么做 | 是 |
| `handoffs/` | 交接文档（Handoff） | 跨会话恢复、上下文压缩后的续接信息 | 是 |
| `state.md` | 当前状态快照（current snapshot） | 当前阶段、下一步、验证状态 | 是 |

推荐流程：

```text
1. 用 devflow 完成 Align / Mini Align（对齐）
2. 写入 Plan（计划）
3. 用 /goal 设置当前会话目标
4. 进入 Apply（实施）
5. 验证后更新 state / checkpoint / decision-log
```

这样做的好处是：`/goal` 负责让当前会话不跑偏，devflow 负责长期可恢复。

## 9. 本项目推荐模板

### 轻量文档任务

```text
/goal 完成 <主题> 的项目内说明文档：只新增文档和必要 devflow 记录，不修改业务代码；文档必须包含 Metadata，并引用官方来源
```

### Bug 修复任务

```text
/goal 修复 <问题现象>：先定位根因，再做最小改动；不处理无关报错；完成后记录问题现象、问题原因、解决方案和验证结果
```

### 前端任务

```text
/goal 完成 <前端能力> 的最小可用版本：遵守 React / TSX 可读性守卫（react-tsx-readability-guard），默认使用 Ant Design（Antd）和 CSS Module，不引入行内样式
```

### 后端任务

```text
/goal 完成 <后端能力> 的最小闭环：使用 backend/.venv 环境验证，保持模块化边界，不引入散落的魔法字符串或魔法数字
```

### 长期 mission 续接

```text
/goal 续接 <mission 名称>：先读取 state.md 和 checkpoints.md，再按当前 Plan 推进；延期项必须写回 decision-log，不只留在聊天里
```

## 10. 风险与注意事项

1. 实验性风险：目标功能（Goals）属于实验性功能（Experimental Feature），后续命令、配置键或行为可能变化。
2. 不要替代文档：重要决策必须写入 devflow 真相源，不要只写进 `/goal`。
3. 不要写太大：`/goal` 应该描述当前会话目标，不要塞完整 PRD（Product Requirements Document，产品需求文档）。
4. 不要写太虚：避免“优化项目”“完善体验”这类没有完成边界的目标。
5. 配置要谨慎：如果启用项目级 `.codex/config.toml`，需要确认不会影响其他协作者的默认行为。

## 11. 快速上手建议

第一次使用可以这样做：

```text
/experimental
```

打开 Goals 后，给当前任务设置一个短目标：

```text
/goal 完成当前文档任务：新增指南文档，不修改配置，不提交 commit；完成后询问是否需要提交代码
```

然后正常继续开发或写文档。任务完成后，如果不再需要目标，可以清除：

```text
/goal clear
```

## 12. 本轮不做 / 后续阶段（Deferred Scope）

本轮暂不做以下事项：

- 不启用 `features.goals`。
  - 原因：当前需求是写指南，不是修改 Codex 配置。
  - 后续触发条件：明确要求“帮我启用 `/goal`”。
- 不把 `/goal` 写入 `.codex/AGENTS.md` 的强制规范。
  - 原因：功能仍是实验性功能（Experimental Feature），需要先观察稳定性。
  - 后续触发条件：确认 `/goal` 在本项目多轮任务中稳定有用。
- 不建立 `/goal` 模板库。
  - 原因：当前文档已经给出基础模板，独立模板库需要更多实践样本。
  - 后续触发条件：多个 devflow mission 开始固定使用 Goals。
