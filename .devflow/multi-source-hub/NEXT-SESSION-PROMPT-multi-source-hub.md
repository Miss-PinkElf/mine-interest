# Metadata（元数据）

- 更新时间（Updated At）：2026-09-21 15:51:15 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：新对话恢复 B 站首版之后的工作。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 最新交接（Latest Handoff）：`handoffs/2026-09-21-005-B站只读采集首版跑通与能力边界.md`。
- 当前状态（Status）：B 站只读采集首版已验收；可选实测与 QQ 延期项待用户选择。
- 文档边界（Scope / Boundary）：恢复入口。004 已过时。

# 下一次对话提示词

请恢复 `.devflow/multi-source-hub/`。默认先读 `state.md` 与 `checkpoints.md`，再读最新交接：

`.devflow/multi-source-hub/handoffs/2026-09-21-005-B站只读采集首版跑通与能力边界.md`

能力与待测清单：`qq-bilibili-capability-boundary.md`。

**方向已批准：复用 AstrBot，收到 B 站 @ 后采集保存，不自动公开回复。不要再问方向。不要启用完整 BiliBot 互动来替代本插件。**

## 当前进度

B 站只读采集首版已完成：插件安装并启用，五类真实 @（视频顶层、回根评、回子评、专栏、图文动态）均为完整。离线测试 33 项通过。图文动态空模块漏正文已修。

QQ 嵌套转发已在 003 跑通。不要重做。媒体落盘、自身消息、去重仍延期。

## 建议优先

由用户选一条，不要默认开工外层 14 项：

1. 按能力边界 B1–B3 补测（专栏子评、动态子评、转发动态）。
2. 回到 QQ：重启 NapCat 测自身消息（Q1），或等体积策略后做媒体落盘。
3. 不要把 Cookie、真实快照、`sourcehub-image-urls.json` 提交或发到聊天。

## 注意

- 验证：`backend/.venv/bin/python -m unittest discover -s tests -p 'test_bilibili*.py' -v`
- 源码：`integrations/astrbot/astrbot_plugin_sourcehub_bilibili/`，改完覆盖 `~/.astrbot/data/plugins/` 再重载
- 运行数据在 AstrBot 用户目录，不写仓库
- 首版不做：扫码登录、自动下载视频、发送者白名单。见 `deferred/B站首版未做与可选实测.md`
