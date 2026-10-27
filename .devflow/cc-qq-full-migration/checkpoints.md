# cc-qq 完整迁移最近检查点（Checkpoints）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:23:07 +08:00
- 更新时间（Updated At）：2026-10-27 15:45:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：记录本 mission 最近的阶段切换与继续位置。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：0.2.2 已覆盖安装目录，待重载与真机验收（Runtime Verification Pending）
- 文档边界（Scope / Boundary）：最近检查点真相源（source of truth）；仅保留最近三条，更早记录见 `checkpoints-archive.md`。

## 2026-09-30 16:08:00 +08:00 — 0.1.16 已提交，待重载

- 已完成：非白名单私聊静默、10 秒同一句去重。22 个单元测试通过。代码提交 `107409f`，安装目录已覆盖。交接是 `handoffs/2026-09-30-004-私聊静默与去重待重载.md`。
- 当前阶段：本轮暂停。AstrBot 尚未重载，运行中仍是 `0.1.14`。
- 下一步：用户重载后确认 `已加载 v0.1.16`，再验空白与非白名单私聊不回复。
- 注意：现场配置当时是私聊关闭、名单为空。`prompt-01.md` 的聚合需求仍未提交、未对齐。

## 2026-10-23 00:00:00 +08:00 — 权限分级 0.2.0 已实施，待提交与真机验收

- 已完成：权限档位、Claude 只读/审批/守护 hook、Codex 权限档案、`/cd`、`/pwd`、`/initbase`、审计表与基础模板。83 个单元测试通过。
- 本机验证：Claude 2.1.202 的 hook→broker→allow/deny 链路可用；只读 hook 阻止工作目录外读取；完全权限守护 hook 阻止 `/etc` 与 `~/.ssh` 写入；Codex 0.162.1 的 `ccqq-readonly`/`ccqq-workspace` 能限制工作区外读写。
- 当前阶段：代码已提交为 `0ad479e`，未推送；未生成 `v0.2.0` ZIP，未覆盖安装目录，AstrBot 尚未重载。
- 注意：Codex 本轮没有逐次审批；审批卡片只在来源会话可见。

## 2026-10-27 15:45:00 +08:00 — 0.2.2 MCP 搜索放行已实测，安装目录已覆盖

- 已完成：`0.2.1` 重排配置页分组与文案；`0.2.2` 放行 `mcp__deepseek-web`（workspace/full）、只读档新增 `readonly_mcp_enabled` 开关（默认开）、原生 `WebSearch`／`WebFetch` 与本机 `mcp__fetch` 全档禁用。87 个单元测试通过。
- 本机验证：Claude 2.1.202 下 deepseek 搜索在 readonly（开关开）/workspace/full 可调用；开关关时不可见；原生 WebSearch 与本机 fetch 在工具列表中不存在；`--setting-sources ""` 不加载用户级 MCP，`user` 才加载。
- 当前阶段：安装目录已覆盖到 `0.2.2`，AstrBot 尚未重载；`claude_setting_sources` 已为 `user`；`readonly_mcp_enabled` 待重载后由 schema 补齐。`0.2.1`／`0.2.2` 在 2026-10-27 收尾提交（未推送），未打包。
- 下一步：重载后确认 `已加载 v0.2.2`，在 QQ 群内验证一次 deepseek 搜索问答与 guest 只读边界；再补 T05.10 其余验收。
- 注意：本机 `mcp__fetch` 被禁用是故意的（防内网访问）；deepseek-web 的抓取在服务端执行，可访问公网但不能碰本机内网。
