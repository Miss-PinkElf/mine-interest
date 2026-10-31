# Mission Workflow

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 16:47:08 CST。
- 更新时间（Updated At）：2026-10-31 22:55:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：定义 AstrBot 插件端到端自动化测试（End-to-End Test，E2E）mission 的目标、范围、路径与阶段门禁。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 原始需求（Raw Input）：`zzz-prompt-debug/插件自动化测试验证/prompt-01.md`。
- 当前状态（Status）：生产环境一键脚本已完成并验证；生产 NapCat 已登录就绪；E2E 测试资产待修。
- 文档边界（Scope / Boundary）：当前 mission 的流程与范围真相源（source of truth）；不是已批准的实施计划（Plan）。

## 目标

建立可重复、可判定的 AstrBot 插件端到端自动化测试能力：在专门的测试群中，用专门的测试账号发送消息，采集插件回复与运行日志，自动断言是否符合预期，并支持插件重载后继续验证。

第二阶段目标：把验证流程固化成通用 skill（环境探测、三服务编排、功能清单、多轮用例、脱敏报告、测试侧自愈）。

## 范围

- 首版：通用测试运行器（Runner） + 探针插件 + `cc_qq /help` 用例。
- 第二阶段：通用测试 skill（`astrbot-plugin-e2e`）+ 多轮 `steps` + `run-suite` + 报告脱敏 + 测试侧自愈。
- 已实现：环境编排、消息注入、结果采集、硬断言、可选 LLM 语义判定、插件重载、测试报告、失败证据。
- 延期：WebUI 页面、CI 集成、多账号并行、自动扫码登录、富媒体、Linux/Windows 可运行。

## 成功标准

- 一条命令完成“检查/启动测试环境 → 发送测试消息 → 采集插件结果 → 断言 → 输出报告”。
- 失败时定位到具体用例、消息、日志时间窗口与原始证据。
- 测试过程不污染生产实例。
- 插件重载后无需重启整个 AstrBot 即可继续执行用例。

## 当前路径

- 重型路径（Heavy Path）：Align → Plan → proposal/design/tasks → Apply → Verify/Close。
- 当前阶段：Verify/Close 完成（需求 2）。
- 设计稿：`plans/2026-10-27-astrbot-plugin-e2e-align.md`。
- 实施计划：`plans/2026-10-27-astrbot-plugin-e2e-plan.md`。
- 需求 2 设计稿：`plans/2026-10-30-通用插件测试skill-align.md`。
- 需求 2 实施计划：`plans/2026-10-30-通用插件测试skill-plan.md`。
- 需求 2 三件套：`spec/proposal.md`、`spec/design.md`、`spec/tasks.md`。
- 第一版三件套归档：`spec/archive/2026-10-27-v1/`。
- Spike 0：`plans/2026-10-27-spike-0-dual-qq-result.md`。
- 完成交接：`handoffs/2026-10-27-002-第一版完成交接.md`。
- 生产环境一键脚本计划：`plans/2026-10-31-生产环境一键启动脚本-plan.md`。
- 生产环境一键脚本交接：`handoffs/2026-10-31-004-生产环境一键启动脚本.md`。

## 主线阶段

```text
Mission Init -> Explore -> Align -> Plan -> Propose/Tasks -> Apply -> Verify/Close
```

## 主要里程碑

1. Align：完成。
2. Plan：完成。
3. Propose/Tasks：完成。
4. Apply Task 0（Spike 0）：通过。
5. Apply Task 1–12：全部完成并通过复审。
6. 首个闭环：探针 E2E PASSED。
7. 真实插件：`cc_qq /help` E2E PASSED（含语义判定）。
8. Verify/Close：完成；延期项与交接落盘。
9. 需求 2 Align：完成；9 项决策落盘。
10. 需求 2 Plan：完成；Task 0–13，待用户批准。
11. 需求 2 spec 三件套：完成；第一版 spec 已归档。
12. 需求 2 Apply Task 0–11：完成；引擎 127/127，skill 12/12。
13. 需求 2 真机验收：完成；多轮与 suite PASSED，脱敏与自愈演练通过。
14. 生产环境一键脚本（`tools/prod_env/`）：完成并验证；iTerm 双标签、幂等 start、显式 `--restart`、`stop` 清理窗口。
15. 生产 NapCat 登录：用户已处理安全风险并扫码；`get_login_info` 返回 17号，复测通过。

## 当前阶段出口条件

- 单元测试 106/106 通过。
- 探针与 `cc_qq /help` 两条 E2E PASSED。
- 增量重载验证 PASSED：`reports/20261027-223642-572604-case`，`--attach --reload` 后返回 v2 回显。
- 生产 AstrBot `6199`、生产 QQ `6099` 未受影响。
- 延期项：`deferred/2026-10-27-post-mvp-deferred.md`。
- 未决问题与首版限定：`backlog.md`。
- 提交：第一版相关文件已提交；未提交 `config.local.json`、`reports/`、`.gitignore` 与无关脏文件。
- 需求 2：已完成并提交。
- 需求 2 验收证据：`reports/20261030-154828-636210-cc-qq`、`reports/20261030-154847-882152-astrbot_plugin_cc_qq-suite`、`reports/20261030-155012-908540-astrbot_plugin_cc_qq-suite`。
- 生产环境一键脚本：`tools/prod_env/prod.sh` + README 已完成并验证；随本轮收尾提交。
- 生产 NapCat 登录：已恢复并复测通过（`get_login_info` 返回 17号）；生产 AstrBot PID `40562`、窗口 `1850`。
- 下一步测试资产：更新 `cc_qq_multi_turn` `/info` 断言、隔离 probe 与 cc-qq。
- 账号策略：生产 17号 不再用于 E2E；用户已新建独立测试 QQ，账号与接入方式待下次对话（`backlog.md` Q24）。
