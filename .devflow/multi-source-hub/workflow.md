# Metadata（元数据）

- 更新时间（Updated At）：2026-10-23 12:00:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：记录当前工作路径与下一次验收入口。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38、50–67 行；本轮追加见当日会话。
- 当前状态（Status）：需求 8 已实施并部署，待重载与真实链接验收。
- 文档边界（Scope / Boundary）：本任务记录；不代表真实 star/fork 已发生。

# 当前工作流（Workflow）

- 恢复：先读 `state.md`、`checkpoints.md`，再按其中的指针读取。本轮深挖读 `plans/2026-10-23-需求8-GitHub链接自动star-fork与Cookie提醒-plan.md`、`spec/2026-10-23-需求8/tasks.md`。
- 本轮路径：轻量路径（Mini Align → Light Plan → Light Tasks → Apply → Verify → Close）。T1–T6 完成，T7 停在「重载 + 页面/真实链接验收」。
- 本轮代码：共享库 `sourcehub/github_links.py`、`sourcehub/github_actions.py`；B 站插件 `login_view.py`、`poller.py`、`webui.py`、`main.py`、页面与配置；检查插件 `github_gate.py`、`main.py`、配置；新增 4 个测试文件。三份共享库已同步。
- 部署状态：inspector `0.6.2`、B 站 `0.3.4` 已覆盖到 `~/.astrbot/data/plugins/`，与仓库 `diff -rq` 一致；**AstrBot 当前未运行，尚未加载本轮版本**。
- 代码提交：`b9ef0fc`「实现需求8 GitHub 链接自动 star/fork 与 Cookie 失效提醒」，未推送。
- 配置：现场已写入 `github_enabled=false`、owner `1961618848`、admin `2844973553`、代理 `http://127.0.0.1:7897`。备份在 `~/.astrbot/data/plugin-backup-20261023-112324/`。
- 测试命令：`PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'`。**必须带 `-t .`**，当前 160 项通过。
- 恢复热路径之外的旧主线：需求 4 的 Verify 仍未关；需求 7 仍未 Close（T5、T7 未勾选）；QQ「整理」端到端确认仍未做。
- 暂缓未变：`remote_private_unverified`、B 站直连 DNS、旧文档重采、超过 100MB 的视频、未识别 `link_type`、`BV1aVjMzeE96`。
- 本轮边界：QQ 合并转发内层链接不处理；fork 冲突不自动解决；私有上游仓库同步不保证；同步频率固定每 6 小时。
