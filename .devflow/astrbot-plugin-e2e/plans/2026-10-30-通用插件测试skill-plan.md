# 通用 AstrBot 插件自动化测试 skill — 实施计划（Plan）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-30 14:20:00 CST。
- 更新时间（Updated At）：2026-10-30 14:20:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：把需求 2 的 Align 结论拆成可执行、可验证的实施任务。
- 关联项目（Related Repository / Project）：当前仓库 `.`；skill 真源仓库 `/Users/mobius/Documents/111AAA-code/person-config`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 关联 Align：`.devflow/astrbot-plugin-e2e/plans/2026-10-30-通用插件测试skill-align.md`。
- 当前状态（Status）：计划中（Planned），等待用户批准后进入 Propose/Tasks 与 Apply。
- 文档边界（Scope / Boundary）：实施计划（Plan）；**不触发实施**。批准前禁止改代码。

> **给执行代理（For agentic workers）：** 必需子技能（REQUIRED SUB-SKILL）：`superpowers-subagent-driven-development`（推荐）或 `executing-plans`，按任务逐项实现。步骤使用复选框（`- [ ]`）跟踪。

**目标（Goal）：** 交付通用 skill `astrbot-plugin-e2e`，覆盖环境探测、三服务编排、插件功能分析、多轮用例执行、报告脱敏与测试侧自愈。

**架构（Architecture）：** 执行引擎仍放在本仓库 `tools/astrbot_e2e/`，新增多轮 `steps`、`run-suite`、插件源解析、报告聚合与自愈；skill 真源放 `person-config/skills/custom/astrbot-plugin-e2e/`，通过 `scripts/` 做探测/分析/生成用例，通过 `vendor/astrbot_e2e/` 携带可移植快照。

**技术栈（Tech Stack）：** Python 3.12（`backend/.venv`）、asyncio、aiohttp、unittest、AstrBot 4.29.3、NapCat 4.18.28、OneBot v11。

---

## 0. 全局约束

1. **硬门禁**：本计划经用户批准后才进入 Apply；每个 Task 完成后先验证，再进入下一个。
2. **提交策略**：本仓库与 person-config 都**不得擅自 commit**；每个 Task 的“提交”步骤改为“向用户申请提交”。用户未批准时保留工作区改动。
3. **不碰生产**：任何 Task 都不自动暂停/恢复生产 AstrBot、不修改生产 NapCat 配置；只在验收 Task 中由用户确认后操作。
4. **不提交敏感文件**：`tools/astrbot_e2e/config.local.json`、`tools/astrbot_e2e/reports/`、真实报告一律不入库。
5. **相对路径**：本仓库内一律使用相对路径；person-config 为跨仓库目标，使用绝对路径 `SKILL_ROOT`。
6. **测试命令统一**：`PYTHONPATH=tools backend/.venv/bin/python -m unittest <target> -v`。

常量约定：

```text
REPO_ROOT   = /Users/mobius/Documents/111AAA-code/mine-interest.worktrees/mine-interest-source-hub
SKILL_ROOT  = /Users/mobius/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e
REPO_SKILL  = .claude/skills/astrbot-plugin-e2e
```

---

## 1. 文件结构总览

### 1.1 本仓库执行引擎（修改 / 新增）

```text
tools/astrbot_e2e/
├─ cases.py                 修改：支持 steps
├─ runner.py                修改：抽取 execute_case，支持多轮
├─ suite.py                 新增：run-suite 批量执行
├─ reports.py               修改：suite 报告与脱敏
├─ config.py                修改：plugin_sources 校验
├─ bootstrap.py             修改：插件源解析
├─ orchestrator.py          修改：公开 port_endpoints
├─ cli.py                   修改：run-suite 子命令、doctor 增强
└─ tests/
   ├─ test_cases.py         修改
   ├─ test_runner.py        修改
   ├─ test_suite.py         新增
   ├─ test_reports.py       修改
   ├─ test_config.py        修改
   ├─ test_bootstrap.py     修改
   └─ test_cli.py           修改
```

### 1.2 skill 真源（新增，位于 person-config）

```text
person-config/skills/custom/astrbot-plugin-e2e/
├─ SKILL.md
├─ README.md
├─ references/
│  ├─ environment-probe.md
│  ├─ compatibility-matrix.md
│  ├─ self-healing.md
│  ├─ coverage-analysis.md
│  ├─ report-template.md
│  └─ safety-rules.md
├─ scripts/
│  ├─ engine_path.py
│  ├─ probe_env.py
│  ├─ discover_plugin.py
│  ├─ gen_cases.py
│  ├─ aggregate_report.py
│  └─ sync_vendor.py
├─ templates/
│  ├─ config.template.json
│  ├─ case.template.json
│  └─ report.template.md
├─ tests/
│  ├─ __init__.py
│  ├─ test_probe_env.py
│  ├─ test_discover_plugin.py
│  ├─ test_gen_cases.py
│  └─ test_sync_vendor.py
└─ vendor/astrbot_e2e/      由 sync_vendor.py 生成
```

---

## 2. 任务分解

### Task 0：基线校验

**Files：** 无代码改动。

- [ ] **Step 1：确认工作区状态**

Run:
```bash
git status --short
```
Expected：只出现已知脏文件（`.devflow/` 改动、`zzz-prompt-debug/接入agent/prompt-01.md`）；无 `tools/astrbot_e2e/config.local.json` 或 `reports/` 被暂存。

- [ ] **Step 2：跑现有单测基线**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools -v
```
Expected：`Ran 106 tests ... OK`。

- [ ] **Step 3：记录基线**

把测试数量与提交哈希写入本任务下方「执行记录」；不修改任何文件。

---

### Task 1：用例模型支持多轮 steps

**Files：**
- Modify：`tools/astrbot_e2e/cases.py:9-78`
- Test：`tools/astrbot_e2e/tests/test_cases.py`

- [ ] **Step 1：写失败测试**

在 `tools/astrbot_e2e/tests/test_cases.py` 追加：

```python
    def test_accepts_multi_step_case(self):
        self.write(
            {
                "name": "multi",
                "plugin": "astrbot_plugin_e2e_probe",
                "steps": [
                    {
                        "send": {"group_id": "{{group_id}}", "text": "/help"},
                        "expect": {"messages": [{"contains": ["帮助"]}]},
                    },
                    {
                        "send": {"group_id": "{{group_id}}", "text": "/info"},
                        "expect": {"messages": [{"regex": r"\S"}]},
                    },
                ],
            }
        )
        case = load_case(self.path)
        rendered = render_case(case, {"group_id": "123456789"})
        self.assertEqual(rendered["steps"][0]["send"]["group_id"], "123456789")
        self.assertEqual(rendered["steps"][1]["send"]["group_id"], "123456789")

    def test_rejects_steps_with_top_level_send(self):
        self.write_case(
            steps=[
                {
                    "send": {"group_id": "{{group_id}}", "text": "/help"},
                    "expect": {"messages": [{"contains": ["帮助"]}]},
                }
            ]
        )
        with self.assertRaisesRegex(CaseError, "不能同时出现"):
            load_case(self.path)

    def test_rejects_empty_steps(self):
        self.write(
            {
                "name": "multi",
                "plugin": "astrbot_plugin_e2e_probe",
                "steps": [],
            }
        )
        with self.assertRaisesRegex(CaseError, "steps 必须是非空数组"):
            load_case(self.path)

    def test_rejects_step_without_expect(self):
        self.write(
            {
                "name": "multi",
                "plugin": "astrbot_plugin_e2e_probe",
                "steps": [{"send": {"group_id": "{{group_id}}", "text": "/help"}}],
            }
        )
        with self.assertRaisesRegex(CaseError, "send 与 expect"):
            load_case(self.path)

    def test_rejects_unknown_step_key(self):
        self.write(
            {
                "name": "multi",
                "plugin": "astrbot_plugin_e2e_probe",
                "steps": [
                    {
                        "send": {"group_id": "{{group_id}}", "text": "/help"},
                        "expect": {"messages": [{"contains": ["帮助"]}]},
                        "sleep": 1,
                    }
                ],
            }
        )
        with self.assertRaisesRegex(CaseError, "未知字段"):
            load_case(self.path)

    def test_case_steps_returns_legacy_as_single_step(self):
        self.write_case()
        case = load_case(self.path)
        steps = case_steps(case)
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0]["send"]["text"], "/e2e_echo hello")
```

同时把 import 改为：

```python
from astrbot_e2e.cases import CaseError, case_steps, load_case, render_case
```

- [ ] **Step 2：运行测试确认失败**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_cases -v
```
Expected：FAIL / ImportError（`case_steps` 不存在）。

- [ ] **Step 3：实现 cases.py**

把 `tools/astrbot_e2e/cases.py` 改为：

```python
"""用例加载与校验（Test Case）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ALLOWED_TOP = frozenset({"name", "plugin", "reload", "send", "expect", "steps"})
ALLOWED_SEND = frozenset({"group_id", "text", "at_bot"})
ALLOWED_EXPECT = frozenset({"timeout_seconds", "messages", "logs", "semantic"})
ALLOWED_STEP = frozenset({"send", "expect"})
EXPECT_MATCHER_KEYS = ("messages", "logs", "semantic")
EXPECT_LIST_KEYS = ("messages", "logs")
MAX_STEPS = 50


class CaseError(ValueError):
    """用例缺失或非法。"""


def load_case(path: Any) -> Dict[str, Any]:
    case_path = Path(path).expanduser()
    if not case_path.exists():
        raise CaseError("用例文件不存在: {}".format(case_path))
    try:
        text = case_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CaseError("用例文件编码非法: {}".format(exc)) from exc
    except OSError as exc:
        raise CaseError("用例文件读取失败: {}".format(exc)) from exc
    try:
        case = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CaseError("用例不是合法 JSON: {}".format(exc)) from exc
    validate_case(case)
    return case


def _validate_send(send: Any, label: str) -> None:
    if not isinstance(send, dict):
        raise CaseError("{} 必须是对象".format(label))
    unknown = set(send) - ALLOWED_SEND
    if unknown:
        raise CaseError("{} 未知字段: {}".format(label, sorted(unknown)))
    if not str(send.get("text") or "").strip():
        raise CaseError("{}.text 必填".format(label))


def _validate_expect(expect: Any, label: str) -> None:
    if not isinstance(expect, dict):
        raise CaseError("{} 必须是对象".format(label))
    unknown = set(expect) - ALLOWED_EXPECT
    if unknown:
        raise CaseError("{} 未知字段: {}".format(label, sorted(unknown)))
    if not any(key in expect for key in EXPECT_MATCHER_KEYS):
        raise CaseError("{} 至少包含 messages / logs / semantic 之一".format(label))
    for key in EXPECT_LIST_KEYS:
        if key in expect and not (isinstance(expect[key], list) and expect[key]):
            raise CaseError("{}.{} 必须是非空数组".format(label, key))
    if "semantic" in expect and not isinstance(expect["semantic"], dict):
        raise CaseError("{}.semantic 必须是对象".format(label))


def validate_case(case: Dict[str, Any]) -> None:
    if not isinstance(case, dict):
        raise CaseError("用例顶层必须是对象")
    unknown = set(case) - ALLOWED_TOP
    if unknown:
        raise CaseError("未知字段: {}".format(sorted(unknown)))
    if not str(case.get("name") or "").strip():
        raise CaseError("name 必填")
    if not str(case.get("plugin") or "").strip():
        raise CaseError("plugin 必填")

    if "steps" in case:
        if "send" in case or "expect" in case:
            raise CaseError("steps 与 send/expect 不能同时出现")
        steps = case["steps"]
        if not isinstance(steps, list) or not steps:
            raise CaseError("steps 必须是非空数组")
        if len(steps) > MAX_STEPS:
            raise CaseError("steps 不能超过 {} 步".format(MAX_STEPS))
        for index, step in enumerate(steps, start=1):
            label = "steps[{}]".format(index)
            if not isinstance(step, dict):
                raise CaseError("{} 必须是对象".format(label))
            unknown_step = set(step) - ALLOWED_STEP
            if unknown_step:
                raise CaseError("{} 未知字段: {}".format(label, sorted(unknown_step)))
            if "send" not in step or "expect" not in step:
                raise CaseError("{} 必须同时包含 send 与 expect".format(label))
            _validate_send(step["send"], label + ".send")
            _validate_expect(step["expect"], label + ".expect")
        return

    if "send" not in case or "expect" not in case:
        raise CaseError("必须提供 send/expect 或 steps")
    _validate_send(case["send"], "send")
    _validate_expect(case["expect"], "expect")


def case_steps(case: Dict[str, Any]) -> List[Dict[str, Any]]:
    """把新旧两种用例形状统一成步骤列表。"""
    if "steps" in case:
        return list(case["steps"])
    return [{"send": case["send"], "expect": case["expect"]}]


def _render_send(send: Dict[str, Any], config: Dict[str, Any]) -> None:
    if send.get("group_id") == "{{group_id}}":
        if "group_id" not in config:
            raise CaseError("配置缺少 group_id，无法渲染用例")
        send["group_id"] = str(config["group_id"])


def render_case(case: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    rendered = json.loads(json.dumps(case))
    for step in case_steps(rendered):
        _render_send(step["send"], config)
    return rendered
```

