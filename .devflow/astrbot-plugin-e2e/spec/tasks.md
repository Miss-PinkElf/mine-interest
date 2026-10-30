# 通用 AstrBot 插件自动化测试 skill 任务清单（Tasks）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-30 14:30:00 CST。
- 更新时间（Updated At）：2026-10-30 14:30:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：把实施计划拆成可独立验证、可勾选的任务，作为 Apply 阶段的追踪真相源。
- 关联项目（Related Repository / Project）：当前仓库 `.`；skill 真源仓库 `/Users/mobius/Documents/111AAA-code/person-config`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 关联提案（Related Proposal）：`./proposal.md`。
- 关联设计（Related Design）：`./design.md`。
- 关联计划（Related Plan）：`../plans/2026-10-30-通用插件测试skill-plan.md`。
- 当前状态（Status）：待用户确认（Pending Approval）。
- 文档边界（Scope / Boundary）：任务与验收追踪；详细代码步骤以 Plan 对应 Task 为准。
- 归档：第一版任务清单已归档到 `./archive/2026-10-27-v1/tasks.md`。

## 执行方式

- 子代理驱动（Subagent-Driven）：每个 Task 派一个子代理实现，任务间做规格与质量复审。
- 每个 Task 完成后：跑测试 → 记录证据 → 进入下一个。
- **不得擅自 commit**；每个 Task 结束向用户申请提交许可。

## 任务清单

### 阶段 A：执行引擎

- [x] **Task 0：基线校验**
  - 产出：现有单测数量与 HEAD 哈希记录。
  - 验证：`PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools` 全量通过。
  - 退出条件：基线为 106/106 或记录差异原因。
  - 结果：2026-10-30；HEAD `7f3fe3b`；106/106 OK。

- [x] **Task 1：用例模型支持多轮 steps**
  - 文件：`tools/astrbot_e2e/cases.py`、`tests/test_cases.py`。
  - 产出：`steps` 校验、`case_steps()`、全步骤 group_id 渲染。
  - 验证：新增 6 个用例测试通过；全量单测通过。
  - 结果：2026-10-30；19/19 用例测试 OK；全量 112/112 OK。

- [x] **Task 2：执行器支持多轮步骤**
  - 文件：`tools/astrbot_e2e/runner.py`、`tests/test_runner.py`。
  - 产出：`execute_case()`、`_run_semantic()`、步骤级目录与断言、失败即停。
  - 验证：多轮成功与失败两条测试通过；旧用例行为不变。
  - 结果：2026-10-30；test_runner 11/11 OK；全量 122/122 OK。

- [x] **Task 3：插件源解析**
  - 文件：`bootstrap.py`、`config.py`、`test_bootstrap.py`、`test_config.py`。
  - 产出：`resolve_plugin_source()`、`plugin_sources` 校验。
  - 验证：配置优先、仓库回退、缺失报错三条测试通过。
  - 结果：2026-10-30；bootstrap + config 31/31 OK；全量 122/122 OK。

- [x] **Task 4：批量执行 run-suite**
  - 文件：`suite.py`（新增）、`cli.py`、`tests/test_suite.py`、`test_cli.py`。
  - 产出：`run_suite()`、`run-suite` 子命令、suite 目录与汇总。
  - 验证：两用例单实例执行、混插件拒绝、CLI 分发测试通过。
  - 结果：2026-10-30；test_suite + test_cli 5/5 OK；全量 122/122 OK。

- [x] **Task 5：报告聚合与脱敏**
  - 文件：`reports.py`、`tests/test_reports.py`。
  - 产出：`sanitize()`、`write_suite_report()`、Markdown 摘要。
  - 验证：QQ/Token 脱敏、长文本截断、`redact=False` 三条测试通过。
  - 结果：2026-10-30；test_reports 9/9 OK；全量 127/127 OK。
  - 复核修复：键名包含 `token`/`secret`/`api_key`/`password`/`jwt` 时也脱敏（覆盖 `reverse_ws_token`），`config.mask_config` 同步加固。

