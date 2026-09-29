# 下一次对话提示词：cc-qq 完整迁移（Next Session Prompt）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 11:00:28 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：提供可直接复制到新对话的 mission 恢复指令。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：待续接（Ready to Resume）
- 文档边界（Scope / Boundary）：恢复提示，不代替当前状态真相源（source of truth）或已批准计划。

## 可复制提示词

继续 `.devflow/cc-qq-full-migration/` mission。先按恢复热路径读 `state.md` 与 `checkpoints.md`，再读 `handoffs/index.md` 指向的最新 handoff；需要完整脉络时再读 `development-overview.md`（若存在），追溯输入、旧状态和延期项时再读 `origin.md`、`state-history.md`、`deferred/阶段二至四功能.md`。请遵守仓库 `AGENTS.md` 与 devflow 的 Align → Plan → Spec/Tasks → Apply 门禁。

当前插件源码在 `integrations/astrbot/astrbot_plugin_cc_qq/`，版本 `0.1.2`。它已有 QQ 入口、准入、回复、SQLite 建表和两种 CLI 适配器，但 `main.py` 仍只回复“代理会话功能正在接入”，**现在不能对话**；T01–T03 未核验完成，T04 尚未实现。先不要把骨架误报为可用。

本轮用户新增“群聊白名单、群聊必须 @ 才能对话”。`enabled_group_ids` 已提供群号白名单入口，`group_rules_json.allowed_user_ids` 是群成员白名单，但缺少真实 QQ 验收；@ 门禁尚未设计确认或实现。下一步先做 Mini Align，明确普通文本和命令的 @ 要求、机器人 QQ 身份识别、@ 段处理及未 @ 时的行为；确认后更新第一阶段计划和开放规格（OpenSpec）任务，再实施。第一版目标是 QQ 群／私聊与 Claude Code、Codex 的可恢复文本对话；阶段 2–4 的延期范围见 `deferred/阶段二至四功能.md`，均须后续继续。

工作区含其他 mission、B 站插件、测试文件、ZIP 和原始提示词目录的改动；不要覆盖或提交无关文件。用户在上一轮明确要求只写收尾文档，先不提交。后续若修改插件代码，要同步提升版本并覆盖本机 AstrBot 插件副本；未经用户明确允许不得提交。
