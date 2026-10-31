"""单个用例的执行流水线（Case Runner）。"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .assertions import (
    AssertionResult,
    evaluate_images,
    evaluate_logs,
    evaluate_messages,
)
from .bootstrap import prepare_instance
from .cases import case_steps, load_case, render_case
from .llm_judge import JudgeError, judge
from .log_capture import LogCapture
from .onebot import OneBotClient, build_group_message, collect_replies, history_bot_replies
from .orchestrator import AstrBotInstance
from .reloader import login_and_reload
from .reports import create_run_dir, write_json, write_summary

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORTS_DIR = REPO_ROOT / "tools" / "astrbot_e2e" / "reports"
INVALID_CASE_NAME = "invalid-case"
DEFAULT_MESSAGE_TIMEOUT_SECONDS = 60


def _status_from_results(results: List[AssertionResult]) -> str:
    """按断言结果计算用例状态。

    优先级：任意非跳过断言失败 → FAILED；否则存在跳过 → SKIPPED；
    否则有结果 → PASSED；否则 FAILED。
    """
    failed = [item for item in results if not item.ok and "SKIPPED" not in item.detail]
    skipped = any("SKIPPED" in item.detail for item in results)
    if failed:
        return "FAILED"
    if skipped:
        return "SKIPPED"
    if results:
        return "PASSED"
    return "FAILED"


def _write_assertions(run_dir: Path, results: List[AssertionResult]) -> None:
    write_json(run_dir / "assertions.json", [_result_dict(item) for item in results])


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


def _error_summary(
    run_dir: Optional[Path],
    case_name: str,
    results: List[AssertionResult],
    exc: Exception,
    started: float,
) -> Dict[str, Any]:
    duration = time.monotonic() - started
    if run_dir is None:
        # 连运行目录都无法创建时，仍返回 ERROR 字典供 CLI 映射为退出码 2。
        return {
            "case": case_name,
            "status": "ERROR",
            "duration_seconds": round(duration, 3),
            "assertions": [],
            "error": repr(exc),
            "run_dir": None,
        }
    _write_assertions(run_dir, results)
    return write_summary(
        run_dir,
        case_name,
        "ERROR",
        results,
        duration,
        {"error": repr(exc), "run_dir": str(run_dir)},
    )


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
    last_message_id = ""

    for index, step in enumerate(case_steps(case), start=1):
        step_started = time.monotonic()
        step_dir = Path(run_dir) / "steps" / "{:02d}".format(index)
        step_dir.mkdir(parents=True, exist_ok=True)
        send = step["send"]
        expect = step["expect"]

        mark = log_capture.mark()
        send_started_at = int(time.time())
        reply_to = send.get("reply_to")
        if reply_to == "last":
            reply_to = last_message_id or None
        if send.get("at_bot", True):
            message = build_group_message(
                send.get("text", ""),
                cfg["bot"]["qq"],
                image=send.get("image"),
                reply_to=reply_to,
            )
        else:
            message = []
            if reply_to:
                message.append({"type": "reply", "data": {"id": str(reply_to)}})
            if str(send.get("text") or "").strip():
                message.append({"type": "text", "data": {"text": str(send["text"])}})
            if send.get("image"):
                message.append({"type": "image", "data": {"file": str(send["image"])}})
        sent = await sender_client.call(
            "send_group_msg",
            {"group_id": int(send["group_id"]), "message": message},
        )
        if isinstance(sent, dict) and sent.get("message_id"):
            last_message_id = str(sent["message_id"])
        write_json(step_dir / "sent.json", {"response": sent, "step": step})

        timeout = float(
            expect.get(
                "timeout_seconds",
                timeouts.get("message_seconds", DEFAULT_MESSAGE_TIMEOUT_SECONDS),
            )
        )
        replies = await collect_replies(
            bot_client,
            cfg["bot"]["qq"],
            str(send["group_id"]),
            timeout,
            since_time=send_started_at - 1,
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
        if expect.get("images"):
            image_count = sum(int(item.get("images") or 0) for item in replies)
            step_results.append(evaluate_images(image_count, expect["images"]))
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


async def run_case(
    cfg: Dict[str, Any],
    case_path: str,
    reload: bool = False,
    reports_dir: Optional[str] = None,
    attach: bool = False,
) -> Dict[str, Any]:
    started = time.monotonic()
    results: List[AssertionResult] = []
    case_name = INVALID_CASE_NAME
    run_dir: Optional[Path] = None
    instance: Optional[AstrBotInstance] = None
    bot_client: Optional[OneBotClient] = None
    sender_client: Optional[OneBotClient] = None
    started_by_runner = False

    try:
        case = render_case(load_case(case_path), cfg)
        case_name = case["name"]
        run_dir = create_run_dir(reports_dir or str(DEFAULT_REPORTS_DIR), case_name)

        instance = AstrBotInstance(cfg, run_dir)
        bot_client = OneBotClient(cfg["bot"]["onebot_ws"], cfg["bot"]["token"])
        sender_client = OneBotClient(cfg["sender"]["onebot_ws"], cfg["sender"]["token"])
        log_capture = LogCapture(Path(cfg["test_root"]) / "data" / "logs" / "astrbot.log")

        if attach:
            if not instance.is_running():
                raise RuntimeError("--attach 需要测试实例已启动")
        else:
            prepare_instance(cfg, case["plugin"])
            if instance.is_running():
                instance.stop()
            instance.start()
            started_by_runner = True

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

        if reload or case.get("reload"):
            try:
                await login_and_reload(
                    "http://{}:{}".format(cfg["webui"]["host"], cfg["webui"]["port"]),
                    cfg["webui"]["username"],
                    cfg["webui"]["password"],
                    case["plugin"],
                )
            except Exception:
                # 设计稿要求：WebUI 重载失败时用重启兜底，不静默跳过。
                instance.stop()
                instance.start()
                started_by_runner = True
            await instance.wait_ready(bot_client, require_platform_log=not attach)

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
    except Exception as exc:
        if run_dir is None:
            # 用例无效时仍尽量落盘；名称使用 fallback，避免依赖非法用例内容。
            try:
                run_dir = create_run_dir(
                    reports_dir or str(DEFAULT_REPORTS_DIR), INVALID_CASE_NAME
                )
            except Exception:
                run_dir = None
        return _error_summary(run_dir, case_name, results, exc, started)
    finally:
        if sender_client is not None:
            await sender_client.close()
        if bot_client is not None:
            await bot_client.close()
        if started_by_runner and instance is not None:
            try:
                instance.stop()
            except Exception:
                # 停止失败不应覆盖已生成的 summary。
                pass
