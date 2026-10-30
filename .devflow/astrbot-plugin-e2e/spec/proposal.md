# 通用 AstrBot 插件自动化测试 skill 提案（Proposal）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-30 14:30:00 CST。
- 更新时间（Updated At）：2026-10-30 14:30:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：把需求 2「通用插件测试 skill」的对齐结论与实施计划固化为正式变更提案。
- 关联项目（Related Repository / Project）：当前仓库 `.`；skill 真源仓库 `/Users/mobius/Documents/111AAA-code/person-config`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 原始需求（Raw Input）：`zzz-prompt-debug/插件自动化测试验证/prompt-01.md`（需求 2，第 6–14 行）。
- 关联对齐稿（Related Align）：`../plans/2026-10-30-通用插件测试skill-align.md`。
- 关联计划（Related Plan）：`../plans/2026-10-30-通用插件测试skill-plan.md`。
- 当前状态（Status）：待用户确认（Pending Approval）；不是实施记录。
- 文档边界（Scope / Boundary）：本 mission 第二阶段的变更提案真相源；批准后才进入 Apply。

## 背景

第一版 `tools/astrbot_e2e/` 已完成并通过验证：

- 单测 106/106 通过。
- 探针、`cc_qq /help`、增量重载三项 E2E PASSED。
- 2026-10-29–30 用它在测试群验收 cc-qq `0.2.5`，A+B+C 共 44 项。

但第一版仍是「手写用例 + 人工编排」：用例要人工写、环境要人工判断、生产要人工暂停、报告要人工汇总。需求 2 要把它固化成可复用的通用 skill。

## 问题

1. **不可复用**：换插件、换机器都要重新理解 `tools/astrbot_e2e` 的配置与拓扑。
2. **覆盖不全**：用例模型只支持单次发送，无法覆盖 `/new` → `/cc` → `/end` 等多轮流程。
3. **效率低**：每个非 attach 用例重启测试实例；批量回归成本高。
4. **环境判断靠人**：AstrBot/NapCat 版本、端口、插件目录没有统一探测。
5. **报告不完整**：只有 JSON/日志证据，没有统一摘要与脱敏。
6. **自愈缺失**：端口占用、残留实例、reload 失败等需要人工排查。

## 提议变更

### 1. 执行引擎增强（本仓库）

- 用例模型支持多轮 `steps`，保持 `send` / `expect` 向后兼容。
- 新增 `run-suite`：一次启动测试实例，串行执行同一插件的全部用例。
- 新增插件源解析：`plugin_sources` 显式配置 → 仓库 `integrations/astrbot/` → 生产插件目录 → fixture。
- 报告聚合：suite 级 `report.json` + `report.md`，默认脱敏 QQ、Token、长消息。
- `doctor` 增强：检查插件源、测试端口、残留实例；未知端口只报告、不误杀。

### 2. 通用 skill（person-config 真源）

- `SKILL.md`：触发条件、S0–S7 主流程、安全门禁。
- `scripts/probe_env.py`：输出统一环境画像。
- `scripts/discover_plugin.py`：从插件源码/文档提取功能清单。
- `scripts/gen_cases.py`：生成安全命令用例草案，高风险命令进 `SKIPPED.md`。
- `scripts/aggregate_report.py`：重新生成脱敏报告。
- `scripts/sync_vendor.py`：把执行引擎同步为 `vendor/` 快照。
- `references/` 与 `templates/`：探测、兼容性、自愈、覆盖分析、报告、安全规则。

### 3. 安装与登记

- 真源：`person-config/skills/custom/astrbot-plugin-e2e/`。
- 副本：本仓库 `.claude/skills/astrbot-plugin-e2e/`。
- 登记：`person-config/skills/catalog.json`。

## 范围

### 本轮做

- macOS 可运行。
- 文本消息、单轮与多轮步骤。
- 测试侧自愈；生产侧必须用户确认。
- 自动分析插件 + 人工确认功能清单。
- JSON + Markdown 报告，默认脱敏。
- 端到端验收：cc-qq 安全命令、多轮、报告、自愈演练。

### 本轮不做

| 暂不做 | 原因 | 后续触发条件 |
| --- | --- | --- |
| 自动扫码登录 | QQ 风控与人工确认不可替代 | 官方提供稳定免扫码方案时 |
| 富媒体消息 | 首版聚焦文本链路 | 被测插件核心功能依赖图片/文件时 |
| 并行执行 | 单实例串行更稳定 | 用例数量导致回归时间不可接受时 |
| WebUI 报告 | JSON + Markdown 已满足 | 需要非技术同学直接查看时 |
| CI 集成 | 依赖人工登录与固定测试群 | 需要每日回归时 |
| Linux/Windows 可运行 | 无验证环境 | 用户提供可验证环境时 |
| 多插件同时测试 | 同一测试群会互相干扰 | 需要插件组合兼容性验证时 |

## 影响面

- 修改：`tools/astrbot_e2e/`（cases、runner、reports、bootstrap、config、cli、orchestrator）。
- 新增：`tools/astrbot_e2e/suite.py`、`tests/test_suite.py`。
- 新增：person-config skill 目录与本仓库副本。
- 不改：生产 AstrBot 代码、生产 NapCat 配置、被测插件源码。

## 风险

1. **多轮步骤回归**：用 `case_steps` 统一形状，保留旧用例测试。
2. **批量执行状态串扰**：每个用例独立目录与日志 mark；失败不终止 suite。
3. **报告泄露**：`sanitize` 单测 + 验收脚本扫描。
4. **自愈误杀**：只停有 PID 文件且校验属于测试实例的进程。
5. **副本漂移**：只改 person-config 真源，副本由同步生成。

## 验收标准

1. `tools/astrbot_e2e` 全量单测通过。
2. skill 脚本单测通过；`probe_env.py` 输出正确版本。
3. cc-qq 提取 ≥10 个命令；生成安全用例并列出跳过项。
4. `run-suite` 生成脱敏报告。
5. 多轮用例真实跑通。
6. 自愈演练通过：未知端口不误杀、残留实例自动停止。
7. skill 已安装并登记。
8. 未擅自 commit。

## 审批门禁

- 本提案与 `design.md`、`tasks.md` 经用户确认后，方可进入 Apply。
- Apply 采用子代理驱动（Subagent-Driven），每个 Task 完成后做验证与复审。
