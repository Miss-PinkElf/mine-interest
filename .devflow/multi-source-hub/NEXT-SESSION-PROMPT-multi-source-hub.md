# Metadata（元数据）

- 更新时间（Updated At）：2026-10-15 23:00:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：给新对话的可复制恢复提示。
- 关联仓库（Related Repository / Project）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：恢复入口（Resume Prompt）。
- 文档边界（Scope / Boundary）：提示词，不是任务真相源。以 `state.md`、`checkpoints.md` 和 014 交接为准。

# 下次对话提示

先读 `.devflow/multi-source-hub/state.md` 和 `.devflow/multi-source-hub/checkpoints.md`，再读 `handoffs/2026-10-15-014-QQ日文档摘要修复与收尾.md`。需要理解 QQ 消息怎么流动时读 `qq-message-pipeline.md`。需要完整过程时再读 `development-overview.md`。需要追溯原始输入、旧状态或延期时再读 `origin.md`、`state-history.md`、`backlog.md` 或 `deferred/`。

不要重做已验收的东西。不要重做 29 条 B 站重排和 184 个 QQ 链接修复。不要再推告警演练。

## 先做（只有一件）

1. 在群里 **@机器人 发「整理」**，然后确认两件事：
   - 生成 `~/.astrbot/data/sourcehub/items/qq/2026-10-15/message/多行测试-836229427-2026-10-15-397313943/`（含 `envelope.json` 与 `content.md`）；
   - 日索引 `items/qq/2026-10-15/content.md` 在「实时消息（Live Messages）」**上方**多出一行 Item 链接，且摘要块**原样保留**。
2. 如果第 1 步通过，本轮切片就可以按 `deferred/QQ日文档摘要首版边界与待验收.md` 收口；不通过的排查入口见 `qq-message-pipeline.md` 第十一节。

## 本轮已经做完（有证据，别重做）

- **代码**：`930e4d5`「修复 QQ 日文档摘要多行截断并补充采集链路说明」，26 个文件。
- **缺陷**：日文档「实时消息」区只留正文最后一行。根因 `sourcehub/vault.py` 的 `append_daily_message` 用了 `render_content_md(envelope).splitlines()[-1]`。全库复扫仅 2026-10-15 的 `1441885612` 1 条受影响。
- **修法**：`markdown.py` 拆出头部与正文，新增 `render_message_body_md`（`render_content_md` 输出字节级不变）；`vault.py` 新增 `format_daily_message_entry` 与续行缩进常量。
- **测试**：全量离线 **130 项通过**。命令必须带 `-t .`：
  `PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'`
  不带 `-t .` 时 `test_sourcehub_vendoring` 会报相对导入错误，那是命令问题不是代码问题。
- **部署与重载**：inspector `0.6.1`、B 站 `0.3.3`，两插件目录与仓库 `diff -rq` 一致。日志证据 `[22:42:28] Plugin astrbot_plugin_sourcehub_inspector (0.6.1)`、`[22:42:30] astrbot_plugin_sourcehub_bilibili (0.3.3)`。
- **真实验证**：重载后消息 `397313943`（多行）在日文档中逐字一致，含连续两个空行。历史条目 `1441885612` 也已按日账本重订正。

## 本轮明确延期与未验收

见 `deferred/QQ日文档摘要首版边界与待验收.md`。要点：

- **`@机器人 整理` 端到端确认未做**——这是唯一还没关的验收项，别当成已完成。
- 延期：成条后清理「实时消息」区、日索引 `content.md` 纳入 Git 提交、超长正文折叠、其它历史日文档重扫。

## 仍然开放的老账（不被本轮关闭）

- **需求 4 的验证（Verify）未关**。
- **需求 7 未 Close**；任务 T5、T7 未勾选。
- 暂缓未变：`remote_private_unverified`（发布闸门仍用匿名接口）、B 站直连 DNS、旧文档重采、超过 100MB 的视频、未识别 `link_type`、`BV1aVjMzeE96`。

## 需要注意的上下文

- **旧记录里的「不要再重载」已被有意覆盖。** 那句是 2026-09-29 版本核对场景的结论；本轮改了代码，必须重载才生效，已执行完毕。下次再改插件代码同样需要重载。
- **`git status` 里三个未提交文件不是本轮的**：`.vscode/controlled-explorer.json`、`zzz-prompt-debug/prompt-1.md`（含一条既有 trailing whitespace）、`zzz-prompt-debug/完整迁移cc-ding/mine-interest-source-hub.code-workspace`（未跟踪）。不要顺手提交，也不要为了 `git diff --check` 干净去改它们。
- **备份位置**：日文档 `~/.astrbot/data/sourcehub-qq-daily-backup-20261015-223332/`；插件目录 `~/.astrbot/data/plugin-backup-20261015-223550/`。
- **敏感边界**：排查时读过真实 Vault 的私人聊天内容，只用于定位，**不写入仓库、不外传**。
- **不要再为 `git diff --check` 的 `zzz-prompt-debug/prompt-1.md` 报警去动那个文件。**

## 建议下次优先

1. 先做上面「先做」的第 1 步（`@机器人 整理` 验收）。
2. 验收通过后，按用户意愿决定是回到需求 4 / 需求 7 的老账，还是继续本切片的延期项。