- [ ] **Step 4：运行单元测试**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_cases -v
```
Expected：全部 PASS（含新增 6 个）。

- [ ] **Step 5：跑全量单测**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools
```
Expected：全量 PASS。

- [ ] **Step 6：申请提交（不自动执行）**

向用户说明 Task 1 改动并请求提交许可。

---

### Task 2：执行器支持多轮步骤

**Files：**
- Modify：`tools/astrbot_e2e/runner.py:1-281`
- Test：`tools/astrbot_e2e/tests/test_runner.py`

- [ ] **Step 1：写失败测试**

在 `tools/astrbot_e2e/tests/test_runner.py` 追加：

```python
class MultiStepCaseTest(unittest.IsolatedAsyncioTestCase):
    @mock.patch("astrbot_e2e.runner.prepare_instance")
    @mock.patch("astrbot_e2e.runner.AstrBotInstance")
    @mock.patch("astrbot_e2e.runner.OneBotClient")
    @mock.patch("astrbot_e2e.runner.collect_replies", new_callable=mock.AsyncMock)
    @mock.patch("astrbot_e2e.runner.history_bot_replies", new_callable=mock.AsyncMock)
    @mock.patch("astrbot_e2e.runner.time.time", return_value=1234567890)
    async def test_runs_all_steps_and_records_step_index(
        self, time_mock, history, collect, client_cls, instance_cls, prepare
    ):
        def make_client(user_id):
            client = mock.MagicMock()
            client.connect = mock.AsyncMock()
            client.close = mock.AsyncMock()

            async def call(action, params):
                if action == "get_login_info":
                    return {"user_id": user_id}
                if action == "send_group_msg":
                    return {"message_id": 7}
                raise AssertionError("unexpected action: {}".format(action))

            client.call = mock.AsyncMock(side_effect=call)
            return client

        client_cls.side_effect = [make_client("10001"), make_client("10002")]
        instance = mock.MagicMock()
        instance.is_running.return_value = False
        instance.start.return_value = mock.MagicMock(pid=4242)
        instance.wait_ready = mock.AsyncMock()
        instance.stop = mock.MagicMock()
        instance_cls.return_value = instance
        collect.side_effect = [
            [{"text": "帮助信息", "raw": {}}],
            [{"text": "当前会话", "raw": {}}],
        ]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            case_path = tmp_path / "case.json"
            case_path.write_text(
                json.dumps(
                    {
                        "name": "multi-step",
                        "plugin": "astrbot_plugin_e2e_probe",
                        "steps": [
                            {
                                "send": {"group_id": "123456789", "text": "/help"},
                                "expect": {"messages": [{"contains": ["帮助"]}]},
                            },
                            {
                                "send": {"group_id": "123456789", "text": "/info"},
                                "expect": {"messages": [{"contains": ["会话"]}]},
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            summary = await run_case(
                _config(tmp_path / "root"),
                str(case_path),
                reports_dir=str(tmp_path / "reports"),
            )

        self.assertEqual(summary["status"], "PASSED")
        self.assertEqual([item["step"] for item in summary["steps"]], [1, 2])
        self.assertEqual(collect.await_count, 2)
        run_dir = Path(summary["run_dir"])
        self.assertTrue((run_dir / "steps" / "01" / "messages.json").exists())
        self.assertTrue((run_dir / "steps" / "02" / "messages.json").exists())

    @mock.patch("astrbot_e2e.runner.prepare_instance")
    @mock.patch("astrbot_e2e.runner.AstrBotInstance")
    @mock.patch("astrbot_e2e.runner.OneBotClient")
    @mock.patch("astrbot_e2e.runner.collect_replies", new_callable=mock.AsyncMock)
    @mock.patch("astrbot_e2e.runner.history_bot_replies", new_callable=mock.AsyncMock)
    @mock.patch("astrbot_e2e.runner.time.time", return_value=1234567890)
    async def test_stops_after_failed_step(
        self, time_mock, history, collect, client_cls, instance_cls, prepare
    ):
        def make_client(user_id):
            client = mock.MagicMock()
            client.connect = mock.AsyncMock()
            client.close = mock.AsyncMock()

            async def call(action, params):
                if action == "get_login_info":
                    return {"user_id": user_id}
                if action == "send_group_msg":
                    return {"message_id": 7}
                raise AssertionError("unexpected action: {}".format(action))

            client.call = mock.AsyncMock(side_effect=call)
            return client

        client_cls.side_effect = [make_client("10001"), make_client("10002")]
        instance = mock.MagicMock()
        instance.is_running.return_value = False
        instance.start.return_value = mock.MagicMock(pid=4242)
        instance.wait_ready = mock.AsyncMock()
        instance.stop = mock.MagicMock()
        instance_cls.return_value = instance
        collect.return_value = [{"text": "不匹配", "raw": {}}]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            case_path = tmp_path / "case.json"
            case_path.write_text(
                json.dumps(
                    {
                        "name": "multi-step-fail",
                        "plugin": "astrbot_plugin_e2e_probe",
                        "steps": [
                            {
                                "send": {"group_id": "123456789", "text": "/help"},
                                "expect": {"messages": [{"contains": ["帮助"]}]},
                            },
                            {
                                "send": {"group_id": "123456789", "text": "/info"},
                                "expect": {"messages": [{"contains": ["会话"]}]},
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            summary = await run_case(
                _config(tmp_path / "root"),
                str(case_path),
                reports_dir=str(tmp_path / "reports"),
            )

        self.assertEqual(summary["status"], "FAILED")
        self.assertEqual(collect.await_count, 1)
        self.assertEqual([item["step"] for item in summary["steps"]], [1])
```

- [ ] **Step 2：运行测试确认失败**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_runner -v
```
Expected：FAIL（`summary["steps"]` 不存在，或只执行一次）。

- [ ] **Step 3：重构 runner.py**

在 `tools/astrbot_e2e/runner.py` 中做以下改动。

3.1 修改 import：

```python
from .cases import case_steps, load_case, render_case
```

3.2 新增结果序列化与语义判定辅助函数（放在 `_write_assertions` 之后）：

```python
def _result_dict(item: AssertionResult) -> Dict[str, Any]:
    return {
        "kind": item.kind,
        "ok": item.ok,
        "expected": item.expected,
        "actual": item.actual,
        "detail": item.detail,
    }


async def _run_semantic(
    cfg: Dict[str, Any],
    semantic: Dict[str, Any],
    texts: List[str],
    run_dir: Path,
) -> AssertionResult:
    judge_cfg = cfg.get("judge") or {}
    criteria = semantic.get("criteria", "")
    if not judge_cfg.get("base_url") or not judge_cfg.get("model"):
        write_json(
            run_dir / "judge.json",
            {"pass": False, "reason": "LLM 判定未配置", "skipped": True},
        )
        return AssertionResult(
            kind="semantic",
            ok=False,
            expected=criteria,
            actual="\n".join(texts),
            detail="SKIPPED: LLM 判定未配置",
        )
    try:
        verdict = await judge(
            judge_cfg.get("base_url", ""),
            judge_cfg.get("api_key", ""),
            judge_cfg.get("model", ""),
            criteria,
            "\n".join(texts),
            headers=judge_cfg.get("headers"),
        )
        write_json(run_dir / "judge.json", verdict)
        return AssertionResult(
            kind="semantic",
            ok=bool(verdict["pass"]),
            expected=criteria,
            actual="\n".join(texts),
            detail=verdict.get("reason", ""),
        )
    except JudgeError as exc:
        write_json(
            run_dir / "judge.json",
            {"pass": False, "reason": str(exc), "skipped": False},
        )
        return AssertionResult(
            kind="semantic",
            ok=False,
            expected=criteria,
            actual="\n".join(texts),
            detail=str(exc),
        )
```

3.3 新增多轮执行函数（放在 `_error_summary` 之后）：

```python
async def execute_case(
    cfg: Dict[str, Any],
    case: Dict[str, Any],
    run_dir: Path,
    bot_client: OneBotClient,
    sender_client: OneBotClient,
    log_capture: LogCapture,
) -> Any:
    """执行一个用例的全部步骤，返回 (results, step_summaries)。"""
    results: List[AssertionResult] = []
    step_summaries: List[Dict[str, Any]] = []
    timeouts = cfg.get("timeouts") or {}

    for index, step in enumerate(case_steps(case), start=1):
        step_started = time.monotonic()
        step_dir = Path(run_dir) / "steps" / "{:02d}".format(index)
        step_dir.mkdir(parents=True, exist_ok=True)
        send = step["send"]
        expect = step["expect"]

        mark = log_capture.mark()
        send_started_at = int(time.time())
        if send.get("at_bot", True):
            message = build_group_message(send["text"], cfg["bot"]["qq"])
        else:
            message = [{"type": "text", "data": {"text": str(send["text"])}}]
        sent = await sender_client.call(
            "send_group_msg",
            {"group_id": int(send["group_id"]), "message": message},
        )
        write_json(step_dir / "sent.json", {"response": sent, "step": step})

        timeout = float(
            expect.get(
                "timeout_seconds",
                timeouts.get("message_seconds", DEFAULT_MESSAGE_TIMEOUT_SECONDS),
            )
        )
        replies = await collect_replies(
            bot_client, cfg["bot"]["qq"], str(send["group_id"]), timeout
        )
        if not replies:
            replies = await history_bot_replies(
                sender_client,
                cfg["bot"]["qq"],
                str(send["group_id"]),
                since_time=send_started_at - 1,
            )
        texts = [item["text"] for item in replies]
        write_json(step_dir / "messages.json", replies)

        step_results: List[AssertionResult] = []
        if expect.get("messages"):
            step_results.extend(evaluate_messages(texts, expect["messages"]))
        log_text = log_capture.read_since(mark)
        if expect.get("logs"):
            step_results.extend(evaluate_logs(log_text, expect["logs"]))
        (step_dir / "log-window.log").write_text(log_text, encoding="utf-8")

        semantic = expect.get("semantic")
        if semantic and semantic.get("enabled"):
            step_results.append(await _run_semantic(cfg, semantic, texts, step_dir))

        _write_assertions(step_dir, step_results)
        status = _status_from_results(step_results)
        step_summaries.append(
            {
                "step": index,
                "status": status,
                "duration_seconds": round(time.monotonic() - step_started, 3),
                "results": [_result_dict(item) for item in step_results],
            }
        )
        results.extend(step_results)
        if status == "FAILED":
            break

    return results, step_summaries
```

3.4 把 `run_case` 中从 `mark = log_capture.mark()` 到语义判定结束的整段替换为：

```python
        results, step_summaries = await execute_case(
            cfg, case, run_dir, bot_client, sender_client, log_capture
        )
        status = _status_from_results(results)
        duration = time.monotonic() - started
        _write_assertions(run_dir, results)
        return write_summary(
            run_dir,
            case_name,
            status,
            results,
            duration,
            {"run_dir": str(run_dir), "steps": step_summaries},
        )
```

3.5 删除 `run_case` 中已迁移到 `execute_case` 的局部变量（`send`、`mark`、`expect`、`texts` 等），确保没有未使用变量。

- [ ] **Step 4：运行 runner 单测**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_runner -v
```
Expected：全部 PASS（含原有 6 个与新增 2 个）。

