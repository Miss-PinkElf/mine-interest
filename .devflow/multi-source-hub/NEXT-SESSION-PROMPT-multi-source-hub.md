# Metadata（元数据）

- 更新时间（Updated At）：2026-09-28 17:10:00 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：为新对话提供需求 7 和需求 4 的短恢复入口。
- 关联仓库或项目（Related Repository / Project）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38、50–58 行。
- 最新交接（Latest Handoff）：`handoffs/2026-09-28-010-需求7首版代码与真实验收待续.md`。
- 当前状态（Status）：需求 7 首版代码完成、真实 Apply/Verify 待续；需求 4 Verify 待续。
- 文档边界（Scope / Boundary）：恢复提示，不把尚未验收的功能视为已完成，不自动授权扩大范围。

# 下一次对话提示词

请恢复 `.devflow/multi-source-hub/`。先读 `state.md` 与 `checkpoints.md`，再读 `handoffs/2026-09-28-010-需求7首版代码与真实验收待续.md` 和 `spec/2026-09-28-需求7/tasks.md`。需求 7 已完成 Align、两份 Plan、Spec、首版代码及独立审查；114 项单测、编译、共享库一致性与差异检查通过。不要重做已批准的对齐或把离线测试写成真实验收。

## 优先续做

1. B 站存量排版：先确认 AstrBot 已停采，再运行 `tools/preview_bilibili_rerender.py` 只读预演；备份后显式 `--apply`，本机代理参数可用 `--proxy http://127.0.0.1:7897`，但先确认代理仍可用。上一轮只读结果为 30 条记录、20 个作品、19 条媒体缺口及 19 条视频待补封面；真实 Vault 尚未改写，数字需重测。验收视频、专栏、动态、封面、评论图片及所有本地链接；失败则按工具备份审慎恢复。
2. B 站独立登录和 GitHub 提醒：新增依赖尚未在 AstrBot Python 环境安装；真实扫码/刷新未做。`gh` 当时凭据无效，专用私有告警仓库 SSH 地址、通知设置和收件邮件均未验收。取得仓库与有效认证后，部署两插件，实测故障和恢复各一次邮件。QQ 目前只有可靠在线/断线探针，未确认独立“需扫码”信号；不能以无消息或网络错误推断登录失效。
3. 需求 4 Verify：旧 QQ 条目 184 个本地媒体链接少一层 `../`；B 站直连 `ClientConnectorDNSError` 原因、既有 Markdown 发布间歇 `remote_private_unverified`、新 QQ/B 站样本稳定性仍待处理。读 `bug-log.md` 和 `spec/2026-09-23-需求4/tasks.md`，不要把需求 7 的本机代理试取当成需求 4 网络问题完全解决。

## 首版、延期与提交边界

- 需求 7 明确延期与待验收分别列在 `deferred/需求7首版边界与真实验收.md`。生成的 `content.md` 手工编辑合并本轮不做；原始排版不使用 LLM 猜标题。外部停机心跳、其他提醒渠道和远端媒体上传留待用户触发后续阶段，均非永久放弃。
- 不要提交 Cookie、二维码、真实快照、媒体、ZIP 或 `sourcehub-image-urls.json`。上一轮暂存区还有其他会话的候选媒体计划、会话记录及 `zzz-prompt-debug/prompt-1.md` 改动；只按明确范围处理，不批量提交。
- 根目录 `devflow-handoff.md` 是只读收尾指导。需要完整开发过程时读 `development-overview.md`；追溯原始输入、旧状态或更多延期项时再读 `origin.md`、`state-history.md`、`backlog.md`、`deferred/`。
