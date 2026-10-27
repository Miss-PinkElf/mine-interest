# cc-qq 完整迁移当前状态（Current State）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:10:32 +08:00
- 更新时间（Updated At）：2026-10-27 15:45:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：提供本 mission 的短当前快照。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：0.2.2 已覆盖安装目录、待重载与真机验收（Deployed / Runtime Verification Pending）
- 文档边界（Scope / Boundary）：当前状态真相源（source of truth）。不代表已在 AstrBot/QQ 上验收通过，也不代表已生成 ZIP。

## 当前快照

- 仓库插件版本升至 `0.2.2`（`0.2.1` 为配置页文案分组，`0.2.2` 为 MCP 放行）。87 个单元测试通过；`0.2.0` 已提交 `0ad479e`，`0.2.1`／`0.2.2` 在 2026-10-27 收尾提交（未推送）。安装目录已覆盖到 `0.2.2`，但 AstrBot 尚未重载；未生成 ZIP。
- MCP 联网：workspace／full 放行服务器级 `mcp__deepseek-web`；只读档由 `readonly_mcp_enabled`（默认开）控制；原生 `WebSearch`／`WebFetch` 与本机 `mcp__fetch` 全档禁用。实测 `""` setting-sources 不加载用户级 MCP，配置需 `claude_setting_sources=user`（同时解决 `ANTHROPIC_AUTH_TOKEN` 鉴权）。
- 权限模型：群内非白名单为 `readonly`，群／私聊白名单为 `workspace`，owner／管理员为 `full`；档位按每轮发言者计算，不写入会话记录。
- Claude Code：只读用 `dontAsk + --tools`；工作区用 `acceptEdits + Seatbelt/bubblewrap 沙箱 + PreToolUse 审批 hook`；完全权限用 `dontAsk + 守护 hook`（实测 `bypassPermissions` 不执行 deny 规则）。默认 `--setting-sources ""`。
- Codex：只读/工作区改用权限档案 `ccqq-readonly`、`ccqq-workspace`，工作区外读写与 `/tmp` 被拒绝；完全权限用 `sandbox_mode="danger-full-access"`。Codex 本轮没有逐次审批。
- 本机 CLI 实测：Claude Code 2.1.202 的 hook 能向本机 broker 请求并放行/拒绝 `rm`；Codex 0.162.1 的权限档案能阻止读取 `~/.codex/config.toml`，工作区档能写当前目录并阻止写 `/tmp`。
- 审批：`/approve`、`/deny` 在 `main.py` 会话队列前处理，避免与等待审批的代理死锁；超时、异常、broker 不可达一律拒绝；`permission_audit` 记录审批与拒绝。
- 管理员 `/cd` 只能进入 `allowed_work_dirs` 的 realpath 子目录；`/initbase` 只补缺失模板，不覆盖已有文件。

## 本轮不做 / 后续阶段（Deferred Scope）

- 真机验收 T05.10：安装目录已是 `0.2.2`，待用户重载 AstrBot 后按清单验收；未生成 ZIP，未推送。
- T05.11 MCP 搜索：CLI 已实测，待重载后在 QQ 内验证一次群聊搜索问答。
- 群内 @bot 管理私聊白名单（候选）：用户 2026-10-27 提出后中断，4 个关键问题未回答（名单类型、@ 或 QQ 号、命令集、私聊总开关关闭时行为），本轮未实现。详见 `deferred/第一版边界与未讨论项.md`。
- 群未配置 `group_rules_json` 时的报错仍是笼统的「插件配置无效」；更准确的提示本轮未改。
- Codex 原生 web search 的关闭方式待确认 0.162.1 配置键；MCP 按服务器/工具的细分开关延期。
- Codex 逐次危险操作审批：`codex exec` 的非交互审批仍为 under development。
- 审批卡片私聊通知管理员、私聊短时聚合与上下文截断（需求3.3）、工作目录人格、图形化权限页：见 `deferred/阶段二至四功能.md`。
- 阶段 2 到阶段 4 的其余功能仍按总体计划继续。
