# Metadata（元数据）

- 更新时间（Updated At）：2026-10-23 12:00:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：提供当前 mission 的短恢复入口。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38、50–67 行。
- 最新计划（Latest Plan）：`plans/2026-10-23-需求8-GitHub链接自动star-fork与Cookie提醒-plan.md`。
- 轻量任务（Light Tasks）：`spec/2026-10-23-需求8/tasks.md`。
- 最新交接（Latest Handoff）：`handoffs/2026-10-23-015-需求8已部署待验收.md`。
- 当前状态（Status）：需求 8 已实施并部署（inspector `0.6.2`、B 站 `0.3.4`），**待重载与真实链接验收**。`github_enabled` 仍关闭。
- 文档边界（Scope / Boundary）：本任务记录；不代表需求 4 / 需求 7 已关闭。

# 当前状态（2026-10-23 轮）

- 路径：轻量路径（Mini Align → Light Plan → Apply），T1–T6 完成，T7 待重载验收。
- 新能力：采集内容里的 GitHub 仓库链接自动 star；有权限的 QQ 发送 `/fork` 时 fork；B 站触发评论含 `/fork` 时 fork。fork 内安装 GitHub Actions，只同步默认分支，每 6 小时用 `git merge` 合并上游。
- 代理：`gh` 直连失败且属于网络错误时，用 `http://127.0.0.1:7897` 重试一次；权限/未登录不重试，提示 `gh auth status`。
- QQ：落点在检查插件；owner `1961618848`、admin `2844973553`，成功/失败都回复；私聊与群聊都按账号权限判断。
- B 站：`login/status` 改为实时校验，返回 `valid/status/message/checked_at`；页面红色提示 Cookie 失效，网络未知不误报。页面新增 GitHub 自动化最近动作。
- 测试：全量离线 **160 项通过**（命令须带 `-t .`）。真实只读验证：`gh api user` 返回 `Miss-PinkElf`，直连成功；真实 B 站 Cookie 检查返回 `healthy`。
- 部署：两插件目录与仓库 `diff -rq` 一致；现场配置已加新键，`github_enabled=false`；备份在 `~/.astrbot/data/plugin-backup-20261023-112324/`。AstrBot 当前未运行，尚未加载本轮版本。
- 代码提交：`b9ef0fc`「实现需求8 GitHub 链接自动 star/fork 与 Cookie 失效提醒」，未推送。收尾文档见同一分支后续提交。
- `prompt-1.md`、`.vscode/controlled-explorer.json` 与 `.code-workspace` 三个既有未提交文件不属于本轮，未纳入提交。

## 本轮不做 / 后续阶段（Deferred Scope）

- QQ 合并转发内部消息里的链接不处理；只处理发送者本条正文。
- fork 与上游冲突时不自动解决；Actions 失败并通知仓库所有者。
- 私有上游仓库的 fork 同步不在首版保证范围。
- 同步频率固定每 6 小时，暂不配置化。
- 需求 4 Verify、需求 7 Close、T5/T7 仍未关闭。
