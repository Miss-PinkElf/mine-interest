"""QQ GitHub 自动化准入（GitHub Gate）：权限判断与回复文案。"""

from __future__ import annotations

from .constants import GITHUB_ADMIN_QQ_IDS_KEY, GITHUB_OWNER_QQ_IDS_KEY

GITHUB_REPLY_HEADER = "GitHub 自动化："
GITHUB_REPLY_MAX_ITEMS = 10


def _id_set(values) -> set[str]:
    if not isinstance(values, (list, tuple, set)):
        return set()
    return {str(value).strip() for value in values if str(value).strip()}


def is_github_authorized(event, config: dict) -> bool:
    """AstrBot 管理员，或配置里的 owner/admin QQ 号，才算有权限。"""
    is_admin = getattr(event, "is_admin", None)
    if callable(is_admin):
        try:
            if is_admin():
                return True
        except Exception:
            pass
    get_sender_id = getattr(event, "get_sender_id", None)
    sender = str(get_sender_id() or "").strip() if callable(get_sender_id) else ""
    if not sender:
        return False
    allowed = _id_set(config.get(GITHUB_OWNER_QQ_IDS_KEY)) | _id_set(
        config.get(GITHUB_ADMIN_QQ_IDS_KEY)
    )
    return sender in allowed


def message_plain_text(event) -> str:
    """只取本条消息的纯文本；转发内容不参与 GitHub 判断。"""
    try:
        return str(event.get_message_str() or "").strip()
    except Exception:
        return ""


def compose_github_reply(results) -> str:
    lines = [GITHUB_REPLY_HEADER]
    for result in results[:GITHUB_REPLY_MAX_ITEMS]:
        mark = "成功" if result.ok else "失败"
        proxy = "（经代理）" if result.via_proxy else ""
        lines.append(f"- [{mark}] {result.repository}：{result.message}{proxy}")
    return "\n".join(lines)
