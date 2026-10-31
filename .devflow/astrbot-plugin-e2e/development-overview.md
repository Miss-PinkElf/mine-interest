# AstrBot 插件端到端自动化测试总记录（Development Overview）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 22:29:58 CST。
- 更新时间（Updated At）：2026-10-31 22:55:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：供人类理解本 mission 的完整演进、最终结构、验证证据与开放项；不是默认恢复热路径。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：E2E 引擎与生产启动脚本已完成；NapCat 生产登录待扫码。
- 文档边界（Scope / Boundary）：阶段总览；详细任务以 Plan/spec 为准。

## 背景

用户希望自动测试 AstrBot 插件：专用测试群、专用测试账号、终端启动 AstrBot/NapCat、自动发消息、采集回复与日志、断言是否符合预期，并支持插件重载。

## 最终结构

```text
tools/astrbot_e2e/
├─ config.py / cases.py / assertions.py / reports.py / log_capture.py / onebot.py
├─ bootstrap.py / orchestrator.py / reloader.py / llm_judge.py
├─ runner.py / cli.py
├─ fixtures/astrbot_plugin_e2e_probe/
├─ cases/probe_echo.json, cc_qq_help.json
└─ tests/（106 个测试）
```

运行链路：

1. 独立测试实例 `~/.astrbot-e2e`，WebUI `6186`，反向 OneBot WS `6198`。
2. 测试机器人 `3254276668（17号）` 接入测试实例；测试发送者 `1961618848（C#）` 通过 `6201` 发消息。
3. 观察通道 `6200` 采集机器人回复；`get_group_msg_history(since_time=...)` 兜底。
4. 断言消息与日志；可选 LLM 语义判定。
5. WebUI 登录后用 Bearer token 重载插件；失败时重启测试实例兜底。
6. 报告写入 `tools/astrbot_e2e/reports/`（gitignored）。

## 完成阶段

| 阶段 | 结果 | 证据 |
| --- | --- | --- |
| Align | 5 项决策确认 | `plans/2026-10-27-astrbot-plugin-e2e-align.md` |
| Plan | Task 0–15 | `plans/2026-10-27-astrbot-plugin-e2e-plan.md` |
| Propose/Tasks | proposal/design/tasks | `spec/` |
| Task 0 Spike 0 | 通过 | 双 QQ 双 NapCat、6099/6098、6200/6201、测试群 701292201 双向收发 |
| Task 1–2 | 通过 | 配置 20 测试、用例 13 测试 |
| Task 3–5 | 通过 | 断言 8、报告 6、日志 5 |
| Task 6 | 通过 | OneBot 13 测试 |
| Task 7–9 | 通过 | Bootstrap 6、Orchestrator 6、Reloader 2 |
| Task 10–11 | 通过 | 探针 4、LLM judge 12 |
| Task 12 | 通过 | Runner 9、CLI 2 |
| Task 13 | PASSED | 探针报告 `reports/20261027-222915-643515-case` |
| Task 14 | PASSED | `cc_qq /help` 报告 `reports/20261027-222837-285382-cc_qq-help`；语义 pass，1 条干净回复；增量重载报告 `reports/20261027-223642-572604-case`，返回 `e2e_echo-v2:hello-e2e`，未重启实例 |
| Task 15 | 完成 | 106/106 单测；生产 6199 连接正常；第一版相关文件已提交 |

## 关键决策

- macOS App Sandbox 下 `NAPCAT_WORKDIR` 必须在容器内：`.../QQ/NapCat-e2e`。
- 测试机器人 = 生产 bot `3254276668`；测试发送者 = `1961618848`；测试群 `701292201`。
- 测试实例关闭内置命令，避免与 `cc_qq /help` 叠加。
- Reload 使用登录响应 Bearer token（AstrBot 的 Secure cookie 在 http 下不会回传）。
- LLM judge 使用本机 provider + `x-opencode-session` 头。
- Orchestrator stop/start 等待端口释放，消除非 attach 用例竞态。

## 生产环境启动脚本（2026-10-31）

```text
tools/prod_env/
├─ prod.sh        # start / stop / status
└─ README.md      # 用法、拓扑、边界、FAQ
```

- 生产侧：`~/napcat` 容器 `napcat`（17号，OneBot 13001 / WebUI 16099）+ `~/.astrbot` AstrBot CLI（Dashboard 6185 / 反向 WS 6199）。
- `start` 幂等；`start --restart` 显式重启；默认 iTerm 双标签（NapCat 日志 + AstrBot 前台），关闭 AstrBot 标签即停服务；`start --no-iterm` 当前终端前台；`stop` 停服务并清理窗口/PID。
- 与 E2E 的边界：启动生产前自动停 `napcat-e2e-bot`；成功后清理过期 `production-stopped` 标记；不管理测试发送者与测试 AstrBot。
- 验证：`bash -n`、首次启动、幂等、`--restart` 窗口复用、`stop`、`--no-iterm`、E2E 冲突、超时返回非 0 均通过。
- 环境阻塞：生产 NapCat 需扫码；QQ 返回安全风险 168，`get_login_info` 未返回 17号；需用户手机 QQ 恢复后复测。

## 开放项

- 未决问题：`backlog.md` Q1–Q10（生产 bot 是否长期兼任测试机器人、`6198` 客户端是否保留、测试实例是否常驻、`.gitignore` 是否提交、报告脱敏与保留等）。
- 首版限定：CLI、单发单断言、串行、单群、文本、人工登录、macOS，见 `backlog.md`。
- cc_qq 长任务、审批、多轮对话。
- 富媒体（图片/文件/语音）与 native addon 警告。
- WebUI 页面、CI、并行用例。
- 更深配置/用例形状校验。
- 测试实例生命周期与 `6198` 重试日志的最终策略。
- 生产启动脚本未决项：`restart` 别名与未知命令提示、`--restart --no-iterm` 旧窗口清理、Dashboard `0.0.0.0:6185` 安全收口、手动关闭 NapCat 标签感知，见 `backlog.md` Q18–Q23。
- 生产 NapCat 登录/QQ 安全风险 168：环境侧待用户处理。

## 推荐读取策略

- 日常恢复：`state.md` → `checkpoints.md` → 最新 handoff。
- 生产启动脚本：`tools/prod_env/README.md`、`plans/2026-10-31-生产环境一键启动脚本-plan.md`。
- 未决问题与首版限定：`backlog.md`。
- 理解完整过程：本文件 + `decision-log.md` + `plans/`。
- 延期项：`deferred/2026-10-27-post-mvp-deferred.md`、`deferred/2026-10-31-prod-env-deferred.md`。