- [x] **Task 6：doctor 增强与自愈可见性**
  - 文件：`orchestrator.py`、`cli.py`、`test_orchestrator.py`、`test_cli.py`。
  - 产出：`port_endpoints()`、插件源检查、端口占用检查。
  - 验证：公开端口方法测试、缺失插件源返回 2 测试通过。
  - 结果：2026-10-30；orchestrator + cli 11/11 OK；全量 127/127 OK。

### 阶段 B：skill 脚本与文档

- [x] **Task 7：skill 骨架与环境探测**
  - 文件：`scripts/engine_path.py`、`scripts/probe_env.py`、`tests/test_probe_env.py`。
  - 产出：环境画像 JSON；不泄露密钥。
  - 验证：两项单测通过；本机探测 AstrBot `4.29.3`、NapCat `4.18.28`。
  - 结果：2026-10-30；test_probe_env 2/2 OK；真实探测版本与密钥检查通过。

- [x] **Task 8：插件功能清单提取**
  - 文件：`scripts/discover_plugin.py`、`tests/test_discover_plugin.py`。
  - 产出：`features.json`；命令/事件/钩子/配置分类与风险分级。
  - 验证：三项单测通过；cc-qq 提取 ≥10 个命令。
  - 结果：2026-10-30；5/5 OK；cc-qq 13 个命令、1 个事件、23 个配置、24 个需人工项。
  - 复核修复：支持 `/cc <参数>`；排除 `/tmp`、`/etc` 等系统路径；目录不存在时报错，不静默返回空清单。

- [x] **Task 9：用例草案生成**
  - 文件：`scripts/gen_cases.py`、`tests/test_gen_cases.py`。
  - 产出：安全命令用例 JSON、`SKIPPED.md`。
  - 验证：两项单测通过；cc-qq 高风险命令进入跳过清单。
  - 结果：2026-10-30；gen_cases 2/2 + discover_plugin 6/6 OK；cc-qq 生成 3 个只读命令用例（`/help`、`/info`、`/pwd`），34 项跳过。
  - 复核修复：`/cd`、`/resume` 纳入高风险；修正“事件”断言。

- [x] **Task 10：skill 文档与模板**
  - 文件：`SKILL.md`、`README.md`、`references/` 6 份、`templates/` 3 份、`scripts/aggregate_report.py`。
  - 产出：S0–S7 主流程、安全规则、探测/兼容/自愈/覆盖/报告参考。
  - 验证：必需文件清单检查无缺失。
  - 结果：2026-10-30；12 个文件齐全；`missing: []`；JSON 模板与 `aggregate_report.py` 编译通过。

- [x] **Task 11：vendor 快照与安装登记**
  - 文件：`scripts/sync_vendor.py`、`tests/test_sync_vendor.py`、`vendor/`、本仓库副本、`catalog.json`。
  - 产出：可移植引擎快照；catalog 条目与 `categories.custom`。
  - 验证：同步测试通过；`sync/sync.py --only astrbot-plugin-e2e --dry-run` 无 schema 错误。
  - 结果：2026-10-30；sync_vendor 1/1 OK；vendor 无 reports/tests/config.local.json；仓库副本 45 个文件与真源一致；dry-run 无 WARN/COPY-MISS。
  - 说明：`copies` 仅支持 person-config 内部路径，外部仓库副本记录在 `external_copies`。

### 阶段 C：验收与收尾

