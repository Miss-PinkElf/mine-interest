# Checkpoints

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 17:10:00 CST。
- 更新时间（Updated At）：2026-11-01 01:55:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录当前 mission 的阶段检查点，只保留最近 3 条。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：独立测试 bot 切换与 skill 对齐完成；cc-qq 多轮与媒体功能 E2E PASSED；进入本轮 Close。
- 文档边界（Scope / Boundary）：恢复热路径的一部分；不替代 `state.md` 或 `handoff`。

## 2026-11-01 01:55:00 CST — E2E 切换独立测试 bot 账号

- 阶段：`Apply`（需求 3，已获用户批准）。
- 账号：测试 bot `3299987672`（独立测试号），发送者仍 `1961618848`（C#）；生产容器 `napcat` 保持 `3254276668`。
- 改动：`tools/napcat_e2e/common.sh` 默认账号与冲突判定；`start-all` / `start-bot` / `start-astrbot` 标签参数化；`tools/prod_env/prod.sh` 仅同号时停 E2E；`config.local.json`、README、skill vendor 同步。
- 验证：`bash -n` 全部脚本通过；`docker compose config` 通过；引擎 127/127、skill 14/14；`print_endpoints` 显示新账号；生产运行时 `check_production_container` 返回 0 并提示可并行；`prod.sh status` 正常。
- 扫码与 smoke：旧登录态归档到 `QQ.bak-20261101-014847`；用户扫码 `3299987672` 后 `doctor` 通过，`cc_qq_multi_turn` PASSED（`reports/20261101-022848-087695-cc-qq`）。
- Skill 对齐：S1/S2/S4/S7 与 safety-rules 适配 Docker + 独立账号；真源、副本与 catalog 哈希同步。
- 异步回复修复：`e2e-observer` 的 `reportSelfMessage=true`；媒体用例 PASSED（`reports/20261101-021808-341659-cc-qq`，14.7 秒，图片数 1），验证 cc-qq 自动媒体发送生效。
- 备注：改 NapCat 网络配置需重启容器，重启后可能要求重新扫码。

## 2026-10-31 22:45:00 CST — 生产环境一键脚本完成

- 新增 `tools/prod_env/prod.sh` + `README.md`：`start/stop/status`；默认 iTerm 双标签（NapCat 日志 + AstrBot 前台），关闭 AstrBot 标签即停服务；`--restart` 复用窗口；`--no-iterm` 当前终端前台。
- 幂等：`start` 在 NapCat 与 AstrBot 都在运行时 no-op；重启显式 `--restart`；启动前自动停 `napcat-e2e-bot`；成功后清理过期 `production-stopped` 标记。
- 验证：`bash -n`；首次启动容器 + `6185/6199` + 双标签；重复 `start` 不新增标签；`--restart` 复用窗口并新增 AstrBot 标签；`stop` 停服务并清 PID/窗口；`--no-iterm` PID 36607 验证；E2E 冲突自动停；OneBot 超时返回非 0。
- 环境阻塞已解除：用户扫码后 `wait_onebot.py` 连接 `13001`，`get_login_info` 返回 17号（exit 0）。
- 当前运行态：生产 AstrBot PID `40562`、窗口 `1850`、`napcat` 已登录；`napcat-e2e-bot` / `napcat-e2e-sender` 已停；测试 AstrBot `6186/6198` 运行；标记已清理。

## 2026-10-31 02:31:26 CST — Docker 双容器 E2E 启动脚本完成

- 新增 `tools/napcat_e2e/`：两个 NapCat 容器（`napcat-e2e-bot` 17号 / `napcat-e2e-sender` C#）+ 测试 AstrBot；`start-all` 打开 iTerm 三标签，另有分开启动、停止、状态脚本。
- 关键修复：`start-astrbot` 先等待 6200/6201，并用 `wait_onebot.py` 调 `get_login_info` 确认账号就绪；`start-instance` 失败重试 3 次；支持 `--detach`、`--restart`、`--force-tabs`；iTerm AppleScript 应用名改为 `iTerm`。
- 验证：`doctor OK`；`/pwd` PASSED；`/info` 实际回复「当前会话 #5，代理：claude，状态：active。」，用例仍期望 `/new`（断言过期）；`probe_echo` 被 cc-qq 回执拦截。
- 收尾：旧原生 e2e 数据归档到 `~/.qq-e2e/archive-20261031/`；生产容器 `napcat` 当前停止，恢复用 `stop-all.sh`。
- 下一步：新会话更新 `/info` 断言、隔离 probe/cc-qq、决定专用测试 bot 账号与 Docker 镜像升级。
