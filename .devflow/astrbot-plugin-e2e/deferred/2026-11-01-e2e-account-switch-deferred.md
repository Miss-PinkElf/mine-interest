# 独立测试账号切换后的延期项（Deferred）

## Metadata（元数据）

- 创建时间（Created At）：2026-11-01 02:30:00 CST。
- 更新时间（Updated At）：2026-11-01 02:30:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录独立测试 bot 切换、skill 对齐与 cc-qq 媒体验证后，本轮明确不做但后续需要继续的事项。
- 关联仓库或项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：延期（Deferred），不是已批准实施项。
- 文档边界（Scope / Boundary）：延期项真相源；触发条件满足后再进入 Align/Plan。

## 延期项

### D1. cc-qq 全功能 E2E 覆盖

- 暂不做：本轮只验证了 `/pwd`、`/info`（多轮）与回复媒体自动发送；以下功能尚未做真实 QQ 端到端覆盖：
  - `/help`（返回图片帮助卡片，属于 `rich_media`，需人工确认或富媒体断言）
  - `/cd`、`/goon`、`/approve`、`/deny`、`/initbase`、`/resume`、`/end`、`/cc`、`/!`
  - 事件 `filter.EventMessageType.ALL`
  - 30 项配置项（`allowed_work_dirs`、`group_rules_json`、`auto_send_media`、`long_text_image_*` 等）
- 原因：高风险/状态变更命令需要逐条设计用例与安全边界；本轮聚焦账号切换与本次媒体改动。
- 触发条件：下一轮明确要求“测试 cc-qq 所有功能”或发版回归。
- 参考：`discover_plugin.py` 生成的清单（46 项）与 `SKIPPED.md`。

### D2. 媒体用例固化为仓库资产

- 暂不做：本轮媒体用例放在 `/tmp/cc_qq_cases/reply_auto_media.json`，未入库。
- 原因：需要先确认用例命名、放置目录（建议 `tools/astrbot_e2e/cases/manual/`）与是否纳入常规回归。
- 触发条件：下一轮决定把“回复媒体自动发送”纳入回归。

### D3. `BOT_QQ` / `SENDER_QQ` 环境变量防呆

- 暂不做：未在脚本中校验 `BOT_QQ` 是否与 `config.local.json` 的 `bot.qq` 一致。
- 原因：本轮用 `env -u` 绕过了陈旧变量（B12），防呆属于脚本改进，需单独评审。
- 触发条件：再次出现终端环境变量污染，或需要多人/多机复用时。

### D4. 执行引擎历史轮询兜底

- 暂不做：本轮通过 `reportSelfMessage=true` 解决异步回复采集；未实现“回执后轮询历史直到超时”的引擎兜底。
- 原因：配置方案更小且已验证；引擎轮询涉及 `runner.py` / `onebot.py` 与 vendor 同步。
- 触发条件：观察端无法开启 `reportSelfMessage`，或需要兼容其他 NapCat 实现时。

### D5. probe 与 cc-qq 隔离

- 暂不做：测试实例仍同时加载 `astrbot_plugin_e2e_probe` 与 `astrbot_plugin_cc_qq`，cc-qq 的执行回执会拦截探针命令。
- 原因：本轮不跑探针用例。
- 触发条件：需要跑 probe 基础设施用例时，使用 probe-only 测试根或在测试群禁用 cc-qq。
- 参考：`backlog.md` Q14。

### D6. 自动扫码与生产自动暂停/恢复

- 暂不做：登录仍需人工扫码；虽然独立账号下生产无需暂停，但无人值守回归仍需自动化。
- 原因：涉及 QQ 风控与生产侧安全，必须人工确认。
- 触发条件：高频回归或 CI 化需求。

### D7. 其他平台与镜像升级

- 暂不做：仅验证 macOS + Docker；NapCat 镜像仍为 2026-03 构建 / 4.17.46。
- 原因：跨平台与镜像升级需要单独验证 Packet/rkey/图片下载。
- 触发条件：镜像更新、QQ 协议变更或新增 Linux/Windows 需求。
- 参考：`backlog.md` Q16、Q17。
