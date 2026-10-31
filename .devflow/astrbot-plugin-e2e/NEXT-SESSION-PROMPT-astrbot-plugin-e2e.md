# 下一次对话提示词：astrbot-plugin-e2e（E2E + 生产环境一键脚本）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-31 02:31:26 CST。
- 更新时间（Updated At）：2026-10-31 22:55:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：给新对话提供可直接复制的恢复提示，继续 E2E 收尾与生产环境一键脚本的登录复测。
- 关联仓库或项目（Related Repository / Project）：`mine-interest-source-hub`（`.`）。
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：生产环境一键脚本已完成并验证；生产 NapCat 已登录就绪；E2E 测试资产待修。
- 文档边界（Scope / Boundary）：恢复提示，不替代 `state.md` / `checkpoints.md` / `handoff`。

## 可复制提示词

继续 `.devflow/astrbot-plugin-e2e/` mission。

先读：
- `.devflow/astrbot-plugin-e2e/state.md`
- `.devflow/astrbot-plugin-e2e/checkpoints.md`
- `.devflow/astrbot-plugin-e2e/handoffs/2026-10-31-004-生产环境一键启动脚本.md`
- `tools/prod_env/README.md`
- 需要理解 E2E 背景时再读 `.devflow/astrbot-plugin-e2e/handoffs/2026-10-31-003-Docker双容器E2E启动脚本.md` 与 `tools/napcat_e2e/README.md`

### 当前状态（2026-10-31 22:55）

- 已新增 `tools/prod_env/`：
  - `prod.sh`：`start` / `stop` / `status`。
  - `start`：幂等启动生产 NapCat（`~/napcat` 容器 `napcat`）+ 生产 AstrBot（`~/.astrbot` CLI）。
  - 默认 iTerm2 一个窗口两个标签：NapCat 日志 + AstrBot 前台；**关闭 AstrBot 标签即停服务**。
  - `start --restart`：显式重启；复用记录的窗口 ID 新增 AstrBot 标签。
  - `start --no-iterm`：不开 iTerm；NapCat 就绪后在当前终端前台运行 AstrBot。
  - `stop`：停 AstrBot + NapCat，关闭窗口，清理 PID/窗口 ID；不碰测试侧。
- 已验证：
  - `bash -n`、首次启动、幂等、`--restart` 窗口复用、`stop`、`--no-iterm`、E2E 冲突自动停、OneBot 超时返回非 0。
  - 生产 AstrBot `6185/6199`、NapCat `13001/16099`；测试 AstrBot `6186/6198`。
- 当前运行态（2026-10-31 22:55）：
  - `napcat` 容器运行且**已登录**（`13001` 监听，`get_login_info` 返回 17号）。
  - 生产 AstrBot 运行：PID `40562`，`6185/6199` 监听。
  - 脚本窗口 `1850` 存在；`napcat-e2e-bot` / `napcat-e2e-sender` 已停；测试 AstrBot 运行；`production-stopped` 标记无。
- 登录历史：首次启动需扫码且 QQ 曾返回安全风险 `168`；用户已处理并扫码，2026-10-31 22:55 复测通过。
- 账号策略（2026-10-31）：生产 QQ 17号 不再改动、不再用于 E2E；用户已新建独立测试 QQ。新账号信息待下次对话确认；当前 E2E 仍按 17号 编写，尚未切换。

### 正确命令（用户曾误用）

```bash
bash tools/prod_env/prod.sh start
bash tools/prod_env/prod.sh start --restart
bash tools/prod_env/prod.sh status
bash tools/prod_env/prod.sh start --no-iterm
bash tools/prod_env/prod.sh stop
```

- `--restart` 是 `start` 的参数，不是独立子命令。
- `status` 不带前导 `--`。
- 未知命令目前只打印 usage；是否加 `restart` 别名与提示见 `backlog.md` Q18。

### 下一步优先级

