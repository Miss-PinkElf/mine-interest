# Metadata（元数据）

- 更新时间（Updated At）：2026-10-23 17:20:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：记录当前工作路径与下一次验收入口。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38、50–67 行；需求 9 来源见 `origin.md`。
- 当前状态（Status）：需求 8 已真实验收；需求 9 已部署，待真实列表归属验证。
- 文档边界（Scope / Boundary）：本任务记录；不代表需求 4 / 需求 7 已关闭。

# 当前工作流（Workflow）

- 恢复：先读 `state.md`、`checkpoints.md`；需求 9 读 `plans/2026-10-23-需求9-GitHub-star列表归类-plan.md` 与 `spec/2026-10-23-需求9/tasks.md`；需求 8 过程读 `spec/2026-10-23-需求8/tasks.md`。
- 本轮路径：需求 8 走 Verify/Close；其间发现 3 个缺陷并走轻量修复；需求 9 走 Mini Align → Light Plan → Apply → Verify（待真实验证）。
- 本轮代码：共享库 `sourcehub/github_actions.py`（star 列表、fork 参数）、检查插件 `main.py`、B 站插件 `main.py` / `poller.py`；新增 `tests/test_sourcehub_plugin_names.py`、`tests/test_bilibili_github_logging.py`，扩展 `tests/test_github_actions.py`。三份共享库字节一致。
- 部署状态：检查插件 `0.6.5`、B 站 `0.3.7` 已覆盖 `~/.astrbot/data/plugins/`，与仓库 `diff -rq` 一致；用户已重载到 `0.6.4` / `0.3.5` 之外的版本需再次重载确认。
- 代码提交：`b9ef0fc` 为需求 8 首版；本轮修复与需求 9 在收尾时提交。
- 配置：`github_enabled=true`（两插件）、owner `1961618848`、admin `2844973553`、代理 `http://127.0.0.1:7897`；`github_star_list` 尚未填写。备份在 `~/.astrbot/data/plugin-backup-20261023-112324/`。
- 测试命令：`PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'`。**必须带 `-t .`**，当前 174 项通过。
- 恢复热路径之外的旧主线：需求 4 的 Verify 仍未关；需求 7 仍未 Close（T5、T7 未勾选）；QQ「整理」端到端确认仍未做；B 站 @ 日志尚未在真实重载后观察。
- 暂缓未变：`remote_private_unverified`、B 站直连 DNS、旧文档重采、超过 100MB 的视频、未识别 `link_type`、`BV1aVjMzeE96`。
- 本轮边界：QQ 合并转发内层链接不处理；fork 冲突不自动解决；私有上游仓库同步不保证；同步频率固定每 6 小时；star 列表只对本次新 star 生效，不迁移历史 star。
