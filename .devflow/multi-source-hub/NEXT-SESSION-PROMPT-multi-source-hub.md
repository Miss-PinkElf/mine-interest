# Metadata（元数据）

- 更新时间（Updated At）：2026-10-23 11:50:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：给新对话的可复制恢复提示。
- 关联仓库（Related Repository / Project）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：恢复入口（Resume Prompt）。
- 文档边界（Scope / Boundary）：提示词，不是任务真相源。以 `state.md`、`checkpoints.md` 和 `spec/2026-10-23-需求8/tasks.md` 为准。

# 下次对话提示

先读 `.devflow/multi-source-hub/state.md`、`checkpoints.md`、`plans/2026-10-23-需求8-GitHub链接自动star-fork与Cookie提醒-plan.md` 和 `spec/2026-10-23-需求8/tasks.md`。需要理解 QQ 消息链路时读 `qq-message-pipeline.md`；需要完整过程时再读 `development-overview.md`。溯源时再读 `origin.md`、`state-history.md`、`decision-log.md`、`deferred/`。

## 当前进度（需求 8）

- 已实施并部署：检查插件 `0.6.2`、B 站插件 `0.3.4`；两插件目录与仓库 `diff -rq` 一致。
- 全量离线 **160 项通过**（命令必须带 `-t .`）：
  `PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'`
- 真实只读验证：`gh api user` 直连返回 `Miss-PinkElf`；B 站 `login/status` 真实返回 `healthy`，账号尾号 4836。
- 现场配置已加键：owner `1961618848`、admin `2844973553`，`github_enabled=false`，代理 `http://127.0.0.1:7897`。
- 备份：`~/.astrbot/data/plugin-backup-20261023-112324/`。
- 代码提交：`b9ef0fc`「实现需求8 GitHub 链接自动 star/fork 与 Cookie 失效提醒」，未推送；收尾文档见同一分支后续提交。

## 下一步（按顺序）

1. 启动/重载 AstrBot，确认日志加载 `astrbot_plugin_sourcehub_inspector (0.6.2)` 与 `astrbot_plugin_sourcehub_bilibili (0.3.4)`；插件日志应出现 `GitHub 自动化：关`（当前是预期状态）。
2. 打开 B 站插件页：
   - 登录区应显示绿色「登录有效」与校验时间；
   - 「GitHub 自动化」区块应显示「未启用」；
   - 若 Cookie 失效应显示红色「Cookie 已失效，请重新扫码登录」。
3. 验收 GitHub 自动化（会产生真实副作用）：
   - 打开 B 站或检查插件的 `github_enabled`，保存并重载；
   - 用 owner/admin QQ 发一条含 GitHub 仓库链接的消息，预期自动 star 并回复；
   - 发 `/fork`，预期创建 fork 并安装 `.github/workflows/sourcehub-fork-sync.yml`，回复安装结果；
   - 在 fork 的 Actions 页面确认工作流已启用；工作流每 6 小时只合并默认分支。
4. 真实链接验收发现问题时，另开修复切片；代码已提交 `b9ef0fc`，不需要重复提交。

## 仍然开放的老账

- 需求 4 Verify 未关；需求 7 未 Close；T5、T7 未勾选。
- `@机器人 整理` 端到端确认仍未做（来自 014 交接）。
- 暂缓未变：`remote_private_unverified`、B 站直连 DNS、旧文档重采、超过 100MB 的视频、未识别 `link_type`、`BV1aVjMzeE96`。

## 不要做

- 未获用户允许不要 commit 或推送。
- 不要顺手提交 `.vscode/controlled-explorer.json`、`zzz-prompt-debug/prompt-1.md`、`zzz-prompt-debug/完整迁移cc-ding/*.code-workspace`。
- 不要修改 NapCat、`devflow-handoff.md`（只读）或 B 站/QQ 之外的插件。
- 不要把 QQ 合并转发内层链接纳入 GitHub 自动化；本轮已明确延期。
- 不要用真实仓库做测试；离线测试使用假 runner。
