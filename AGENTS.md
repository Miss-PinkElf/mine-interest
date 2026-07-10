
# 协作约束

## 工具约束

## 1. 输出与语言

1. 必须始终使用简体中文。
2. 产出的文档默认使用简体中文，禁止默认输出英文。
3. 包括但不限于 spark-workflow、handoff、openspec、skills 相关文档，默认都使用简体中文。
4. 重要！！**涉及专业术语、模块名、规则名时，必须使用“中文 + 英文”双语表达；首次出现建议采用“中文（English）”格式，例如：关系记忆服务（RelationshipMemoryService）、任务聚焦日（task_focus_day）、习惯服务（HabitService）。**

## 2. 提交流程

1. 每次完成代码修改后，必须先询问我是否需要提交代码。
2. 没有我的明确允许，不能执行 commit。
3. 如果需要 commit，提交信息必须使用中文。

## 3. 工作流要求

1. 默认使用 `devflow` 进行长期开发、记录和推进。
2. 在走 `devflow` 流程时，需要先完成 Align / Mini Align，并进入其内置的 OpenSpec / Superpowers 子技能做需求对齐、方案收敛与实施门禁。
3. 在进入实现前，先进行一次头脑风暴，和我讨论方案，不要跳过讨论直接改代码。
4. 需要顺手判断：这次需求是否需要补充或更新相关文档。
5. **硬门禁（Hard Gate）**：必须先完成计划（Plan）再进入实施（Apply），禁止跳过计划直接改代码。
6. subagent 默认使用 gpt-5.6-terra high

## 4. 文档与计划落盘要求

1. plan 文件名必须与本次需求强相关，便于后续查找。
2. 如果当前任务走 `devflow`，plan 必须优先落到对应 mission 真相源下：
   - `.devflow/<mission>/plans/`
   - 不要默认写到 `zzz-doc/` 或 `docs/superpowers/plans/`
3. 更新问题清单时，必须写清楚：
   - 问题现象
   - 问题原因
   - 解决方案
4. 对于“本轮不做，但后续必须继续”的延期项（Deferred Scope），不能只写在聊天里，必须落盘到当前 mission 的真相源中：
   - Align（对齐）或 Plan（计划）文档的 `本轮不做 / 后续阶段` 小节。
   - `.devflow/<mission>/decision-log.md` 中的关键决策。
   - 阶段收尾时同步到 `.devflow/<mission>/state.md`、`checkpoints.md` 或 `NEXT-SESSION-PROMPT`。
5. 延期项（Deferred Scope）必须写清楚：
   - 暂不做的对象或能力。
   - 本轮暂不做的原因。
   - 后续进入的触发条件或推荐阶段。
   - 禁止把“暂不做”写成永久放弃。
6. 新增或重写说明类文档、候选方案文档、设计文档、交接文档时，必须在文档开头写清楚 `Metadata（元数据）`。
7. `Metadata（元数据）` 至少包含：
   - 创建时间（Created At）或更新时间（Updated At），需要写具体日期和时间。
   - 作者（Author）。
   - 目的（Purpose）。
   - 关联仓库或项目（Related Repository / Project）。
   - 关联 mission（Related Mission），如果没有明确 mission，需要写“无”或说明原因。
   - 当前状态（Status），例如：候选项（Candidate）、计划中（Planned）、实施中（In Progress）、已完成（Completed）、已废弃（Deprecated）。
   - 文档边界（Scope / Boundary），说明该文档是否是真相源（source of truth）、是否代表已批准方案、是否会触发实现。
8. 如果文档与原始需求、PRD（Product Requirements Document，产品需求文档）、OpenSpec（开放规格）或 devflow mission 有关，`Metadata（元数据）` 中必须写相对路径，便于后续追溯。
9.  候选方案文档必须明确标注“候选项（Candidate）”，禁止把未批准方向写成已批准计划（Plan）或已进入实施（Apply）的结论。

## 5. 路径与环境要求

1. 本仓库内涉及文件路径时，必须使用相对路径。
2. 后端 Python 环境使用 `backend/.venv`，不要使用全局 Python。

## 6. 校验与改动边界

1. 不需要做全局 ESLint 校验。
2. 不影响运行的 TypeScript 报错可以先不处理。
3. 如果要顺手修改 TypeScript 错误，必须先征求我的确认。

---

# 开发规范

## 1. 代码风格

1. 可读性优先。
2. 修改 React / TSX 代码时，优先参考现有代码风格保持一致。
3. 需要使用 `react-tsx-readability-guard` 提升 React / TSX 代码可读性。
4. 前端最好组件化，降低耦合，提高内聚，拆开，不要让一个tsx，或者ts文件，太大
4. 后端最好模块化，降低耦合，提高内聚，拆开，不要让一个py，别的文件，太大
5. 组件，现成的库，优先，不要自己造轮子

## 1.1 常量与提示词管理

