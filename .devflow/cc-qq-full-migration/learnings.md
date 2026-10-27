# cc-qq 本次踩坑（Learnings）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-30 15:38:00 +08:00
- 更新时间（Updated At）：2026-10-28 01:20:00 +08:00
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
- 插件单测通过（Python 3.9.6）不等于运行时可用：AstrBot 跑 3.12.13。想在不重载的前提下验证真实运行时，可直接用 `/Users/mobius/.local/share/uv/tools/astrbot/bin/python3` 把安装目录加入 `sys.path` 再导入，能捕获版本相关的导入错误。
- `/cd` 的三种形式（list／序号／路径）必须共用同一套边界校验；把原 `_change_work_dir` 的校验体抽成 `_apply_work_dir`，序号入口只负责选目标，避免为快捷方式开出免校验旁路。
- 清单类命令的编号不要落库：配置顺序一变，历史序号就失效。每次实时读配置、在提示里说明「以当次顺序为准」，比维护一份映射表更简单可靠。
- `/goon` 里 `return await self._execute(...) or ""` 是个隐形陷阱：`_execute` 被取消时返回 `None`，`or ""` 把它变成空串，`service` 判 `reply is not None` 标 `done`、`main` 判 `if reply:` 不发，形成「回执显示成功、用户完全无感知」。凡是 `None` 有语义（取消／失败）的返回值，禁止用 `or ""` 兜底。
- 「哪些命令会启动代理」要有唯一判定函数（`commands/registry.py::will_run_agent`），不要在多处散写「命令都同步返回」这种假设。`/goon`、`/cc <msg>`、带参数的 `/new` 与 `/!` 都会跑代理，恰恰最需要执行回执。
- NapCat 的 `onebot11_*.json` 和 AstrBot 插件配置同一类：运行中改磁盘文件会被内存快照覆盖，改完必须重启 QQ 才生效。
- NapCat 的 `onebot11_*.json` 带 UTF-8 BOM，脚本读写必须用 `encoding="utf-8-sig"`，否则 `json.load` 直接抛 `Unexpected UTF-8 BOM`。
- 用户在终端启动的是 `QQ.app`，NapCat 是注入进 QQ 的 Node 辅助进程（`QQ Helper`）里运行的，不是独立进程。NapCat 的连接日志出现在 QQ 侧属正常，不代表「用了另一种启动方式」。
- 排查「消息没响应」先对三个名单：生产 `enabled_group_ids`、`group_rules_json`、以及 e2e 测试实例自己的配置。群 `701292201` 只在 `~/.astrbot-e2e`，不在生产，属于预期静默而非 bug。
- 会话 JSONL（`~/.claude/projects/<cwd-slug>/*.jsonl`）里 `timestamp` 是 UTC，本地要 +8。同一 assistant 事件会重复落盘 3–4 次，统计工具调用次数必须按 `tool_use.id` 去重。
- 排查耗时的主要来源不是「单条命令慢」，而是「往返次数多 + 完全不并行」。定量方法是配对 `tool_use.id` 与 `tool_result.tool_use_id` 算工具耗时，再用总时长相减得到模型生成耗时；并行度 = 每条 assistant 消息内的 `tool_use` 数量。详见 `2026-10-28-排查耗时分析与优化方案.md`。
