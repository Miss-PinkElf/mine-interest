"""OpenAI 兼容接口的语义判定（LLM-as-a-Judge）。"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional

import aiohttp

SYSTEM_PROMPT = (
    "你是自动化测试的断言器。根据判定标准与机器人实际回复，"
    "判断实际回复是否满足标准。只返回 JSON：{\"pass\": true/false, \"reason\": \"简短理由\"}。"
)


class JudgeError(RuntimeError):
    """语义判定不可用或返回非法。"""


def _parse_json_content(content: str) -> Any:
    """解析模型返回内容，兼容代码围栏与前后杂文本。"""
    text = str(content or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass
    raise JudgeError("LLM 判定返回非法: {}".format(content))


async def judge(
    base_url: str,
    api_key: str,
    model: str,
    criteria: str,
    actual: str,
    timeout: float = 60.0,
    headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    if not base_url or not model:
        raise JudgeError("LLM 判定未配置")
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "判定标准：{}\n实际回复：{}".format(criteria, actual)},
        ],
    }
    request_headers = {"Content-Type": "application/json"}
    if api_key:
        request_headers["Authorization"] = "Bearer {}".format(api_key)
    request_headers.update(headers or {})
    base = base_url.rstrip("/")
    endpoint = "{}/chat/completions".format(base) if base.endswith("/v1") else "{}/v1/chat/completions".format(base)
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    try:
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.post(
                endpoint,
                json=payload,
                headers=request_headers,
            ) as response:
                if response.status != 200:
                    raise JudgeError("LLM 判定请求失败: HTTP {}".format(response.status))
                text = await response.text()
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        raise JudgeError("LLM 判定请求失败: {}".format(exc)) from exc
    try:
        body = json.loads(text)
    except json.JSONDecodeError as exc:
        raise JudgeError("LLM 判定响应不是合法 JSON: {}".format(text)) from exc
    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise JudgeError("LLM 判定返回非法: {}".format(body)) from exc
    result = _parse_json_content(content)
    if not isinstance(result, dict):
        raise JudgeError("LLM 判定返回不是对象: {}".format(result))
    if not isinstance(result.get("pass"), bool):
        raise JudgeError("LLM 判定缺少 pass 布尔值: {}".format(result))
    return {"pass": result["pass"], "reason": str(result.get("reason") or "")}
