# 下一次对话提示词：cc-qq 完整迁移（Next Session Prompt）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 11:00:28 +08:00
- 更新时间（Updated At）：2026-09-30 15:38:00 +08:00
- 作者（Author）：Grok
- 目的（Purpose）：提供可直接复制到新对话的 mission 恢复指令。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：待续接（Ready to Resume）
- 文档边界（Scope / Boundary）：恢复提示，不代替当前状态真相源（source of truth）或已批准计划。

## 可复制提示词

继续 `.devflow/cc-qq-full-migration/` mission。先读 `state.md` 与 `checkpoints.md`，再读 `handoffs/index.md` 指向的 `handoffs/2026-09-30-003-三项修复待真实验收.md`。任务勾选看 `spec/tasks.md`。需要完整过程时再读 `development-overview.md`（当前 mission 下没有这份文件）。追溯原始输入、旧状态或延期项时再读 `origin.md`、`state-history.md`、`backlog.md`、`deferred/`。遵守仓库 `AGENTS.md` 与 devflow 的 Align → Plan → Spec/Tasks → Apply 门禁。

仓库和安装目录 `~/.astrbot/data/plugins/astrbot_plugin_cc_qq/` 都是 `0.1.14`。代码提交是 `7a714ac`，未推送。这一版包含 `0.1.13` 的 `default_claude_model` / `default_codex_model`，并加上三项第一版修复：私聊空文本静默、群聊空 @ 仍提示；`stale_message_max_age_seconds` 默认 180，填 0 关闭，非法值回落 180；标准输入 `ConnectionResetError` 收成带退出码的代理错误。`queued` 重放不按秒数过滤。配置 JSON 本轮没改，新键没保存时走默认 180。11 个单元测试在实现时通过。

用户已经说插件重载过了。上一会话按用户要求先收尾，没有读重载后的 `~/.astrbot/logs/backend.log`。下一步先确认日志里的版本是 `0.1.14`，再验证过期消息、空白私聊和代理早退。日志若仍是旧版，先说明，不要擅自再覆盖或重载。三条有证据之后，再做 Claude Code、双代理恢复／中断、白名单组合和 T03-M.4b、T04.4、T04.5。旧版 Codex 回复不能代替这些验收。

不要改 NapCat，不要改 AstrBot 核心，不要在没有原始补推事件时再加第二套过期启发式。`/model`、任务、媒体、`/qa`、管理页和 A2A 仍在阶段 2 之后，见 `deferred/阶段二至四功能.md`。`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md` 工作区有一条未提交、未讨论的私聊短时聚合，不要实现，也不要把它算进 cc-qq 提交；边界见 `deferred/第一版边界与未讨论项.md`。不要推送。不要动 B 站插件。根目录 `devflow-handoff.md` 只读。
