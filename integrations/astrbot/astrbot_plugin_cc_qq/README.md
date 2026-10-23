# cc-qq：AstrBot 原生 QQ 代理插件

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:40:00 +08:00
- 更新时间（Updated At）：2026-10-23 00:00:00 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：说明 cc-qq 插件的当前能力、权限模型、配置方式与后续迁移范围。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：实施中（In Progress）
- 文档边界（Scope / Boundary）：插件安装和使用说明；第一阶段代码仍需真实 QQ 与双 CLI 验收，完整迁移以当前 mission 的计划和开放规格（OpenSpec）为准。

## 当前状态

当前版本 `0.2.0` 已接通 QQ 文本准入、按角色的代理权限分级、危险操作审批、工作目录切换、基础模板、Claude Code／Codex 异步进程、SQLite 会话和基础命令。群聊只处理白名单内群号中明确 @ 当前机器人的消息；自然语言和命令均须 @，未 @ 时插件静默。私聊无需 @。不在 `private_user_ids` 且不是 owner／管理员的私聊不回复。同一私聊会话、同一发送者、同一正文在 10 秒内重复出现时只处理一次。`0.2.0` 起，群内非白名单成员不再被拒绝，而是以只读档参与对话；白名单成员为工作目录读写；owner／管理员为完全权限。权限主链路仍需真实 QQ 与双 CLI 验收。

## 配置准备

在 AstrBot 中启用插件，并填写 `qq_platform_id`、`enabled_group_ids`、`owner_qq_id` 和各群工作目录。`group_rules_json` 使用 QQ 群号作为键，例如：

```json
{
  "123456789": {
    "work_dir": "/path/to/project",
    "agent": "claude",
    "allowed_user_ids": ["10001"]
  }
}
```

群号白名单使用 `enabled_group_ids`；`group_rules_json.allowed_user_ids` 是该群成员白名单，全局成员名单使用 `global_allowed_user_ids`。owner 和管理员也必须处于已启用的群内。群聊 @ 目标由 AstrBot 消息中的机器人 QQ ID 与 `At.qq` 精确比对；身份缺失或 @ 他人时静默。

私聊需要启用 `private_enabled` 并填写 `private_work_dir`；普通私聊用户另填 `private_user_ids`。不在名单中的私聊与关闭私聊一样静默，不回复未授权提示。插件为每位私聊用户建立独立子目录。空配置默认不处理任何 QQ 群或私聊。群聊 @ 后不在白名单时不再拒绝，而是进入 `readonly` 只读档。

Claude Code 和 Codex 分别使用 `default_claude_model`、`default_codex_model`。群规则中的 `model` 非空时优先；对应默认模型留空时，插件不传 `--model`，由该代理 CLI 自行选择默认模型。旧共享字段 `default_model` 已停用，升级后需将原值手动填入适用代理的新字段。已有会话继续使用其原代理；若群规则改用另一代理，旧会话仍取原代理的独立默认模型，新代理需用 `/new` 开始新会话。

使用代理功能需要在 AstrBot 进程的命令搜索路径（PATH）中安装并可调用 `claude` 或 `codex`；桌面进程找不到命令时，在插件配置页填写 `claude_command` 或 `codex_command` 的可执行文件绝对路径。

## 权限分级（Permission Profiles）

| 角色 | 默认档位 | Claude Code | Codex |
| --- | --- | --- | --- |
| 群内非白名单（guest） | `readonly` | `dontAsk` + `Read/Grep/Glob/TodoWrite` + 只读 hook 限制工作目录 | 权限档案 `ccqq-readonly`：工作区只读，其余拒绝 |
| 白名单成员（member） | `workspace` | `acceptEdits` + OS 沙箱 + 审批 hook | 权限档案 `ccqq-workspace`：工作区读写，关闭网络并排除 `/tmp` |
| owner／管理员 | `full` | `dontAsk` + 全量守护 hook（默认放行，拦关键路径） | `danger-full-access` |

