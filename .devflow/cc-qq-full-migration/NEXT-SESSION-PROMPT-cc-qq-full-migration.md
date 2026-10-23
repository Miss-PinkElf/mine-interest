# 下一次对话提示词：cc-qq 完整迁移（Next Session Prompt）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 11:00:28 +08:00
- 更新时间（Updated At）：2026-10-23 00:00:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：提供可直接复制到新对话的 mission 恢复指令。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：待续接（Ready to Resume）
- 文档边界（Scope / Boundary）：恢复提示，不代替当前状态真相源（source of truth）或已批准计划。

## 可复制提示词

继续 `.devflow/cc-qq-full-migration/` mission。先读 `state.md`、`checkpoints.md`，再读 `handoffs/2026-10-23-005-权限分级待真机验收.md`。任务勾选看 `spec/tasks.md` 的 T05。遵守仓库 `AGENTS.md` 与 devflow 的 Align → Plan → Spec/Tasks → Apply 门禁。

当前仓库插件版本是 `0.2.0`，权限分级已实施，83 个单元测试通过，但**未提交、未生成 v0.2.0 ZIP、未覆盖安装目录、AstrBot 未重载**。安装目录仍是旧版。

本轮新增：群内非白名单 guest 只读；白名单 member 工作区读写；owner/管理员完全权限 + 守护 hook 拦关键路径（不用 bypassPermissions，因为 2.1.202 实测其不执行 deny）；Claude 通过 PreToolUse hook + 本机 broker + QQ `/approve`、`/deny` 做逐次审批；Codex 使用权限档案 `ccqq-readonly`、`ccqq-workspace` 限制读写；管理员 `/cd`、`/pwd`、`/initbase`；审计表 `permission_audit`；基础模板。

下一步：先问用户是否提交、是否生成 ZIP、是否覆盖安装目录。用户同意后才提交或覆盖。然后重载并验收 T05.10：guest 只读、member 工作区写入、目录外审批、`/cd`、`/initbase`，Claude 与 Codex 分别取证。再补验 T03-M.4b、T04.4、T04.5。

不要把 Codex 的逐次审批说成已实现；`codex exec` 的非交互审批仍是 under development。不要把审批卡片说成会私聊管理员；当前只发来源会话。不要推送远端。不要动 B 站插件。根目录 `devflow-handoff.md` 只读。
