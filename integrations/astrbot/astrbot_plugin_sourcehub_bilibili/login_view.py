"""登录状态展示映射（Login Status View）。"""

from __future__ import annotations

from .sourcehub.alerts import HEALTHY, LOGIN_REQUIRED, UNKNOWN

MISSING_LOGIN_STATUS = "missing"
LOGIN_VALIDITY_MESSAGES = {
    HEALTHY: "登录有效。",
    LOGIN_REQUIRED: "Cookie 已失效，请重新扫码登录。",
    UNKNOWN: "暂时无法确认登录状态（可能是网络问题），请稍后重试。",
    MISSING_LOGIN_STATUS: "还没有登录凭证，请扫码登录。",
}


def login_validity(status: str, checked_at: str) -> dict:
    """把登录检查结果映射成页面可直接展示的字段。"""
    normalized = status if status in LOGIN_VALIDITY_MESSAGES else UNKNOWN
    if normalized == HEALTHY:
        valid = True
    elif normalized in {LOGIN_REQUIRED, MISSING_LOGIN_STATUS}:
        valid = False
    else:
        valid = None
    return {
        "valid": valid,
        "status": normalized,
        "message": LOGIN_VALIDITY_MESSAGES[normalized],
        "checked_at": checked_at,
    }