- 权限按**每轮发言者**计算；同一个群会话里，成员和访客不会互相继承权限。
- 档位可用 `guest_permission_profile`、`member_permission_profile`、`owner_permission_profile` 修改；群规则也可覆盖 guest／member 档位。
- 只读档只限制代理工具面与工作目录，不等于“整个宿主机只读”；代理仍可能通过它被允许的只读工具读取工作目录内文件。
- 工作区档下，工作目录内编辑自动放行；工作目录外写入、Bash 命令引用工作目录外路径、危险命令和申请脱离沙箱的操作会触发审批。审批卡片发到来源会话，owner／管理员回复 `/approve <审批号>` 或 `/deny <审批号>`，默认 300 秒后自动拒绝。
- `sudo`、关机、格式化、磁盘工具、`rm -rf /`、凭据目录和系统目录属于硬拒绝，不会进入审批；管理员批准也不会执行。
- 审批服务只监听 `127.0.0.1`，使用随机 token；插件重载会丢失待审批请求并按拒绝处理。
- 审批卡片发到来源会话，并尽量发到 owner／管理员最近一次与机器人交互的会话；管理员需在本次插件加载后至少发言过一次，否则只在来源会话可见。群聊中其他成员也能看到命令摘要，不要把密钥写进命令。
- 完全权限档不启用文件沙箱，改用 `dontAsk + 守护 hook`：默认放行所有工具，但 `~/.ssh`、`~/.aws`、`~/.gnupg`、`/etc`、`/usr`、`/System`、`/Library` 以及 `sudo`、关机、磁盘格式化、`rm -rf /` 等仍会被拒绝。Claude Code 2.1.202 实测 `bypassPermissions` 不执行 deny 规则，因此没有继续使用它。
- 完全权限档的守护 hook 是应用层规则，无法拦截 `python -c` 等间接写入关键路径；需要强隔离时，请把 owner 档改为 `workspace`，或把 AstrBot 放进容器。
- Claude Code 默认使用 `--setting-sources ""`，屏蔽用户和仓库的 settings，只加载插件注入的策略；如果现网 Claude 依赖 settings 中的 `apiKeyHelper`，把 `claude_setting_sources` 设为 `user`。
- Codex `exec` 当前没有稳定的非交互审批通道，因此 Codex 只依赖 OS 沙箱硬边界：工作目录外读写直接失败，不会弹出 QQ 审批。逐次审批目前只对 Claude Code 生效。
- Codex 的传统 `read-only` 只限制写入、不限制读取范围；插件改用 Codex 权限档案（Permission Profiles，Beta）收紧读取：`ccqq-readonly` 只读工作区，`ccqq-workspace` 只写工作区，二者都排除 `/tmp`。`/etc`、`/usr` 等运行工具所需的最小路径仍由 Codex 的 `:minimal` 放行。该配置在本机 `codex-cli 0.162.1` 验证；更旧版本不支持权限档案时需升级。
- 沙箱技术栈：Claude Code 在 macOS 使用 Seatbelt，在 Linux／WSL2 使用 bubblewrap，网络经本机代理白名单；Codex 在 macOS 使用 Seatbelt，在 Linux 使用 Landlock + seccomp。沙箱覆盖 shell 及其子进程；内置 `Read/Edit/Write` 由权限规则约束。

## 工作目录与基础模板

- `/pwd` 查看当前工作目录、角色和权限档。
- `/cd <目录>` 仅 owner／管理员可用；目标必须位于 `allowed_work_dirs` 内，按 realpath 防符号链接逃逸。切换会结束当前会话，下一条消息在新目录开始。
- `/initbase` 仅 owner／管理员可用；把插件自带的 `CLAUDE.md`、`AGENTS.md`、`.claude/settings.json`、`.claude/skills/...`、`.codex/config.toml`、`.codex/skills/...` 补到当前工作目录。只补缺失文件，不覆盖已有内容。
- 模板里的 `.claude/settings.json` 供用户手动运行 Claude 时参考；插件会话默认 `--setting-sources ""`，不会加载工作区自带的 settings，实际策略以插件注入文件为准。

私聊没有正文时插件不回复。同一私聊在 10 秒内出现相同正文（含空白）时只处理一次，相同回复也不会连发。群聊 @ 机器人但没有文字时，仍提示在 @ 后输入文本或命令。`stale_message_max_age_seconds` 默认 180：OneBot 原始发送时间比插件收到时间更早、且超过这个秒数的消息会被忽略，不进入代理；填 0 则不按时间忽略。插件重载时尚未完成的排队消息仍会继续处理。代理若在读完输入前退出，QQ 会收到带退出码的短句，详细输出留在插件日志。

## 基础命令与权限命令

- `/help` 查看命令；`/info` 查看当前会话。
- `/new [初始消息]` 创建新会话；`/resume [会话ID]` 恢复当前群或私聊的历史会话；`/end` 结束会话。
- `/goon` 中断当前执行并用已保存的代理会话继续；`/cc <代理消息>` 透传代理命令；`/!` 中断当前执行。
- `/pwd` 查看工作目录与权限档；`/cd <目录>` 切换工作目录（owner／管理员）。
- `/initbase` 补齐基础模板（owner／管理员）；`/approve <审批号>`、`/deny <审批号>` 处理危险操作审批（owner／管理员）。
- 访客（guest）只能使用 `/help`、`/info` 和普通对话；管理命令会收到无权限提示。

普通文本自动创建当前会话，并在后续消息中使用保存的代理会话 ID。消息回执用于去重；同会话串行，等待中的文本消息写入 SQLite 队列状态，插件重载后会重新核对授权再处理。已经启动的代理进程在重载时中断，不自动重复执行。

## 版本与手动安装

仓库源码位置：`integrations/astrbot/astrbot_plugin_cc_qq/`。用户选择自行在 AstrBot 中上传 ZIP；ZIP 根层必须直接包含 `metadata.yaml`、`_conf_schema.json`、`main.py`，并保留各 Python 包的相对结构；不要把整个 `astrbot_plugin_cc_qq/` 文件夹连同 macOS 的 `__MACOSX/` 一起压入 ZIP。打包时必须包含 `hooks/` 和 `templates/base/.claude/`、`templates/base/.codex/` 等隐藏目录，建议从插件目录内部执行 `zip -r ... .` 或显式加入隐藏文件。当前版本的安装包是 `integrations/astrbot/astrbot_plugin_cc_qq-v0.2.0-upload.zip`（需在用户确认后生成）。旧包 `integrations/astrbot/astrbot_plugin_cc_qq-v0.1.16-upload.zip` 与更早版本仍保留。

## 后续阶段

- 第一阶段：QQ 消息、授权、双代理、会话与基础命令。
- 第二阶段：任务、调度、辅助命令、媒体与问答模式。
- 第三阶段：管理控制台（Web Console）、跨实例管理与代理间通信（A2A）。
- 第四阶段：逐项验收、文档和部署收口。

各阶段均属 `.devflow/cc-qq-full-migration/` 的完整目标，阶段性交付不代表提前完成。
