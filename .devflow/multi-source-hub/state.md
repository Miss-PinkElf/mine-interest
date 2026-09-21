# Metadata（元数据）

- 更新时间（Updated At）：2026-09-21 18:38:00 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：提供短恢复入口。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`。
- 最新交接（Latest Handoff）：`handoffs/2026-09-21-006-成条入库首版与QQ会话标记.md`。
- 当前状态（Status）：成条首版已落地；B 站 Vault 可用；QQ 会话标记已放宽。
- 文档边界（Scope / Boundary）：本任务记录；不代表整体信息中心 14 项业务已获准实施。

# 当前状态

- 阶段：成条切片首版已落地。Align/Plan 已执行。外层 14 项未开工。
- Vault：`~/.astrbot/data/sourcehub/`。B 站按作品合并已回填；QQ 需重载后用宽松标记重发会话段落。
- 插件：检查器 0.5.0，B 站 0.2.0。改源码后 rsync 到 `~/.astrbot/data/plugins/` 再重载。
- 验证：`PYTHONPATH=.:backend/src backend/.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v`
- 延期清单：`deferred/成条与原始资料落盘-首版未做.md`。自身消息、自动清理仍延期。
- 私人数据：Cookie、真实快照、`sourcehub-image-urls.json` 不提交。
