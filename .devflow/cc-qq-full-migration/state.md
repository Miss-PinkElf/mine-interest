# cc-qq 完整迁移当前状态（Current State）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:10:32 +08:00
- 更新时间（Updated At）：2026-09-30 16:08:00 +08:00
- 作者（Author）：Grok
- 目的（Purpose）：提供本 mission 的短当前快照。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：第一阶段待运行验收；`0.1.16` 已覆盖安装目录，AstrBot 尚未重载（Stage 1 Runtime Verification Pending）
- 文档边界（Scope / Boundary）：当前状态真相源（source of truth）。不代表第一阶段已通过，也不代表 `0.1.16` 已在真实 QQ 上生效。

## 当前快照

- 仓库源码和安装目录都是插件版本（Plugin Version）`0.1.16`。本轮代码提交是 `107409f`（让非白名单私聊静默并抑制重复空白回复），未推送。安装包是 `integrations/astrbot/astrbot_plugin_cc_qq-v0.1.16-upload.zip`。运行中的 AstrBot 最后一次加载日志仍是 `0.1.14`，私聊关闭。
- `0.1.16` 第一版行为：私聊空白不回复；不在 `private_user_ids` 且不是 owner／管理员的私聊按范围外静默并 `stop_event()`；同一私聊同一发送者同一正文（含空白）10 秒内只处理一次；相同回复 10 秒内不连发。群聊 @ 后未授权仍提示。22 个单元测试通过。
- 15:44 保存插件设置时，`private_enabled` 变成 `false`，`private_user_ids` 被清空，并写入了 `stale_message_max_age_seconds: 180`。15:42–15:44 对 `1968401530` 刷了「未获此会话授权」。现场配置本轮没有改回。
- 空白事件是双端登录机器人号 `1961618848` 时多推进来的空包，发送者仍是对方。插件侧丢掉即可；源头是不要再用个人客户端登录这个机器人号。
- 第一阶段仍未通过。未勾选：T03-M.4b、T04.4、T04.5。下一步：用户重载 `0.1.16`，确认日志版本，再看空白私聊是否静默。最新交接是 `handoffs/2026-09-30-004-私聊静默与去重待重载.md`。

## 本轮不做 / 后续阶段（Deferred Scope）

- 阶段 2 到阶段 4 仍见 `deferred/阶段二至四功能.md`。
- 10 秒去重只压同一句重复，不把不同内容聚合成一条。私聊聚合、改 NapCat、改 AstrBot 核心，见 `deferred/第一版边界与未讨论项.md`。
