# Metadata（元数据）

- 更新时间（Updated At）：2026-09-21 18:38:00 +08:00
- 作者（Author）：Grok
- 目的（Purpose）：新对话恢复成条入库之后的工作。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 最新交接（Latest Handoff）：`handoffs/2026-09-21-006-成条入库首版与QQ会话标记.md`。
- 当前状态（Status）：成条首版已落地；QQ 会话段落待用宽松标记重测。
- 文档边界（Scope / Boundary）：恢复入口。005 仍是 B 站采集事实来源。

# 下一次对话提示词

请恢复 `.devflow/multi-source-hub/`。默认先读 `state.md` 与 `checkpoints.md`，再读最新交接：

`.devflow/multi-source-hub/handoffs/2026-09-21-006-成条入库首版与QQ会话标记.md`

延期：`deferred/成条与原始资料落盘-首版未做.md`。

**方向已批准：先成条，再知识整理。判断槽关闭。不要开工外层 14 项。不要用 BiliBot 自动回复替代只读采集。**

## 当前进度

成条入库首版已实现：统一封套、Vault（`~/.astrbot/data/sourcehub/`）、QQ 成条、B 站按作品合并。B 站用户认为没有大问题。QQ 会话标记已放宽（去空白、中英文逗号/句号等价）。

表情包合集已在 `items/qq/session/1693473199/`。第二段「段落测试 / 123 / 喜欢你」因旧标记过严拆成单条，需重载插件后整段重发。

## 建议优先

1. 重载两个 SourceHub 插件，用 `, , ,` 或 `，，，` 重发一段会话并收口。
2. 若用户要 `content.md` 按转发层分组，或会话内转发拆成独立条目，先对齐再改。
3. 不要把 Cookie、真实快照、`sourcehub-image-urls.json` 提交或发到聊天。

## 注意

- 验证：`PYTHONPATH=.:backend/src backend/.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v`
- 源码：`backend/src/sourcehub/` 与两个插件；改完覆盖 `~/.astrbot/data/plugins/` 再重载
- `media/` 是哈希库，条目在 `items/`
