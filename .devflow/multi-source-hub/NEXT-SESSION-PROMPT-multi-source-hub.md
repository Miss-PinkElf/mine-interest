# Metadata（元数据）

- 更新时间（Updated At）：2026-09-20 19:10:00 +08:00
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：提供可复制的新会话提示。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`。
- 关联计划（Related Plan）：`plans/2026-09-20-检查插件嵌套转发展开-plan.md`、`plans/2026-09-20-检查插件群级启用范围-plan.md`。
- 当前状态（Status）：交接中（Handoff）。
- 文档边界（Scope / Boundary）：本任务记录；诊断插件不代表完整信息中心已获准实施。

# 下一次对话提示词

请恢复 `.devflow/multi-source-hub/`，先只读 `state.md` 和 `checkpoints.md`；需要细节再读 `handoffs/2026-09-20-003-个人号转发展开跑通与媒体待落盘.md`、`bug-log.md`、`deferred/媒体落盘与机器人自身消息.md`。

**平台已经换了，不要再用旧前提。** QQ 官方机器人已停用（`api.sgroup.qq.com` DNS 解析失败），现在走 **QQ 个人号协议：NapCat 4.18.28 + AstrBot aiocqhttp（OneBot v11）**，平台 id `Test-01`，机器人 QQ `1961618848`（昵称 C#）。本机已跑通真实群消息，不要再问是否已安装、是否要登录。

**已完成、不要再重做**：检查插件已升到 0.4.0，四项能力——事件快照、合并转发展开（`get_forward_msg` 递归）、可读文本输出、群级启用范围。用户已实测：转发样例展开出 **3 层 / 35 条 / 157 图 / 19 文本**，内层保留原始来源群号与发送者。**原「多层转发内层缺失」卡点已关闭。**

**下一步优先做两件事：**

1. **媒体落盘（最急）**。图片现在只有 `file` + 会过期的腾讯 CDN `url`，`rkey` 实测已有个别失效。方案可行性已验证（手动下载成功，HTTP 200 / 1.2 MB / `GIF89a`）。**卡在用户未定策略**：体积（全量 / 限单张 / 缩略图）与清理（是否保留最近 N 天）。用户一给方向就写 plan 实施。
   - 已知坑：`file` 字段的扩展名**不可信**（写 `.jpg` 实际是 GIF），必须按内容魔数判断。
   - 已知坑：直连腾讯 CDN 可用，**走本机 Clash 代理（127.0.0.1:7897）反而全失败**，下载器别走代理。
   - 顺带要处理「顶层直接发的图片」——AstrBot 的 `data/temp/media_image_*` 一分钟内即被清理。

2. **机器人自己发的消息没进 AstrBot**。用户明确要求「在这个群里的消息都需要记录，不要按照发送人过滤」。插件侧**没有**发送人过滤、AstrBot 的 `ignore_bot_self_message=False`，但 `1961618848` 在 AstrBot 全部日志中出现 **0 次**——事件根本没到。拦点定位在 NapCat `handleMsg` 的 `reportSelfMessage` 判断。**先请用户重启一次 NapCat 再测**；若仍不上报，再评估换 NapCat 版本或插件侧 `get_group_msg_history` 回填（回填**必须先补去重**）。

**私人数据边界（重要）**：`~/.astrbot/data/sourcehub-inspector/` 下的真实快照与媒体、以及仓库根目录的 `sourcehub-image-urls.json`（含 `rkey` 鉴权参数）**禁止提交、禁止外传**。快照目前还递归保存整个 `event`（含 bot/platform），未脱敏。

**工作方式**：遵守 devflow 与 `AGENTS.md`；**改代码前必须先落盘 plan**（本轮两次新增功能都遵守了）。改完覆盖安装目录 `~/.astrbot/data/plugins/astrbot_plugin_sourcehub_inspector/`，再在 WebUI 重载；不要在两份源码各自修改。日志用 `self.logger`，前缀 `[SourceHub Inspector]`。

整体信息中心规格仍待审，不自动开工原有 14 项业务任务。日常群条件筛选明确延期；技术栈、开关积压、模型范围、GitHub 私人资料同步、其他来源、历史导入、UI 仍待讨论。
