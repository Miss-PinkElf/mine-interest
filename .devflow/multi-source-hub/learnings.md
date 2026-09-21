# Metadata（元数据）

- 创建时间（Created At）：2026-09-21 18:38:00 +08:00
- 更新时间（Updated At）：2026-09-21 18:38:00 +08:00
- 作者（Author）：Grok
- 目的（Purpose）：沉淀本轮成条切片的踩坑。
- 关联仓库或项目（Related Repository / Project）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：有效（Active）。
- 文档边界（Scope / Boundary）：经验记录，不是需求真相源。

# 经验

1. AstrBot 把插件当包加载（`data.plugins.<plugin_name>`），插件目录里的 `sourcehub/` 必须用相对导入 `from .sourcehub...`，不能当顶层包。
2. 在 `async` 消息处理里用同步 `urllib` 下图会卡住整个事件循环（本轮约 10 分钟），B 站轮询和后续 QQ 消息一起停。应先 upsert 条目，下载放到 `asyncio.to_thread`。
3. 会话标记不要只做「整句等于中文标点」。手机输入常带空格，或打成英文 `, , ,` / `。 。 。`。匹配前去空白并归一化中英文逗号/句号。
4. 已 complete 的采集档案不会再走 `save()`，新 Vault 必须另做 `export_existing` 回填。
5. `media/` 是哈希库；给人看的是 `items/<id>/content.md`。会话里的嵌套转发按当时规则是子块，不是第二条。
