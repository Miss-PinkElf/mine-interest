# Mission Workflow

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 16:47:08 CST。
- 更新时间（Updated At）：2026-10-27 22:40:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：定义 AstrBot 插件端到端自动化测试（End-to-End Test，E2E）mission 的目标、范围、路径与阶段门禁。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 原始需求（Raw Input）：`zzz-prompt-debug/插件自动化测试验证/prompt-01.md`。
- 当前状态（Status）：已完成（Completed），第一版收尾并提交。
- 文档边界（Scope / Boundary）：当前 mission 的流程与范围真相源（source of truth）；不是已批准的实施计划（Plan）。

## 目标

建立可重复、可判定的 AstrBot 插件端到端自动化测试能力：在专门的测试群中，用专门的测试账号发送消息，采集插件回复与运行日志，自动断言是否符合预期，并支持插件重载后继续验证。

## 范围

- 首版：通用测试运行器（Runner） + 探针插件 + `cc_qq /help` 用例。
- 已实现：环境编排、消息注入、结果采集、硬断言、可选 LLM 语义判定、插件重载、测试报告、失败证据。
- 延期：WebUI 页面、CI 集成、多账号并行、自动扫码登录、复杂多轮对话、cc_qq 长任务全量覆盖。

## 成功标准

- 一条命令完成“检查/启动测试环境 → 发送测试消息 → 采集插件结果 → 断言 → 输出报告”。
- 失败时定位到具体用例、消息、日志时间窗口与原始证据。
- 测试过程不污染生产实例。
- 插件重载后无需重启整个 AstrBot 即可继续执行用例。

## 当前路径

- 重型路径（Heavy Path）：Align → Plan → proposal/design/tasks → Apply → Verify/Close。
- 当前阶段：Close（第一版完成）。
- 设计稿：`plans/2026-10-27-astrbot-plugin-e2e-align.md`。
- 实施计划：`plans/2026-10-27-astrbot-plugin-e2e-plan.md`。
- 三件套：`spec/proposal.md`、`spec/design.md`、`spec/tasks.md`。
- Spike 0：`plans/2026-10-27-spike-0-dual-qq-result.md`。
- 完成交接：`handoffs/2026-10-27-002-第一版完成交接.md`。

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

## 当前阶段出口条件

- 单元测试 106/106 通过。
- 探针与 `cc_qq /help` 两条 E2E PASSED。
- 增量重载验证 PASSED：`reports/20261027-223642-572604-case`，`--attach --reload` 后返回 v2 回显。
- 生产 AstrBot `6199`、生产 QQ `6099` 未受影响。
- 延期项：`deferred/2026-10-27-post-mvp-deferred.md`。
- 未决问题与首版限定：`backlog.md`。
- 提交：第一版相关文件已提交；未提交 `config.local.json`、`reports/`、`.gitignore` 与无关脏文件。
