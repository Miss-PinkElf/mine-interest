# Metadata（元数据）

- 更新时间（Updated At）：2026-09-28 18:55:00 +08:00。
- 作者（Author）：Grok。
- 目的（Purpose）：给新对话的可复制恢复提示。
- 关联仓库（Related Repository / Project）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：恢复入口（Resume Prompt）。
- 文档边界（Scope / Boundary）：提示词，不是任务真相源。以 `state.md` 和 011 交接为准。

# 下次对话提示

先读 `.devflow/multi-source-hub/state.md`、`checkpoints.md`，再读 `handoffs/2026-09-28-011-存量迁移告警仓库与扫码页.md`。不要重做对齐，不要重跑已经完成的 29 条 B 站重排和 184 个 QQ 链接修复。

## 先看什么

1. 插件卡片和插件页是否都是 `0.3.1`。页面标题下应有「插件版本 0.3.1」。
2. 登录区是否离开「正在读取登录状态」。本机凭据里已经有刷新令牌。若仍不动，先确认插件没有再次被禁用，并确认页面先加载了 `/api/plugin/page/bridge-sdk.js`。
3. 仓库区应显示 `Miss-PinkElf/data-hub` 与 `Miss-PinkElf/sourcehub-alerts` 都是私有、可读、可推。这是 18:33 的演练结果。

## 还没验收

- 故障和恢复邮件。GitHub 默认不给自己的推送发信。用户打开「包含我自己的更新」之后，再推一轮。没收到邮件不能关 T6。
- 插件页上的扫码还没有被用户确认成功。

## 本轮暂缓

- `BV1aVjMzeE96` 的超时评论图。
- B 站直连 `ClientConnectorDNSError`。
- 发布日志里的 `remote_private_unverified`。页面校验已经用 `gh`，真正发布闸门仍是匿名接口。用户要求先不做。

改插件代码后：先改版本号，再整份覆盖到 `~/.astrbot/data/plugins/` 对应目录，然后重载。不要提交 `config.ts`、`.gitignore`、`tsconfig.json`，也不要提交无关的 zip。
