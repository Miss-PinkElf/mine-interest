# 当前状态（Current State）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 16:47:08 CST。
- 更新时间（Updated At）：2026-10-31 02:31:26 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：保存当前 mission 的短快照，供下一次恢复使用。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 原始需求（Raw Input）：`zzz-prompt-debug/插件自动化测试验证/prompt-01.md`。
- 当前状态（Status）：Docker 双容器 E2E 启动脚本完成并验证；测试资产有 1 条过期断言待修（Completed / Test Asset Pending）。
- 文档边界（Scope / Boundary）：恢复热路径（Resume Hot Path）真相源；不是实施计划。

## 2026-10-31 收尾快照

- 本会话完成 Docker 双容器 E2E 启动脚本：`tools/napcat_e2e/`（compose + `start-all` / `start-bot` / `start-sender` / `start-astrbot` / `stop-all` / `status` + `wait_onebot.py` + README）。
- 环境验证：`doctor OK`；测试 AstrBot（6186/6198）运行；两个 NapCat 容器 Up；`/pwd` PASSED；`/info` 实际回复正确（「当前会话 #5，代理：claude，状态：active。」），但用例断言仍期望 `/new`。
- 已知问题：`cc_qq_multi_turn` 的 `/info` 断言过期；`probe_echo` 被 cc-qq 执行回执拦截；iTerm AppleScript 已修正为 `tell application "iTerm"`。
- 数据：旧原生 e2e 已归档到 `~/.qq-e2e/archive-20261031/`；Docker 数据在 `~/.qq-e2e-docker`；生产容器 `napcat` 当前被 `--stop-production` 停止，恢复用 `stop-all.sh`。
- 详见 `handoffs/2026-10-31-003-Docker双容器E2E启动脚本.md`。

