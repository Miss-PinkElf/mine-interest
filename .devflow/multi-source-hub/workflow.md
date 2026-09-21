# Metadata（元数据）

- 更新时间（Updated At）：2026-09-21 15:51:15 +08:00
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：记录当前工作路径。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`。
- 当前状态（Status）：B 站只读采集首版已验收；可选实测或 QQ 延期项待选。
- 文档边界（Scope / Boundary）：本任务记录；诊断插件不代表完整信息中心已获准实施。

# 当前工作流（Workflow）

- 主线：B 站只读提及采集首版已验收。下一步由用户选：可选续测 B1–B3，或回到 QQ 延期项。外层 14 项未开工。
- 插件源码：`integrations/astrbot/astrbot_plugin_sourcehub_bilibili/`。安装目录：`~/.astrbot/data/plugins/astrbot_plugin_sourcehub_bilibili/`。改源码后覆盖再重载。
- 采集已启用。不要用 BiliBot 自动回复替代本插件。不要把 Cookie 发到聊天。
- 恢复：`state.md` → `checkpoints.md` → 005 交接 → 能力边界文档。
- 离线验证：`backend/.venv/bin/python -m unittest discover -s tests -p 'test_bilibili*.py' -v`。
- QQ 嵌套转发已跑通；媒体落盘与自身消息仍延期。
- 私人数据：真实快照、媒体、凭证、`sourcehub-image-urls.json` 不提交。

