# cc-qq：AstrBot 原生 QQ 代理插件

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:40:00 +08:00
- 更新时间（Updated At）：2026-09-29 16:55:23 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：说明 cc-qq 插件的当前能力、配置方式与后续迁移范围。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：实施中（In Progress）
- 文档边界（Scope / Boundary）：插件安装和使用说明；第一阶段代码仍需真实 QQ 与双 CLI 验收，完整迁移以当前 mission 的计划和开放规格（OpenSpec）为准。

## 当前状态

当前版本 `0.1.13` 已接通 QQ 文本准入、Claude Code／Codex 异步进程、SQLite 会话和基础命令。群聊只处理白名单内群号中明确 @ 当前机器人的消息；自然语言和命令均须 @，未 @ 时插件静默。私聊无需 @。旧版 `0.1.12` 已有 Codex 群聊与私聊真实回复；Claude Code、新版独立模型及恢复／中断等仍待验收，第一阶段尚未通过。

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

私聊需要启用 `private_enabled` 并填写 `private_work_dir`；普通私聊用户另填 `private_user_ids`。插件为每位私聊用户建立独立子目录。空配置默认不处理任何 QQ 群或私聊。

Claude Code 和 Codex 分别使用 `default_claude_model`、`default_codex_model`。群规则中的 `model` 非空时优先；对应默认模型留空时，插件不传 `--model`，由该代理 CLI 自行选择默认模型。旧共享字段 `default_model` 已停用，升级后需将原值手动填入适用代理的新字段。已有会话继续使用其原代理；若群规则改用另一代理，旧会话仍取原代理的独立默认模型，新代理需用 `/new` 开始新会话。

使用代理功能需要在 AstrBot 进程的命令搜索路径（PATH）中安装并可调用 `claude` 或 `codex`；桌面进程找不到命令时，在插件配置页填写 `claude_command` 或 `codex_command` 的可执行文件绝对路径。普通会话沿用源项目 `cc-ding` 的默认执行权限：Claude Code 使用 `bypassPermissions`，Codex 使用 `danger-full-access`；消息白名单只限制谁能发起请求，不限制代理进程对宿主机文件的访问。问答模式（`/qa`）将在第二阶段实现两种代理可验证的只读行为。

## 第一阶段基础命令

- `/help` 查看命令；`/info` 查看当前会话。
- `/new [初始消息]` 创建新会话；`/resume [会话ID]` 恢复当前群或私聊的历史会话；`/end` 结束会话。
- `/goon` 中断当前执行并用已保存的代理会话继续；`/cc <代理消息>` 透传代理命令；`/!` 中断当前执行。

普通文本自动创建当前会话，并在后续消息中使用保存的代理会话 ID。消息回执用于去重；同会话串行，等待中的文本消息写入 SQLite 队列状态，插件重载后会重新核对授权再处理。已经启动的代理进程在重载时中断，不自动重复执行。

## 版本与手动安装

仓库源码位置：`integrations/astrbot/astrbot_plugin_cc_qq/`。用户选择自行在 AstrBot 中上传 ZIP；ZIP 根层必须直接包含 `metadata.yaml`、`_conf_schema.json`、`main.py`，并保留各 Python 包的相对结构；不要把整个 `astrbot_plugin_cc_qq/` 文件夹连同 macOS 的 `__MACOSX/` 一起压入 ZIP。当前版本的安装包是 `integrations/astrbot/astrbot_plugin_cc_qq-v0.1.13-upload.zip`，安装由用户自行操作。

## 后续阶段

- 第一阶段：QQ 消息、授权、双代理、会话与基础命令。
- 第二阶段：任务、调度、辅助命令、媒体与问答模式。
- 第三阶段：管理控制台（Web Console）、跨实例管理与代理间通信（A2A）。
- 第四阶段：逐项验收、文档和部署收口。

各阶段均属 `.devflow/cc-qq-full-migration/` 的完整目标，阶段性交付不代表提前完成。
