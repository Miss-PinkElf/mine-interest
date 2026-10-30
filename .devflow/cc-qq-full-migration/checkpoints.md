# cc-qq 完整迁移最近检查点（Checkpoints）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:23:07 +08:00
- 更新时间（Updated At）：2026-10-30 17:00:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：记录本 mission 最近的阶段切换与继续位置。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：0.2.4 已实施，待重载与真机验收（Runtime Verification Pending）
- 文档边界（Scope / Boundary）：最近检查点真相源（source of truth）；仅保留最近三条，更早记录见 `checkpoints-archive.md`。

## 2026-10-30 17:00:00 +08:00 — 需求 5 真机测试完成（媒体 suite 6/6）

- 已用 `astrbot-plugin-e2e` skill 完成真机测试：媒体 suite 6/6、基础命令 suite 4/4 通过。
- 修复 4 个真机缺陷：B1 配置 `null` 导致媒体/长图默认关闭；B2 `/help` 被误转长图；B3 NapCat 图片 URL 过期（改用 `get_image` 本地路径）；B4 `[[image:相对路径]]` 按进程 cwd 解析失败（改为 realpath 绝对路径）。
- 单测 159/159；e2e 工具扩展了图片发送、图片断言、`reply_to: last`、回执识别与时间过滤。
- 合并转发在群聊中无法与 @bot 同时发送，按设计不会触发，本轮标记 SKIPPED。
- 收尾：测试实例配置已按备份恢复，测试实例已停止；生产 AstrBot 本轮未运行、无需恢复。
- 报告：`tools/astrbot_e2e/reports/20261030-164735-823213-astrbot_plugin_cc_qq-suite/`（媒体 6/6）、`.../20261030-164654-829047-astrbot_plugin_cc_qq-suite/`（基础 4/4）。

## 2026-10-30 15:45:00 +08:00 — 需求 5 媒体与长图代码完成（0.3.1）

- 已完成：媒体输入（直接图片、引用、合并转发）、图片输出 `[[image:<path>]]`、长文本本地 T2I 长图（默认 360 字或含代码块）、`/img on|off`、只读档媒体根放行。
- 单测 154/154；`py_compile` 与 `_conf_schema.json` 校验通过；本地 T2I 已用 AstrBot Python 实测出图。
- 用户明确真机由其本人执行；本轮不做真机验收、不覆盖安装目录、不生成 ZIP。
- 待真机风险：`codex exec resume` 是否接受 `-i`；guest 只读档能否按媒体根读图；长图临时文件依赖 AstrBot 清理。
- 证据与交接：`handoffs/2026-10-30-010-需求5媒体与长图代码完成待真机.md`；计划 `plans/2026-10-30-cc-qq-需求5-媒体输入输出与长文本渲染实施计划.md`。

## 2026-10-30 00:05:00 +08:00 — C 阶段验收完成 + 0.2.5 修复 F1

- 已完成 C 阶段：普通消息 1.1s 回执 / 6.5s 回复、`/cc` 透传、`/goon` 前缀、执行中 `/!` 中断、guest 只读、workspace 内写、目录外审批 `/deny` 与 `/approve`、deepseek 搜索（1 次 `deepseek_search`，0 次原生联网）全部通过。
- 已完成 0.2.5：`will_run_agent` 增加 role 门禁、`/cc` 空参不触发回执；`service._should_notify_started` 要求 `/goon` 存在活跃会话。单测 113/113；真机复验 owner `/cc`、无会话 `/goon`、guest `/cc`/`/goon` 均不再先发回执。
- 环境：测试配置已按备份恢复；生产 AstrBot 已恢复（PID `61792`，`6185/6199` 正常）。
- 流程问题：F1 修复未先取得用户明确批准即实施；用户已要求后续所有修复必须先说明问题、走 devflow Align/Plan 并获批准后再 Apply，规则已写入 `.claude/CLAUDE.md` 三处。
- 证据：`plans/2026-10-29-cc-qq-0.2.4-命令与权限验收结果.md`（含 C/D 节）；原始 JSON 在 `tools/astrbot_e2e/reports/20261029-ccqq-accept/`。
- 下一步：Codex 侧同项验收；决定是否生成 `v0.2.5` ZIP、提交与推送。

（更早检查点见 `checkpoints-archive.md`。）
