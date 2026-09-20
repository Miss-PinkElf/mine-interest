# Metadata（元数据）

- 更新时间（Updated At）：2026-09-20 19:10:00 +08:00
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：提供短恢复入口。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`。
- 当前状态（Status）：交接中（Handoff）。
- 文档边界（Scope / Boundary）：本任务记录；诊断插件不代表完整信息中心已获准实施。

# 当前状态

- 阶段：检查插件（Inspector Plugin）已从官方网站原型升级为**个人号协议版**并跑通；**嵌套转发展开已解决**；暂停交接。
- **平台已换**：从 QQ 官方机器人（qq_official，因 `api.sgroup.qq.com` DNS 解析失败关闭）切到 **aiocqhttp（OneBot v11）**，平台 id `Test-01`，接入方式为本机 **NapCat 4.18.28**，机器人账号 `1961618848`（昵称 C#）。2026-09-09 交接里关于官方机器人的描述已过时。
- 本机路径：仓库源码 `integrations/astrbot/astrbot_plugin_sourcehub_inspector/`；安装目录 `~/.astrbot/data/plugins/astrbot_plugin_sourcehub_inspector/`；AstrBot 用户目录 `~/.astrbot/`；NapCat 配置 `~/Library/Containers/com.tencent.qq/.../QQ/NapCat/config/onebot11_1961618848.json`。
- 插件版本 **0.4.0**，本轮四项能力：事件快照、转发展开（`get_forward_msg`）、可读文本输出、群级启用范围。
- 用户验收结果（2026-09-20 18:50）：本地转发样例展开为 **3 层 / 35 条 / 段类型 {'forward': 6, 'image': 157, 'text': 19}**，内层保留原始来源群号、原始发送者、原始时间与 message_id。官方机器人路径做不到这点。
- 关键结论：**官方 QQ 机器人拿不到内层树**（`message_type=102` 只给扁平预览，无 `msg_elements`，无二次获取接口）；**个人号路径可以**（`get_forward_msg`）。证据见 `bug-log.md` 与本轮 plan。
- **未解决**：① 图片仍未落盘（`rkey` 会过期，实测已有个别失效）；② 机器人自己发的消息（`1961618848`）从未进入 AstrBot（疑似 NapCat `reportSelfMessage` 未生效，需重启 NapCat 复测）；③ 快照未脱敏、事件身份不可靠、无去重。
- 明确延期仍是日常群规则/正则/LLM 筛选。**新增待定**：媒体落盘体积策略（全量/限单张/缩略图）、是否自动清理旧媒体，均未选定。
- 用户已给出但**尚未实现**的新要求：在该群内「消息都需要记录，不要按发送人过滤」——插件侧已无发送人过滤，卡点在 NapCat 未上报自身消息。
- 下一步：① 重启 NapCat 后用机器人发消息复测自身消息；② 定媒体落盘体积策略后实施；③ NapCat 开启 `parseMultMsg` 是否更优未评估。
- 最新交接：`handoffs/2026-09-20-003-个人号转发展开跑通与媒体待落盘.md`。
- 本轮授权提交并推送相关源码与任务记录；**不含**真实消息快照、`sourcehub-image-urls.json`（含 rkey）、`.vscode/controlled-explorer.json`、编辑器配置与凭证。
