# 覆盖分析（Coverage Analysis）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-30 14:45:00 CST。
- 更新时间（Updated At）：2026-10-30 14:45:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：说明功能清单的输入、输出字段、风险分级与不可测项标记方式。
- 关联仓库或项目（Related Repository / Project）：`person-config` 与本仓库 `tools/astrbot_e2e/`。
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：实施中（In Progress）。
- 文档边界（Scope / Boundary）：参考说明，非真相源；不触发实现。

## 输入

`scripts/discover_plugin.py --plugin-dir <plugin_dir>` 读取：

| 来源 | 提取内容 |
| --- | --- |
| `metadata.yaml` | 插件名、作者、版本等元数据 |
| `_conf_schema.json` | 配置项（每个键生成一条 `kind=config`） |
| `*.py` | `@filter.command`、`@filter.command_group`、`register_command`、`@filter.event_message_type`、LLM 与消息钩子 |
| `README.md` | 反引号包裹的 `/命令` 文本 |

## 输出 `features.json`

| 字段 | 说明 |
| --- | --- |
| `plugin` | 插件名（优先取 `metadata.yaml` 的 `name`） |
| `plugin_dir` | 插件源码绝对路径 |
| `metadata` | `metadata.yaml` 解析结果 |
| `features[].id` | 稳定标识，如 `command-help`、`event-ALL`、`config-timeout` |
| `features[].title` | 中文标题 |
| `features[].kind` | `command` / `event` / `hook` / `config` |
| `features[].trigger` | 触发文本、事件名或配置键 |
| `features[].expected` | 期望结果（默认空，待人工补充） |
| `features[].testability` | `text` / `manual` / `config` / `rich_media` |
| `features[].risk` | `high` / `medium` / `low` |
| `features[].notes` | 来源文件或 README 行 |
| `summary.total/commands/events/hooks/config/manual` | 汇总计数 |

## 风险分级

- `risk=high`：会启动代理、改变会话状态或执行外部动作的命令。当前集合：
  `/cc`、`/goon`、`/!`、`/new`、`/resume`、`/end`、`/cd`、`/initbase`、`/approve`、`/deny`。
- `risk=medium`：普通文本命令、事件与钩子。
- `risk=low`：配置项。
- 高风险的判定来源是源码装饰器与 README 中的命令；README 中出现的路径（如 `/tmp`）会被过滤，不计入命令。

## 用例生成规则

`scripts/gen_cases.py` 只自动生成满足以下条件的命令：

1. `kind=command`。
2. 有 `trigger`。
3. `testability=text`（`manual`、`config`、`rich_media` 一律跳过）。
4. 基础命令不在高风险集合中。
5. 命令文本不含参数占位（如 `<dir>`、`[x]`、`{y}`）。

其余项写入 `cases/SKIPPED.md`，逐条给出原因；不得静默丢弃。

已知例子：cc-qq 的 `/help` 返回图片帮助卡片，属于 `rich_media`，必须人工标记并跳过文本用例。

## 不可测项标记

- 生成阶段：写入 `SKIPPED.md`（功能、原因）。
- 执行阶段：无法执行的断言（例如未配置 LLM 判定）标记为 `SKIPPED`，并在报告中写明原因。
- 富媒体：返回图片、文件、语音或引用卡片的命令标记 `testability=rich_media`，首版不自动生成文本用例。
- 人工确认：`risk=high` 与 `testability=manual/config/rich_media` 的功能必须由用户确认后再设计用例。
- 多轮功能（如 `/new` → `/cc` → `/end`）由 AI 手写用例，放入独立目录并单独执行。

## 注意

- 静态扫描可能遗漏动态注册的命令；以运行时 `/help` 输出为准做人工补充。
- README 中的命令可能包含示例参数，自动生成会跳过带参数的项。
- `features.json` 是中间产物，不提交到仓库。
