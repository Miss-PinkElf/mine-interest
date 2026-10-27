# Decision Log

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 16:47:08 CST。
- 更新时间（Updated At）：2026-10-27 22:40:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录当前 mission 的关键决策与尚未批准的候选方向。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：已完成（Completed），第一版收尾并提交。
- 文档边界（Scope / Boundary）：决策真相源（source of truth）；候选建议不等于已批准方案。

## 最新决策

| 时间 | 决策 | 备选方案 | 原因 | 影响 |
| --- | --- | --- | --- | --- |
| 2026-10-27 16:47:08 CST | 新建独立 mission `astrbot-plugin-e2e`，不并入暂停中的 `astrbot-napcat-terminal` | 并入终端联启 mission；复用现有 mission | 本需求目标是插件端到端测试，终端联启只是前置条件；两者验收标准不同 | 后续复用终端联启结论，但独立维护测试目标与延期项 |
| 2026-10-27 16:47:08 CST | 当前只做 Explore / Align，不进入实现 | 直接写测试脚本 | 用户要求先讨论方案；测试账号拓扑、实例隔离与断言渠道尚未确认 | 未确认前不修改插件代码、不启动新实例 |
| 2026-10-27 16:52:00 CST | 首版范围为“通用测试运行器（Runner） + 1 个简单插件用例” | 只测 cc_qq；一次覆盖 3 个插件 | 先用快速命令打通发送、采集、断言、重载闭环，降低长任务与多插件差异带来的调试成本 | 首版不做 cc_qq 长任务全量覆盖；cc_qq 用例进入第二阶段 |
| 2026-10-27 16:54:00 CST | 自动化测试使用独立测试实例（Isolated Test Instance） | 复用当前生产实例；只做设计不动环境 | 避免测试触发真实 Claude/Codex、写入生产会话或打扰真实群；独立数据根、端口与插件数据可重复清理 | 需要初始化 `~/.astrbot-e2e`（候选路径）与单独测试 QQ 登录；当前生产实例保持不动 |
| 2026-10-27 16:57:00 CST | 采用双账号拓扑：测试机器人号接入独立实例，另一个测试发送者号在测试群发消息 | 单账号 + 内部事件注入；人工发送 + Runner 断言 | 最接近真实链路，能覆盖 OneBot 消息段、@ 与群聊/私聊；`cc_qq` 会过滤自身消息，单号无法真实触发 | 需要两个 QQ 号同时在线；具体账号、测试群号与第二号在线方式待确认 |
| 2026-10-27 17:00:00 CST | 断言采用“消息为主、日志为辅 + 可选 LLM 语义判定” | 只读日志；只做硬断言 | 消息是用户实际看到的结果，日志适合补充后台行为；LLM 语义判定用于开放式回复，先作为可选用例字段而非全局开关 | Runner 需要同时采集 OneBot 消息与 AstrBot 日志；用例需要支持 `contains` / `regex` / `semantic` 三类断言 |
| 2026-10-27 17:05:00 CST | 发送方采用“同机双开 QQ”：独立 `--user-data-dir` + 第二个 NapCat 实例 + 独立 OneBot 端口 | Linux 容器/WSL；第二台设备半自动 | 最自动化且不依赖额外机器，发送与接收都在本机可控 | 必须先做技术验证（Spike）：确认 macOS QQ 双开、NapCat 配置隔离、两个 OneBot 端口共存；不可行则回退容器或半自动 |
| 2026-10-27 17:10:00 CST | 首版用例采用“探针插件 + `cc_qq /help`”，目录采用 `tools/astrbot_e2e/` | 只做 `cc_qq /help`；放在 `tests/e2e/` | 探针插件先验证 Runner 自检，真实插件再用快速命令验证；独立目录避免与现有 `tests/` 的引导逻辑耦合 | 首版需要维护一个最小探针插件；Runner 能力与真实插件验证分两步 |
| 2026-10-27 17:10:00 CST | Align 设计稿落盘，等待用户书面审阅 | 直接进入 Plan | brainstorming 门禁要求把设计写成可审阅文档，再进入实施计划 | 设计稿：`plans/2026-10-27-astrbot-plugin-e2e-align.md`；审阅通过后才进入 Plan |
| 2026-10-27 17:38:12 CST | Plan 落盘：`plans/2026-10-27-astrbot-plugin-e2e-plan.md`，共 Task 0–15 | 直接写 spec/tasks；直接实施 | 重型路径要求 Plan 先于 Propose/Tasks；计划已覆盖 Spike 0、Runner、探针、cc_qq、验证与延期项 | 等待用户审阅；通过后进入 Propose/Tasks，未通过前不实施 |
| 2026-10-27 17:38:12 CST | 插件隔离：探针用例禁用 `cc_qq`，`cc_qq` 用例才启用测试群 | 两个插件共用同一启用群 | `cc_qq` 监听群消息，会把 `/e2e_echo` 当普通消息启动 Claude/Codex，污染探针测试 | 每次运行按用例插件重写 `cc_qq` 配置；Runner 停止并重启测试实例，确保配置生效 |
| 2026-10-27 17:41:14 CST | Propose/Tasks 三件套落盘：`spec/proposal.md`、`spec/design.md`、`spec/tasks.md` | 只保留 Plan；跳过三件套直接 Apply | 重型路径实施门禁要求 proposal/design/tasks 齐备；三件套与 Plan 对齐 | 等待用户确认三件套；确认后进入 Apply，从 Task 0 Spike 0 开始 |
| 2026-10-27 17:41:14 CST | Apply 执行方式采用子代理驱动（Subagent-Driven） | 当前会话内联执行 | 16 个任务跨度大，子代理可降低上下文污染，并在任务间审查 | Apply 时每个任务派生子代理，任务完成后再进入下一项 |
| 2026-10-27 18:22:00 CST | Spike 0 通过：同机双开 QQ + 双 NapCat 可行 | Linux 容器/WSL；第二台设备 | 两个 QQ 号同时在线；NapCat `6099/6098`、OneBot `6200/6201` 同时可用；测试群 `701292201` 双向文本收发成功；生产 `6199` 保持连接 | 主方案继续；Runner 按 `6200/6201` 设计；native addon/FFmpeg 警告保留为风险 |
| 2026-10-27 18:22:00 CST | 账号拓扑固定：测试机器人 `3254276668（17号）`，测试发送者 `1961618848（C#）` | 反向分工 | 用户选择；Spike 0 实测通过 | 生产 bot NapCat 增加 `6200` 与 `6198`；测试发送者 NapCat 增加 `6201`；配置已备份 |
| 2026-10-27 18:22:00 CST | `NAPCAT_WORKDIR` 固定在 macOS 容器内 `.../QQ/NapCat-e2e` | `~/.qq-e2e/NapCat` | macOS App Sandbox 拒绝沙盒外写入，报 `EPERM mkdir`；`--no-sandbox` 只关闭 Chromium 沙箱 | 启动脚本与 Plan 已更新；`~/.qq-e2e/NapCat` 废弃 |
| 2026-10-27 18:35:00 CST | Task 1 完成：`tools/astrbot_e2e/` 配置模块与 20 个测试 | 只保留计划中的 5 个测试；跳过复审 | 规格复审通过；质量复审首轮 With fixes，修复后 Ready to merge = Yes；无 Critical/Important | 未提交；Minor 延期项已登记；进入 Task 2 |
| 2026-10-27 21:15:52 CST | Task 2 质量收紧：拒绝空 `messages`/`logs`、要求 `semantic` 为 dict、包装 `OSError`/`UnicodeDecodeError`、`render_case` 缺 `group_id` 抛 `CaseError` | 严格保持原 Plan 的最小校验 | 质量复审认为空断言数组会导致零断言假 PASSED；错误包装避免 Runner 泄漏 traceback | Task 2 测试增至 13 个；更深值形状校验延期到 Task 3/6/12，见 `deferred/2026-10-27-case-validation-deferred.md` |
| 2026-10-27 21:24:11 CST | Task 2 完成：`cases.py` 与 13 个测试，规格/质量复审通过 | 只保留原 Plan 的 3 个测试 | 质量复审修复后 Ready to merge = Yes；空数组收紧与异常包装已验证 | 全量 33/33；未提交；进入 Task 3–5 批量 |
| 2026-10-27 21:24:11 CST | 为加速推进，Task 3–5（断言、报告、日志采集）合并为一个实现批次 | 每个任务单独派实现与复审 | 用户要求连续完成所有任务；三个模块文件互不重叠，合并批次可减少调度开销 | 批次完成后统一规格+质量复审；仍按 TDD 与每模块测试 |
| 2026-10-27 22:22:00 CST | 测试 AstrBot 实例启动于 `6186/6198`，生产 bot 的 `6198` 反向连接打通，探针 E2E PASSED | 复用生产实例 | 独立测试实例隔离；探针用例验证发送、采集、断言、日志与重载 | 报告 `tools/astrbot_e2e/reports/20261027-222247-208754-case` |
| 2026-10-27 22:27:00 CST | 测试实例关闭内置命令；`cc_qq /help` E2E PASSED（含语义判定） | 允许内置 `/help` 叠加 | 内置命令与 `cc_qq` 的 `/help` 会重复回复，证据不干净；关闭后只有被测插件响应 | 报告 `tools/astrbot_e2e/reports/20261027-222837-285382-cc_qq-help`；judge pass |
| 2026-10-27 22:29:00 CST | Orchestrator `stop()/start()` 端口释放竞态修复 | 停止后立即 start 预检 | 旧实例停止后 6186 尚未释放，start 误报占用；改为等待端口释放 | 106/106 单测；非 attach 用例稳定 |
| 2026-10-27 22:29:58 CST | LLM judge 支持自定义 headers，使用本机 provider 的 `x-opencode-session` | 只用 Authorization | 本机 provider 缺该头返回 400；固定 session 实测可用 | 仅本地 `config.local.json`，不入库；judge 真实返回 pass |
| 2026-10-27 22:29:58 CST | 第一版完成：Task 0–15 全部完成；106/106 单测；探针与 `cc_qq` 两条 E2E PASSED | 继续扩展长任务 | 用户要求连续完成所有任务；首版闭环已达成 | 所有改动未提交；延期项与交接已落盘 |
| 2026-10-27 22:36:42 CST | 补做增量重载验证并通过：修改测试实例副本为 `e2e_echo-v2`，`--attach --reload` 后返回 `e2e_echo-v2:hello-e2e`，未重启整个实例 | 只验证 WebUI reload 接口返回成功；跳过 Task 14 Step 4 | 只证明“调用了接口”不足以证明热重载真的加载新代码；前后对比才满足完成定义 | 证据 `reports/20261027-223642-572604-case`；临时 v2 用例与副本已清理；Task 14 闭环 |
| 2026-10-27 22:40:00 CST | 收尾分类：首版限定与明确延期分开记录，未讨论问题集中到 `backlog.md` | 全部塞进 `deferred/`；只写在聊天里 | 用户要求区分“只做第一版”和“后续明确延期”，并记录未讨论问题 | `backlog.md` 记录 Q1–Q10 与首版限定；`deferred/2026-10-27-post-mvp-deferred.md` 记录明确延期 |
| 2026-10-27 22:40:00 CST | 收尾提交范围：mission 文档 + `tools/astrbot_e2e/` + 原始需求文档；不含无关脏文件 | 提交全部工作区；只提交代码 | 用户要求只提交本次对话相关文件；`config.local.json` 含密钥、`reports/` 含敏感证据，均不入库 | 提交时显式排除 `config.local.json`、`reports/`；`.gitignore` 按用户默认要求未提交；未提交 `AGENTS.md`、`.claude/settings.local.json`、`zzz-prompt-debug/接入agent/`、`zzz-prompt-debug/调研bridge/` |
