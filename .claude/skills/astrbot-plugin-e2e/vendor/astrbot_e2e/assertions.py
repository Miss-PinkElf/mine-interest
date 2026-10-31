"""消息与日志断言（Assertion）。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class AssertionResult:
    kind: str
    ok: bool
    expected: Any
    actual: str
    detail: str = ""


def contains(text: str, needles: Iterable[str], mode: str = "all") -> AssertionResult:
    if mode not in ("all", "any"):
        raise ValueError("contains.mode 只能是 all 或 any")
    wants = [str(item) for item in needles]
    if not wants:
        raise ValueError("contains.needles 不能为空")
    hits = [item for item in wants if item in text]
    ok = len(hits) == len(wants) if mode == "all" else bool(hits)
    return AssertionResult(
        kind="contains",
        ok=ok,
        expected={"needles": wants, "mode": mode},
        actual=text,
        detail="命中 {}/{}".format(len(hits), len(wants)),
    )


def regex(text: str, pattern: str) -> AssertionResult:
    match = re.search(pattern, text, re.S)
    return AssertionResult(
        kind="regex",
        ok=bool(match),
        expected=pattern,
        actual=text,
        detail=match.group(0) if match else "未匹配",
    )


def evaluate_images(count: int, spec: Dict[str, Any]) -> AssertionResult:
    """断言回复中的图片数量；spec 支持 min（默认 0）与可选 max。"""
    try:
        minimum = int(spec.get("min", 0))
        maximum = spec.get("max")
        maximum = int(maximum) if maximum is not None else None
    except (TypeError, ValueError):
        return AssertionResult("images", False, spec, str(count), "images 断言参数非法")
    ok = count >= minimum and (maximum is None or count <= maximum)
    return AssertionResult(
        kind="images",
        ok=ok,
        expected=spec,
        actual=str(count),
        detail="图片数 {}，期望 min={} max={}".format(count, minimum, maximum),
    )


def evaluate_messages(messages: List[str], specs: List[Dict[str, Any]]) -> List[AssertionResult]:
    text = "\n".join(messages)
    results: List[AssertionResult] = []
    for spec in specs:
        if not isinstance(spec, dict):
            raise ValueError("断言必须是对象")
        if "contains" in spec:
            result = contains(text, spec["contains"], spec.get("mode", "all"))
        elif "regex" in spec:
            result = regex(text, spec["regex"])
        else:
            raise ValueError("断言必须包含 contains 或 regex")
        results.append(result)
        if not result.ok:
            break
    return results


def evaluate_logs(log_text: str, specs: List[Dict[str, Any]]) -> List[AssertionResult]:
    return evaluate_messages([log_text], specs)
