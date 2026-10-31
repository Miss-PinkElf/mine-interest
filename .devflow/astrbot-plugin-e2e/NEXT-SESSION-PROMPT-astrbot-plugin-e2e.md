# 下一次对话提示词：astrbot-plugin-e2e

## Metadata（元数据）

- 创建时间（Created At）：2026-10-31 02:31:26 CST。
- 更新时间（Updated At）：2026-11-01 02:30:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：给新对话提供可直接复制的恢复提示，继续 cc-qq 覆盖与 E2E 收尾。
- 关联仓库或项目（Related Repository / Project）：`mine-interest-source-hub`（`.`）。
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：独立测试 bot 切换完成；skill 对齐；cc-qq 多轮与媒体功能 E2E PASSED；存在延期项。
- 文档边界（Scope / Boundary）：恢复提示，不替代 `state.md` / `checkpoints.md` / `handoff`。

## 可复制提示词

继续 `.devflow/astrbot-plugin-e2e/` mission。

先读：
- `.devflow/astrbot-plugin-e2e/state.md`
- `.devflow/astrbot-plugin-e2e/checkpoints.md`
- `.devflow/astrbot-plugin-e2e/handoffs/2026-11-01-005-独立测试账号切换与ccqq媒体验证.md`
- `tools/napcat_e2e/README.md`、`tools/prod_env/README.md`
- 需要完整过程时再读 `development-overview.md`、`decision-log.md`、`deferred/`

### 当前状态（2026-11-01 02:30）

- 账号：测试 bot `3299987672`，发送者 `1961618848`（C#），生产 `3254276668`（17号）。E2E 与生产可并行。
- 测试环境：两个 NapCat 容器运行；测试 AstrBot `6186/6198`（本轮 PID `99530`）；生产 AstrBot `6185/6199` 保持运行。
- 旧 bot 登录态归档：`~/.qq-e2e-docker/bot/QQ.bak-20261101-014847`。
- 验证：`doctor OK`；`cc_qq_multi_turn` PASSED（`reports/20261101-022848-087695-cc-qq`）；回复媒体自动发送 PASSED（`reports/20261101-021808-341659-cc-qq`）。
- 修复：观察端 `reportSelfMessage=true`，解决异步代理回复只抓到「处理中」的假失败。
- Skill：S2 优先 `tools/napcat_e2e/start-all.sh`；生产暂停仅同号时需要；多轮示例为 `/start`。

### 下一步优先级

1. 决定是否把 `/tmp/cc_qq_cases/reply_auto_media.json` 固化到 `tools/astrbot_e2e/cases/manual/`（Q25）。
2. 决定是否增加 `BOT_QQ` / `SENDER_QQ` 与 `config.local.json` 的一致性防呆（Q26 / B12）。
3. 如需完整回归：按 `discover_plugin.py` 的 46 项清单扩展 cc-qq 用例；`/help` 属 rich_media，高风险命令逐条确认。
4. 既有延期：probe/cc-qq 隔离（Q14）、微信/其他平台（Q17）、镜像升级（Q16）、自动扫码（D6）。
5. 生产脚本候选：`restart` 别名（Q18）、`--restart --no-iterm` 旧窗口（Q19）、Dashboard 收口（Q21）、发送者容器（Q22）。

### 常用命令

```bash
cd /Users/mobius/Documents/111AAA-code/mine-interest.worktrees/mine-interest-source-hub

# 状态
bash tools/napcat_e2e/status.sh
bash tools/prod_env/prod.sh status

# 启动 E2E（生产可保持运行）
bash tools/napcat_e2e/start-all.sh
bash tools/napcat_e2e/start-astrbot.sh --detach

# 自检与用例
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor \
  --config tools/astrbot_e2e/config.local.json
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run \
  --attach --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/cc_qq_multi_turn.json
```

### 必须记住的坑

- **改 NapCat 网络配置需重启**：如 `reportSelfMessage`；重启后可能要求重新扫码。
- **陈旧环境变量会覆盖默认账号**：终端残留 `BOT_QQ=3254276668` 会让脚本等待旧号（B12）；用 `env -u BOT_QQ -u SENDER_QQ -u PRODUCTION_QQ` 启动。
- **自动媒体会消费路径文本**：断言用 `images.min=1`，不要同时断言路径文本。
- **异号时 `--stop-production` 会被忽略**：不会停生产；仅同号时才停。
- **生产 AstrBot 是前台标签**：关闭标签会停服务；统一停止用 `prod.sh stop`。
- **AstrBot CLI 按 cwd 判断根目录**：手动 `astrbot run` 先 `cd ~/.astrbot` 或 `~/.astrbot-e2e`。
- **Docker 容器重启用 `docker compose restart`**：不要进容器 `kill` QQ。
- **不要提交** `tools/astrbot_e2e/config.local.json`、`reports/`、`tools/napcat_e2e/.env`、`~/.qq-e2e-docker`。

### 未决与延期

- `backlog.md` Q1–Q27；`deferred/2026-11-01-e2e-account-switch-deferred.md`（cc-qq 全功能覆盖、媒体用例入仓、BOT_QQ 防呆、引擎轮询、probe 隔离、自动扫码、跨平台/镜像）。
- `deferred/2026-10-27-post-mvp-deferred.md`、`deferred/2026-10-31-prod-env-deferred.md`。
- `bug-log.md` B1–B13；`learnings.md` 1–19。

### 恢复读取建议

- 日常恢复：`state.md` → `checkpoints.md` → 最新 handoff（005）。
- 账号/启动：`tools/napcat_e2e/README.md`；生产：`tools/prod_env/README.md`。
- 完整过程：`development-overview.md`、`decision-log.md`、`plans/`。
- 延期：`backlog.md`、`deferred/`、`learnings.md`、`bug-log.md`。