- [x] **Task 12：端到端验收**
  - 前置：用户启动三服务并扫码登录两个 QQ。
  - 产出：多轮示例用例；cc-qq suite 报告；自愈演练记录。
  - 验证：
    - `run --case cc_qq_multi_turn.json` PASSED。
    - `run-suite` 生成 `report.json` + `report.md`。
    - 报告不含完整 QQ/Token。
    - 未知端口占用不误杀；残留实例自动停止。
  - 结果：2026-10-30。
    - `doctor OK`：bot `3254276668`、sender `1961618848`。
    - 多轮 PASSED：`reports/20261030-154828-636210-cc-qq`（`/pwd` → `/info`）。
    - suite PASSED：`reports/20261030-154847-882152-astrbot_plugin_cc_qq-suite`，2/2 用例。
    - 脱敏：`report.json` + `report.md` 无完整 QQ/Token/password。
    - 自愈：未知端口占用只报错不误杀；残留实例自动停止并重启，`reports/20261030-155012-908540-astrbot_plugin_cc_qq-suite` 的 ops 含“已停止残留测试实例”。
    - 发现：cc-qq `/help` 返回图片帮助卡片，已标记 `rich_media` 并移出文本 suite。

- [x] **Task 13：文档与收尾**
  - 文件：`tools/astrbot_e2e/README.md`、`backlog.md`、`state.md`、`checkpoints.md`、`decision-log.md`。
  - 产出：使用说明、未决项、验收证据、阶段检查点。
  - 验证：引擎与 skill 两套测试全部通过；文档无占位符。
  - 结果：2026-10-30；README 补充 `run-suite`/`steps`/`plugin_sources`/报告脱敏/富媒体边界；backlog 标记需求 2 已验证并新增 Q11/Q12；两套测试全绿；未提交。

## 完成定义（Definition of Done）

1. 引擎全量单测通过，新增能力均有测试。
2. skill 脚本与测试全部通过。
3. cc-qq 功能清单、用例草案、suite 报告可复现。
4. 多轮用例真实跑通。
5. 自愈演练通过，生产未被误操作。
6. skill 真源、仓库副本、catalog 三者一致。
7. 文档更新完成；未擅自 commit。

## 依赖关系

```text
Task 0
  ├→ Task 1 → Task 2 → Task 4 → Task 5
  ├→ Task 3 → Task 6
  └→ Task 7 → Task 8 → Task 9 → Task 10
                              Task 11（依赖 4/5/7/8/9/10）
                              Task 12（依赖 4/5/6/9/11）
                              Task 13（依赖 12）
```

## 执行记录

由执行代理在每个 Task 完成后追加：

```text
Task 0：2026-10-30 基线 106/106 OK；HEAD 7f3fe3b
Task 1：2026-10-30 多轮 steps；19/19 用例测试 OK；全量 112/112 OK
Task 2：2026-10-30 多轮执行器；test_runner 11/11 OK；全量 122/122 OK
Task 3：2026-10-30 插件源解析；bootstrap+config 31/31 OK；全量 122/122 OK
Task 4：2026-10-30 run-suite；test_suite+test_cli 5/5 OK；全量 122/122 OK
Task 5：2026-10-30 报告脱敏；9/9 OK；全量 127/127 OK；复核修复 reverse_ws_token 脱敏
Task 6：2026-10-30 doctor 增强；11/11 OK；全量 127/127 OK
Task 7：2026-10-30 环境探测；2/2 OK；AstrBot 4.29.3 / NapCat 4.18.28
Task 8：2026-10-30 功能清单；5/5 OK；cc-qq 13 命令/1 事件/23 配置
Task 9：2026-10-30 用例生成；8/8 OK；cc-qq 生成 3 个只读用例、34 项跳过
Task 10：2026-10-30 skill 文档；12 文件齐全；missing []
Task 11：2026-10-30 vendor+安装；sync_vendor 1/1 OK；副本 45 文件一致；dry-run 干净
Task 12：2026-10-30 真机验收；doctor OK；多轮 PASSED；suite 2/2 PASSED；脱敏通过；两项自愈通过；/help 标记 rich_media
Task 13：2026-10-30 文档收尾；引擎 127/127；skill 12/12；未提交
```
