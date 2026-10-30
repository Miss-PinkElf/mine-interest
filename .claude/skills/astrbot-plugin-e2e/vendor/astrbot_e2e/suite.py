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
    redact: bool = True,
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
        write_suite_report(suite_dir, suite, cfg, redact=redact)
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
