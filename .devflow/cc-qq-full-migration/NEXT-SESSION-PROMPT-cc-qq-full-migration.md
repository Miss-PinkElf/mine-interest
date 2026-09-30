# 下一次对话提示词：cc-qq 完整迁移（Next Session Prompt）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 11:00:28 +08:00
- 更新时间（Updated At）：2026-09-30 16:08:00 +08:00
- 作者（Author）：Grok
- 目的（Purpose）：提供可直接复制到新对话的 mission 恢复指令。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：待续接（Ready to Resume）
- 文档边界（Scope / Boundary）：恢复提示，不代替当前状态真相源（source of truth）或已批准计划。

## 可复制提示词

继续 `.devflow/cc-qq-full-migration/` mission。先读 `state.md` 与 `checkpoints.md`，再读 `handoffs/index.md` 指向的 `handoffs/2026-09-30-004-私聊静默与去重待重载.md`。任务勾选看 `spec/tasks.md`。需要完整过程时再读 `development-overview.md`（当前没有这份文件）。追溯原始输入、旧状态或延期项时再读 `origin.md`、`state-history.md`、`backlog.md`、`deferred/`。遵守仓库 `AGENTS.md` 与 devflow 的 Align → Plan → Spec/Tasks → Apply 门禁。

仓库和安装目录都是 `0.1.16`。代码提交 `107409f`，未推送。这一版在 `0.1.14` 之上增加：不在私聊白名单且不是 owner／管理员则静默并停止事件；同一私聊同一正文（含空白）10 秒内只处理一次；相同回复不连发。22 个单元测试通过。AstrBot 最后一次加载日志仍是 `0.1.14`，私聊关闭。现场配置 `private_enabled` 为 false，`private_user_ids` 为空。

下一步：让用户重载插件，确认日志 `已加载 v0.1.16`。再验证私聊空白、非白名单不回复、同一句不连发。若要和 `1968401530` 私聊，在设置里打开私聊并填回该号。有证据后再做 Claude Code、T03-M.4b、T04.4、T04.5。空白事件来自机器人号双端登录，插件丢掉即可，不要改 NapCat。

不要把不同内容的私聊聚合成一条。`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md` 工作区那一行仍未讨论、未提交。`/model`、任务、媒体、`/qa`、管理页和 A2A 仍在阶段 2 之后。不要推送。不要动 B 站插件。根目录 `devflow-handoff.md` 只读。
