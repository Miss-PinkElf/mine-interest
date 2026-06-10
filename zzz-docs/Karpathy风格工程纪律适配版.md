# Metadata（元数据）

- 创建时间（Created At）：2026-05-18 18:58:20 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：整理一份面向 agent-desktop-pet 项目的 Karpathy 风格工程纪律（Karpathy-Inspired Engineering Discipline）适配版，供用户审阅是否后续写入 `AGENTS.md`。
- 关联仓库或项目（Related Repository / Project）：agent-desktop-pet
- 关联 mission（Related Mission）：`.devflow/codex-goal-command-guide`
- 关联计划（Related Plan）：`.devflow/codex-goal-command-guide/plans/2026-05-18-karpathy-adapted-guide-root-doc-plan.md`
- 当前状态（Status）：候选项（Candidate）
- 文档边界（Scope / Boundary）：本文是候选说明文档，不是当前仓库强制规则；不会自动触发实现（Apply），也不替代 `AGENTS.md`、devflow、计划（Plan）或交接文档（Handoff）。

# Karpathy 风格工程纪律适配版（Karpathy-Inspired Engineering Discipline）

本文基于 `andrej-karpathy-skills` 中文版中的四个核心原则，并结合本仓库桌宠（desktop pet）、智能体（Agent）、上下文管理（context management）、工具（tool）、LLM（Large Language Model，大语言模型）和记忆系统（memory system）的特点，整理为候选协作规则。

本适配版的定位：

- 它是工程纪律，不替代 devflow。
- 它用于约束 Codex 在开发、调试、写文档和跨会话续接时的行为。
- 它可以与 `/goal` 命令配合使用，但 `/goal` 只是当前会话目标锚点（session-level objective anchor）。
- 长期任务真相源（source of truth）仍然应放在 `.devflow/<mission>/` 下。

## 1. 编码前思考（Think Before Coding）

1. 不要默认做错误假设；不确定时必须显式说明假设。
2. 需求存在多种解释时，先呈现取舍，不要默默选择一种直接实现。
3. 如果上下文、目标、边界或验收标准不清楚，应停止推进并澄清。
4. 在动手前先理解当前代码结构、已有约束和最近改动。
5. 如果存在更简单、更贴合当前架构的方案，需要主动提出。
6. 对复杂任务，应先把目标拆成可验证步骤，再进入实施（Apply）。
7. 对本项目而言，思考时必须默认考虑桌宠（desktop pet）、智能体（Agent）、上下文管理（context management）、工具（tool）和记忆系统（memory system）的关系。
8. 涉及 LLM（Large Language Model，大语言模型）能力时，应优先思考它在 Agent + 记忆系统中的职责边界，而不是只把它当普通文本生成器。
9. 如果需求影响主动行为、记忆写入、工具调用或用户打扰程度，应先明确风险边界，再进入实现。

## 2. 简洁优先（Simplicity First）

1. 使用能解决当前问题的最小实现，不新增需求外功能。
2. 不为一次性代码创建抽象，不为了“未来可能需要”增加配置或扩展点。
3. 不添加未要求的灵活性（flexibility）或可配置性（configurability）。
4. 不引入无必要的新依赖、新框架或新架构层。
5. 如果实现明显过度复杂，必须回退并简化。
6. 抽象只在能减少真实复杂度、降低重复或匹配既有模式时才引入。
7. 组件、服务、工具函数的拆分应服务于真实可读性、边界清晰和复用，不做形式化拆分。
8. 对本项目而言，桌宠能力应优先形成可运行的最小闭环（minimum viable loop），再逐步扩展感知、记忆、工具和主动行为。
9. LLM 相关能力应优先采用清晰的输入、输出、状态和验证口径，不把复杂度藏进提示词（prompt）里。

## 3. 精准修改（Surgical Changes）