1. 禁止新增魔法数字（magic number）和魔法字符串（magic string）；有业务含义、配置含义、展示含义或阈值含义的值，必须提取为具名常量。
2. 前端提示词（frontend prompt）、后端提示词（backend prompt）、Agent 目标（Agent goal）、工具列表（tool list）、默认文案（default copy）、状态 key（state key）和阈值（threshold）必须集中管理，不要散落在函数体或 JSX 中。
3. 常量命名必须表达业务语义，例如 `PROACTIVE_MEMORY_PREVIEW_GOAL`、`DEFAULT_AGENT_MAX_STEPS`、`MISSING_REQUIREMENT_COOLDOWN`，禁止使用 `TEMP_TEXT`、`VALUE_1` 这类弱命名。
4. 如果一组常量只服务于单个模块，可以放在该模块顶部；如果跨模块复用，应抽到专门的 constants / prompts 文件作为真相源（source of truth）。
5. 修改或新增提示词（prompt）时，优先保留中文 + 英文双语术语表达，并避免把提示词语义硬编码在多个位置。

## 1.2 注释与可读性

1. 代码以可读性优先；函数、方法、工厂函数和非直观业务规则必须添加简短注释或文档字符串，说明职责、输入输出约束或“为什么这样做”。
2. 配置（configuration）、环境变量（environment variable）、代理地址、跨域白名单和依赖源必须说明用途、作用范围与安全边界；不得把密钥、令牌或真实凭据写入注释。
3. 每一个有业务含义的常量都必须在其声明处添加简短注释，说明其服务的模块和状态/阈值语义；禁止仅用常量组注释代替逐常量说明。
4. 禁止逐行翻译式注释、重复命名信息或为显而易见的数据字段、枚举成员、测试断言和 CSS 规则堆叠注释；注释应帮助理解意图而非增加噪音。

## 2. 组件库

1. 默认使用 Ant Design（Antd）。

## 3. 样式规范

1. 默认不要使用行内样式。
2. 默认使用 CSS Module，推荐 `less` 或 `sass`。
3. 样式结构默认采用“外层包裹 + 内层 className”的写法。

### CSS Module 示例

```css
.wrapper {
  padding: 20px;
  background: #f5f5f5;

  :global {
    .user-info {
      .user-name {
      }
    }
  }
}
```

```tsx
<div className={styles.wrapper}>
  <div className="user-info">
    <span className="user-name">张三</span>
  </div>
</div>
```

### CSS-in-JS 示例

```tsx
export const DetailDiv = styled.div`
  .user-info {
    .user-name {
    }
  }
`

<DetailDiv>
  <div className="user-info">
    <div className="user-name" />
  </div>
</DetailDiv>
```

---

## 四个原则

### 1. 编码前思考

**不要假设。不要隐藏困惑。呈现权衡。**

LLM 经常默默选择一种解释然后执行。这个原则强制明确推理：

- **明确说明假设** — 如果不确定，询问而不是猜测
- **呈现多种解释** — 当存在歧义时，不要默默选择
- **适时提出异议** — 如果存在更简单的方法，说出来
- **困惑时停下来** — 指出不清楚的地方并要求澄清

### 2. 简洁优先

**用最少的代码解决问题。不要过度推测。**

对抗过度工程的倾向：

- 不要添加要求之外的功能
- 不要为一次性代码创建抽象
- 不要添加未要求的"灵活性"或"可配置性"
- 不要为不可能发生的场景做错误处理
- 如果 200 行代码可以写成 50 行，重写它

**检验标准：** 资深工程师会觉得这过于复杂吗？如果是，简化。

### 3. 精准修改

**只碰必须碰的。只清理自己造成的混乱。**

编辑现有代码时：

- 不要"改进"相邻的代码、注释或格式
- 不要重构没坏的东西
- 匹配现有风格，即使你更倾向于不同的写法
- 如果注意到无关的死代码，提一下 —— 不要删除它

当你的改动产生孤儿代码时：

- 删除因你的改动而变得无用的导入/变量/函数
- 不要删除预先存在的死代码，除非被要求

**检验标准：** 每一行修改都应该能直接追溯到用户的请求。

### 4. 目标驱动执行

**定义成功标准。循环验证直到达成。**

将指令式任务转化为可验证的目标：

| 不要这样做... | 转化为... |
|--------------|-----------------|
| "添加验证" | "为无效输入编写测试，然后让它们通过" |
| "修复 bug" | "编写重现 bug 的测试，然后让它通过" |
| "重构 X" | "确保重构前后测试都能通过" |

对于多步骤任务，说明一个简短的计划：

```
1. [步骤] → 验证: [检查]
2. [步骤] → 验证: [检查]
3. [步骤] → 验证: [检查]
```

强有力的成功标准让 LLM 能够独立循环执行。弱标准（"让它工作"）需要不断澄清。

-----
可以多考虑一下llm介入，或者辅助判断
不能使用硬编码，有些可以使用llm进行辅助判断，意图识别
让agent自己选择工具，把工具列表给agent，比如codex不就是把skillls的元数据给codex吗，让codex自己调用tool
