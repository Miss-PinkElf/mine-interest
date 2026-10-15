# Metadata（元数据）

- 更新时间（Updated At）：2026-10-15 22:36:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：记录当前工作路径与下一次验收入口。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38、50–58 行；本轮追加见当日会话。
- 当前状态（Status）：QQ 日文档摘要多行截断已修复并部署，待重载验收。
- 文档边界（Scope / Boundary）：本任务记录；诊断插件不代表完整信息中心已获准实施。

# 当前工作流（Workflow）

- 恢复：先读 `state.md`、`checkpoints.md`，再按其中的指针读取。本轮如需深挖，读 `plans/2026-10-15-QQ日文档摘要多行截断修复与链路说明-plan.md` 与 `qq-message-pipeline.md`。
- 本轮路径：轻量路径（Mini Align → Light Plan → Light Tasks → Apply → Verify → Close）。任务 1–5 已完成，任务 6 停在「重载 + 真实消息复现」与「是否提交」。
- 本轮代码：`backend/src/sourcehub/markdown.py`、`backend/src/sourcehub/vault.py`（各 3 份副本已同步），`tests/test_sourcehub_markdown.py`、`tests/test_sourcehub_vault.py`，两插件版本号。**未 commit。**
- 部署状态：inspector `0.6.1`、B 站 `0.3.3` 已覆盖到 `~/.astrbot/data/plugins/`，与仓库 `diff -rq` 一致；**进程尚未重载**。
- 本轮有意覆盖的旧结论：旧 `state.md` / `NEXT-SESSION-PROMPT` 写「不要再重载」。本轮代码改动必须重载才生效，已改为需要重载。
- 测试命令：`PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'`。**必须带 `-t .`**，否则 `test_sourcehub_vendoring` 会因相对导入报错。当前 130 项通过。
- 恢复热路径之外的旧主线：需求 4 的 Verify 仍未关；需求 7 仍未 Close（T5、T7 未勾选）。这些不被本轮自动关闭。
- 暂缓未变：`remote_private_unverified`（发布闸门仍用匿名接口）、B 站直连 DNS、旧文档重采、超过 100MB 的视频、未识别 `link_type`、`BV1aVjMzeE96`。
- 边界：远端媒体上传与 Git LFS 仍暂缓；现有 Markdown 发布行为不变。外层 14 项不因本轮自动开工。
