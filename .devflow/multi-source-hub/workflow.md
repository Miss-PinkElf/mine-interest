# Metadata（元数据）

- 更新时间（Updated At）：2026-11-01 13:00:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：记录当前工作路径与下一次验收入口。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38、50–67 行；需求 9 来源见 `origin.md`。
- 当前状态（Status）：需求 8 已真实验收；需求 9 缺陷已修复并完成历史补做，待消息链路验证。
- 文档边界（Scope / Boundary）：本任务记录；不代表需求 4 / 需求 7 已关闭。

# 当前工作流（Workflow）

- 恢复：先读 `state.md`、`checkpoints.md`；需求 9 读 `plans/2026-11-01-需求9-fix-star列表mutation返回字段-plan.md`、`plans/2026-10-23-需求9-GitHub-star列表归类-plan.md` 与 `spec/2026-10-23-需求9/tasks.md`；需求 8 过程读 `spec/2026-10-23-需求8/tasks.md`。
- 最近路径：需求 9 缺陷排查（只读定位）→ 方案 A 获批准 → 修复 mutation 与错误处理 → 补回归测试 → 升版本部署 → 补 `user` scope → 历史 5 个仓库一次性补做 → 收尾。
- 本轮代码：`sourcehub/github_actions.py`（三副本）、两个插件的 `constants.py` / `metadata.yaml`、`tests/test_github_actions.py`。
- 部署状态：检查插件 `0.6.6`、B 站 `0.3.8` 已覆盖 `~/.astrbot/data/plugins/`，与仓库 `diff -rq -x __pycache__` 一致；**AstrBot 尚未重载**。
- 代码提交：`23e0bef`（star 列表修复）；此前的需求 8 / 需求 9 首版提交见 `git log`；均未推送。
- 配置：`github_enabled=true`（两插件）；B 站 `github_star_list=bilibili_star`、检查插件 `github_star_list=qq_star`；代理 `http://127.0.0.1:7897`；`gh` 账号 `Miss-PinkElf`，scopes 含 `user`。
- 测试命令：`PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'`。**必须带 `-t .`**，当前 **176 项通过**。
- 恢复热路径之外的旧主线：需求 4 的 Verify 仍未关；需求 7 仍未 Close（T5、T7 未勾选）；QQ「整理」端到端确认仍未做；B 站 @ 日志尚未在真实重载后观察。
- 暂缓未变：`remote_private_unverified`、B 站直连 DNS、旧文档重采、超过 100MB 的视频、未识别 `link_type`、`BV1aVjMzeE96`。
- 本轮边界：QQ 合并转发内层链接不处理；fork 冲突不自动解决；私有上游仓库同步不保证；同步频率固定每 6 小时；star 列表只对本次新 star 生效，历史全量归类仍不做。