- [ ] **Step 5：跑全量单测**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools
```
Expected：全量 PASS；旧用例行为不变。

- [ ] **Step 6：申请提交**

向用户说明 Task 2 改动并请求提交许可。

---

### Task 3：插件源解析（支持任意生产插件）

**Files：**
- Modify：`tools/astrbot_e2e/bootstrap.py:81-101`
- Modify：`tools/astrbot_e2e/config.py:67-106`
- Test：`tools/astrbot_e2e/tests/test_bootstrap.py`
- Test：`tools/astrbot_e2e/tests/test_config.py`

- [ ] **Step 1：写失败测试（bootstrap）**

在 `tools/astrbot_e2e/tests/test_bootstrap.py` 追加：

```python
class ResolvePluginSourceTest(unittest.TestCase):
    def test_prefers_configured_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            configured = tmp_path / "custom-plugin"
            configured.mkdir()
            cfg = {"plugin_sources": {"demo": str(configured)}}
            source = resolve_plugin_source(cfg, tmp_path / "repo", "demo")
            self.assertEqual(source, configured)

    def test_falls_back_to_repo_integrations(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source_dir = tmp_path / "repo" / "integrations" / "astrbot" / "demo"
            source_dir.mkdir(parents=True)
            source = resolve_plugin_source({}, tmp_path / "repo", "demo")
            self.assertEqual(source, source_dir)

    def test_raises_with_all_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with self.assertRaisesRegex(RuntimeError, "插件源目录不存在"):
                resolve_plugin_source({}, tmp_path / "repo", "missing")
```

import 改为：

```python
from astrbot_e2e.bootstrap import prepare_instance, resolve_plugin_source
```

- [ ] **Step 2：写失败测试（config）**

在 `tools/astrbot_e2e/tests/test_config.py` 追加：

```python
    def test_accepts_plugin_sources(self):
        self.write(plugin_sources={"demo": "~/plugins/demo"})
        cfg = load_config(self.path)
        self.assertTrue(cfg["plugin_sources"]["demo"].endswith("plugins/demo"))

    def test_rejects_non_object_plugin_sources(self):
        self.write(plugin_sources=["demo"])
        with self.assertRaisesRegex(ConfigError, "plugin_sources 必须是对象"):
            load_config(self.path)
```

- [ ] **Step 3：运行测试确认失败**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_bootstrap tools.astrbot_e2e.tests.test_config -v
```
Expected：FAIL（`resolve_plugin_source` 不存在；`plugin_sources` 未被校验）。

- [ ] **Step 4：实现 bootstrap 源解析**

在 `tools/astrbot_e2e/bootstrap.py` 顶部增加：

```python
PRODUCTION_PLUGINS_DIR = Path.home() / ".astrbot" / "data" / "plugins"
```

新增函数（放在 `sync_plugins` 之前）：

```python
def resolve_plugin_source(cfg: Dict[str, Any], repo_root: Path, name: str) -> Path:
    """按优先级解析插件源目录，返回第一个存在的候选。"""
    candidates: List[Path] = []
    configured = (cfg.get("plugin_sources") or {}).get(name)
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.append(Path(repo_root) / "integrations" / "astrbot" / name)
    candidates.append(PRODUCTION_PLUGINS_DIR / name)
    candidates.append(Path(repo_root) / "tools" / "astrbot_e2e" / "fixtures" / name)
    for source in candidates:
        if source.is_dir():
            return source
    raise RuntimeError(
        "插件源目录不存在，已尝试: {}".format([str(item) for item in candidates])
    )
```

把 `sync_plugins` 中的源解析替换为：

```python
    for name in plugins:
        source = resolve_plugin_source(cfg, repo_root, name)
        target = target_base / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "tests"),
        )
```

- [ ] **Step 5：实现 config 校验**

在 `tools/astrbot_e2e/config.py` 的 `validate_config` 末尾（`cfg["sender"]["qq"] = sender_qq` 之前）加入：

```python
    sources = cfg.get("plugin_sources")
    if sources is not None:
        if not isinstance(sources, dict):
            raise ConfigError("plugin_sources 必须是对象")
        normalized: Dict[str, str] = {}
        for name, path in sources.items():
            if not str(path or "").strip():
                raise ConfigError("plugin_sources.{} 不能为空".format(name))
            normalized[str(name)] = str(Path(path).expanduser())
        cfg["plugin_sources"] = normalized
```

- [ ] **Step 6：运行测试**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_bootstrap tools.astrbot_e2e.tests.test_config -v
```
Expected：全部 PASS。

- [ ] **Step 7：跑全量单测**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools
```
Expected：全量 PASS。

- [ ] **Step 8：申请提交**

向用户说明 Task 3 改动并请求提交许可。

---

### Task 4：批量执行 run-suite

**Files：**
- Create：`tools/astrbot_e2e/suite.py`
- Modify：`tools/astrbot_e2e/cli.py:26-39,103-140`
- Test：`tools/astrbot_e2e/tests/test_suite.py`（新增）
- Test：`tools/astrbot_e2e/tests/test_cli.py`（修改）

- [ ] **Step 1：写失败测试（suite）**

新建 `tools/astrbot_e2e/tests/test_suite.py`：

```python
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict
from unittest import mock

from astrbot_e2e.suite import run_suite


def _config(root: Path) -> Dict[str, Any]:
    return {
        "test_root": str(root),
        "webui": {"host": "127.0.0.1", "port": 6186, "username": "e2e", "password": "pass"},
        "astrbot": {
            "command": "astrbot",
            "reverse_ws_host": "127.0.0.1",
            "reverse_ws_port": 6198,
            "reverse_ws_token": "token",
            "plugins": ["astrbot_plugin_e2e_probe"],
            "startup_timeout_seconds": 1,
        },
        "bot": {"qq": "10001", "onebot_ws": "ws://127.0.0.1:6200/onebot/v11/ws", "token": "t"},
        "sender": {"qq": "10002", "onebot_ws": "ws://127.0.0.1:6201/onebot/v11/ws", "token": "t"},
        "group_id": "123456789",
        "judge": {},
        "timeouts": {"message_seconds": 1},
    }


def _write_case(path: Path, name: str, text: str) -> None:
    path.write_text(
        json.dumps(
            {
                "name": name,
                "plugin": "astrbot_plugin_e2e_probe",
                "send": {"group_id": "{{group_id}}", "text": text},
                "expect": {"messages": [{"contains": ["ok"]}]},
            }
        ),
        encoding="utf-8",
    )


class RunSuiteTest(unittest.IsolatedAsyncioTestCase):
    @mock.patch("astrbot_e2e.suite.prepare_instance")
    @mock.patch("astrbot_e2e.suite.AstrBotInstance")
    @mock.patch("astrbot_e2e.suite.OneBotClient")
    @mock.patch("astrbot_e2e.suite.execute_case", new_callable=mock.AsyncMock)
    async def test_runs_all_cases_with_one_instance(
        self, execute, client_cls, instance_cls, prepare
    ):
        execute.return_value = (
            [mock.MagicMock(kind="x", ok=True, expected="", actual="", detail="")],
            [{"step": 1, "status": "PASSED", "results": []}],
        )

        def make_client(user_id):
            client = mock.MagicMock()
            client.connect = mock.AsyncMock()
            client.close = mock.AsyncMock()

            async def call(action, params):
                if action == "get_login_info":
                    return {"user_id": user_id}
                raise AssertionError("unexpected action: {}".format(action))

            client.call = mock.AsyncMock(side_effect=call)
            return client

        client_cls.side_effect = [make_client("10001"), make_client("10002")]
        instance = mock.MagicMock()
        instance.is_running.return_value = False
        instance.start.return_value = mock.MagicMock(pid=4242)
        instance.wait_ready = mock.AsyncMock()
        instance.stop = mock.MagicMock()
        instance_cls.return_value = instance

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_dir = tmp_path / "cases"
            cases_dir.mkdir()
            _write_case(cases_dir / "01.json", "case-1", "/help")
            _write_case(cases_dir / "02.json", "case-2", "/info")
            suite = await run_suite(
                _config(tmp_path / "root"),
                [str(cases_dir / "01.json"), str(cases_dir / "02.json")],
                reports_dir=str(tmp_path / "reports"),
            )

        self.assertEqual(suite["status"], "PASSED")
        self.assertEqual(len(suite["cases"]), 2)
        self.assertEqual(execute.await_count, 2)
        instance.start.assert_called_once()
        instance.stop.assert_called_once()
        prepare.assert_called_once()
        self.assertTrue((Path(suite["suite_dir"]) / "report.json").exists())
        self.assertTrue((Path(suite["suite_dir"]) / "report.md").exists())

    async def test_rejects_mixed_plugins(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            first = tmp_path / "01.json"
            second = tmp_path / "02.json"
            _write_case(first, "case-1", "/help")
            second.write_text(
                json.dumps(
                    {
                        "name": "case-2",
                        "plugin": "other_plugin",
                        "send": {"group_id": "{{group_id}}", "text": "/info"},
                        "expect": {"messages": [{"contains": ["ok"]}]},
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "同一插件"):
                await run_suite(
                    _config(tmp_path / "root"),
                    [str(first), str(second)],
                    reports_dir=str(tmp_path / "reports"),
                )
```

- [ ] **Step 2：写失败测试（CLI）**

在 `tools/astrbot_e2e/tests/test_cli.py` 追加：

```python
    @mock.patch("astrbot_e2e.cli._run_suite", new_callable=mock.AsyncMock)
    def test_run_suite_dispatches(self, run_suite_mock):
        run_suite_mock.return_value = 0
        cases_dir = Path(self.tmp.name) / "cases"
        cases_dir.mkdir()
        code = main(
            [
                "run-suite",
                "--config",
                str(self.config),
                "--cases-dir",
                str(cases_dir),
            ]
        )
        self.assertEqual(code, 0)
        run_suite_mock.assert_called_once()
```

- [ ] **Step 3：运行测试确认失败**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_suite tools.astrbot_e2e.tests.test_cli -v
```
Expected：FAIL（`astrbot_e2e.suite` 不存在；`run-suite` 子命令不存在）。

- [ ] **Step 4：实现 suite.py**

新建 `tools/astrbot_e2e/suite.py`：

```python
"""批量用例执行（Suite Runner）。"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .bootstrap import prepare_instance
from .cases import CaseError, load_case, render_case
from .config import mask_config
from .log_capture import LogCapture
from .onebot import OneBotClient
from .orchestrator import AstrBotInstance
from .reloader import login_and_reload
from .reports import create_run_dir, slugify, write_suite_report
from .runner import DEFAULT_REPORTS_DIR, _status_from_results, execute_case

AUTO_HEAL_MAX_ATTEMPTS = 2


def suite_status(cases: List[Dict[str, Any]]) -> str:
    statuses = {item["status"] for item in cases}
    if "ERROR" in statuses:
        return "ERROR"
    if "FAILED" in statuses:
        return "FAILED"
    if "SKIPPED" in statuses:
        return "SKIPPED"
    return "PASSED"


def _append_op(ops: List[str], message: str) -> None:
    ops.append("{} {}".format(time.strftime("%Y-%m-%d %H:%M:%S"), message))


def _start_with_retry(cfg: Dict[str, Any], instance: AstrBotInstance, ops: List[str]) -> None:
    last_exc: Optional[Exception] = None
    for attempt in range(1, AUTO_HEAL_MAX_ATTEMPTS + 1):
        try:
            instance.start()
            return
        except Exception as exc:
            last_exc = exc
            _append_op(ops, "测试实例启动失败（第 {} 次）：{}".format(attempt, exc))
            if instance.is_running():
                instance.stop()
                _append_op(ops, "已停止残留测试实例")
    raise RuntimeError("测试实例启动失败: {}".format(last_exc))


async def run_suite(
    cfg: Dict[str, Any],
    case_paths: List[str],
    reload: bool = False,
    reports_dir: Optional[str] = None,
    attach: bool = False,
    keep_running: bool = False,
) -> Dict[str, Any]:
    started = time.monotonic()
    cases = [render_case(load_case(path), cfg) for path in case_paths]
    if not cases:
        raise CaseError("用例列表为空")
    plugin = cases[0]["plugin"]
    for case in cases:
        if case["plugin"] != plugin:
            raise CaseError(
                "run-suite 只支持同一插件: {} vs {}".format(plugin, case["plugin"])
            )

    suite_dir = create_run_dir(
        reports_dir or str(DEFAULT_REPORTS_DIR), "{}-suite".format(plugin)
    )
    instance = AstrBotInstance(cfg, suite_dir / "instance")
    bot_client = OneBotClient(cfg["bot"]["onebot_ws"], cfg["bot"]["token"])
    sender_client = OneBotClient(cfg["sender"]["onebot_ws"], cfg["sender"]["token"])
    log_capture = LogCapture(Path(cfg["test_root"]) / "data" / "logs" / "astrbot.log")
    ops: List[str] = []
    started_by_runner = False

    try:
        if attach:
            if not instance.is_running():
                raise RuntimeError("--attach 需要测试实例已启动")
            _append_op(ops, "复用已运行的测试实例")
        else:
            prepare_instance(cfg, plugin)
            if instance.is_running():
                instance.stop()
                _append_op(ops, "已停止残留测试实例")
            _start_with_retry(cfg, instance, ops)
            started_by_runner = True
            _append_op(ops, "已启动测试实例 PID {}".format(instance.proc.pid))

        await bot_client.connect()
        await sender_client.connect()
        bot_info = await bot_client.call("get_login_info", {})
        if str(bot_info.get("user_id")) != str(cfg["bot"]["qq"]):
            raise RuntimeError(
                "机器人号不匹配: 期望 {} 实际 {}".format(cfg["bot"]["qq"], bot_info.get("user_id"))
            )
        sender_info = await sender_client.call("get_login_info", {})
        if str(sender_info.get("user_id")) != str(cfg["sender"]["qq"]):
            raise RuntimeError(
                "发送者号不匹配: 期望 {} 实际 {}".format(cfg["sender"]["qq"], sender_info.get("user_id"))
            )
        await instance.wait_ready(bot_client, require_platform_log=not attach)

        case_summaries: List[Dict[str, Any]] = []
        for index, case in enumerate(cases, start=1):
            case_dir = (
                suite_dir
                / "cases"
                / "{:02d}-{}".format(index, slugify(case["name"]))
            )
            case_dir.mkdir(parents=True, exist_ok=True)
            if reload or case.get("reload"):
                try:
                    await login_and_reload(
                        "http://{}:{}".format(cfg["webui"]["host"], cfg["webui"]["port"]),
                        cfg["webui"]["username"],
                        cfg["webui"]["password"],
                        case["plugin"],
                    )
                    _append_op(ops, "已热重载插件 {}".format(case["plugin"]))
                except Exception as exc:
                    _append_op(ops, "热重载失败，改为重启测试实例：{}".format(exc))
                    instance.stop()
                    _start_with_retry(cfg, instance, ops)
                    started_by_runner = True
                await instance.wait_ready(bot_client, require_platform_log=not attach)

            results, step_summaries = await execute_case(
                cfg, case, case_dir, bot_client, sender_client, log_capture
            )
            status = _status_from_results(results)
            case_summaries.append(
                {
                    "case": case["name"],
                    "status": status,
                    "run_dir": str(case_dir),
                    "steps": step_summaries,
                }
            )

        suite = {
            "suite": suite_dir.name,
            "suite_dir": str(suite_dir),
            "plugin": plugin,
            "status": suite_status(case_summaries),
            "duration_seconds": round(time.monotonic() - started, 3),
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "config": mask_config(cfg),
            "cases": case_summaries,
            "ops": ops,
        }
        write_suite_report(suite_dir, suite, cfg)
        return suite
    finally:
        if sender_client is not None:
            await sender_client.close()
        if bot_client is not None:
            await bot_client.close()
        if started_by_runner and not keep_running and instance is not None:
            try:
                instance.stop()
            except Exception:
                pass
```

- [ ] **Step 5：实现 reports.write_suite_report（本 Task 先做最小可用版）**

在 `tools/astrbot_e2e/reports.py` 追加：

```python
def write_suite_report(
    suite_dir: Any,
    suite: Dict[str, Any],
    cfg: Dict[str, Any],
    redact: bool = True,
) -> Dict[str, Any]:
    data = sanitize(suite, cfg, redact=redact)
    write_json(Path(suite_dir) / "report.json", data)
    (Path(suite_dir) / "report.md").write_text(
        render_markdown(data), encoding="utf-8"
    )
    return data
```

同时追加 `sanitize` 与 `render_markdown` 的最小实现（Task 5 会补全脱敏细节）：

```python
def sanitize(value: Any, cfg: Dict[str, Any] = None, redact: bool = True) -> Any:
    return value


def render_markdown(suite: Dict[str, Any]) -> str:
    cases = suite.get("cases") or []
    counts = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "ERROR": 0}
    for item in cases:
        counts[item.get("status", "ERROR")] = counts.get(item.get("status", "ERROR"), 0) + 1
    lines = [
        "# AstrBot 插件测试报告",
        "",
        "## 摘要（Summary）",
        "",
        "- 插件：{}".format(suite.get("plugin", "")),
        "- 状态：{}".format(suite.get("status", "")),
        "- 用例：{} 个（通过 {} / 失败 {} / 跳过 {} / 错误 {}）".format(
            len(cases),
            counts.get("PASSED", 0),
            counts.get("FAILED", 0),
            counts.get("SKIPPED", 0),
            counts.get("ERROR", 0),
        ),
        "- 耗时：{} 秒".format(suite.get("duration_seconds", 0)),
        "",
        "## 用例结果（Cases）",
        "",
        "| # | 用例 | 状态 | 证据 |",
        "| --- | --- | --- | --- |",
    ]
    for index, item in enumerate(cases, start=1):
        lines.append(
            "| {} | {} | {} | `{}` |".format(
                index, item.get("case", ""), item.get("status", ""), item.get("run_dir", "")
            )
        )
    lines.append("")
    return "\n".join(lines)
```

- [ ] **Step 6：实现 CLI run-suite**

在 `tools/astrbot_e2e/cli.py` 中：

6.1 修改 import：

```python
from .runner import run_case
from .suite import run_suite
```

6.2 在 `build_parser` 中新增：

```python
    suite = _add_subcommand(sub, "run-suite")
    suite.add_argument("--cases-dir", required=True)
    suite.add_argument("--plugin", default=None)
    suite.add_argument("--reload", action="store_true")
    suite.add_argument("--attach", action="store_true")
    suite.add_argument("--keep-running", action="store_true")
```

6.3 新增函数：

```python
def _case_paths(cases_dir: str, plugin: Optional[str]) -> List[str]:
    directory = Path(cases_dir).expanduser()
    if not directory.is_dir():
        raise ValueError("用例目录不存在: {}".format(directory))
    paths = sorted(
        str(path)
        for path in directory.glob("*.json")
        if not path.name.startswith("_")
    )
    if not paths:
        raise ValueError("用例目录为空: {}".format(directory))
    if plugin:
        keep = []
        for path in paths:
            if load_case(path)["plugin"] != plugin:
                raise ValueError(
                    "用例 {} 的插件不是 {}".format(path, plugin)
                )
            keep.append(path)
        paths = keep
    return paths


async def _run_suite(args: argparse.Namespace, cfg: Dict[str, Any]) -> int:
    try:
        paths = _case_paths(args.cases_dir, args.plugin)
        suite = await run_suite(
            cfg,
            paths,
            reload=args.reload,
            attach=args.attach,
            keep_running=args.keep_running,
        )
    except Exception as exc:
        print("批量执行异常: {}".format(exc), file=sys.stderr)
        return 2
    print(
        "{}: {} ({})".format(
            suite["plugin"], suite["status"], suite["suite_dir"]
        )
    )
    if suite["status"] == "PASSED":
        return 0
    if suite["status"] == "ERROR":
        return 2
    if suite["status"] == "SKIPPED":
        return 3
    return 1
```

6.4 在 `main` 中新增分发：

```python
    if args.command == "run-suite":
        return asyncio.run(_run_suite(args, cfg))
```

6.5 引入 `load_case`：

```python
from .cases import load_case
```

- [ ] **Step 7：运行测试**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_suite tools.astrbot_e2e.tests.test_cli -v
```
Expected：全部 PASS。

- [ ] **Step 8：跑全量单测**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools
```
Expected：全量 PASS。

- [ ] **Step 9：申请提交**

向用户说明 Task 4 改动并请求提交许可。

---

### Task 5：报告聚合与脱敏

**Files：**
- Modify：`tools/astrbot_e2e/reports.py`
- Test：`tools/astrbot_e2e/tests/test_reports.py`

- [ ] **Step 1：写失败测试**

在 `tools/astrbot_e2e/tests/test_reports.py` 追加：

```python
class SanitizeTest(unittest.TestCase):
    def test_masks_qq_tokens_and_long_text(self):
        cfg = {
            "bot": {"qq": "3254276668", "token": "bot-token"},
            "sender": {"qq": "1961618848", "token": "sender-token"},
            "webui": {"password": "secret-pass"},
            "judge": {"api_key": "judge-key"},
        }
        data = {
            "message": "机器人 3254276668 与发送者 1961618848 通信",
            "token": "bot-token",
            "nested": {"password": "secret-pass", "long": "x" * 900},
        }
        result = sanitize(data, cfg)
        text = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("3254276668", text)
        self.assertNotIn("1961618848", text)
        self.assertNotIn("bot-token", text)
        self.assertNotIn("secret-pass", text)
        self.assertIn("***", text)
        self.assertIn("truncated", text)

    def test_redact_false_keeps_original(self):
        cfg = {"bot": {"qq": "3254276668", "token": "bot-token"}}
        data = {"message": "3254276668", "token": "bot-token"}
        self.assertEqual(sanitize(data, cfg, redact=False), data)
```

import 改为：

```python
from astrbot_e2e.reports import sanitize
```

`test_reports.py` 顶部已有 `import json`，无需重复添加。

- [ ] **Step 2：运行测试确认失败**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_reports -v
```
Expected：FAIL（`sanitize` 未脱敏、未截断）。

- [ ] **Step 3：实现脱敏**

把 `tools/astrbot_e2e/reports.py` 中最小版 `sanitize` 替换为：

```python
SECRET_KEYS = frozenset({"password", "token", "api_key", "jwt_secret", "secret"})
LONG_TEXT_LIMIT = 500


def _qq_ids(cfg: Dict[str, Any] = None) -> list:
    if not cfg:
        return []
    ids = []
    for section in ("bot", "sender"):
        value = (cfg.get(section) or {}).get("qq")
        if value:
            ids.append(str(value))
    return ids


def _secrets(cfg: Dict[str, Any] = None) -> list:
    if not cfg:
        return []
    found = []
    for section in ("webui", "bot", "sender", "judge", "astrbot"):
        source = cfg.get(section) or {}
        if not isinstance(source, dict):
            continue
        for key, value in source.items():
            if key.lower() in SECRET_KEYS and value:
                found.append(str(value))
    return found


def _mask_qq(text: str, qq_ids: list) -> str:
    for qq in qq_ids:
        if not qq or qq not in text:
            continue
        if len(qq) <= 4:
            masked = "***"
        else:
            masked = qq[:2] + "*" * (len(qq) - 4) + qq[-2:]
        text = text.replace(qq, masked)
    return text


def sanitize(value: Any, cfg: Dict[str, Any] = None, redact: bool = True) -> Any:
    if not redact:
        return value
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if str(key).lower() in SECRET_KEYS:
                result[key] = "***"
            else:
                result[key] = sanitize(item, cfg, redact)
        return result
    if isinstance(value, list):
        return [sanitize(item, cfg, redact) for item in value]
    if isinstance(value, str):
        text = value
        for secret in _secrets(cfg):
            text = text.replace(secret, "***")
        text = _mask_qq(text, _qq_ids(cfg))
        if len(text) > LONG_TEXT_LIMIT:
            text = text[:LONG_TEXT_LIMIT] + "...[truncated {} chars]".format(
                len(text) - LONG_TEXT_LIMIT
            )
        return text
    return value
```

- [ ] **Step 4：增强 Markdown 报告**

把 `render_markdown` 替换为带失败摘要与未覆盖项的版本：

```python
def render_markdown(suite: Dict[str, Any]) -> str:
    cases = suite.get("cases") or []
    counts = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "ERROR": 0}
    for item in cases:
        status = item.get("status", "ERROR")
        counts[status] = counts.get(status, 0) + 1
    lines = [
        "# AstrBot 插件测试报告",
        "",
        "## 摘要（Summary）",
        "",
        "- 插件：{}".format(suite.get("plugin", "")),
        "- 状态：{}".format(suite.get("status", "")),
        "- 开始时间：{}".format(suite.get("started_at", "")),
        "- 用例：{} 个（通过 {} / 失败 {} / 跳过 {} / 错误 {}）".format(
            len(cases),
            counts.get("PASSED", 0),
            counts.get("FAILED", 0),
            counts.get("SKIPPED", 0),
            counts.get("ERROR", 0),
        ),
        "- 耗时：{} 秒".format(suite.get("duration_seconds", 0)),
        "",
        "## 用例结果（Cases）",
        "",
        "| # | 用例 | 状态 | 证据 |",
        "| --- | --- | --- | --- |",
    ]
    for index, item in enumerate(cases, start=1):
        lines.append(
            "| {} | {} | {} | `{}` |".format(
                index, item.get("case", ""), item.get("status", ""), item.get("run_dir", "")
            )
        )

    failed = [item for item in cases if item.get("status") in ("FAILED", "ERROR")]
    lines.extend(["", "## 失败摘要（Failures）", ""])
    if not failed:
        lines.append("无。")
    else:
        for item in failed:
            lines.append("### {}".format(item.get("case", "")))
            lines.append("")
            lines.append("- 状态：{}".format(item.get("status", "")))
            lines.append("- 证据：`{}`".format(item.get("run_dir", "")))
            for step in item.get("steps") or []:
                if step.get("status") == "PASSED":
                    continue
                for result in step.get("results") or []:
                    if result.get("ok"):
                        continue
                    lines.append(
                        "- 步骤 {} / {}：{}".format(
                            step.get("step"), result.get("kind"), result.get("detail", "")
                        )
                    )
            lines.append("")

    lines.extend(["", "## 操作记录（Ops）", ""])
    ops = suite.get("ops") or []
    if not ops:
        lines.append("无。")
    else:
        for item in ops:
            lines.append("- {}".format(item))
    lines.append("")
    return "\n".join(lines)
```

- [ ] **Step 5：运行测试**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_reports -v
```
Expected：全部 PASS。

- [ ] **Step 6：跑全量单测**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools
```
Expected：全量 PASS。

- [ ] **Step 7：申请提交**

向用户说明 Task 5 改动并请求提交许可。

---

### Task 6：doctor 增强与自愈可见性

**Files：**
- Modify：`tools/astrbot_e2e/orchestrator.py:109-120,213-217`
- Modify：`tools/astrbot_e2e/cli.py:58-74`
- Test：`tools/astrbot_e2e/tests/test_orchestrator.py`
- Test：`tools/astrbot_e2e/tests/test_cli.py`

- [ ] **Step 1：写失败测试（端口公开方法）**

在 `tools/astrbot_e2e/tests/test_orchestrator.py` 追加：

```python
class PortEndpointsTest(unittest.TestCase):
    def test_exposes_port_endpoints(self):
        cfg = {
            "test_root": "/tmp/test-root",
            "webui": {"host": "127.0.0.1", "port": 6186},
            "astrbot": {"reverse_ws_host": "127.0.0.1", "reverse_ws_port": 6198},
        }
        instance = AstrBotInstance(cfg, Path("/tmp/run"))
        endpoints = instance.port_endpoints()
        self.assertEqual(
            [(label, port) for label, _, port in endpoints],
            [("WebUI", 6186), ("OneBot 反向 WS", 6198)],
        )
```

- [ ] **Step 2：写失败测试（doctor 插件源与端口）**

在 `tools/astrbot_e2e/tests/test_cli.py` 追加：

```python
    @mock.patch("astrbot_e2e.cli._check_login", new_callable=mock.AsyncMock)
    @mock.patch("astrbot_e2e.cli.resolve_plugin_source")
    @mock.patch("astrbot_e2e.cli.port_open", return_value=False)
    def test_doctor_reports_missing_plugin_source(self, port_open, resolve, check_login):
        check_login.return_value = 0
        resolve.side_effect = RuntimeError("插件源目录不存在")
        (Path(self.tmp.name) / "root" / ".astrbot").mkdir(parents=True)
        code = main(["doctor", "--config", str(self.config)])
        self.assertEqual(code, 2)
```

- [ ] **Step 3：运行测试确认失败**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_orchestrator tools.astrbot_e2e.tests.test_cli -v
```
Expected：FAIL（`port_endpoints` 不存在；doctor 未检查插件源）。

- [ ] **Step 4：实现 orchestrator 公开方法**

把 `tools/astrbot_e2e/orchestrator.py` 的 `_port_endpoints` 改为：

```python
    def port_endpoints(self):
        webui = self.cfg.get("webui") or {}
        reverse_host = str(self.cfg["astrbot"].get("reverse_ws_host", "127.0.0.1"))
        return [
            ("WebUI", "127.0.0.1", int(webui.get("port", 6186))),
            ("OneBot 反向 WS", reverse_host, int(self.cfg["astrbot"].get("reverse_ws_port", 6198))),
        ]

    def _port_endpoints(self):
        return self.port_endpoints()
```

- [ ] **Step 5：实现 doctor 增强**

在 `tools/astrbot_e2e/cli.py` 中：

5.1 修改 import：

```python
from .bootstrap import prepare_instance, resolve_plugin_source
from .orchestrator import AstrBotInstance, port_open
```

5.2 新增函数（放在 `_doctor` 之前）：

```python
def _check_plugin_sources(cfg: Dict[str, Any]) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    for name in cfg["astrbot"]["plugins"]:
        try:
            source = resolve_plugin_source(cfg, repo_root, name)
        except RuntimeError as exc:
            print("插件源不可用: {}".format(exc))
            return 2
        print("插件源 OK: {} -> {}".format(name, source))
    return 0


def _check_test_ports(cfg: Dict[str, Any]) -> int:
    instance = AstrBotInstance(cfg, Path(cfg["test_root"]) / "bootstrap-run")
    running = instance.is_running()
    for label, host, port in instance.port_endpoints():
        if port_open(host, port):
            if running:
                print("{} {} 由测试实例占用（已运行）".format(label, port))
            else:
                print("{} {} 被未知进程占用；请先排查，不自动终止".format(label, port))
                return 2
    return 0
```

5.3 在 `_doctor` 中、登录检查之后加入：

```python
    code = _check_plugin_sources(cfg)
    if code:
        return code
    code = _check_test_ports(cfg)
    if code:
        return code
```

- [ ] **Step 6：运行测试**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest tools.astrbot_e2e.tests.test_orchestrator tools.astrbot_e2e.tests.test_cli -v
```
Expected：全部 PASS。

- [ ] **Step 7：跑全量单测**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools
```
Expected：全量 PASS。

- [ ] **Step 8：申请提交**

向用户说明 Task 6 改动并请求提交许可。

---

### Task 7：skill 骨架与环境探测

**Files：**
- Create：`SKILL_ROOT/scripts/engine_path.py`
- Create：`SKILL_ROOT/scripts/probe_env.py`
- Create：`SKILL_ROOT/tests/__init__.py`
- Create：`SKILL_ROOT/tests/test_probe_env.py`

> 后续 Task 均在 `SKILL_ROOT`（person-config）内创建；本仓库副本在 Task 11 统一同步。

- [ ] **Step 1：创建目录**

Run:
```bash
mkdir -p "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e"/{scripts,tests,references,templates}
touch "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e/scripts/__init__.py"
touch "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e/tests/__init__.py"
```

- [ ] **Step 2：写 engine_path.py**

```python
"""定位执行引擎：优先项目内 tools/astrbot_e2e，其次 vendor 快照。"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional


def engine_dir(start: Optional[Path] = None) -> Optional[Path]:
    skill_root = Path(__file__).resolve().parents[1]
    current = Path(start or Path.cwd()).resolve()
    for base in [current, *current.parents]:
        candidate = base / "tools" / "astrbot_e2e"
        if (candidate / "__init__.py").exists():
            return candidate
    vendor = skill_root / "vendor" / "astrbot_e2e"
    if (vendor / "__init__.py").exists():
        return vendor
    return None


def ensure_engine_importable(start: Optional[Path] = None) -> Path:
    engine = engine_dir(start)
    if engine is None:
        raise RuntimeError(
            "未找到 astrbot_e2e 执行引擎；请在本仓库运行，或先执行 scripts/sync_vendor.py"
        )
    package_root = engine.parent
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))
    return engine
