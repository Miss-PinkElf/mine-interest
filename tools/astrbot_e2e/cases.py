"""用例加载与校验（Test Case）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ALLOWED_TOP = frozenset({"name", "plugin", "reload", "send", "expect"})
ALLOWED_SEND = frozenset({"group_id", "text", "at_bot"})
ALLOWED_EXPECT = frozenset({"timeout_seconds", "messages", "logs", "semantic"})
EXPECT_MATCHER_KEYS = ("messages", "logs", "semantic")
EXPECT_LIST_KEYS = ("messages", "logs")


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
    send = case.get("send")
    if not isinstance(send, dict):
        raise CaseError("send 必须是对象")
    unknown_send = set(send) - ALLOWED_SEND
    if unknown_send:
        raise CaseError("send 未知字段: {}".format(sorted(unknown_send)))
    if not str(send.get("text") or "").strip():
        raise CaseError("send.text 必填")
    expect = case.get("expect")
    if not isinstance(expect, dict):
        raise CaseError("expect 必须是对象")
    unknown_expect = set(expect) - ALLOWED_EXPECT
    if unknown_expect:
        raise CaseError("expect 未知字段: {}".format(sorted(unknown_expect)))
    if not any(key in expect for key in EXPECT_MATCHER_KEYS):
        raise CaseError("expect 至少包含 messages / logs / semantic 之一")
    for key in EXPECT_LIST_KEYS:
        if key in expect and not (isinstance(expect[key], list) and expect[key]):
            raise CaseError("expect.{} 必须是非空数组".format(key))
    if "semantic" in expect and not isinstance(expect["semantic"], dict):
        raise CaseError("expect.semantic 必须是对象")


def render_case(case: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    rendered = json.loads(json.dumps(case))
    send = rendered.get("send", {})
    if send.get("group_id") == "{{group_id}}":
        if "group_id" not in config:
            raise CaseError("配置缺少 group_id，无法渲染用例")
        send["group_id"] = str(config["group_id"])
    return rendered
