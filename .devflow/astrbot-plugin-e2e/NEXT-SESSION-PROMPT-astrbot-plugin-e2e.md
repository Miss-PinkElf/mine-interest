继续 `astrbot-plugin-e2e` mission。

第一版已完成并提交：Task 0–15 全部完成，106/106 单测通过，探针、`cc_qq /help`、增量重载三项验证 PASSED。测试 AstrBot 已停止，`6186/6198` 空闲；生产 AstrBot `6199` 与生产 QQ `6099/6200` 正常。

工作目录：
`/Users/mobius/Documents/111AAA-code/mine-interest.worktrees/mine-interest-source-hub`

默认先读：
- `.devflow/astrbot-plugin-e2e/state.md`
- `.devflow/astrbot-plugin-e2e/checkpoints.md`
- `.devflow/astrbot-plugin-e2e/handoffs/2026-10-27-002-第一版完成交接.md`

需要完整过程时再读：
- `.devflow/astrbot-plugin-e2e/development-overview.md`
- `.devflow/astrbot-plugin-e2e/decision-log.md`
- `.devflow/astrbot-plugin-e2e/plans/2026-10-27-astrbot-plugin-e2e-plan.md`

下一步优先从以下选择：
1. 未决问题：`.devflow/astrbot-plugin-e2e/backlog.md` Q1–Q10，优先确认生产 bot 是否长期兼任测试机器人、`6198` 客户端是否保留、测试实例是否常驻、`.gitignore` 两行是否提交、报告脱敏策略。
2. 明确延期：`.devflow/astrbot-plugin-e2e/deferred/2026-10-27-post-mvp-deferred.md`，包括 cc_qq 长任务/审批/多轮、富媒体、WebUI/CI/并行。
3. 若要复跑：
   - 单测：`PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools`
   - 自检：`PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor --config tools/astrbot_e2e/config.local.json`
   - 探针：`PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run --config tools/astrbot_e2e/config.local.json --case tools/astrbot_e2e/cases/probe_echo.json`
   - cc_qq：`PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run --config tools/astrbot_e2e/config.local.json --case tools/astrbot_e2e/cases/cc_qq_help.json`
4. 若要消除 `6198` 重试日志：
   `PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli start-instance --plugin astrbot_plugin_cc_qq --config tools/astrbot_e2e/config.local.json`

注意：
- `tools/astrbot_e2e/config.local.json` 含本地 QQ/Token/LLM key，已在本地 `.gitignore` 忽略，但 `.gitignore` 本身未提交；不要提交该配置或 `reports/`。
- 不要提交无关脏文件（`AGENTS.md`、`.claude/settings.local.json`、`zzz-prompt-debug/接入agent/`、`zzz-prompt-debug/调研bridge/`）。
- 任何新的 commit 先征得用户明确同意。
