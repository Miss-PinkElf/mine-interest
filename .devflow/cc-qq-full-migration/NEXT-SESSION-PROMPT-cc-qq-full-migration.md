# 下一次对话提示词：cc-qq 完整迁移（Next Session Prompt）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 11:00:28 +08:00
- 更新时间（Updated At）：2026-10-27 15:45:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：提供可直接复制到新对话的 mission 恢复指令。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：待续接（Ready to Resume）
- 文档边界（Scope / Boundary）：恢复提示，不代替当前状态真相源（source of truth）或已批准计划。

## 可复制提示词

继续 `.devflow/cc-qq-full-migration/` mission。先读 `state.md`、`checkpoints.md`，再读 `handoffs/2026-10-27-006-0.2.2-MCP搜索待真机验收.md`。任务勾选看 `spec/tasks.md` 的 T05.10、T05.11。遵守仓库 `AGENTS.md` 与 devflow 的 Align → Plan → Spec/Tasks → Apply 门禁。

当前安装目录已是 `0.2.2`：`0.2.1` 重排配置页文案，`0.2.2` 放行 deepseek-web MCP 搜索、禁用原生 `WebSearch`/`WebFetch` 与本机 `mcp__fetch`，只读档新增 `readonly_mcp_enabled`（默认开）。87 个单元测试通过，Claude 2.1.202 的 CLI 实测通过；但 **AstrBot 尚未重载，QQ 真机未验收**，代码未推送、未生成 ZIP。

下一步：
1. 重载 cc-qq，确认日志 `已加载 v0.2.2`，确认配置页出现 `readonly_mcp_enabled`。
2. 群里 @bot 让其「用 deepseek 搜索今天的新闻」，确认 `mcp__deepseek-web__deepseek_search` 正常返回；再验 guest 只读边界。
3. 按 T05.10 继续验 guest 只读、member 工作区写入、目录外审批、`/cd`、`/initbase`；补验 T03-M.4b、T04.4、T04.5，证据回填 `spec/feature-mapping.md`。
4. 真机通过后再决定是否提交后续、生成 `v0.2.2` ZIP、推送远端。

关键约束：
- 插件配置只能从 WebUI 改；运行中直接改配置文件会被内存配置覆盖。
- `claude_setting_sources` 已设为 `user`，改回 `""` 会导致 Claude `Not logged in` 且 MCP 不加载。
- 本机 `mcp__fetch` 在插件会话中不可用是预期行为，不要当 bug 修。
- 群内 @bot 管理私聊白名单只是候选需求，4 个问题未确认，禁止直接实施；详见 `deferred/第一版边界与未讨论项.md`。
- 群 `432199252` 的群规则由用户在 WebUI 配置，不要把真实 work_dir 写进仓库。
- 不要动 B 站插件；根目录 `devflow-handoff.md` 只读。
