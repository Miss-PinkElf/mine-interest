# Metadata（元数据）

- 更新时间（Updated At）：2026-10-23 12:00:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：记录最近三个检查点。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：需求 8 已实施并部署，待重载与真实链接验收。
- 文档边界（Scope / Boundary）：本任务记录；不代表真实 star/fork 已发生。

# 最近检查点

## 2026-10-23 12:00:00 +08:00：需求 8 已实施并部署，待重载

- 新能力：GitHub 链接自动 star；有权限的 QQ 与 B 站触发评论 `/fork` 自动 fork；fork 内安装 Actions，每 6 小时只合并默认分支；直连失败回退 7897 代理；QQ 成功/失败回复；B 站页面实时显示 Cookie 是否失效。
- 代码：共享库新增 `github_links.py`、`github_actions.py`；B 站 `0.3.4`、检查插件 `0.6.2`。两插件目录已覆盖并 `diff -rq` 一致。
- 测试：全量离线 **160 项通过**；真实 `gh api user` 直连返回 `Miss-PinkElf`；真实 B 站 Cookie 检查返回 `healthy`。
- 配置：现场新增键已写入，`github_enabled=false`；owner `1961618848`、admin `2844973553`。
- 备份：`~/.astrbot/data/plugin-backup-20261023-112324/`。
- 代码提交：`b9ef0fc`（未推送）。
- **下一步**：用户重载插件 → 打开 B 站插件页确认 Cookie 与 GitHub 区块 → 打开 `github_enabled` 后用真实链接验收。代码已提交 `b9ef0fc`；验收发现问题再另开修复切片。

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
