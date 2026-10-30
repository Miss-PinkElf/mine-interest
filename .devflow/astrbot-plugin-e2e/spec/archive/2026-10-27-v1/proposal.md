# AstrBot 插件端到端自动化测试提案（Proposal）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 17:41:14 CST。
- 更新时间（Updated At）：2026-10-27 17:41:14 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：把已对齐的设计与实施计划固化为当前 mission 的正式变更提案。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 原始需求（Raw Input）：`zzz-prompt-debug/插件自动化测试验证/prompt-01.md`。
- 关联对齐稿（Related Align）：`../plans/2026-10-27-astrbot-plugin-e2e-align.md`。
- 关联计划（Related Plan）：`../plans/2026-10-27-astrbot-plugin-e2e-plan.md`。
- 当前状态（Status）：待用户确认（Pending Approval）；不是实施记录。
- 文档边界（Scope / Boundary）：本 mission 的变更提案真相源；批准后才进入 Apply。

## 背景

用户希望自动测试 AstrBot 插件：使用专门的测试群和测试账号，通过终端启动 AstrBot 与 NapCat，自动发送消息、采集插件回复与日志、判断是否符合预期，并支持插件重载。

现有 `tests/` 与各插件目录下的 `tests/` 负责逻辑级验证；本提案新增真实 QQ 链路下的端到端测试（End-to-End Test，E2E）能力，不替代原有单元测试。

## 目标

1. 建立独立、可重复的测试运行器（Runner），支持启动/停止测试 AstrBot 实例、发送测试消息、采集消息与日志、断言、重载插件。
2. 首版用探针插件验证 Runner 自身闭环，再用 `cc_qq /help` 验证真实插件。
3. 测试过程不触碰生产 AstrBot 实例、生产端口与生产 QQ 配置。
4. 失败时保留消息、日志、断言与语义判定证据。

## 范围

- 新增 `tools/astrbot_e2e/` 运行器与测试用例。
- 新增独立测试实例（Isolated Test Instance）的初始化与配置写入。
- 新增双账号 OneBot 通道：机器人号观察、发送者号注入。
- 新增消息断言、日志断言与可选 LLM 语义判定。
- 新增 WebUI 登录与插件重载；重载失败时重启测试实例兜底。
- 新增探针插件与 `cc_qq /help` 用例。
- 新增失败证据目录与退出码约定。

## 非目标

- 不替代现有单元测试与集成测试。
- 不在本轮实现 `cc_qq` 长任务、审批流程、多轮对话。
- 不实现 WebUI 页面、CI 集成、并行用例。
- 不实现自动扫码登录、QQ 风控绕过。
- 不修改生产插件代码、生产配置或生产数据库。

## 边界场景

| 场景 | 处理 |
| --- | --- |
| 同机双开 QQ 不可行 | Spike 0 失败时回退 Linux 容器/WSL 或第二台设备半自动；不硬推双开 |
| 机器人自身消息不上报 | 优先事件流；失败时用 `get_group_msg_history` 回填 |
| WebUI 重载鉴权失败 | 重启测试实例兜底，仍以消息证据为准 |
| 探针与 `cc_qq` 同时加载 | 探针用例禁用 `cc_qq` 的群名单；`cc_qq` 用例才启用测试群 |
| 测试实例已在运行 | Runner 停止旧实例并按当前用例配置重新启动 |
| 日志路径与轮转 | 以 `test_root/data/logs/astrbot.log` 为准，按偏移截取窗口 |
| 测试群外消息 | Runner 只允许向配置的 `group_id` 发送 |
| LLM 判定未配置 | 语义断言标记 `SKIPPED`，不伪装成通过；退出码 `3` |
| LLM 判定请求失败 | 语义断言失败，状态 `FAILED`，保留错误原文 |

## 开放问题

- 两个测试 QQ 号的具体号码、专用测试群号与登录方式由本地配置提供，不写入仓库。
- LLM 判定的 provider、模型与 Key 由本地配置提供；未配置时 `cc_qq` 用例只能验收硬断言。
- WebUI 初始密码设置方式依赖 AstrBot 4.29.3 的 `astrbot password` 行为，需在 Apply 中实测。
- NapCat 双开后的配置目录隔离方式需由 Spike 0 给出结论。

## 与 Align / Plan 的关系

- 本提案不重新讨论方向；方向以 Align 稿为准。
- 实施细节以 Plan 为准；本提案只固定“做什么、为什么、边界与验收”。
- 任何与本提案冲突的改动，先回写 Align / Plan，再继续。

## 验收概览

- Spike 0 通过，或已按回退方案切换并记录。
- 单元测试全部通过。
- 探针用例与 `cc_qq /help` 用例稳定 `PASSED`（语义判定需配置 judge）。
- `--reload` 增量验证有前后对比证据。
- 生产实例、端口与 QQ 配置未被修改。
