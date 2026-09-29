# Metadata（元数据）

- 更新时间（Updated At）：2026-09-29 11:03:00 +08:00。
- 作者（Author）：Grok。
- 目的（Purpose）：给新对话的可复制恢复提示。
- 关联仓库（Related Repository / Project）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：恢复入口（Resume Prompt）。
- 文档边界（Scope / Boundary）：提示词，不是任务真相源。以 `state.md` 和 012 交接为准。

# 下次对话提示

先读 `.devflow/multi-source-hub/state.md` 和 `checkpoints.md`，再读 `handoffs/2026-09-29-012-告警邮件验收与播放地址.md`。需要完整过程时再读 `development-overview.md`。需要追溯原始输入、旧状态或延期时再读 `origin.md`、`state-history.md`、`backlog.md` 或 `deferred/`。011 只在要核对存量迁移时补读。

不要重做对齐。不要重跑已经完成的 29 条 B 站重排和 184 个 QQ 链接修复。不要再推告警演练。代码 `0fb5a79` 和本轮文档都已提交。

## 先做

1. 重载 AstrBot 里的 **SourceHub B站只读采集**。确认插件卡片和页面标题下都是「插件版本 0.3.2」。目录已经覆盖过，进程还没重载，所以现在打开仍可能看到 `0.3.1`。
2. 登录区应离开「正在读取登录状态」。两个仓库应仍是私有、可读、可推：`Miss-PinkElf/data-hub`、`Miss-PinkElf/sourcehub-alerts`。这三项在 `0.3.1` 上已经由用户确认过，重载后顺手再看一眼即可。

## 已验收

- 故障和恢复邮件。2026-09-29 10:32 的 `events/00000003.md`（`4e2cb32`）和 `events/00000004.md`（`5021d71`），10:35 用户确认两封都收到。T6 已勾选。账号是「尾号 0001」。

## 还没验收

- `0.3.2` 还没有在运行中的插件里看过。T7 因此不勾选。
- 本轮没有新的扫码。QQ 仍无可靠「需扫码」信号。T5 因此不勾选。
- 需求 7 未 Close。需求 4 的验证（Verify）未关。

## 本轮只做了第一版

- 播放地址：已允许的主地址或备用地址优先；否则只把 `/upgcxcode` 的 PCDN 按 `og` 改到官方 upos。不调用 yt-dlp 或 BBDown，不放宽主机白名单，仍是 720P 单文件 mp4。
- 链接卡片：`link_type` 1 写成 `av`，`link_type` 15 写成 `cv`，自带 `link` 的卡片用原文链接。其它类型仍保留 JSON 和 `unknown_paragraph`。

## 本轮暂缓，用户点名再做

- 旧文档里的 PCDN 视频和链接卡片。播放签名大约 120 分钟过期，补救不能只重试已存地址。用户点名后再重采。
- 超过 100MB 的视频。`MEDIA_MAX_BYTES` 本轮没改。
- 未识别的新 `link_type`。不要猜地址。
- `BV1aVjMzeE96` 的超时评论图。
- B 站直连 `ClientConnectorDNSError`。
- 发布日志里的 `remote_private_unverified`。页面校验已经用 `gh`，真正发布闸门仍是匿名接口。

改插件代码后：先改版本号，再整份覆盖到 `~/.astrbot/data/plugins/` 对应目录，然后重载。不要提交 `config.ts`、`.gitignore`、`tsconfig.json`，也不要提交无关的 zip。