1. 只修改当前任务必须修改的内容。
2. 每一行改动都应能追溯到当前用户请求或当前计划（Plan）。
3. 不顺手重构无关代码，不改无关格式，不删除自己没有充分理解的旧逻辑。
4. 匹配现有代码风格，即使存在个人更偏好的写法。
5. 如果发现无关死代码、坏味道、历史问题或 TypeScript 报错，只记录或提醒，除非用户明确要求处理。
6. 只清理本轮改动产生的无用导入、变量、函数或文件。
7. 如果工作区存在其他 mission 或用户改动，不得覆盖、回退或混入本轮改动。
8. 对本项目而言，一次 `/goal` 默认只处理一个 mission 的一个需求，不能跨 mission 混改。
9. 涉及记忆系统（memory system）、工具调用（tool calling）或 Agent 状态（Agent state）的改动时，应特别避免顺手改变跨模块契约。

## 4. 目标驱动执行（Goal-Driven Execution）

1. 将用户请求转化为可验证目标（verifiable goal），并写清成功标准。
2. 多步骤任务必须写明“步骤 + 验证方式”。
3. 修复 bug 时，优先定义可复现现象、问题原因、解决方案和验证方式。
4. 没有新的验证证据，不声明完成。
5. 如果验证失败，应根据失败原因回退到调试（Debugging）、计划（Plan）或方案（Proposal）阶段，而不是继续猜改。
6. 对长期任务，必须通过 devflow 维护真相源（source of truth），包括计划、决策日志、状态、检查点和必要的交接文档。
7. `/goal` 可用于记录当前会话目标，但不能替代 `.devflow/<mission>/` 下的计划（Plan）、决策日志（Decision Log）和交接文档（Handoff）。
8. 当上下文不足或需要跨会话继续时，应优先写清 handoff 和 NEXT-SESSION-PROMPT，而不是只依赖聊天记录。
9. 如果本轮只做第一版或最小闭环，延期项（Deferred Scope）必须写入当前 mission 真相源，并说明后续触发条件。

## 5. 与本项目 devflow 的关系

1. 本节是通用工程纪律，devflow 是长期任务主工作流。
2. 任何长期任务仍然必须遵守 Align / Mini Align、Plan、Apply、Verify、Close 门禁。
3. 进入实现前必须先完成计划（Plan），禁止跳过计划直接改代码。
4. 本轮不做但后续必须继续的延期项（Deferred Scope），必须写入当前 mission 的真相源（source of truth），不能只写在聊天里。
5. `/goal` 适合描述当前会话目标；devflow 负责长期记录、阶段推进和恢复。
6. 如果发现当前工作区已有其他 mission 的改动，应先提醒用户确认边界，避免一次目标跨多个 mission。

## 6. 推荐使用方式

### 6.1 开始任务时

推荐先把用户目标改写成可验证目标：

```text
/goal 完成 <当前 mission 的一个需求>：先 Align / Mini Align，再写 Plan，然后 Apply；不处理其他 mission；完成后更新 state 和 checkpoint
```

### 6.2 进入实现前

必须确认：

- 当前 mission 是否明确。
- 是否已有 Plan（计划）。
- 是否有 Light Tasks（轻量任务）或正式 tasks。
- 延期项是否写入了计划或决策日志。
- 工作区是否存在会影响本轮判断的其他改动。

### 6.3 收尾时

必须确认：

- 是否有新的验证证据。
- 是否更新了 `state.md`。
- 是否需要写 `checkpoints.md`。
- 是否需要 handoff 或 NEXT-SESSION-PROMPT。
- 是否需要询问用户是否提交代码。

## 7. 本轮不做 / 后续阶段（Deferred Scope）

本文只是候选适配版，当前不做以下事项：

- 不自动写入 `AGENTS.md`。
  - 原因：用户需要先审阅。
  - 后续触发条件：用户明确要求合并。
- 不替换 `AGENTS.md` 中已追加的四原则原文版。
  - 原因：原文版是上一轮明确要求保留的内容。
  - 后续触发条件：用户明确要求删除或替换。
- 不安装外部仓库的 skills、插件或 Cursor 规则。
  - 原因：本文只讨论规则文本，不引入外部执行机制。
  - 后续触发条件：用户明确要求安装或评估外部 skill。
