# cc-qq 完整迁移当前状态（Current State）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:10:32 +08:00
- 更新时间（Updated At）：2026-09-30 15:38:00 +08:00
- 作者（Author）：Grok
- 目的（Purpose）：提供本 mission 的短当前快照。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：第一阶段代码已接通；`0.1.14` 已覆盖安装目录；三条修复待真实 QQ 验收（Stage 1 Runtime Verification Pending）
- 文档边界（Scope / Boundary）：当前状态真相源（source of truth）。记录已交付代码和尚未核对的重载结果，不代表第一阶段已通过，也不代表三条修复已在真实 QQ 上消失。

## 当前快照

- 仓库源码和安装目录 `~/.astrbot/data/plugins/astrbot_plugin_cc_qq/` 都是插件版本（Plugin Version）`0.1.14`。代码提交是 `7a714ac`，信息为“修复 cc-qq 过期消息、私聊空文本和标准输入重置”，未推送。安装包是 `integrations/astrbot/astrbot_plugin_cc_qq-v0.1.14-upload.zip`。这一版带上了此前未单独装上的 `0.1.13` 独立默认模型字段。
- 三项第一版修复已在代码里，11 个单元测试通过。私聊空文本静默，群聊 @ 后空文本仍提示。过期消息秒数（Stale Message Max Age）配置键是 `stale_message_max_age_seconds`，默认 180，填 0 关闭，非法值回落 180。标准输入重置收成带退出码的代理错误。启动时状态为 `queued` 的回执重放不按这条秒数过滤。
- 用户在收尾时说已经重载。本会话没有再读 `~/.astrbot/logs/backend.log`。插件配置 JSON 本轮没有改，设置页还没保存新键时，代码按默认 180 秒判断。
- 第一阶段仍未通过。Claude Code 真实回复、两代理恢复／中断／结束、白名单组合，以及独立默认模型的真实 QQ 行为都还没验收。未勾选任务是 T03-M.4b、T04.4、T04.5。
- 下一步：新对话先核对重载后是否真是 `0.1.14`，再看过期消息、空白私聊和代理早退。不要先重载或再覆盖，除非日志显示跑的仍不是这一版。最新交接是 `handoffs/2026-09-30-003-三项修复待真实验收.md`。

## 本轮不做 / 后续阶段（Deferred Scope）

- 阶段 2 到阶段 4 的 `/model` 动态切换、任务、媒体、`/qa`、管理控制台（Web Console）和代理间通信（A2A）仍须做，见 `deferred/阶段二至四功能.md`。
- 这三项修复只做了第一版。NapCat 若把原始 `time` 改成当前时间、空白的 `Prepare to send` 日志，以及收尾时工作区里新出现、本轮没有讨论的私聊短时聚合，都记在 `deferred/第一版边界与未讨论项.md`。这些不是永久放弃。