- Mission：`astrbot-plugin-e2e`（AstrBot 插件端到端自动化测试）。
- 当前阶段（Current Stage）：Docker E2E 启动脚本（First Version）完成；测试 AstrBot 运行中；用例断言待修。
- 当前结论：
  - 单元测试：**106/106 通过**。
  - 探针 E2E：**PASSED**，`tools/astrbot_e2e/reports/20261027-222915-643515-case`。
  - `cc_qq /help` E2E：**PASSED**，`tools/astrbot_e2e/reports/20261027-222837-285382-cc_qq-help`；消息断言 2/2，语义判定 `pass=true`，最终只有 1 条干净回复。
  - 增量重载验证：**PASSED**，`tools/astrbot_e2e/reports/20261027-223642-572604-case`；`--attach --reload` 后探针返回 `e2e_echo-v2:hello-e2e`，未重启整个测试实例。
  - 生产 AstrBot `6199` 连接正常；生产 QQ `6099` 正常；测试发送者 `6098/6201` 正常。
  - 2026-10-29–30 实战：cc-qq `0.2.5` 验收期间测试 AstrBot 常驻运行（PID `31955`，`6186/6198`），生产 NapCat 的 `AstrBot-E2E`（`6198`）已启用，重试日志消失；测试期间暂停生产 AstrBot 避免干扰，测完恢复（PID `61792`）。
  - 新增本地一键脚本 `~/.qq-e2e/start-e2e.sh`：iTerm2 单窗口三标签（生产 QQ / 测试 QQ / 测试 AstrBot），自动启用 6198、幂等启停测试实例；不入库。
  - 2026-10-31 新增 Docker 版启动脚本 `tools/napcat_e2e/`：两个 NapCat 容器（`napcat-e2e-bot` / `napcat-e2e-sender`）+ 测试 AstrBot；一键 `start-all.sh` 打开 iTerm2 三标签，另有 `start-bot.sh` / `start-sender.sh` / `start-astrbot.sh` / `stop-all.sh` / `status.sh`。计划见 `plans/2026-10-31-Docker双容器E2E启动脚本-plan.md`，用法见 `tools/napcat_e2e/README.md`。已通过 `bash -n` 与 `docker compose config`；尚未实际启动（需扫码并处理 17号 生产容器冲突）。
  - 2026-10-31 脚本修正：`start-astrbot.sh` 先等待 `6200/6201` 再调用 `start-instance`（否则 NapCat 未登录时 CLI 会报「测试实例未就绪 / Cannot connect to 6200」）；新增 `--detach` 后台启动与启动锁；`start-all.sh` 新增 `--force-tabs`、`--restart`、重复执行保护、iTerm 标签颜色/徽章/标题。已通过 `bash -n`。
  - 2026-10-31 02:15 验证：Docker 双容器已启动并登录（17号 / C#），测试 AstrBot 启动成功（PID `42265`，6186/6198），`doctor OK`，`aiocqhttp(Test-E2E) 适配器已连接`。`probe_echo` 失败的原因是同一测试群内 `astrbot_plugin_cc_qq` 先回执行回执，不是链路故障；探针测试需只加载 probe 或在测试群禁用 cc-qq。`start-instance` 已加入 3 次重试（间隔 3 秒）应对 NapCat 重启瞬断。
  - 2026-10-31 02:35 新增 `tools/napcat_e2e/wait_onebot.py`：AstrBot 启动前的就绪探测从「端口监听」升级为「连接 OneBot 并校验 `get_login_info` 的 user_id」；`start-astrbot.sh` 等账号真正就绪后再调用 `start-instance`，并保留 3 次重试。`tools/napcat_e2e/README.md` 补充「如何生成/首次部署」与 FAQ（单容器/双容器、`Server disconnected`、probe 与 cc-qq、重复执行、终端关闭、端口冲突等）。
  - 2026-10-31 02:45 修复 `start-all.sh` 的 iTerm AppleScript：iTerm2 3.6.7 的脚本应用名是 `iTerm`，使用 `iTerm2` 会报 `-2741`/`-1728` 且不弹终端；已改为 `tell application "iTerm"`，AppleScript 编译通过，并实际打开三标签验证。
  - 2026-10-31 02:29 验证：`doctor OK`；`cc_qq_multi_turn` 第 1 步 `/pwd` **PASSED**（工作目录、角色、权限档、代理均正确），第 2 步 `/info` 实际回复「当前会话 #5，代理：claude，状态：active。」，但用例仍断言包含 `/new`，属于**用例断言过期**，不是插件/链路故障。`probe_echo` 仍被 cc-qq 的执行回执拦截。待用户确认后更新用例断言或调整 probe 测试实例。
  - 2026-10-31 旧原生 e2e 数据已归档到 `~/.qq-e2e/archive-20261031/`（`production-qq.log`、`qq-e2e.log`、`NapCat-e2e`，权限 `700`；含真实聊天日志，不外传）；保留 `~/.qq-e2e/start-*.sh` 作回退参考，保留 `~/.astrbot-e2e` 与 `~/napcat`。Docker 运行数据在 `~/.qq-e2e-docker`。
  - 2026-10-30 14:02 只读检查：`6186/6198`、`6185/6199`、`6098/6099/6200/6201` 均无监听，`ps` 无 AstrBot/NapCat 进程；当前所有服务均已停止，需要时用 `~/.qq-e2e/start-e2e.sh` 或 `start-instance` 拉起。
  - 第一版相关文件已提交：`.devflow/astrbot-plugin-e2e/`、`tools/astrbot_e2e/`（不含 `config.local.json` 与 `reports/`）、原始需求文档。
  - `.gitignore` 本地已追加忽略规则，但按收尾约定**未提交**；提交时已显式排除 `config.local.json` 与 `reports/`。
  - 需求 2（通用测试 skill）已完成 Align：`plans/2026-10-30-通用插件测试skill-align.md`；9 项关键决策已记录。
  - 需求 2 Plan 已落盘：`plans/2026-10-30-通用插件测试skill-plan.md`；Task 0–13、95 个步骤。
  - 需求 2 spec 三件套已落盘：`spec/proposal.md`、`spec/design.md`、`spec/tasks.md`；第一版 spec 已归档到 `spec/archive/2026-10-27-v1/`。
  - 需求 2 Apply：Task 0–11 已完成并复核；引擎全量 **127/127**；skill 脚本测试全部通过；vendor 快照与仓库副本一致；catalog dry-run 无 WARN/COPY-MISS。
  - Task 12 阻塞：本机 QQ 应用签名/quarantine 问题导致 QQ 无法启动。排查中发现 `codesign --force --deep --sign -` 会破坏 QQ 7.0.2 的 nested Helper 签名，Worker 被 `SIGKILL (Code Signature Invalid)`；不要再对 NapCat 注入后的 QQ 使用 `--deep`。用户决定自行还原 QQ 环境。
  - Task 12 已验收（2026-10-30）：`doctor OK`；多轮 `/pwd` → `/info` PASSED（`reports/20261030-154828-636210-cc-qq`）；文本 suite 2/2 PASSED（`reports/20261030-154847-882152-astrbot_plugin_cc_qq-suite`）；报告脱敏无泄漏；端口占用不误杀、残留实例自动停止/重启（`reports/20261030-155012-908540-astrbot_plugin_cc_qq-suite`）。
  - 已知限制：cc-qq `/help` 返回图片帮助卡片，首版文本断言无法验证；已约定标记 `testability=rich_media` 并跳过自动用例（`backlog.md` Q11）。
  - 当前未提交：所有 Task 0–13 的代码与文档改动仍在工作区；本仓库与 person-config 均未 commit。（2026-10-31 收尾提交仅包含本轮 Docker E2E 脚本与相关文档，见 `handoffs/2026-10-31-003-...`。）