- **下次对话第一件事**：确认新测试 QQ 的号码、NapCat 配置、OneBot 端口与发送者安排，再改造 E2E；在此之前不要动生产 17号。
1. **生产环境已就绪**：保持运行；日常重启用 `bash tools/prod_env/prod.sh start --restart`。新测试 QQ 接入前，跑 E2E 仍需先停生产，避免 17号 冲突。
2. **修测试资产**：把 `tools/astrbot_e2e/cases/cc_qq_multi_turn.json` 的 `/info` 断言改为包含「当前会话」或匹配「状态」，重跑用例。
3. **隔离 probe 与 cc-qq**：probe 测试使用只加载 `astrbot_plugin_e2e_probe` 的测试根，或在测试群禁用 cc-qq。
4. **决定 UX/安全候选**：`restart` 别名（Q18）、`--restart --no-iterm` 旧窗口（Q19）、Dashboard `0.0.0.0:6185` 收口（Q21）、是否停发送者容器（Q22）。
5. **既有后续**：专用测试 bot 账号（Q13）、Docker 镜像升级（Q16）、微信/其他平台 E2E（Q17）、富媒体断言（Q11）。

### 常用命令

```bash
cd /Users/mobius/Documents/111AAA-code/mine-interest.worktrees/mine-interest-source-hub

# 生产环境
bash tools/prod_env/prod.sh start
bash tools/prod_env/prod.sh start --restart
bash tools/prod_env/prod.sh status
bash tools/prod_env/prod.sh stop

# E2E 环境
bash tools/napcat_e2e/start-all.sh --stop-production --restart --force-tabs
bash tools/napcat_e2e/start-astrbot.sh --restart --detach
bash tools/napcat_e2e/status.sh
bash tools/napcat_e2e/stop-all.sh

# E2E 自检与用例
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor \
  --config tools/astrbot_e2e/config.local.json
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run \
  --attach --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/cc_qq_multi_turn.json
```

### 必须记住的坑

- **子命令在前**：`prod.sh start --restart`，不是 `prod.sh --restart`；`status` 不是 `--status`。
- **生产 17号 不再用于测试**：用户已新建独立测试 QQ；切换前 E2E 仍会和 17号 冲突，接入后生产可与 E2E 并行。
- **同一 QQ 不能双端在线**（切换前）：生产 `napcat` 与 E2E `napcat-e2e-bot` 都是 17号；`prod.sh start` 自动停 E2E 机器人，`start-all.sh --stop-production` 自动停生产容器。
- **生产 AstrBot 是前台标签**：关闭 AstrBot 标签会停服务；`prod.sh stop` 用于标签已关但进程残留或统一停止。
- **先停服务再关窗口**：窗口里有长任务时 `close window` 可能弹确认；脚本先停 AstrBot/容器再关窗口。
- **窗口 ID 复用**：记录在 `~/.astrbot/.prod-iterm-window-id`；窗口被手动关闭时自动新建。手动关单个 NapCat 日志标签无法感知。
- **生产 NapCat 可能需要扫码**：持久登录态不等于免扫码；QQ 安全风险 168 需手机 QQ 处理。
- **AstrBot CLI 按 cwd 判断根目录**：手动 `astrbot run` 先 `cd ~/.astrbot` 或 `~/.astrbot-e2e`。
- **Docker 容器重启用 `docker compose restart`**：不要进容器 `kill` QQ；`docker logs -f` 标签可继续跟随同一容器。
- **iTerm2 3.6.7 应用名是 `iTerm`**：不是 `iTerm2`。
- **不要提交** `tools/astrbot_e2e/config.local.json`、`reports/`、`tools/napcat_e2e/.env`、`~/.qq-e2e-docker`。

### 未决与延期

- `backlog.md` Q1–Q23（新增 Q18–Q23 为生产脚本相关）。
- `deferred/2026-10-31-prod-env-deferred.md`：别名/提示、无 GUI 重启清理、自动扫码、Dashboard 收口、跨平台等。
- `deferred/2026-10-27-post-mvp-deferred.md`：cc_qq 长任务、审批、富媒体、WebUI、CI、并行、自动登录等。
- `bug-log.md` B8–B11：幂等未校验 OneBot、超时返回 0、QQ 168、命令误用。
- `learnings.md` 条目 9–15：生产启动与 iTerm/窗口/PID 经验。

### 恢复读取建议

- 日常恢复：`state.md` → `checkpoints.md` → 最新 handoff（004）。
- 生产脚本：`tools/prod_env/README.md` + `plans/2026-10-31-生产环境一键启动脚本-plan.md`。
- E2E 完整过程：`development-overview.md`、`decision-log.md`、`plans/`、`handoffs/2026-10-31-003-...`。
- 延期与候选：`backlog.md`、`deferred/`、`learnings.md`、`bug-log.md`。
