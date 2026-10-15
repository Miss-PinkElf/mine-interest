# Metadata（元数据）

- 更新时间（Updated At）：2026-10-15 22:36:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：记录最近三个检查点。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：QQ 日文档摘要多行截断已修复并部署，待重载验收。
- 文档边界（Scope / Boundary）：本任务记录；诊断插件不代表完整信息中心已获准实施。

# 最近检查点

## 2026-10-15 22:36:00 +08:00：QQ 日文档摘要多行截断已修复，待重载

- 缺陷：日文档「实时消息（Live Messages）」区只留正文最后一行。根因 `sourcehub/vault.py` 的 `append_daily_message` 用 `render_content_md(envelope).splitlines()[-1]` 从整篇 Markdown 抠最后一行。全库复扫仅 2026-10-15 的 `1441885612` 1 条受影响（此前日子都是单行消息，缺陷被掩盖）。
- 修法：`markdown.py` 拆出 `_envelope_header_lines` / `_envelope_body_lines` 并新增 `render_message_body_md`（`render_content_md` 输出保持字节级不变）；`vault.py` 新增 `format_daily_message_entry` 与 `DAILY_MESSAGE_CONTINUATION_INDENT`，多行正文按续行 2 空格缩进。
- 历史订正：按日账本重新投影 2026-10-15 摘要区；备份 `~/.astrbot/data/sourcehub-qq-daily-backup-20261015-223332/`。
- 部署：inspector `0.6.1`、B 站 `0.3.3`；两插件目录已覆盖并 `diff -rq` 复核与仓库一致，`py_compile` 通过。插件目录备份 `~/.astrbot/data/plugin-backup-20261015-223550/`。
- 测试：全量离线 130 项通过（命令须带 `-t .`）。`git diff --check` 本轮改动无空白错误。
- 新增文档：`qq-message-pipeline.md`（QQ 群消息链路说明），并给 `qq-bilibili-capability-boundary.md` 补了文档分工说明。
- 有意覆盖旧结论：旧记录写「不要再重载」，本轮代码改了必须重载才能生效。
- **下一步**：重载两插件 → 群里发一条多行普通消息验证摘要行不丢 → `@机器人 整理` 验证成条 → 询问是否提交代码。

## 2026-09-29 13:56:00 +08:00：收尾前再次核对

- 插件列表、登录接口和仓库状态与 11:12 相同：运行中是 `0.3.2`，已登录且可刷新，两个仓库仍是 10:24 的私有、可读、可推记录。
- 本轮没有改代码、没有重载、没有重采、没有再推告警。最新交接改为 013。
- 下一步仍是用户点名后再重采。T5、T7 和需求 4 的验证（Verify）继续开着。

## 2026-09-29 11:12:00 +08:00：运行中的插件已是 0.3.2

- 插件列表返回 `astrbot_plugin_sourcehub_bilibili` `0.3.2`，已启用。页面标题和「插件版本」都是 `0.3.2`。10:52 的加载日志与此一致，不需要再重载。
- `login/status` 立即返回已登录、可刷新，账号「尾号 4836」。两个仓库的上次校验仍是 10:24：`Miss-PinkElf/data-hub`、`Miss-PinkElf/sourcehub-alerts` 都是私有、可读、可推。
- T5、T7 仍开。下一步是用户点名后再重采一篇旧视频或专栏。没有改代码。
