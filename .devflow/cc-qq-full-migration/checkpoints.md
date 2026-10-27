# cc-qq 完整迁移最近检查点（Checkpoints）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:23:07 +08:00
- 更新时间（Updated At）：2026-10-28 00:20:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：记录本 mission 最近的阶段切换与继续位置。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：0.2.3 已实施，待重载与真机验收（Runtime Verification Pending）
- 文档边界（Scope / Boundary）：最近检查点真相源（source of truth）；仅保留最近三条，更早记录见 `checkpoints-archive.md`。

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

## 2026-10-28 00:20:00 +08:00 — 0.2.3 `/cd list` 已实施，待重载

- 已完成：`/cd list` 按 `allowed_work_dirs` 配置顺序编号列出并标记当前目录；`/cd <序号>` 切换；`/cd <目录>` 行为不变。新增常量集中在 `constants.py`，展示逻辑在 `commands/session.py::cd_list_text`。94 个单元测试通过。
- 当前阶段：仓库与安装目录都是 `0.2.3`，AstrBot 尚未重载；本轮未生成 ZIP。
- 下一步：用户确认后重载，在 QQ 内实测 `/cd list`、`/cd 2` 与越界提示。
- 注意：序号以当次配置顺序为准，配置调整后旧序号失效；纯数字目录名需用 `/cd ./123` 形式。
- 本轮未讨论 / 未实现的议题已记入 `deferred/第一版边界与未讨论项.md` 的「2026-10-28 `/cd list` 与需求收口」小节。