```

- [ ] **Step 3：写失败测试（probe）**

新建 `SKILL_ROOT/tests/test_probe_env.py`：

```python
import json
import tempfile
import unittest
from pathlib import Path

from scripts.probe_env import build_profile


class ProbeEnvTest(unittest.TestCase):
    def test_builds_profile_with_injected_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            plugin = home / ".astrbot" / "data" / "plugins" / "demo_plugin"
            plugin.mkdir(parents=True)
            napcat = (
                home
                / "Library/Containers/com.tencent.qq/Data/Documents/napcat"
            )
            napcat.mkdir(parents=True)
            (napcat / "package.json").write_text(
                json.dumps({"name": "napcat", "version": "4.18.28"}),
                encoding="utf-8",
            )
            profile = build_profile(None, home)
        self.assertEqual(profile["schema_version"], 1)
        self.assertEqual(profile["napcat"]["version"], "4.18.28")
        self.assertIn("demo_plugin", profile["plugins"]["available"])
        self.assertIn("ports", profile)
        self.assertIn("config", profile)

    def test_config_info_does_not_leak_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            config = home / "config.json"
            config.write_text(
                json.dumps(
                    {
                        "test_root": str(home / "root"),
                        "bot": {"qq": "10001", "token": "secret-token"},
                        "sender": {"qq": "10002", "token": "secret-token"},
                        "webui": {"password": "secret-pass"},
                        "group_id": "123456789",
                    }
                ),
                encoding="utf-8",
            )
            profile = build_profile(config, home)
        text = json.dumps(profile, ensure_ascii=False)
        self.assertNotIn("secret-token", text)
        self.assertNotIn("secret-pass", text)
        self.assertEqual(profile["config"]["bot_qq"], "10001")