- 残留风险：
  - NapCat native addon / FFmpeg / PacketBackend 警告存在；文本链路已验证，富媒体未验证。
  - 两个 QQ 实例共享同一个 macOS 容器，只隔离 NapCat 工作目录与端口。
  - 测试实例关闭内置命令，避免与 `cc_qq` 的 `/help` 叠加。
  - 生产 bot 继续兼任测试机器人，测试群流量会进入生产 bot。
- 未决问题：`backlog.md`（Q1–Q17），包括生产 bot 是否长期兼任测试机器人、`6198` 客户端是否保留、测试实例是否常驻、`.gitignore` 是否提交、报告脱敏与保留策略、Docker 双容器/专用测试账号等。
- 延期项：`deferred/2026-10-27-post-mvp-deferred.md`（cc_qq 长任务、审批、多轮、富媒体、WebUI、CI、并行、更深校验、自动登录等）。
- **本轮新增延期 / 未讨论（2026-10-31）**：
  - **专用测试 bot 账号（Deferred）**：当前 17号 只能“生产或 E2E”二选一；测试时用 `--stop-production` 停生产容器。原因：同一 QQ 不能双端在线。触发条件：需要生产与 E2E 并行时，新增专用测试 bot 账号并单独适配器。
  - **微信/其他平台 E2E 驱动（Deferred）**：当前只覆盖 OneBot/NapCat；微信适配器（`weixin_oc`/`wecom`/公众号）没有 OneBot 驱动，需要单独 Align。触发条件：确定微信渠道后。
  - **probe 与 cc-qq 隔离（Deferred）**：测试实例同时加载两个插件时，cc-qq 会先回执行回执，探针命令被拦截。触发条件：需要跑 probe 基础设施用例时，使用 probe-only 测试根或测试群禁用 cc-qq。
  - **`cc_qq_multi_turn` `/info` 断言（待修）**：实际回复「当前会话 #N…状态」，用例仍期望 `/new`；属于用例过期，需改为包含「当前会话」或匹配「状态」。
  - **Docker 镜像升级（Deferred）**：本地镜像 2026-03 构建 / NapCat 4.17.46；升级后需重新验证 `get_rkey`、图片下载、Packet 后端。触发条件：镜像更新或 QQ 协议变更。
  - **自动扫码登录、生产 AstrBot 自动暂停/恢复（Deferred）**：当前人工扫码、人工停生产；触发条件：高频回归或无人值守。
- 下一步：
  1. 本次收尾：提交本轮 Docker E2E 脚本与文档（`tools/napcat_e2e/`、`.devflow/astrbot-plugin-e2e/`、相关 multi-source-hub 文档）。
  2. 新会话优先：更新 `cc_qq_multi_turn.json` 的 `/info` 断言并复跑；隔离 probe 与 cc-qq。
  3. 决策：专用测试 bot 账号 / 生产与 E2E 并存；Docker 镜像升级；微信/其他平台驱动。
  4. 复跑：先 `doctor`，再用 `--attach` 跑用例；测试实例用 `start-astrbot.sh --detach`，停止用 `stop-all.sh`。
- 交接：
  - `handoffs/2026-10-27-002-第一版完成交接.md`
  - `handoffs/2026-10-31-003-Docker双容器E2E启动脚本.md`
  - `NEXT-SESSION-PROMPT-astrbot-plugin-e2e.md`
