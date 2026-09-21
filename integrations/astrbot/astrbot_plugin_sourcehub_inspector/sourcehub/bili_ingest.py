"""把 B 站采集 record 映射成按作品合并的片段。"""

from __future__ import annotations

import re
from typing import Any, Optional

from .bili_merge import mention_fragment
from .constants import WORK_ARTICLE, WORK_OPUS, WORK_VIDEO

ARTICLE_PATH = re.compile(r"/read/cv(\d+)")
OPUS_PATH = re.compile(r"/opus/(\d+)")


def _comment_payload(comment: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    if not isinstance(comment, dict):
        return None
    rpid = comment.get("rpid_str") or comment.get("rpid")
    if not rpid:
        return None
    content = comment.get("content") or {}
    text = content.get("message") if isinstance(content, dict) else ""
    member = comment.get("member") or {}
    return {
        "rpid": str(rpid),
        "text": str(text or ""),
        "sender_id": str(member.get("mid") or comment.get("mid") or ""),
    }


def record_to_fragment(raw: dict[str, Any]) -> Optional[dict[str, Any]]:
    notification = raw.get("notification") or {}
    item = notification.get("item") or {}
    comments = raw.get("comments") or {}
    trigger = _comment_payload(comments.get("trigger"))
    if trigger is None:
        source = item.get("source_content") or ""
        source_id = item.get("source_id")
        if not source_id:
            return None
        trigger = {"rpid": str(source_id), "text": str(source), "sender_id": ""}
    kind, object_id, title, body, url = _work_fields(raw, item)
    if not object_id:
        return None
    return mention_fragment(
        kind=kind,
        object_id=object_id,
        title=title,
        url=url,
        body=body,
        trigger=trigger,
        parent=_comment_payload(comments.get("parent")),
        root=_comment_payload(comments.get("root")),
        received_at=str(raw.get("attempted_at") or ""),
        conversation_id=str((notification.get("user") or {}).get("mid") or ""),
        event_id=trigger["rpid"],
    )


def _work_fields(raw: dict[str, Any], item: dict[str, Any]):
    source_url = str(raw.get("source_url") or item.get("uri") or "")
    objects = raw.get("objects") or []
    first = objects[0] if objects and isinstance(objects[0], dict) else {}
    if first.get("bvid"):
        return (
            WORK_VIDEO,
            str(first["bvid"]),
            str(first.get("title") or item.get("title") or ""),
            str(first.get("desc") or ""),
            source_url or f"https://www.bilibili.com/video/{first['bvid']}",
        )
    article = ARTICLE_PATH.search(source_url)
    if article:
        return (
            WORK_ARTICLE,
            article.group(1),
            str(first.get("title") or item.get("title") or ""),
            str(first.get("content") or first.get("summary") or ""),
            source_url,
        )
    opus = OPUS_PATH.search(source_url)
    if opus:
        return (
            WORK_OPUS,
            opus.group(1),
            str(item.get("title") or "动态"),
            str(first.get("summary") or ""),
            source_url,
        )
    if first.get("title") and item.get("business_id") == 1:
        bvid = str(first.get("bvid") or "")
        return WORK_VIDEO, bvid, str(first.get("title") or ""), str(first.get("desc") or ""), source_url
    return WORK_VIDEO, "", str(item.get("title") or ""), "", source_url