```

- [ ] **Step 4：运行测试确认失败**

Run:
```bash
cd "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e" && PYTHONPATH=. python3 -m unittest tests.test_probe_env -v
```
Expected：FAIL（`scripts.probe_env` 不存在）。

- [ ] **Step 5：实现 probe_env.py**

```python
"""探测本机 AstrBot 插件测试环境（Environment Probe）。"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

SCHEMA_VERSION = 1
QQ_APP = Path("/Applications/QQ.app")
DEFAULT_PORTS = {
    "production_webui": 6185,
    "production_onebot": 6199,
    "production_napcat": 6099,
    "test_webui": 6186,
    "test_onebot": 6198,
    "test_sender_napcat": 6098,
    "test_bot_onebot": 6200,
    "test_sender_onebot": 6201,
}


def _paths(home: Path) -> Dict[str, Path]:
    return {
        "qq_app": QQ_APP,
        "qq_container": home
        / "Library/Containers/com.tencent.qq/Data/Library/Application Support/QQ",
        "napcat_install": home
        / "Library/Containers/com.tencent.qq/Data/Documents/napcat",
        "astrbot_data": home / ".astrbot",
    }


def _run(argv, cwd=None, timeout=10.0) -> Optional[str]:
    try:
        proc = subprocess.run(
            argv,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def _port_open(host: str, port: int, timeout: float = 0.3) -> bool:
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


def astrbot_info(paths: Dict[str, Path]) -> Dict[str, Any]:
    exe = shutil.which("astrbot")
    if not exe:
        fallback = Path.home() / ".local/bin/astrbot"
        exe = str(fallback) if fallback.exists() else ""
    version = None
    if exe:
        output = _run([exe, "--version"], cwd=paths["astrbot_data"])
        if output and "version" in output.lower():
            version = output.split()[-1]
    data_root = paths["astrbot_data"]
    return {
        "command": exe or "astrbot",
        "available": bool(exe),
        "version": version,
        "data_root": str(data_root),
        "data_root_exists": data_root.exists(),
    }


def napcat_info(paths: Dict[str, Path]) -> Dict[str, Any]:
    install = paths["napcat_install"]
    version = None
    package = install / "package.json"
    if package.exists():
        try:
            version = json.loads(package.read_text(encoding="utf-8")).get("version")
        except (OSError, ValueError):
            version = None
    workdirs = []
    for name in ("NapCat", "NapCat-e2e"):
        workdir = paths["qq_container"] / name
        if workdir.exists():
            workdirs.append(str(workdir))
    return {
        "install_dir": str(install),
        "available": install.exists(),
        "version": version,
        "workdirs": workdirs,
    }


def qq_info(paths: Dict[str, Path]) -> Dict[str, Any]:
    output = _run(["ps", "-axo", "command="]) or ""
    running = "QQ.app/Contents/MacOS/QQ" in output
    app = paths["qq_app"]
    return {"app": str(app), "app_exists": app.exists(), "running": running}


def plugin_info(paths: Dict[str, Path]) -> Dict[str, Any]:
    directory = paths["astrbot_data"] / "data" / "plugins"
    available = []
    if directory.exists():
        available = sorted(item.name for item in directory.iterdir() if item.is_dir())
    return {"production_dir": str(directory), "available": available}


def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    config_path = Path(path).expanduser()
    try:
        data = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return {"_error": str(exc), "_path": str(config_path)}
    if not isinstance(data, dict):
        return {"_error": "配置顶层不是对象", "_path": str(config_path)}
    data["_path"] = str(config_path)
    return data


def config_info(cfg: Dict[str, Any]) -> Dict[str, Any]:
    if not cfg:
        return {}
    return {
        "path": cfg.get("_path"),
        "error": cfg.get("_error"),
        "test_root": cfg.get("test_root"),
        "bot_qq": (cfg.get("bot") or {}).get("qq"),
        "sender_qq": (cfg.get("sender") or {}).get("qq"),
        "group_id": cfg.get("group_id"),
        "webui_port": (cfg.get("webui") or {}).get("port"),
        "reverse_ws_port": (cfg.get("astrbot") or {}).get("reverse_ws_port"),
    }


def port_info(cfg: Dict[str, Any]) -> Dict[str, Any]:
    ports = dict(DEFAULT_PORTS)
    if cfg:
        ports["test_webui"] = int((cfg.get("webui") or {}).get("port", 6186))
        ports["test_onebot"] = int((cfg.get("astrbot") or {}).get("reverse_ws_port", 6198))
    return {
        name: {"port": port, "open": _port_open("127.0.0.1", port)}
        for name, port in ports.items()
    }


def build_profile(config_path: Optional[str], home: Path) -> Dict[str, Any]:
    paths = _paths(Path(home))
    cfg = load_config(config_path)
    return {
        "schema_version": SCHEMA_VERSION,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "is_macos": platform.system() == "Darwin",
        },
        "python": {
            "version": sys.version.split()[0],
            "executable": sys.executable,
        },
        "astrbot": astrbot_info(paths),
        "napcat": napcat_info(paths),
        "qq": qq_info(paths),
        "plugins": plugin_info(paths),
        "ports": port_info(cfg),
        "config": config_info(cfg),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="探测 AstrBot 插件测试环境")
    parser.add_argument("--config", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--home", default=None, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    home = Path(args.home) if args.home else Path.home()
    profile = build_profile(args.config, home)
    text = json.dumps(profile, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6：运行测试**

Run:
```bash
cd "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e" && PYTHONPATH=. python3 -m unittest tests.test_probe_env -v
```
Expected：PASS。

- [ ] **Step 7：真实探测一次**

Run:
```bash
cd "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e" && python3 scripts/probe_env.py --config "$REPO_ROOT/tools/astrbot_e2e/config.local.json"
```
Expected：输出 JSON；`astrbot.version` 为 `4.29.3`，`napcat.version` 为 `4.18.28`，`config` 中不含 token/password。

- [ ] **Step 8：记录结果，不提交**

把探测结果摘要写入本任务的执行记录；person-config 与本仓库均不 commit，等待用户统一决定。

---

### Task 8：插件功能清单提取

**Files：**
- Create：`SKILL_ROOT/scripts/discover_plugin.py`
- Create：`SKILL_ROOT/tests/test_discover_plugin.py`

- [ ] **Step 1：写失败测试**

新建 `SKILL_ROOT/tests/test_discover_plugin.py`：

```python
import json
import tempfile
import unittest
from pathlib import Path

from scripts.discover_plugin import build_features


class DiscoverPluginTest(unittest.TestCase):
    def _make_plugin(self, home: Path) -> Path:
        plugin = home / "demo_plugin"
        plugin.mkdir()
        (plugin / "metadata.yaml").write_text(
            "name: demo_plugin\n"
            "display_name: 演示插件\n"
            "desc: 用于测试\n"
            "version: 0.1.0\n"
            "author: tester\n"
            "support_platforms:\n"
            "  - aiocqhttp\n",
            encoding="utf-8",
        )
        (plugin / "_conf_schema.json").write_text(
            json.dumps({"enabled": {"type": "bool", "default": True}}),
            encoding="utf-8",
        )
        (plugin / "main.py").write_text(
            "from astrbot.api.event import filter\n"
            "@filter.command('help')\n"
            "async def help_cmd(event):\n"
            "    pass\n"
            "@filter.event_message_type(filter.EventMessageType.ALL)\n"
            "async def on_message(event):\n"
            "    pass\n",
            encoding="utf-8",
        )
        (plugin / "README.md").write_text(
            "# demo\n\n- `/info` 查看信息\n- `/pwd` 查看目录\n",
            encoding="utf-8",
        )
        return plugin

    def test_extracts_commands_events_and_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = self._make_plugin(Path(tmp))
            result = build_features(plugin)
        self.assertEqual(result["plugin"], "demo_plugin")
        commands = {
            item["trigger"] for item in result["features"] if item["kind"] == "command"
        }
        self.assertTrue({"/help", "/info", "/pwd"}.issubset(commands))
        kinds = {item["kind"] for item in result["features"]}
        self.assertIn("event", kinds)
        self.assertIn("config", kinds)
        self.assertEqual(result["metadata"]["version"], "0.1.0")

    def test_marks_event_features_as_manual(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = self._make_plugin(Path(tmp))
            result = build_features(plugin)
        event = next(
            item for item in result["features"] if item["kind"] == "event"
        )
        self.assertEqual(event["testability"], "manual")

    def test_deduplicates_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = self._make_plugin(Path(tmp))
            readme = plugin / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8") + "\n- `/help` 再写一次\n",
                encoding="utf-8",
            )
            result = build_features(plugin)
        helps = [
            item
            for item in result["features"]
            if item["kind"] == "command" and item["trigger"] == "/help"
        ]
        self.assertEqual(len(helps), 1)
```

- [ ] **Step 2：运行测试确认失败**

Run:
```bash
cd "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e" && PYTHONPATH=. python3 -m unittest tests.test_discover_plugin -v
```
Expected：FAIL（模块不存在）。

- [ ] **Step 3：实现 discover_plugin.py**

```python
"""从插件源码与文档提取功能清单（Feature Inventory）。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

