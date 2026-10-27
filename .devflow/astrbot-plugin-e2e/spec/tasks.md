# AstrBot 插件端到端自动化测试任务清单（Tasks）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 17:41:14 CST。
- 更新时间（Updated At）：2026-10-27 17:41:14 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：把实施计划拆成可独立验证、可勾选的任务，作为 Apply 阶段的追踪真相源。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 关联提案（Related Proposal）：`./proposal.md`。
- 关联设计（Related Design）：`./design.md`。
- 关联计划（Related Plan）：`../plans/2026-10-27-astrbot-plugin-e2e-plan.md`。
- 当前状态（Status）：待用户确认（Pending Approval）。
- 文档边界（Scope / Boundary）：任务与验收追踪；详细代码步骤以 Plan 对应 Task 为准。

## 任务清单

- [x] **Task 0：Spike 0 — 同机双开 QQ 可行性**
  - 产出：`.devflow/astrbot-plugin-e2e/plans/2026-10-27-spike-0-dual-qq-result.md`。
  - 验收：两个 QQ 号在线；两个 NapCat 配置隔离；`6200/6201/6198/6186` 可用；测试群收发成功；生产实例未被触碰。
  - 失败：按设计稿 6.4 回退，并写回 `decision-log.md`，暂停后续任务。

- [x] **Task 1：Runner 包骨架与配置加载**
  - 文件：`tools/astrbot_e2e/__init__.py`、`config.py`、`config.example.json`、`tests/test_config.py`。
  - 验收：5 个配置测试通过；`.gitignore` 已加入 `config.local.json` 与 `reports/`。
  - 对应 Plan：Task 1。

- [x] **Task 2：用例加载与校验**
  - 文件：`tools/astrbot_e2e/cases.py`、`tests/test_cases.py`。
  - 验收：3 个用例测试通过；`{{group_id}}` 可渲染；未知字段被拒绝。
  - 对应 Plan：Task 2。

- [x] **Task 3：断言模块**
  - 文件：`tools/astrbot_e2e/assertions.py`、`tests/test_assertions.py`。
  - 验收：5 个断言测试通过；失败结果保留实际值。
  - 对应 Plan：Task 3。

- [x] **Task 4：报告与失败证据**
  - 文件：`tools/astrbot_e2e/reports.py`、`tests/test_reports.py`。
  - 验收：4 个报告测试通过；运行目录唯一；`summary.json` 含状态与断言。
  - 对应 Plan：Task 4。

- [x] **Task 5：日志窗口采集**
  - 文件：`tools/astrbot_e2e/log_capture.py`、`tests/test_log_capture.py`。
  - 验收：2 个日志测试通过；只读取新增行；`wait_for` 可等待关键字。
  - 对应 Plan：Task 5。

- [x] **Task 6：OneBot 消息构造与 WebSocket 客户端**
  - 文件：`tools/astrbot_e2e/onebot.py`、`tests/test_onebot.py`。
  - 验收：5 个 OneBot 测试通过；`call` 能匹配 echo；历史回填函数可用。
  - 对应 Plan：Task 6。

- [x] **Task 7：测试实例引导（Bootstrap）**
  - 文件：`tools/astrbot_e2e/bootstrap.py`、`tests/test_bootstrap.py`。
  - 验收：4 个 Bootstrap 测试通过；平台/端口/插件配置正确；`cc_qq` 可启用/禁用；插件复制忽略 `tests/`。
  - 对应 Plan：Task 7。

- [x] **Task 8：测试实例编排（Orchestrator）**
  - 文件：`tools/astrbot_e2e/orchestrator.py`、`tests/test_orchestrator.py`。
  - 验收：2 个编排测试通过；PID 归属校验；端口预检；停止只杀自己启动的实例。
  - 对应 Plan：Task 8。

- [x] **Task 9：插件重载（WebUI 登录 + Reload）**
  - 文件：`tools/astrbot_e2e/reloader.py`、`tests/test_reloader.py`。
  - 验收：2 个重载测试通过；登录 Cookie 与 `plugin_id` 正确；错误密码被拒绝。
  - 对应 Plan：Task 9。

- [x] **Task 10：探针插件（Probe Plugin）**
  - 文件：`tools/astrbot_e2e/fixtures/astrbot_plugin_e2e_probe/main.py`、`metadata.yaml`、`tests/test_probe_fixture.py`。
  - 验收：3 个静态测试通过；`e2e_echo`、`e2e_sleep`、`e2e_log` 三个命令存在。
  - 对应 Plan：Task 10。

- [x] **Task 11：LLM 语义判定**
  - 文件：`tools/astrbot_e2e/llm_judge.py`、`tests/test_llm_judge.py`。
  - 验收：2 个判定测试通过；未配置时抛 `JudgeError`；返回 `pass/reason`。
  - 对应 Plan：Task 11。

- [x] **Task 12：Runner 与 CLI**
  - 文件：`tools/astrbot_e2e/runner.py`、`cli.py`、`tests/test_cli.py`。
  - 验收：2 个 CLI 测试通过；`doctor`、`init-instance`、`start-instance`、`stop-instance`、`run`、`--attach`、`--reload` 可用；退出码符合设计。
  - 对应 Plan：Task 12。

- [x] **Task 13：端到端验证 — 探针用例**
  - 文件：`tools/astrbot_e2e/cases/probe_echo.json`。
  - 验收：探针用例 `PASSED`；消息与日志证据齐全；生产端口未变。
  - 证据：`tools/astrbot_e2e/reports/20261027-222915-643515-case`。
  - 对应 Plan：Task 13。

- [x] **Task 14：端到端验证 — `cc_qq /help` 与重载**
  - 文件：`tools/astrbot_e2e/cases/cc_qq_help.json`。
  - 验收：`cc_qq /help` `PASSED`（语义判定需配置 judge）；`--attach` 增量重载验证通过；临时 v2 用例与改动已清理。
  - 证据：`tools/astrbot_e2e/reports/20261027-222837-285382-cc_qq-help`；重载验证 `tools/astrbot_e2e/reports/20261027-223642-572604-case`。
  - 对应 Plan：Task 14。

- [x] **Task 15：Verify / Close**
  - 验收：单元测试全通过；两条 E2E 通过；生产影响检查通过；`state.md`、`checkpoints.md`、`decision-log.md`、`deferred/` 已更新。
  - 收尾补充：`backlog.md`（未决问题与首版限定）、`development-overview.md`、最终 handoff 与 `NEXT-SESSION-PROMPT`。
  - 对应 Plan：Task 15。

## 验证

```bash
# 单元测试
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools -v

# 环境自检
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor --config tools/astrbot_e2e/config.local.json

# 探针闭环
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run \
  --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/probe_echo.json

# 真实插件闭环
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run \
  --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/cc_qq_help.json --reload

# 生产影响检查
lsof -nP -iTCP -sTCP:LISTEN | grep -E ':(6185|6199|6099)' || true
```

## 进入 Apply 前的检查清单

- [x] 用户已确认 `proposal.md`、`design.md`、`tasks.md`。
- [x] Plan 已落盘且与三件套一致。
- [x] 用户已选择执行方式（子代理驱动）。
- [x] Spike 0 明确排在第一项，未通过不进入 Runner 实现。
- [x] 本地配置、账号、测试群与 LLM judge 配置由用户提供，未写入仓库。
- [x] 生产隔离检查项已写入任务。
