# Metadata（元数据）

- 更新时间（Updated At）：2026-09-22 18:35:00 +08:00
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：记录当前工作路径。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`。
- 当前状态（Status）：按天归档与直连媒体首版已收尾，等待下一阶段对齐。
- 文档边界（Scope / Boundary）：本任务记录；诊断插件不代表完整信息中心已获准实施。

# 当前工作流（Workflow）

- 主线：QQ 日总文档与无重复整理、按采集日目录、历史迁移、100 MiB 直连 QQ 媒体及 B 站视频流 URL 已实现并验证。外层 14 项未开工。
- 最新交接：`handoffs/2026-09-22-007-按天归档与直连媒体首版.md`。
- 延期：`deferred/按天归档与媒体首版未做.md`、`deferred/成条与原始资料落盘-首版未做.md`。
- 源码：`backend/src/sourcehub/` + 两个 AstrBot 插件。覆盖 `~/.astrbot/data/plugins/` 再重载。
- 验证：`PYTHONPATH=.:backend/src backend/.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v`
- 不要用 BiliBot 自动回复替代只读采集。不要把 Cookie 发到聊天。
- 恢复：`state.md` → `checkpoints.md` → 007 交接；需追溯时再读 `development-overview.md` 与本轮两份 plan / spec。