COMMAND_PATTERNS = (
    re.compile(r"@filter\.command\(\s*[\"']([^\"']+)[\"']"),
    re.compile(r"@filter\.command_group\(\s*[\"']([^\"']+)[\"']"),
    re.compile(r"register_command\(\s*[\"']([^\"']+)[\"']"),
)
EVENT_PATTERN = re.compile(
    r"@filter\.event_message_type\(\s*([A-Za-z0-9_.]+)"
)
HOOK_PATTERN = re.compile(
    r"@filter\.(on_llm_request|on_decorating_result|on_after_message_sent)"
)
README_COMMAND_PATTERN = re.compile(r"`(/[A-Za-z0-9_!]+)`")
DANGEROUS_COMMANDS = frozenset(
    {"/cc", "/goon", "/!", "/new", "/end", "/initbase", "/approve", "/deny"}
)


def parse_metadata(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    current = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current:
            data.setdefault(current, []).append(line[4:].strip())
            continue
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value:
                data[key] = value
                current = None
            else:
                data[key] = []
                current = key
    return data


def _slugify(value: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z_-]+", "-", value).strip("-")
    return slug or "feature"


def scan_python(plugin_dir: Path) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[Dict[str, str]]]:
    commands: List[Dict[str, str]] = []
    events: List[Dict[str, str]] = []
    hooks: List[Dict[str, str]] = []
    for path in sorted(plugin_dir.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = str(path.relative_to(plugin_dir))
        for pattern in COMMAND_PATTERNS:
            for match in pattern.findall(text):
                commands.append({"command": "/" + match.lstrip("/"), "source": relative})
        for match in EVENT_PATTERN.findall(text):
            events.append({"event": match, "source": relative})
        for match in HOOK_PATTERN.findall(text):
            hooks.append({"hook": match, "source": relative})
    return commands, events, hooks


def scan_readme(plugin_dir: Path) -> List[Dict[str, str]]:
    readme = plugin_dir / "README.md"
    if not readme.exists():
        return []
    commands: List[Dict[str, str]] = []
    for line_no, line in enumerate(readme.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        for match in README_COMMAND_PATTERN.finditer(line):
            commands.append(
                {
                    "command": match.group(1),
                    "source": "README.md:{}".format(line_no),
                    "line": line.strip()[:200],
                }
            )
    return commands


def build_features(plugin_dir: Path) -> Dict[str, Any]:
    plugin_dir = Path(plugin_dir)
    metadata_path = plugin_dir / "metadata.yaml"
    metadata = (
        parse_metadata(metadata_path.read_text(encoding="utf-8", errors="replace"))
        if metadata_path.exists()
        else {}
    )
    schema_path = plugin_dir / "_conf_schema.json"
    schema = {}
    if schema_path.exists():
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
        except ValueError:
            schema = {}

    decorator_commands, events, hooks = scan_python(plugin_dir)
    readme_commands = scan_readme(plugin_dir)

    features: List[Dict[str, Any]] = []
    seen = set()
    for item in readme_commands + decorator_commands:
        command = item["command"]
        if command in seen:
            continue
        seen.add(command)
        features.append(
            {
                "id": "command-" + _slugify(command.lstrip("/")),
                "title": "命令 {}".format(command),
                "kind": "command",
                "trigger": command,
                "expected": "",
                "testability": "text",
                "risk": "high" if command in DANGEROUS_COMMANDS else "medium",
                "notes": item.get("line") or item.get("source", ""),
            }
        )

    seen_events = set()
    for item in events:
        if item["event"] in seen_events:
            continue
        seen_events.add(item["event"])
        features.append(
            {
                "id": "event-" + _slugify(item["event"]),
                "title": "事件 {}".format(item["event"]),
                "kind": "event",
                "trigger": item["event"],
                "expected": "",
                "testability": "manual",
                "risk": "medium",
                "notes": item["source"],
            }
        )

    seen_hooks = set()
    for item in hooks:
        if item["hook"] in seen_hooks:
            continue
        seen_hooks.add(item["hook"])
        features.append(
            {
                "id": "hook-" + _slugify(item["hook"]),
                "title": "钩子 {}".format(item["hook"]),
                "kind": "hook",
                "trigger": item["hook"],
                "expected": "",
                "testability": "manual",
                "risk": "medium",
                "notes": item["source"],
            }
        )

    if isinstance(schema, dict):
        for key in schema:
            features.append(
                {
                    "id": "config-" + _slugify(str(key)),
                    "title": "配置 {}".format(key),
                    "kind": "config",
                    "trigger": str(key),
                    "expected": "",
                    "testability": "config",
                    "risk": "low",
                    "notes": "_conf_schema.json",
                }
            )

    plugin_name = metadata.get("name") or plugin_dir.name
    return {
        "plugin": plugin_name,
        "plugin_dir": str(plugin_dir),
        "metadata": metadata,
        "features": features,
        "summary": {
            "total": len(features),
            "commands": sum(1 for item in features if item["kind"] == "command"),
            "events": sum(1 for item in features if item["kind"] == "event"),
            "hooks": sum(1 for item in features if item["kind"] == "hook"),
            "config": sum(1 for item in features if item["kind"] == "config"),
            "manual": sum(
                1 for item in features if item["testability"] in ("manual", "config")
            ),
        },
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="提取 AstrBot 插件功能清单")
    parser.add_argument("--plugin-dir", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)
    result = build_features(Path(args.plugin_dir).expanduser())
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4：运行测试**

Run:
```bash
cd "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e" && PYTHONPATH=. python3 -m unittest tests.test_discover_plugin -v
```
Expected：PASS。

- [ ] **Step 5：对 cc_qq 真实执行一次**

Run:
```bash
cd "$REPO_ROOT" && python3 "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e/scripts/discover_plugin.py" --plugin-dir integrations/astrbot/astrbot_plugin_cc_qq --output /tmp/cc_qq-features.json
```
Expected：`summary.commands` ≥ 10；`/help`、`/info`、`/pwd`、`/new`、`/cc`、`/end` 均在 features 中；`/cc`、`/new`、`/end` 的 `risk` 为 `high`。

---

### Task 9：用例草案生成

**Files：**
- Create：`SKILL_ROOT/scripts/gen_cases.py`
- Create：`SKILL_ROOT/tests/test_gen_cases.py`

- [ ] **Step 1：写失败测试**

新建 `SKILL_ROOT/tests/test_gen_cases.py`：

```python
import json
import tempfile
import unittest
from pathlib import Path

from scripts.gen_cases import generate_cases


def _features():
    return {
        "plugin": "demo_plugin",
        "features": [
            {
                "id": "command-help",
                "title": "命令 /help",
                "kind": "command",
                "trigger": "/help",
                "testability": "text",
                "risk": "medium",
            },
            {
                "id": "command-cc",
                "title": "命令 /cc",
                "kind": "command",
                "trigger": "/cc",
                "testability": "text",
                "risk": "high",
            },
            {
                "id": "command-cd",
                "title": "命令 /cd",
                "kind": "command",
                "trigger": "/cd <目录>",
                "testability": "text",
                "risk": "high",
            },
            {
                "id": "event-all",
                "title": "事件 ALL",
                "kind": "event",
                "trigger": "ALL",
                "testability": "manual",
                "risk": "medium",
            },
        ],
    }


class GenCasesTest(unittest.TestCase):
    def test_generates_safe_command_cases_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = generate_cases(_features(), out, timeout=30)
            self.assertEqual(result["generated"], 1)
            case = json.loads((out / "command-help.json").read_text(encoding="utf-8"))
        self.assertEqual(case["plugin"], "demo_plugin")
        self.assertEqual(case["send"]["text"], "/help")
        self.assertEqual(case["send"]["group_id"], "{{group_id}}")
        self.assertIn("messages", case["expect"])

    def test_records_skipped_reasons(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = generate_cases(_features(), out, timeout=30)
            skipped = (out / "SKIPPED.md").read_text(encoding="utf-8")
        self.assertEqual(result["skipped"], 3)
        self.assertIn("/cc", skipped)
        self.assertIn("/cd", skipped)
        self.assertIn("event", skipped.lower())
```

- [ ] **Step 2：运行测试确认失败**

Run:
```bash
cd "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e" && PYTHONPATH=. python3 -m unittest tests.test_gen_cases -v
```
Expected：FAIL（模块不存在）。

- [ ] **Step 3：实现 gen_cases.py**

```python
"""根据功能清单生成用例草案（Case Generation）。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

DANGEROUS_COMMANDS = frozenset(
    {"/cc", "/goon", "/!", "/new", "/end", "/initbase", "/approve", "/deny"}
)
ARG_PLACEHOLDER = re.compile(r"[<\[{].*?[>\]}]")
SAFE_REPLY_PATTERN = r"\S"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z_-]+", "-", value).strip("-")
    return slug or "case"


def _generatable(feature: Dict[str, Any]) -> Tuple[bool, str]:
    if feature.get("kind") != "command":
        return False, "非命令功能，需人工设计用例"
    trigger = str(feature.get("trigger") or "").strip()
    if not trigger:
        return False, "缺少触发文本"
    base = trigger.split()[0]
    if base in DANGEROUS_COMMANDS:
        return False, "命令会启动代理或改变会话状态，需人工确认用例"
    if ARG_PLACEHOLDER.search(trigger):
        return False, "命令需要参数，需人工补充"
    return True, ""


def _case_for(feature: Dict[str, Any], plugin: str, timeout: float) -> Dict[str, Any]:
    trigger = str(feature["trigger"]).strip()
    return {
        "name": "命令 {}".format(trigger),
        "plugin": plugin,
        "send": {
            "group_id": "{{group_id}}",
            "text": trigger,
            "at_bot": True,
        },
        "expect": {
            "timeout_seconds": timeout,
            "messages": [{"regex": SAFE_REPLY_PATTERN}],
        },
    }


def generate_cases(
    features: Dict[str, Any], output_dir: Path, timeout: float = 30.0
) -> Dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plugin = str(features.get("plugin") or "unknown_plugin")
    generated = 0
    skipped: List[Tuple[str, str]] = []

    for feature in features.get("features") or []:
        ok, reason = _generatable(feature)
        if not ok:
            skipped.append((feature.get("title") or feature.get("id") or "?", reason))
            continue
        case = _case_for(feature, plugin, timeout)
        path = output_dir / (_slugify(feature.get("id") or case["name"]) + ".json")
        path.write_text(
            json.dumps(case, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        generated += 1

    lines = [
        "# 未自动生成的用例",
        "",
        "| 功能 | 原因 |",
        "| --- | --- |",
    ]
    for title, reason in skipped:
        lines.append("| {} | {} |".format(title, reason))
    lines.append("")
    (output_dir / "SKIPPED.md").write_text("\n".join(lines), encoding="utf-8")

    return {
        "plugin": plugin,
        "output_dir": str(output_dir),
        "generated": generated,
        "skipped": len(skipped),
        "skipped_items": [{"title": title, "reason": reason} for title, reason in skipped],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="生成 AstrBot 插件用例草案")
    parser.add_argument("--features", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(argv)
    features = json.loads(Path(args.features).read_text(encoding="utf-8-sig"))
    result = generate_cases(features, Path(args.out), args.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4：运行测试**

Run:
```bash
cd "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e" && PYTHONPATH=. python3 -m unittest tests.test_gen_cases -v
```
Expected：PASS。

- [ ] **Step 5：对 cc_qq 生成一次**

Run:
```bash
cd "$REPO_ROOT" && python3 "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e/scripts/gen_cases.py" --features /tmp/cc_qq-features.json --out /tmp/cc_qq-cases
```
Expected：`/help`、`/info`、`/pwd`、`/cd list` 等安全命令生成 JSON；`/cc`、`/new`、`/end`、`/goon`、`/approve`、`/deny` 出现在 `SKIPPED.md`。

---

### Task 10：skill 文档、模板与报告脚本

**Files：**
- Create：`SKILL_ROOT/SKILL.md`
- Create：`SKILL_ROOT/README.md`
- Create：`SKILL_ROOT/scripts/aggregate_report.py`
- Create：`SKILL_ROOT/templates/config.template.json`
- Create：`SKILL_ROOT/templates/case.template.json`
- Create：`SKILL_ROOT/templates/report.template.md`
- Create：`SKILL_ROOT/references/environment-probe.md`
- Create：`SKILL_ROOT/references/compatibility-matrix.md`
- Create：`SKILL_ROOT/references/self-healing.md`
- Create：`SKILL_ROOT/references/coverage-analysis.md`
- Create：`SKILL_ROOT/references/report-template.md`
- Create：`SKILL_ROOT/references/safety-rules.md`

- [ ] **Step 1：写 SKILL.md**

```markdown
---
name: astrbot-plugin-e2e
description: "对 AstrBot 插件做真实 QQ 端到端验证：探测本机环境、拉起两个 QQ 与独立测试 AstrBot、按被测插件生成功能清单与用例、执行多轮用例、产出脱敏报告，并对测试侧故障自愈。触发词：测试 AstrBot 插件、插件端到端测试、e2e、验证插件功能、跑插件回归、生成测试报告、双 QQ 测试。适用于 macOS；其他平台给出适配思路。"
---

# AstrBot 插件端到端测试（AstrBot Plugin E2E）

## 什么时候用

- 用户要验证某个 AstrBot 插件的真实 QQ 行为。
- 用户要跑插件回归、生成测试报告。
- 用户要把测试流程复用到另一台 macOS 机器。

## 前置条件

1. macOS，已安装 AstrBot 与 NapCat。
2. 两个 QQ 号：一个作为机器人（bot），一个作为测试发送者（sender）。
3. 一个专用测试群。
4. 用户能手动扫码登录两个 QQ。

## 主流程（S0–S7）

### S0 环境探测

```bash
python3 scripts/probe_env.py --config <config.local.json> --output environment.json
```

- 读取 `environment.json`，检查 `astrbot.available`、`napcat.available`、`config.error`。
- 关键项缺失时停止，并给出修复命令；不要猜。

### S1 安全闸

- 识别生产实例（默认 `~/.astrbot`，端口 `6185/6199`）。
- **暂停/恢复生产必须用户明确确认**；执行前备份生产配置。
- 不杀未知进程；只停止有 PID 文件且校验属于测试实例的进程。

### S2 起服务

- 指导用户执行 `~/.qq-e2e/start-e2e.sh`（或等价脚本）拉起 2 个 NapCat + 1 个测试 AstrBot。
- 等待用户扫码登录两个 QQ。
- 用 `doctor` 验证两个账号在线与插件源可用。

### S3 覆盖分析

```bash
python3 scripts/discover_plugin.py --plugin-dir <plugin_dir> --output features.json
```

- 把功能清单摘要给用户确认；重点列出 `risk=high` 与 `testability=manual/config` 的项。
- 用户确认后才继续；`--yes` 可跳过确认。

### S4 生成用例

```bash
python3 scripts/gen_cases.py --features features.json --out cases/ --timeout 30
```

- 自动生成的用例只覆盖安全命令。
- 多轮功能（如 `/new` → `/cc` → `/end`）由 AI 根据 `features.json` 手写，写入 `cases/manual/`。
- 向用户展示生成与跳过清单。

### S5 执行

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run-suite \
  --cases-dir cases/ --config <config.local.json> --attach
```

- 失败时先按 `references/self-healing.md` 自愈；同一故障最多自动修复 2 次。
- 环境类失败停止并报告；插件类失败继续跑完剩余用例。

### S6 报告

- `run-suite` 已生成 `report.json` 与 `report.md`。
- 检查 `report.md` 的失败摘要、未覆盖项、操作记录。
- **默认脱敏**；不要关闭脱敏，除非用户明确要求。

### S7 收尾

- 恢复生产 AstrBot 需用户确认。
- 按用户意愿保留或停止测试实例。
- 报告保留在本地，不入库。

## 铁律

1. 生产侧操作必须用户确认。
2. 不自动扫码登录。
3. 不自动修改被测插件源码。
4. 不杀未知进程。
5. 不可测项标 `SKIPPED` 并写原因，不静默丢弃。
6. 报告默认脱敏。

## 参考

- `references/environment-probe.md`
- `references/compatibility-matrix.md`
- `references/self-healing.md`
- `references/coverage-analysis.md`
- `references/report-template.md`
- `references/safety-rules.md`
```

- [ ] **Step 2：写 README.md**

README 至少包含：

- 一键安装/同步方式（`sync_vendor.py` 与本仓库副本）。
- 配置模板复制步骤。
- 每个脚本的用法与退出码。
- macOS 已验证版本：AstrBot `4.29.3`、NapCat `4.18.28`。
- 已知边界与排障表。

- [ ] **Step 3：写 aggregate_report.py**

```python
"""重新生成 suite 报告（Aggregate Report）。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from engine_path import ensure_engine_importable


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="重新生成 AstrBot 插件测试报告")
    parser.add_argument("--suite-dir", required=True)
    parser.add_argument("--config", default=None)
    parser.add_argument("--no-redact", action="store_true")
    args = parser.parse_args(argv)

    suite_dir = Path(args.suite_dir).expanduser()
    report = suite_dir / "report.json"
    if not report.exists():
        print("报告不存在: {}".format(report), file=sys.stderr)
        return 2
    ensure_engine_importable()
    from astrbot_e2e.config import load_config
    from astrbot_e2e.reports import write_suite_report

    cfg = load_config(args.config) if args.config else {}
    suite = json.loads(report.read_text(encoding="utf-8-sig"))
    write_suite_report(suite_dir, suite, cfg, redact=not args.no_redact)
    print(str(suite_dir / "report.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

> 注意：`report.json` 可能已经是脱敏后的内容；重新生成不会恢复原文。原始证据在各 `cases/*/steps/*` 目录。

- [ ] **Step 4：写 templates**

`config.template.json`：

```json
{
  "test_root": "~/.astrbot-e2e",
  "webui": {
    "host": "127.0.0.1",
    "port": 6186,
    "username": "e2e",
    "password": "<webui-password>"
  },
  "astrbot": {
    "command": "astrbot",
    "reverse_ws_host": "127.0.0.1",
    "reverse_ws_port": 6198,
    "reverse_ws_token": "<reverse-ws-token>",
    "plugins": ["<plugin-id>"],
    "startup_timeout_seconds": 120
  },
  "plugin_sources": {
    "<plugin-id>": "<absolute-plugin-source-dir>"
  },
  "bot": {
    "qq": "<bot-qq>",
    "onebot_ws": "ws://127.0.0.1:6200/onebot/v11/ws",
    "token": "<bot-token>"
  },
  "sender": {
    "qq": "<sender-qq>",
    "onebot_ws": "ws://127.0.0.1:6201/onebot/v11/ws",
    "token": "<sender-token>"
  },
  "group_id": "<dedicated-test-group-id>",
  "judge": {
    "base_url": "<openai-compatible-base-url>",
    "api_key": "<judge-api-key>",
    "model": "<judge-model>"
  },
  "timeouts": {
    "message_seconds": 60,
    "reload_seconds": 120,
    "log_window_padding_seconds": 5
  }
}
```

`case.template.json`：

```json
{
  "name": "<case-name>",
  "plugin": "<plugin-id>",
  "steps": [
    {
      "send": {
        "group_id": "{{group_id}}",
        "text": "/help",
        "at_bot": true
      },
      "expect": {
        "timeout_seconds": 30,
        "messages": [{"contains": ["<expected-substring>"]}]
      }
    }
  ]
}
```

`report.template.md` 使用 Task 5 的 `render_markdown` 输出结构，作为人工补充说明的骨架。

- [ ] **Step 5：写 references**

每个文件必须包含以下内容：

`environment-probe.md`
- macOS 路径：AstrBot `~/.astrbot`、NapCat `~/Library/Containers/com.tencent.qq/Data/Documents/napcat`、QQ 容器路径。
- 探测项：OS、Python、AstrBot 版本、NapCat 版本、QQ 进程、端口、插件目录。
- Linux/Windows 差异：systemd/docker、路径、进程检查方式。

`compatibility-matrix.md`
- AstrBot 4.x：WebUI 登录与 reload 接口、日志路径。
- NapCat 4.x：`NAPCAT_WORKDIR`、WebUI 端口、OneBot 反向 WS。
- 已验证组合：AstrBot `4.29.3` + NapCat `4.18.28` + macOS。
- 未知组合：先跑 `probe_env.py` 与 `doctor`，不要假设接口一致。

`self-healing.md`
- 自动动作：停止残留测试实例、启动重试、reload 失败重启、插件副本重同步、历史消息窗口调整。
- 需确认：生产暂停/恢复、生产配置修改、删除数据。
- 禁止：杀未知进程、改插件源码。
- 自愈上限：同一故障 2 次。

`coverage-analysis.md`
- 输入：`metadata.yaml`、`_conf_schema.json`、`*.py`、`README.md`。
- 输出：`features.json` 字段说明。
- 高风险命令（`/cc`、`/new`、`/end`、`/goon`、`/approve`、`/deny`、`/!`）必须人工确认。
- 不可测项标记方式。

`report-template.md`
- 摘要、用例结果、失败摘要、操作记录、未覆盖项。
- 脱敏字段清单。

`safety-rules.md`
- 生产/测试实例隔离要求。
- 备份规则。
- 只停止自有 PID。
- 报告与配置不入库。

- [ ] **Step 6：校验文档**

Run:
```bash
cd "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e" && python3 - <<'PY'
from pathlib import Path
required = [
    "SKILL.md", "README.md",
    "references/environment-probe.md", "references/compatibility-matrix.md",
    "references/self-healing.md", "references/coverage-analysis.md",
    "references/report-template.md", "references/safety-rules.md",
    "templates/config.template.json", "templates/case.template.json",
    "templates/report.template.md",
]
missing = [item for item in required if not Path(item).exists()]
print("missing:", missing)
raise SystemExit(1 if missing else 0)
PY
```
Expected：`missing: []`。

---

### Task 11：vendor 快照与安装登记

**Files：**
- Create：`SKILL_ROOT/scripts/sync_vendor.py`
- Create：`SKILL_ROOT/tests/test_sync_vendor.py`
- Create：`REPO_SKILL/`（person-config → 本仓库副本）
- Modify：`/Users/mobius/Documents/111AAA-code/person-config/skills/catalog.json`

- [ ] **Step 1：写失败测试**

新建 `SKILL_ROOT/tests/test_sync_vendor.py`：

```python
import tempfile
import unittest
from pathlib import Path

from scripts.sync_vendor import sync_vendor


class SyncVendorTest(unittest.TestCase):
    def test_copies_engine_and_writes_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "tools" / "astrbot_e2e"
            source.mkdir(parents=True)
            (source / "__init__.py").write_text("", encoding="utf-8")
            (source / "reports").mkdir()
            (source / "reports" / "secret.json").write_text("{}", encoding="utf-8")
            dest = tmp_path / "vendor" / "astrbot_e2e"
            manifest = sync_vendor(source, dest)
            self.assertTrue((dest / "__init__.py").exists())
            self.assertFalse((dest / "reports").exists())
            self.assertEqual(manifest["source"], str(source))
            self.assertIn("sha256", manifest)
```

- [ ] **Step 2：运行测试确认失败**

Run:
```bash
cd "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e" && PYTHONPATH=. python3 -m unittest tests.test_sync_vendor -v
```
Expected：FAIL（模块不存在）。

- [ ] **Step 3：实现 sync_vendor.py**

```python
"""把执行引擎同步为 skill 的 vendor 快照。"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from pathlib import Path

IGNORE = shutil.ignore_patterns(
    "__pycache__", "*.pyc", "reports", "config.local.json", "tests"
)


def _tree_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if not item.is_file():
            continue
        relative = item.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def sync_vendor(source: Path, dest: Path) -> dict:
    source = Path(source).expanduser().resolve()
    dest = Path(dest).expanduser().resolve()
    if not (source / "__init__.py").exists():
        raise RuntimeError("源目录不是 astrbot_e2e 包: {}".format(source))
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest, ignore=IGNORE)
    manifest = {
        "source": str(source),
        "synced_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "sha256": _tree_hash(dest),
    }
    (dest / "VERSION.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="同步 astrbot_e2e 执行引擎到 vendor")
    parser.add_argument("--source", required=True)
    parser.add_argument("--dest", required=True)
    args = parser.parse_args(argv)
    manifest = sync_vendor(Path(args.source), Path(args.dest))
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4：运行测试**

Run:
```bash
cd "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e" && PYTHONPATH=. python3 -m unittest tests.test_sync_vendor -v
```
Expected：PASS。

- [ ] **Step 5：生成 vendor 快照**

Run:
```bash
cd "$REPO_ROOT" && python3 "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e/scripts/sync_vendor.py" --source tools/astrbot_e2e --dest "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e/vendor/astrbot_e2e"
```
Expected：`vendor/astrbot_e2e/` 存在，含 `VERSION.json`；不含 `reports/`、`config.local.json`、`tests/`。

- [ ] **Step 6：同步到本仓库副本**

Run:
```bash
rsync -a --delete \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e/" \
  .claude/skills/astrbot-plugin-e2e/
```
Expected：`.claude/skills/astrbot-plugin-e2e/SKILL.md` 存在。

- [ ] **Step 7：登记 catalog.json**

Run:
```bash
python3 - <<'PY'
import hashlib
import json
from pathlib import Path

root = Path.home() / "Documents/111AAA-code/person-config"
skill = root / "skills/custom/astrbot-plugin-e2e"
catalog_path = root / "skills/catalog.json"

def tree_hash(path):
    ignored = {".git", "node_modules", "dist", "out", "__pycache__", ".pytest_cache", "gen-images"}
    digest = hashlib.sha256()
    files = []
    for item in path.rglob("*"):
        if not item.is_file():
            continue
        relative = item.relative_to(path)
        if any(part in ignored for part in relative.parts):
            continue
        if relative.name in (".DS_Store", ".env") or relative.suffix == ".vsix":
            continue
        files.append((relative.as_posix(), item))
    for name, item in sorted(files):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(item.read_bytes()).hexdigest().encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()

data = json.loads(catalog_path.read_text(encoding="utf-8"))
data.setdefault("categories", {}).setdefault("custom", [])
if "astrbot-plugin-e2e" not in data["categories"]["custom"]:
    data["categories"]["custom"].append("astrbot-plugin-e2e")
data.setdefault("skills", {})["astrbot-plugin-e2e"] = {
    "source": "skills/custom/astrbot-plugin-e2e",
    "category": "custom",
    "version": "0.1.0",
    "origin": "person-config:skills/custom/astrbot-plugin-e2e",
    "targets": ["claude", "codex"],
    "mode": "copy",
    "sha256": tree_hash(skill),
    "copies": [".claude/skills/astrbot-plugin-e2e"],
}
catalog_path.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print("catalog updated")
PY
```
Expected：`catalog updated`。

- [ ] **Step 8：对账**

Run:
```bash
cd "$HOME/Documents/111AAA-code/person-config" && python3 sync/sync.py --only astrbot-plugin-e2e --dry-run
```
Expected：输出包含该 skill，无 schema 错误（`--apply` 未实现，不要使用）。

- [ ] **Step 9：申请提交**

分别向用户申请本仓库与 person-config 的提交许可；未批准时保留改动。

---

### Task 12：端到端验收

> 本 Task 需要用户参与：启动三服务并扫码登录两个 QQ。执行前先确认用户在场。

**Files：**
- Create：`tools/astrbot_e2e/cases/cc_qq_multi_turn.json`（示例多轮用例）

- [ ] **Step 1：准备多轮示例用例**

新建 `tools/astrbot_e2e/cases/cc_qq_multi_turn.json`：

```json
{
  "name": "cc-qq 多轮安全命令",
  "plugin": "astrbot_plugin_cc_qq",
  "steps": [
    {
      "send": {"group_id": "{{group_id}}", "text": "/pwd", "at_bot": true},
      "expect": {"timeout_seconds": 30, "messages": [{"regex": "\\S"}]}
    },
    {
      "send": {"group_id": "{{group_id}}", "text": "/help", "at_bot": true},
      "expect": {"timeout_seconds": 30, "messages": [{"contains": ["/new"]}]}
    }
  ]
}
```

- [ ] **Step 2：用户拉起服务并登录**

由用户执行：
```bash
bash ~/.qq-e2e/start-e2e.sh
```
Expected：iTerm2 打开 3 个标签；用户完成两个 QQ 扫码登录。

- [ ] **Step 3：doctor**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor --config tools/astrbot_e2e/config.local.json
```
Expected：`doctor OK`，两个账号匹配，插件源 OK，测试端口由测试实例占用。

- [ ] **Step 4：跑多轮用例**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run \
  --attach --config tools/astrbot_e2e/config.local.json \
  --case tools/astrbot_e2e/cases/cc_qq_multi_turn.json
```
Expected：`PASSED`；`steps/01`、`steps/02` 各有 `messages.json`。

- [ ] **Step 5：跑生成用例 suite**

Run:
```bash
cd "$REPO_ROOT" && python3 "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e/scripts/discover_plugin.py" \
  --plugin-dir integrations/astrbot/astrbot_plugin_cc_qq --output /tmp/cc_qq-features.json
python3 "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e/scripts/gen_cases.py" \
  --features /tmp/cc_qq-features.json --out /tmp/cc_qq-cases
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run-suite \
  --cases-dir /tmp/cc_qq-cases --config tools/astrbot_e2e/config.local.json --attach --keep-running
```
Expected：`report.json` 与 `report.md` 生成；安全命令用例 PASSED 或给出明确失败证据；`SKIPPED.md` 列出高风险命令。

- [ ] **Step 6：验证脱敏**

Run:
```bash
python3 - <<'PY'
import json
from pathlib import Path
import glob
reports = sorted(glob.glob("tools/astrbot_e2e/reports/*-suite/report.json"))
assert reports, "未找到 suite 报告"
text = Path(reports[-1]).read_text(encoding="utf-8")
cfg = json.loads(Path("tools/astrbot_e2e/config.local.json").read_text(encoding="utf-8-sig"))
for qq in (cfg["bot"]["qq"], cfg["sender"]["qq"]):
    assert qq not in text, "报告未脱敏 QQ: {}".format(qq)
for key in ("token", "password", "api_key"):
    value = (cfg.get("webui") or {}).get(key) or (cfg.get("judge") or {}).get(key)
    if value:
        assert value not in text, "报告未脱敏 {}".format(key)
print("脱敏通过:", reports[-1])
PY
```
Expected：`脱敏通过`。

- [ ] **Step 7：自愈演练（端口占用）**

说明：先停掉测试实例，再让未知进程占用测试端口，验证工具不误杀。

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli stop-instance \
  --config tools/astrbot_e2e/config.local.json
python3 -m http.server 6186 >/tmp/port-occupy.log 2>&1 &
echo $! > /tmp/port-occupy.pid
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run-suite \
  --cases-dir /tmp/cc_qq-cases --config tools/astrbot_e2e/config.local.json
kill "$(cat /tmp/port-occupy.pid)"
```
Expected：命令返回非 0，提示 `端口已被占用` 或 `WebUI 6186 被未知进程占用`；`http.server` 进程仍存活（工具未杀未知进程），随后由命令手动结束。

- [ ] **Step 8：自愈演练（残留测试实例）**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli start-instance \
  --plugin astrbot_plugin_cc_qq --config tools/astrbot_e2e/config.local.json
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run-suite \
  --cases-dir /tmp/cc_qq-cases --config tools/astrbot_e2e/config.local.json
```
Expected：suite 自动停止残留实例并重新启动；`report.md` 的「操作记录」包含 `已停止残留测试实例`。

- [ ] **Step 9：收尾**

- 由用户确认是否恢复生产 AstrBot。
- 若不需要常驻，执行：
```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli stop-instance \
  --config tools/astrbot_e2e/config.local.json
```
- 记录验收证据路径到 `state.md` 与 `checkpoints.md`。

---

### Task 13：文档与收尾

**Files：**
- Modify：`tools/astrbot_e2e/README.md`
- Modify：`.devflow/astrbot-plugin-e2e/backlog.md`
- Modify：`.devflow/astrbot-plugin-e2e/state.md`
- Modify：`.devflow/astrbot-plugin-e2e/checkpoints.md`
- Modify：`.devflow/astrbot-plugin-e2e/decision-log.md`

- [ ] **Step 1：更新工具 README**

补充：

- `run-suite` 命令与退出码。
- 多轮 `steps` 用例格式与示例。
- `plugin_sources` 配置项与源解析优先级。
- 报告脱敏行为与 `--no-redact`。
- 自愈动作与边界。

- [ ] **Step 2：更新 backlog**

- 把「需求 2」条目标记为已实施/已验证，并写证据路径。
- 新增未决项：skill 真源与副本同步责任、报告保留天数、Linux/Windows 验证。

- [ ] **Step 3：更新 state 与 checkpoint**

- `state.md`：当前阶段改为 `Verify/Close`；写入验收证据。
- `checkpoints.md`：新增本阶段条目；超过 3 条时归档最旧条目。

- [ ] **Step 4：更新 decision-log**

记录实施中发现的新决策（例如多轮上限、自愈重试次数、报告脱敏规则）。

- [ ] **Step 5：最终验证**

Run:
```bash
PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools
cd "$HOME/Documents/111AAA-code/person-config/skills/custom/astrbot-plugin-e2e" && PYTHONPATH=. python3 -m unittest discover -s tests -t . -v
```
Expected：两套测试全部 PASS。

- [ ] **Step 6：申请提交**

向用户申请本仓库与 person-config 的提交许可；提交信息使用中文。

---

## 3. 依赖关系

```text
Task 0
  -> Task 1 -> Task 2
  -> Task 3
  -> Task 4 (依赖 Task 2)
  -> Task 5 (依赖 Task 4)
  -> Task 6 (依赖 Task 3)
  -> Task 7 -> Task 8 -> Task 9 -> Task 10
  -> Task 11 (依赖 Task 4/5/7/8/9/10)
  -> Task 12 (依赖 Task 4/5/6/9/11)
  -> Task 13 (依赖 Task 12)
```

可并行：Task 3 与 Task 1；Task 8 与 Task 9 可在 Task 7 完成后并行设计，但 Task 9 的测试不依赖 Task 8 的真实输出。

---

## 4. 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 多轮步骤导致旧用例回归 | `case_steps` 统一形状；保留旧 `send/expect` 测试 |
| `run-suite` 一次启动后状态串扰 | 每个用例独立目录与日志 mark；失败不终止 suite |
| 插件源解析误用生产目录 | 只读复制；`plugin_sources` 显式优先；不写生产目录 |
| 报告泄露 QQ/Token | `sanitize` 单测 + 验收脚本扫描 |
| 自愈误杀进程 | 只停止 PID 文件校验通过的测试实例；未知端口只报告 |
| person-config 与仓库副本漂移 | 只改真源；副本由 `rsync --delete` 生成；catalog 记录 hash |
| vendor 快照过期 | `sync_vendor.py` 写入 `VERSION.json`；Task 11 重新生成 |

---

## 5. 完成定义（Definition of Done）

1. `tools/astrbot_e2e` 全量单测通过；新增 `steps`、`run-suite`、插件源解析、脱敏、doctor 增强均有测试。
2. skill 的 `scripts/` 与 `tests/` 全部通过；`probe_env.py` 在本机输出正确版本。
3. `discover_plugin.py` 对 cc_qq 提取出 ≥10 个命令；`gen_cases.py` 生成安全用例并列出跳过项。
4. `run-suite` 对 cc_qq 生成 `report.json` + `report.md`，默认脱敏。
5. 多轮用例真实跑通（`/pwd` → `/help`）。
6. 自愈演练：端口被未知进程占用时不误杀；残留测试实例被自动停止。
7. skill 真源在 person-config，仓库副本同步，`catalog.json` 已登记。
8. 所有文档更新完成；**未擅自 commit**。

---

## 6. 执行记录

留空，由执行代理在每个 Task 完成后追加：

```text
Task 0：<日期> 基线测试 <数量> OK；HEAD <hash>
Task 1：...
```
