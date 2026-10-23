# Metadata（元数据）

- 更新时间（Updated At）：2026-10-23 17:20:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：给新对话的可复制恢复提示。
- 关联仓库（Related Repository / Project）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：恢复入口（Resume Prompt）。
- 文档边界（Scope / Boundary）：提示词，不是任务真相源。以 `state.md`、`checkpoints.md`、`spec/2026-10-23-需求8/tasks.md` 和 `spec/2026-10-23-需求9/tasks.md` 为准。

# 下次对话提示

先读 `.devflow/multi-source-hub/state.md`、`checkpoints.md`、`handoffs/2026-10-23-020-本轮收尾与交接.md`；需求 9 读 `plans/2026-10-23-需求9-GitHub-star列表归类-plan.md` 与 `spec/2026-10-23-需求9/tasks.md`；需求 8 读 `spec/2026-10-23-需求8/tasks.md`。需要完整过程时读 `development-overview.md`；溯源时读 `origin.md`、`state-history.md`、`decision-log.md`、`deferred/`。

## 当前进度

- 已部署：检查插件 `0.6.5`、B 站插件 `0.3.7`；现场目录与仓库 `diff -rq` 一致。
- 需求 8：真实 star 成功（`Blinue/Magpie`）；真实 fork 成功（`Miss-PinkElf/Magpie`，默认分支 `dev`，每 6 小时同步工作流已安装）。
- 已修复：`_github_reply` 属性遮蔽、`gh repo fork --remote` 参数、B 站正常流程缺日志。
- 需求 9：`github_star_list` 已实现；只对本次新 star 生效；按名称完全匹配；保留已有其他列表；不匹配回退默认位置。
- 全量离线 **174 项通过**（命令必须带 `-t .`）：
  `PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'`
- 现场配置：owner `1961618848`、admin `2844973553`，`github_enabled=true`，代理 `http://127.0.0.1:7897`；`github_star_list` 尚未填写。
- 代码提交：`b9ef0fc` 为需求 8 首版；本轮修复与需求 9 已在收尾时提交，未推送（提交号见 `git log`）。

## 下一步（按顺序）

1. 重载 AstrBot，确认加载 `astrbot_plugin_sourcehub_inspector (0.6.5)` 与 `astrbot_plugin_sourcehub_bilibili (0.3.7)`；日志应出现 `GitHub 自动化：开`。
2. 需求 9 验证：在两个插件页填写 `github_star_list`（现有列表：自动化日常、AI相关、Useful、Want to Learn）→ 用**尚未 star** 的仓库链接验证「已加入列表」且原其他列表保留。
3. B 站日志验证：在 B 站 @ 机器人，确认出现「收到 N 条 B 站通知」「开始采集 B 站通知」「已保存 B 站条目」。
4. B 站页面：登录区绿色「登录有效」；GitHub 区块「已启用」；Cookie 失效时红色提示。
5. 继续老账：需求 4 Verify、需求 7 Close、需求 8 T7 勾选、`@机器人 整理` 端到端。

## 未讨论 / 只做第一版 / 明确延期

- 同一插件配置多个列表、按来源或链接类型分流：**未讨论**，当前是「每个插件一个列表」。
- 历史已 star 仓库批量归类：本轮明确不做。
- 自动创建不存在的列表、slug/别名/模糊匹配、超过 100 条目的完整分页、列表移除/改名同步：明确延期。
- 需求 8 原有延期：QQ 合并转发内层链接、fork 冲突自动解决、私有上游同步、同步频率配置化。
- 详见 `deferred/需求9-star列表首版边界.md` 与 `deferred/需求8首版边界与待验收.md`。

## 仍然开放的老账

- 需求 4 Verify 未关；需求 7 未 Close；需求 8 T7 未勾选。
- `@机器人 整理` 端到端确认仍未做（来自 014 交接）。
- 暂缓未变：`remote_private_unverified`、B 站直连 DNS、旧文档重采、超过 100MB 的视频、未识别 `link_type`、`BV1aVjMzeE96`。

## 不要做

- 未获用户允许不要 commit 或推送。
- 不要顺手提交 `.claude/settings.local.json`、`.vscode/controlled-explorer.json`、`zzz-prompt-debug/prompt-1.md`、`zzz-prompt-debug/完整迁移cc-ding/*.code-workspace`。
- 不要修改 NapCat、`devflow-handoff.md`（只读）或 B 站/QQ 之外的插件。
- 不要把 QQ 合并转发内层链接纳入 GitHub 自动化；本轮已明确延期。
- 不要用真实仓库做离线测试；离线测试使用假 runner。真实 star/列表验证需用户确认仓库与列表。
