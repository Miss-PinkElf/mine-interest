# 下一次对话提示词：cc-qq 完整迁移（Next Session Prompt）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 11:00:28 +08:00
- 更新时间（Updated At）：2026-10-28 00:50:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：提供可直接复制到新对话的 mission 恢复指令。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：待续接（Ready to Resume）
- 文档边界（Scope / Boundary）：恢复提示，不代替当前状态真相源（source of truth）或已批准计划。

## 可复制提示词

继续 `.devflow/cc-qq-full-migration/` mission。先读 `state.md`、`checkpoints.md`，再读 `handoffs/2026-10-28-007-0.2.3-cd-list待真机验收.md`。任务勾选看 `spec/tasks.md` 的 T05.10、T05.11、T05.12。遵守仓库 `AGENTS.md` 与 devflow 的 Align → Plan → Spec/Tasks → Apply 门禁。

当前仓库与安装目录都是 `0.2.3`：`0.2.1` 重排配置页文案，`0.2.2` 放行 deepseek-web MCP 搜索并禁用原生联网，`0.2.3` 新增 `/cd list` 与 `/cd <序号>` 切换。94 个单元测试通过；已用 AstrBot 自带的 Python 3.12.13 从安装目录加载验证；但 **AstrBot 尚未重载，QQ 真机未验收**，未生成 ZIP。

下一步：
1. 重载 cc-qq，确认日志 `[cc-qq] 已加载 v0.2.3`。
2. 群里 @bot 试 `/cd list`（应看到 6 个目录按配置顺序编号、当前目录带「← 当前」）、`/cd 2`、`/cd 99`（应提示 1-6）。
3. 验 T05.11：群里 @bot 让其「用 deepseek 搜索今天的新闻」，确认走 `mcp__deepseek-web__deepseek_search`；再验 guest 只读边界。
4. 按 T05.10 继续验 guest 只读、member 工作区写入、目录外审批、`/cd`、`/initbase`；补验 T03-M.4b、T04.4、T04.5，证据回填 `spec/feature-mapping.md`。
5. 真机通过后再决定是否生成 `v0.2.3` ZIP、推送远端。

关键约束：
- 插件配置只能从 WebUI 改；运行中直接改配置文件会被内存配置覆盖。
- `claude_setting_sources` 已设为 `user`，改回 `""` 会导致 Claude `Not logged in` 且 MCP 不加载。
- 本机 `mcp__fetch` 在插件会话中不可用是预期行为，不要当 bug 修。
- `/cd` 序号以当次配置顺序为准，配置调整后旧序号失效；纯数字目录名用 `/cd ./123`。
- 群内 @bot 管理私聊白名单只是候选需求，4 个问题未确认，禁止直接实施；详见 `deferred/第一版边界与未讨论项.md`。
- `/cd list` 的扩展（一级子目录、两级列表、分页、序号持久化）用户已明确否决或延期，不要自行扩展。
- 群 `432199252` 的群规则由用户在 WebUI 配置，不要把真实 work_dir 写进仓库。
- 不要动 B 站插件；根目录 `devflow-handoff.md` 只读。

未讨论 / 明确延期的议题（详见 `deferred/第一版边界与未讨论项.md`）：
- 需求 4.2：把代码 diff 转成 HTML 上传 GitHub Pages，或用语雀 MCP 展示长文本。
- 需求 5：群内 guest 与白名单成员的对话是否共享上下文（当前按会话共享，不按发言者隔离）。
- 未来需求：长时间不对话时检测输入状态、告知上下文长度并推荐 `/new`。
- 需求 3.3：私聊短时聚合与上下文截断。
