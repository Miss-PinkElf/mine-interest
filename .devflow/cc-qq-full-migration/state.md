# cc-qq 完整迁移当前状态（Current State）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:10:32 +08:00
- 更新时间（Updated At）：2026-09-29 17:04:38 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：提供本 mission 的短当前快照。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：第一阶段代码已接通、待运行验收（Stage 1 Runtime Verification Pending）
- 文档边界（Scope / Boundary）：当前状态真相源（source of truth）；记录已交付代码和未完成的真实 QQ 验收，不代表第一阶段已通过。

## 当前快照

- 第一阶段对齐、计划及开放规格（OpenSpec）已完成；T00 功能映射和 T01–T04 的源码链路已接通。群号／成员白名单与群聊精确 @ 门禁已编码，私聊不要求 @；会话、命令、双 CLI 和回执使用插件 SQLite。
- 仓库源码版本为 `0.1.13`，新增 `default_claude_model`、`default_codex_model`，旧共享 `default_model` 不再读取；群规则 `model` 非空时优先，已存在会话按持久化代理类型选模型。新安装包是 `integrations/astrbot/astrbot_plugin_cc_qq-v0.1.13-upload.zip`，根层含 `metadata.yaml`。用户选择自行在 AstrBot 上传，当前运行的仍是 `0.1.12`。
- 旧版 `0.1.12` 的真实 QQ 证据：16:51–16:54，QQ `2844973553` 在群 `836229427` 和私聊均由 Codex 返回非空文本；SQLite 两条会话的代理类型均为 `codex`，多条轮次状态为 `done`。早期不回复问题分别由 AstrBot 全局 `plugin_set`、非法群规则 JSON 和桌面进程找不到短命令 `codex` 引起；用户已修正配置，详情见 `bug-log.md`。
- **第一阶段仍未通过**：Claude Code 真实 QQ 回复、两代理恢复／中断／结束及白名单组合行为未完成验收；`0.1.13` 的独立模型选择尚未安装实测。未讨论完的 `/model` 动态切换在第一阶段验收后进入阶段 2，其他延期能力见 `deferred/阶段二至四功能.md`。
- 下一步：用户上传 `0.1.13` ZIP，分别填写两个默认模型或留空，验证 Claude Code、Codex、群覆盖与旧会话代理选择；然后继续 `spec/tasks.md` T03-M.4b、T04.4、T04.5。最新交接是 `handoffs/2026-09-29-002-独立模型待运行验收.md`。

## 本轮不做 / 后续阶段（Deferred Scope）

- 第一版优先完成 QQ 群／私聊与双代理文本闭环、白名单和已对齐的 @ 门禁；任务、媒体、`/qa` 等在阶段 1 通过后进入阶段 2，管理页与 A2A 在阶段 2 接口稳定后进入阶段 3，完整性收口在阶段 3 后进入阶段 4。对象、原因和触发条件见 `deferred/阶段二至四功能.md`；这些不是永久放弃项。
