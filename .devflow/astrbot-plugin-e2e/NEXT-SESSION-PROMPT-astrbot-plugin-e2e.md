# 下一次对话提示词：astrbot-plugin-e2e（Docker 双容器 E2E）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-31 02:31:26 CST。
- 更新时间（Updated At）：2026-10-31 02:31:26 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：给新对话提供可直接复制的恢复提示，继续 Docker 双容器 E2E 的收尾与测试资产维护。
- 关联仓库或项目（Related Repository / Project）：`mine-interest-source-hub`（`.`）。
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：Docker 双容器启动脚本已完成并验证；测试资产有 1 条断言待修。
- 文档边界（Scope / Boundary）：恢复提示，不替代 `state.md` / `checkpoints.md` / `handoff`。

## 可复制提示词

继续 `.devflow/astrbot-plugin-e2e/` mission。

先读：
- `.devflow/astrbot-plugin-e2e/state.md`
- `.devflow/astrbot-plugin-e2e/checkpoints.md`
- `.devflow/astrbot-plugin-e2e/handoffs/2026-10-31-003-Docker双容器E2E启动脚本.md`
- `tools/napcat_e2e/README.md`

### 当前状态（2026-10-31）

- 已新增 `tools/napcat_e2e/`：
  - `compose.yaml`：`napcat-e2e-bot`（17号，OneBot 6200）+ `napcat-e2e-sender`（C#，OneBot 6201）。
  - `start-all.sh`：一键启动两个容器 + 测试 AstrBot，打开 iTerm 三标签。
  - `start-bot.sh` / `start-sender.sh` / `start-astrbot.sh` / `stop-all.sh` / `status.sh`。
  - `wait_onebot.py`：启动 AstrBot 前实际校验 `get_login_info`。
  - 支持 `--stop-production`、`--restart`、`--force-tabs`、`--detach`、`--no-iterm`。
- 环境验证：
  - `doctor OK`；测试 AstrBot `6186/6198` 运行；两个 NapCat 容器 Up。
  - `cc_qq_multi_turn` 的 `/pwd` **PASSED**；`/info` 实际回复「当前会话 #5，代理：claude，状态：active。」，但用例仍期望 `/new`（**断言过期**）。
  - `probe_echo` 被 cc-qq 执行回执拦截（测试实例同时加载了 cc-qq 和 probe）。
- 数据与安全：
  - 旧原生 e2e 已归档到 `~/.qq-e2e/archive-20261031/`（权限 700，含真实聊天日志，不外传）。
  - Docker 数据在 `~/.qq-e2e-docker`；测试 AstrBot 数据在 `~/.astrbot-e2e`。
  - 生产容器 `napcat` 当前被 `--stop-production` 停止；恢复用 `stop-all.sh`，不要手动 `docker start napcat`（会抢 17号）。
  - 不要提交 `tools/astrbot_e2e/config.local.json`、`reports/`、`.env`；`.gitignore` 默认不提交。

### 下一步优先级

1. **修测试资产**：把 `tools/astrbot_e2e/cases/cc_qq_multi_turn.json` 的 `/info` 断言改为包含「当前会话」或匹配「状态」，重跑用例。
2. **隔离 probe 与 cc-qq**：probe 测试使用只加载 `astrbot_plugin_e2e_probe` 的测试根，或在测试群禁用 cc-qq。
3. **决定专用测试 bot 账号**：当前 17号 只能生产/E2E 二选一；若需要并行，新增专用测试 bot 与独立适配器。
4. **Docker 镜像升级**：当前镜像 2026-03 / NapCat 4.17.46；升级后重验 `get_rkey`、图片下载、Packet 后端。
5. **微信/其他平台 E2E 驱动**：当前只覆盖 OneBot/NapCat；微信适配器（`weixin_oc`/`wecom`/公众号）没有 OneBot 驱动，需单独 Align。
6. **可选**：自动扫码登录、生产 AstrBot 自动暂停/恢复、CI/并行、富媒体断言。

### 常用命令

```bash
cd /Users/mobius/Documents/111AAA-code/mine-interest.worktrees/mine-interest-source-hub

# 启动/重启
bash tools/napcat_e2e/start-all.sh --stop-production --restart --force-tabs
bash tools/napcat_e2e/start-astrbot.sh --restart --detach

# 状态/停止
bash tools/napcat_e2e/status.sh
bash tools/napcat_e2e/stop-all.sh

# 自检
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor \
  --config tools/astrbot_e2e/config.local.json

# 用例
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run \
  --attach --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/cc_qq_multi_turn.json
```

### 必须记住的坑

- **端口监听 ≠ 账号就绪**：6200/6201 已监听不代表 OneBot WS 稳定；启动 AstrBot 前先用 `wait_onebot.py` 校验 `get_login_info`，失败重试/`--restart`。
- **iTerm2 3.6.7 的 AppleScript 应用名是 `iTerm`**，不是 `iTerm2`；用错会报 `-2741`/`-1728`。
- **AstrBot CLI 根目录按当前工作目录判断**：手动 `astrbot run` 先 `cd ~/.astrbot-e2e`。
- **不要进容器 `kill` QQ**：用 `docker restart` / `docker compose restart`；入口脚本没有守护进程。
- **同一 QQ 不能双端在线**：生产 `napcat` 与 E2E `napcat-e2e-bot` 都是 17号；`--stop-production` 与 `stop-all.sh` 成对使用。
- **关闭终端**：Docker 容器不会停；`--detach` 启动的测试 AstrBot 也不会停；前台模式可能被 SIGHUP 杀掉。

### 恢复读取建议

- 日常恢复：`state.md` → `checkpoints.md` → 最新 handoff。
- 完整过程：`development-overview.md`、`decision-log.md`、`plans/`。
- 延期与候选：`backlog.md`、`deferred/`、`learnings.md`、`bug-log.md`。
- 启动脚本用法：`tools/napcat_e2e/README.md`。
