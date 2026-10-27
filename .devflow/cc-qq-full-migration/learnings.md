# cc-qq 本次踩坑（Learnings）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-30 15:38:00 +08:00
- 更新时间（Updated At）：2026-10-27 15:45:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：留下这次排查里下次还会用到的判断，避免再走错证据。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：已记录（Recorded）
- 文档边界（Scope / Boundary）：经验记录，不是验收结论，也不代替 `bug-log.md`。

- 判断消息是不是过期，只读 OneBot 原始 `time`（`message_obj.raw_message["time"]`）。AstrBot 会把 `message_obj.timestamp` 改成收到时刻。
- 用户和 NapCat 同时登录的是同一个机器人号 `1961618848`。空白私聊的发送者仍是对方 `1968401530`，不是第二个机器人号在线。插件只丢弃 `sender_id == self_id`。
- CPython 3.12 的 `StreamWriter.drain()` 在对端已关掉管道时抛 `ConnectionResetError('Connection lost')`。`0.1.14` 之前这段不在 `AgentProcessError` 里，子进程 stderr 会被丢掉。
- 上传 ZIP 必须在插件目录内部打包，让 `metadata.yaml` 位于压缩包根层。在工作区根目录执行 `zip -r ../... .` 会把整个仓库打进工作区的上一级目录。
- 插件单测要用 `backend/.venv/bin/python -m unittest discover -s integrations/astrbot/astrbot_plugin_cc_qq/tests -t integrations/astrbot -p 'test_*.py'`。这个虚拟环境是 Python 3.9.6，AstrBot 运行时是 3.12。直接 `python -m unittest integrations.astrbot...` 会找不到包。
- 不要在整个 `$HOME` 里做宽搜索，macOS 隐私权限会拦住。插件配置 JSON 带 UTF-8 BOM，读取时用 `utf-8-sig`。
- 空白事件是双端登录机器人号时多推进来的空包，日志为 `1968401530/1968401530:`，发送者仍是对方。回执按 `message_id` 去重，拦不住这种连发空包。
- 在 AstrBot 插件设置页保存新 schema 字段时，可能把 `private_enabled` 和 `private_user_ids` 写回默认值。15:44 那次保存清掉了 `1968401530`。
- 未授权判断若排在空文本静默之前，空白私聊会刷「未获授权」。私聊未在名单应走范围外静默。
- Claude Code 2.1.202 实测 `bypassPermissions` 不执行 `permissions.deny`（`Write` 能写 `/etc` 和 `~/.ssh`）。需要保留关键路径保护时，用 `dontAsk` + PreToolUse 守护 hook，而不是 `bypassPermissions`。
- PreToolUse hook 用 `permissionDecision: "allow"` 可以覆盖 `dontAsk` 的默认拒绝；hook 异常或超时按拒绝处理。`--setting-sources ""` 可以屏蔽仓库 settings，同时 `--settings` 注入的 hooks 仍然生效。
- Codex 传统 `read-only` 只限制写入，不限制读取；权限档案（Permission Profiles，Beta）才能用 `:root = deny` + `:workspace_roots = read/write` 把读写收进工作区。`codex exec resume` 不接受 `-s`，要用 `-c` 覆盖。
- Claude 沙箱只包 shell 子进程，不包内置 `Read/Edit/Write`；因此内置文件工具要用权限规则或 hook，不能只靠沙箱。
- 审批回复要在进入会话串行队列之前处理，否则会与等待审批的代理进程死锁。
- AstrBot 插件配置以内存对象为准：运行中直接改磁盘 JSON 会被下一次保存覆盖；配置必须走 WebUI，或在停进程后改文件。
- AstrBot 的 `AstrBotConfig` 会按 `_conf_schema.json` 自动补齐缺失键；新增配置项无需手工写进 JSON，重载时补默认值。
- Claude Code `--setting-sources ""` 不只屏蔽仓库 settings：用户 settings 里的 `env.ANTHROPIC_AUTH_TOKEN` 鉴权和用户级 MCP server 都不加载。需要 MCP 或 token 鉴权时必须用 `user`。
- MCP 权限规则实测：精确工具名 `mcp__server__tool` 和服务器级 `mcp__server` 都能生效，`mcp__*` 通配不生效。
- `permissions.deny` 会把工具直接从工具列表移除，PreToolUse hook 的 `allow` 不会把被 deny 的工具加回来；这与“hook allow 可以覆盖 dontAsk 默认拒绝”不矛盾，deny 优先级更高。
- 群在 `enabled_group_ids` 但 `group_rules_json` 缺少条目时，`policy` 返回 `REASON_CONFIGURATION_INVALID`，用户看到的是「插件配置无效」，不是「未配置工作目录」；排查时先对这两个名单。
- 服务端 MCP（deepseek-web）与本机 MCP（fetch）风险不同：前者在服务端抓取，碰不到 localhost/内网；后者在本机进程直连 URL，需要单独禁用。
