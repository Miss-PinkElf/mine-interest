# cc-qq `/new` 更名为 `/start` 以避免与 AstrBot 内置命令冲突（Align + Plan）

## Metadata（元数据）

- 创建时间（Created At）：2026-11-01 00:45:00 +08:00
- 更新时间（Updated At）：2026-11-01 00:45:00 +08:00
- 作者（Author）：Claude
- 目的（Purpose）：把 cc-qq 的 `/new` 改名为 `/start`，从命名层消除与 AstrBot 内置 `/new` 的冲突。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 当前状态（Status）：已批准、实施并发布 `0.3.2`（生产与测试安装目录已覆盖并重启）
- 文档边界（Scope / Boundary）：本文件是本次改名的 Align + Plan 真相源，含实施记录；发布动作需另行批准。

## 一、背景与根因

AstrBot 本体自带一个 `/new`（`builtin_stars/builtin_commands/main.py`），用于新建 AstrBot 自己的 LLM 对话，并标记为「共享群管理员（SHARED_GROUP_ADMIN）」。该命令的权限检查发生在 `waking_check` 阶段，先于所有插件 handler：

- 群聊中非 AstrBot 核心管理员发送 `/new` → 核心直接回复「权限不足」并 `stop_event()`；
- cc-qq 的 `/new` 根本不会执行；
- cc-qq 的 owner 配置（`owner_qq_id`）与 AstrBot 核心 `admins_id` 是两套独立体系，互不生效。

因此同名冲突无法在插件 handler 内部规避，直接改命令名是最干净的解决方式。

## 二、命名检查

- `/start` 未被当前 AstrBot 内置命令使用；
- 未被已安装插件（sourcehub、bilibili、group_chat_plus、proactive_chat、qq_group_daily_analysis）注册；
- 结论：可以安全占用 `/start`。

## 三、修改点清单

| 文件 | 位置 | 修改 |
| --- | --- | --- |
| `commands/registry.py` | `COMMANDS` | `Command("/new", ...)` → `Command("/start", "/start [初始消息]", "新建会话", ROLE_MEMBER)` |
| `commands/registry.py` | `ARGUMENT_AGENT_COMMANDS` | `frozenset({"/new", "/!"})` → `frozenset({"/start", "/!"})` |
| `service.py` | `_command()` | `if name == "/new":` → `if name == "/start":` |
| `constants.py` | `NO_ACTIVE_SESSION_REPLY` | 文案中的 `/new` → `/start` |
| `commands/session.py` | `info_text()` | 文案中的 `/new` → `/start` |
| `README.md` | 第 37、95、97 行 | 用户文档中的 `/new` → `/start` |
| `tests/test_execution_feedback.py` | 3 组用例 | `/new 初始消息`、`/new` → `/start` 对应形式 |
| `tests/test_commands.py` | 2 处权限断言 | `/new` → `/start` |

**行为变化**：`/start [初始消息]` 与旧 `/new [初始消息]` 完全等价；`/start` 无参数只新建会话不发回执，带参数会启动代理并发执行回执。`/help` 文本由 `COMMANDS` 自动生成，无需单独改。

## 四、明确不做的部分

- **不保留 `/new` 兼容别名（推荐）**：群里 `/new` 仍会先被 AstrBot 内置命令拦截，保留别名只会造成「私聊能用、群里不能用」的不一致；彻底改用 `/start` 更清晰。
- 不改 AstrBot 核心配置、不新增插件配置项。

> 改名后，若仍习惯性发送 `/new`：群聊中会继续看到 AstrBot 内置命令的「权限不足」提示；如不希望看到，可另行在 WebUI「指令管理」禁用内置 `/new`（属于独立配置动作，不在本计划内）。

## 五、验证方式

1. 全量单测：AstrBot Python 3.12.13 运行 `unittest discover`，预期 164/164 通过（改名前基线）。
2. 断言补充：
   - `parse_command("/start")` 被识别，`parse_command("/new")` 在插件层不再识别；
   - `will_run_agent("/start 初始消息")` 为真，`will_run_agent("/start")` 为假；
   - `help_text` 中出现 `/start`、不再出现 `/new`。
3. 静态检查：插件代码与 README 中不再残留命令形式的 `/new`。
4. 真机验证：需覆盖安装目录并重启后，群内 `@机器人 /start` 复测；本轮未获发布授权时不执行。

## 六、风险与回滚

- 风险：用户文档或肌肉记忆仍使用 `/new`；通过 README 与帮助文本更新缓解。
- 风险：其他插件或技能引用旧命令名；已全局检索，仅本插件代码与测试引用。
- 回滚：改动集中在命令名与文案，回退对应文件即可。

## 七、实施记录（Apply）

- 已完成：`registry.py`、`service.py`、`constants.py`、`commands/session.py`、`README.md`、`tests/test_execution_feedback.py`、`tests/test_commands.py` 全部改用 `/start`；新增一条断言「`parse_command("/new")` 不再识别、`/start` 出现在帮助文本中」。
- 静态检查：插件代码、测试与 README 中已无命令形式的 `/new`。
- 验证：AstrBot Python 3.12.13 全量单测 **165/165 通过**。
- 发布：版本升为 `0.3.2`，ZIP 已生成并覆盖生产/测试安装目录，两实例重启后均为「已加载 v0.3.2」。
- 待做：群内 `@机器人 /start` 真机复测。

## 八、后续待定

- 是否升版本并覆盖安装目录：待用户另行确认。
- 是否禁用 AstrBot 内置 `/new`：独立配置动作，待用户决定。
