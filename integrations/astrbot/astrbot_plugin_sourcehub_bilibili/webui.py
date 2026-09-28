"""插件页面接口（Plugin Page API）：扫码登录与仓库推送校验。"""

from __future__ import annotations

import asyncio
import base64
import io
import json
from datetime import datetime
from typing import Any, Awaitable, Callable

from astrbot.api import logger
from astrbot.api.star import Context
from astrbot.api.web import error_response, json_response

from .auth import AuthError, BilibiliAuth
from .constants import ALERT_REMOTE_KEY, PLUGIN_NAME
from .sourcehub.publish import DEFAULT_PUBLISH_REMOTE, verify_remote_access

LOG_PREFIX = "[SourceHub Bilibili]"
ACCOUNT_TAIL_LENGTH = 4
QR_START_ROUTE = "login/qr/start"
QR_STATUS_ROUTE = "login/qr/status"
LOGIN_STATUS_ROUTE = "login/status"
REPO_CHECK_ROUTE = "repo/check"
REPO_STATUS_ROUTE = "repo/status"
ACCESS_RECORD_NAME = "repo_access.json"
PUBLISH_ROLE = "资料发布"
ALERT_ROLE = "告警"
QR_FINISHED = {"success", "expired"}
REASON_LABELS = {
    "push_ok": "可以推送",
    "push_denied": "没有推送权限",
    "push_failed": "推送演练没有通过",
    "ssh_unreadable": "SSH 读不到这个仓库",
    "not_private": "仓库不是私有",
    "private_check_failed": "可以推送。匿名接口暂时无法确认私有性",
    "remote_invalid": "不是 GitHub SSH 地址",
    "remote_missing": "还没有填写仓库地址",
}
SAME_REPOSITORY_NOTE = "告警仓库不能和资料仓库相同"
Handler = Callable[[Any], Awaitable[Any]]


def _response(data: dict | None = None):
    payload: dict[str, Any] = {"status": "ok"}
    if data is not None:
        payload["data"] = data
    return json_response(payload)


def _failure(message: str, status_code: int = 400):
    return error_response(message, status_code=status_code)


def _bind(plugin: Any, handler: Handler):
    async def bound_handler():
        return await handler(plugin)

    bound_handler.__name__ = f"sourcehub_{handler.__name__}"
    return bound_handler


def register_webui(plugin: Any, context: Context) -> None:
    routes = (
        (LOGIN_STATUS_ROUTE, "GET", handle_login_status, "SourceHub 登录状态"),
        (QR_START_ROUTE, "POST", handle_qr_start, "SourceHub 生成登录二维码"),
        (QR_STATUS_ROUTE, "GET", handle_qr_status, "SourceHub 查询扫码状态"),
        (REPO_STATUS_ROUTE, "GET", handle_repo_status, "SourceHub 读取上次仓库校验"),
        (REPO_CHECK_ROUTE, "POST", handle_repo_check, "SourceHub 校验仓库推送权限"),
    )
    for endpoint, method, handler, description in routes:
        context.register_web_api(
            f"/{PLUGIN_NAME}/{endpoint}", _bind(plugin, handler), [method], description,
        )


def _credentials(plugin: Any) -> dict:
    return plugin.credential_store.load(plugin.config)


def _account_tail(credentials: dict) -> str:
    account = str(credentials.get("account_id") or "")
    if account.isdecimal() and len(account) >= ACCOUNT_TAIL_LENGTH:
        return f"尾号 {account[-ACCOUNT_TAIL_LENGTH:]}"
    return ""


def _login_view(plugin: Any) -> dict:
    credentials = _credentials(plugin)
    return {
        "logged_in": bool(credentials.get("SESSDATA")),
        "refreshable": bool(credentials.get("refresh_token")),
        "account": _account_tail(credentials),
        "qr": getattr(plugin, "_qr_status", "idle"),
    }


async def handle_login_status(plugin: Any):
    return _response(_login_view(plugin))


async def handle_qr_start(plugin: Any):
    try:
        import qrcode

        async with BilibiliAuth(plugin.credential_store, plugin.config) as auth:
            url, key = await auth.generate_qr()
        image = qrcode.make(url)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    except AuthError:
        logger.warning("%s 二维码生成失败", LOG_PREFIX)
        return _failure("二维码生成失败", 502)
    except Exception:
        logger.exception("%s 二维码生成失败", LOG_PREFIX)
        return _failure("二维码生成失败", 502)
    plugin._qr_key = key
    plugin._qr_status = "waiting"
    return _response({"image": f"data:image/png;base64,{encoded}", "status": "waiting"})


async def handle_qr_status(plugin: Any):
    key = str(getattr(plugin, "_qr_key", "") or "")
    if not key:
        return _response(_login_view(plugin))
    try:
        async with BilibiliAuth(plugin.credential_store, plugin.config) as auth:
            status = await auth.poll_qr(key)
    except AuthError:
        view = _login_view(plugin)
        view["qr"] = "unknown"
        return _response(view)
    plugin._qr_status = status
    if status in QR_FINISHED:
        plugin._qr_key = ""
    view = _login_view(plugin)
    view["qr"] = status
    return _response(view)


def _target_view(role: str, remote: str, publish_remote: str) -> dict:
    if not remote:
        return {
            "role": role,
            "repository": "",
            "private": False,
            "readable": False,
            "pushable": False,
            "label": REASON_LABELS["remote_missing"],
        }
    access = verify_remote_access(remote)
    label = REASON_LABELS.get(str(access["reason"]), "校验没有通过")
    if role == ALERT_ROLE and remote == publish_remote:
        label = f"{label}。{SAME_REPOSITORY_NOTE}"
    return {
        "role": role,
        "repository": access["repository"],
        "private": access["private"],
        "readable": access["readable"],
        "pushable": access["pushable"],
        "label": label,
    }


def _access_record_path(plugin: Any):
    return plugin.credential_store.path.parent / ACCESS_RECORD_NAME


def _read_access_record(plugin: Any) -> dict:
    path = _access_record_path(plugin)
    if not path.is_file():
        return {"checked_at": "", "targets": []}
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"checked_at": "", "targets": []}
    if not isinstance(record, dict):
        return {"checked_at": "", "targets": []}
    targets = record.get("targets")
    return {
        "checked_at": str(record.get("checked_at") or ""),
        "targets": targets if isinstance(targets, list) else [],
    }


def _write_access_record(plugin: Any, targets: list[dict]) -> dict:
    record = {
        "checked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "targets": targets,
    }
    path = _access_record_path(plugin)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)
    return record


async def handle_repo_status(plugin: Any):
    return _response(_read_access_record(plugin))


async def handle_repo_check(plugin: Any):
    alert_remote = str(plugin.config.get(ALERT_REMOTE_KEY) or "").strip()
    targets = [
        await asyncio.to_thread(_target_view, PUBLISH_ROLE, DEFAULT_PUBLISH_REMOTE, DEFAULT_PUBLISH_REMOTE),
        await asyncio.to_thread(_target_view, ALERT_ROLE, alert_remote, DEFAULT_PUBLISH_REMOTE),
    ]
    return _response(_write_access_record(plugin, targets))
