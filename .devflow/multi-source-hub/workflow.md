# Metadata（元数据）

- 更新时间（Updated At）：2026-09-21 18:38:00 +08:00
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：记录当前工作路径。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`。
- 当前状态（Status）：成条首版已落地；下次重载插件后重发 QQ 会话段落。
- 文档边界（Scope / Boundary）：本任务记录；诊断插件不代表完整信息中心已获准实施。

# 当前工作流（Workflow）

- 主线：成条入库首版已落地。下次：重载插件，用宽松标记重发 QQ 会话段落。外层 14 项未开工。
- 最新交接：`handoffs/2026-09-21-006-成条入库首版与QQ会话标记.md`。
- 延期：`deferred/成条与原始资料落盘-首版未做.md`。
- 源码：`backend/src/sourcehub/` + 两个 AstrBot 插件。覆盖 `~/.astrbot/data/plugins/` 再重载。
- 验证：`PYTHONPATH=.:backend/src backend/.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v`
- 不要用 BiliBot 自动回复替代只读采集。不要把 Cookie 发到聊天。
- 恢复：`state.md` → `checkpoints.md` → 006 交接。

