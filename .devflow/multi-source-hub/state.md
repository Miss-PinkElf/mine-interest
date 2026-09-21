# Metadata（元数据）

- 更新时间（Updated At）：2026-09-21 15:51:15 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：提供短恢复入口。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 1–8 行。
- 最新交接（Latest Handoff）：`handoffs/2026-09-21-005-B站只读采集首版跑通与能力边界.md`。
- 当前状态（Status）：B 站只读采集首版已验收。
- 文档边界（Scope / Boundary）：本任务记录；不代表整体信息中心 14 项业务已获准实施。

# 当前状态

- 阶段：B 站只读提及采集 T1–T7 五类样本已通过。方向：收到 @ 后采集保存，不自动公开回复。
- 插件：`integrations/astrbot/astrbot_plugin_sourcehub_bilibili/` 0.1.0，已安装并启用。ZIP：`astrbot_plugin_sourcehub_bilibili.zip`。
- 离线：`backend/.venv/bin/python -m unittest discover -s tests -p 'test_bilibili*.py' -v`，33 tests OK。
- 真实验收：视频顶层、回根评、回子评、专栏、图文动态均为完整。图文动态空 `module_content` 漏正文已修。
- 能力边界：`qq-bilibili-capability-boundary.md`。可选续测 B1–B10；首版不做项见 `deferred/B站首版未做与可选实测.md`。
- QQ：嵌套转发以 003 为准。媒体落盘、自身消息、去重仍延期。
- 私人数据：本机归档、`tmp/bilibili-t7-samples/`、`sourcehub-image-urls.json`、Cookie 不提交。
