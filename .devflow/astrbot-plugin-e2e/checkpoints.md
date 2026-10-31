# Checkpoints

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 17:10:00 CST。
- 更新时间（Updated At）：2026-10-31 22:45:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录当前 mission 的阶段检查点，只保留最近 3 条。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：生产环境一键脚本完成并验证；NapCat 生产登录待扫码（QQ 安全风险 168）。
- 文档边界（Scope / Boundary）：恢复热路径的一部分；不替代 `state.md` 或 `handoff`。

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

## 2026-10-30 15:55:00 CST — 需求 2 真机验收与收尾完成

- 阶段：`Verify/Close`（需求 2）。
- 完成：
  - `doctor OK`：bot `3254276668`、sender `1961618848`。
  - 多轮 `/pwd` → `/info` PASSED：`reports/20261030-154828-636210-cc-qq`。
  - 文本 suite 2/2 PASSED：`reports/20261030-154847-882152-astrbot_plugin_cc_qq-suite`；报告脱敏无泄漏。
  - 自愈：未知端口占用只报错不误杀；残留实例自动停止/重启（`reports/20261030-155012-908540-astrbot_plugin_cc_qq-suite`）。
  - 发现并固化：cc-qq `/help` 返回图片卡片，标记 `testability=rich_media`，不自动生成文本用例。
- 当前边界：Task 0–13 完成；引擎 127/127，skill 12/12；未提交。
- 下一步：向用户申请提交许可；未批准前不 commit。
- 已知风险：Q11 富媒体断言；Q12 QQ/NapCat 签名与 App 管理权限；生产 bot 兼任测试机器人。
