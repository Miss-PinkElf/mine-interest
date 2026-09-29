# 下一次对话提示词：cc-qq 完整迁移（Next Session Prompt）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 11:00:28 +08:00
- 更新时间（Updated At）：2026-09-29 17:04:38 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：提供可直接复制到新对话的 mission 恢复指令。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：待续接（Ready to Resume）
- 文档边界（Scope / Boundary）：恢复提示，不代替当前状态真相源（source of truth）或已批准计划。

## 可复制提示词

继续 `.devflow/cc-qq-full-migration/` mission。先读 `state.md` 与 `checkpoints.md`，再读 `handoffs/index.md` 指向的 `handoffs/2026-09-29-002-独立模型待运行验收.md`；详细任务见 `spec/tasks.md`。需要完整过程时再读 `development-overview.md`（若存在），追溯原始输入、旧状态和延期项时再读 `origin.md`、`state-history.md`、`deferred/阶段二至四功能.md`。遵守仓库 `AGENTS.md` 与 devflow 的 Align → Plan → Spec/Tasks → Apply 门禁。

仓库插件源码 `integrations/astrbot/astrbot_plugin_cc_qq/` 已升至 `0.1.13`，新包 `integrations/astrbot/astrbot_plugin_cc_qq-v0.1.13-upload.zip` 根层含元数据。用户明确选择自行在 AstrBot 上传和填写配置，当前 AstrBot 运行的仍是旧版 `0.1.12`。`0.1.13` 新增 `default_claude_model` 和 `default_codex_model`，旧共享 `default_model` 停用，群规则 `model` 非空时优先，已有会话按持久化代理类型选模型。本轮代码与相关文档已提交为 `eb462ec`；交接文档另有后续提交。

旧版 `0.1.12` 在 16:51–16:54 已通过 Codex 在群聊和私聊返回非空文本；此前未回复的问题由全局 `plugin_set`、群规则 JSON 和 CLI 短命令 PATH 引起，已记录于 `bug-log.md`。**Claude Code、`0.1.13` 独立模型、两代理恢复／中断和白名单组合仍未完成运行验收，不能宣布第一阶段通过。**当前旧会话均为 Codex；若要验证私聊 Claude Code，先在升级后使用 `/new` 建立新会话。

下一步：让用户上传 `0.1.13` 包，在插件 UI 分别填写两个默认模型或留空；取得真实 QQ 证据并回填 T03-M.4b、T04.4、T04.5。`/model` 动态切换、任务、媒体、管理控制台和 A2A 是后续阶段必做能力，进入条件见 `deferred/阶段二至四功能.md`。工作区另有无关 `.vscode`、B 站资料 ZIP、`data/`、旧插件 ZIP 和原始提示词目录，未纳入本 mission 提交；不要擅自改动。后续代码变更继续提升版本，用户没有再次授权前不要提交。
