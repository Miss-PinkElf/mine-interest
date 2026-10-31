"""用例加载与校验（Test Case）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ALLOWED_TOP = frozenset({"name", "plugin", "reload", "send", "expect", "steps"})
ALLOWED_SEND = frozenset({"group_id", "text", "at_bot", "image", "reply_to"})
ALLOWED_EXPECT = frozenset({"timeout_seconds", "messages", "logs", "semantic", "images"})
ALLOWED_STEP = frozenset({"send", "expect"})
EXPECT_MATCHER_KEYS = ("messages", "logs", "semantic", "images")
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
    if not str(send.get("text") or "").strip() and not send.get("image"):
        raise CaseError("{}.text 与 image 至少填一个".format(label))


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
