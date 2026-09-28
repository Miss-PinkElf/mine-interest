"""由捕获封套生成可读原文 Markdown。"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from .envelope import ContentNode, Envelope
from .paths import item_storage_path

ROLE_HEADINGS = {
    "object": "作品",
    "trigger": "评论",
    "parent": "上一级评论",
    "root": "根评论",
}
FILE_LABEL = "文件"
BILIBILI_TIMEZONE = ZoneInfo("Asia/Shanghai")


def media_href(envelope: Envelope, filename: str) -> str:
    relpath = item_storage_path(envelope)
    depth = 1 + len([part for part in relpath.split("/") if part])
    return ("../" * depth) + f"media/{filename}"


def render_content_md(envelope: Envelope) -> str:
    if envelope.platform == "bilibili" and (envelope.grouping or {}).get("type") == "work_object":
        return _render_bilibili(envelope)
    lines = [
        f"# {envelope.item_id}",
        "",
        f"- 平台（Platform）：{envelope.platform}",
        f"- 会话（Conversation）：{envelope.conversation_id}",
        f"- 成条（Grouping）：{(envelope.grouping or {}).get('type', '')}",
        f"- 来源时间（Source Time）：{envelope.source_time or ''}",
        f"- 接收时间（Received At）：{envelope.received_at}",
        "",
    ]
    if envelope.gaps:
        lines.append("## 缺口（Gaps）")
        lines.append("")
        for gap in envelope.gaps:
            lines.append(f"- {gap}")
        lines.append("")
    for node in envelope.content:
        lines.extend(_render_node(envelope, node))
    return "\n".join(lines).rstrip() + "\n"


def _render_bilibili(envelope: Envelope) -> str:
    object_node = next((node for node in envelope.content if (node.extra or {}).get("role") == "object"), None)
    if object_node is None:
        return ""
    detail = object_node.extra or {}
    kind = str(detail.get("kind") or envelope.item_id.split(":")[1])
    label = {"video": "原视频", "article": "原专栏", "opus": "原动态"}.get(kind, "原作品")
    section = "简介" if kind == "video" else "正文"
    lines = [f"# {detail.get('title') or envelope.item_id}", "", f"- {label}：[在 B 站查看]({detail.get('url') or ''})"]
    if envelope.received_at:
        lines.append(f"- 首次采集：{_bilibili_time(envelope.received_at)}")
    cover = (envelope.extra or {}).get("cover")
    if cover:
        lines.extend(["", f"![视频封面]({cover})"])
    lines.extend(["", f"## {section}", "", (object_node.text or "").strip()])
    files = list(dict.fromkeys((envelope.extra or {}).get("files") or []))
    if files:
        lines.extend(["", "## 附件", ""])
        lines.extend(f"- [本地视频（{str(file).rsplit('.', 1)[-1].upper()}）]({file})" for file in files)
    comments = [node for node in envelope.content if (node.extra or {}).get("role") in {"trigger", "parent", "root"}]
    if comments:
        lines.extend(["", "## 相关评论", ""])
        by_id = {str(node.extra.get("rpid") or ""): node for node in comments if node.extra.get("rpid")}
        groups: dict[str, list[ContentNode]] = {}
        for node in comments:
            if node.extra.get("role") != "trigger":
                continue
            key = str(node.extra.get("parent_rpid") or node.extra.get("root_rpid") or node.extra.get("rpid") or "")
            groups.setdefault(key, []).append(node)
        shown: set[str] = set()
        for index, (key, triggers) in enumerate(groups.items(), 1):
            if len(groups) > 1:
                lines.extend([f"### 评论串 {index}", ""])
            root_ids = list(dict.fromkeys(str(trigger.extra.get("root_rpid") or "") for trigger in triggers))
            for root_id in root_ids:
                root = by_id.get(root_id)
                if root_id and root_id != key and root and root_id not in shown:
                    lines.extend(_render_bilibili_comment(root, "根评论"))
                    shown.add(root_id)
            parent = by_id.get(key)
            if parent and parent.extra.get("role") != "trigger" and key not in shown:
                is_root = any(str(trigger.extra.get("root_rpid") or "") == key for trigger in triggers)
                lines.extend(_render_bilibili_comment(parent, "上一级评论（也是根评论）" if is_root else "上一级评论"))
                shown.add(key)
            for trigger in triggers:
                rpid = str(trigger.extra.get("rpid") or "")
                if rpid not in shown:
                    lines.extend(_render_bilibili_comment(trigger, "触发采集的评论"))
                    shown.add(rpid)
        for node in comments:
            rpid = str(node.extra.get("rpid") or "")
            if rpid and rpid not in shown:
                lines.extend(_render_bilibili_comment(node, "相关评论"))
                shown.add(rpid)
    if envelope.gaps:
        lines.extend(["## 采集缺口", ""])
        lines.extend(f"- {gap}" for gap in envelope.gaps)
    return "\n".join(lines).rstrip() + "\n"


def _bilibili_time(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    if parsed.tzinfo is None:
        return value
    return parsed.astimezone(BILIBILI_TIMEZONE).strftime("%Y-%m-%d %H:%M") + "（北京时间）"


def _render_bilibili_comment(node: ContentNode, label: str) -> list[str]:
    lines = [f"**{label}（ID：{node.extra.get('rpid') or ''}）**", "", node.text or "", ""]
    for image in node.extra.get("images") or []:
        lines.extend([f"![评论图片]({image})", ""])
    return lines


def _render_node(envelope: Envelope, node: ContentNode) -> list[str]:
    lines: list[str] = []
    role = (node.extra or {}).get("role")
    if role in ROLE_HEADINGS:
        lines.append(f"## {ROLE_HEADINGS[role]}")
        lines.append("")
        title = (node.extra or {}).get("title")
        url = (node.extra or {}).get("url")
        if title:
            lines.append(str(title))
            lines.append("")
        if url:
            lines.append(str(url))
            lines.append("")
    if node.type == "image":
        filename = _image_filename(node)
        href = media_href(envelope, filename) if node.sha256 else (node.url or "")
        lines.append(f"![图片]({href})")
        lines.append("")
    elif node.type == "file":
        filename = _image_filename(node)
        href = media_href(envelope, filename) if node.sha256 else (node.url or "")
        label = (node.extra or {}).get("name") or FILE_LABEL
        lines.append(f"[{label}]({href})")
        lines.append("")
    elif node.text:
        lines.append(node.text)
        lines.append("")
    for child in node.children:
        lines.extend(_render_node(envelope, child))
    return lines


def _image_filename(node: ContentNode) -> str:
    ext = (node.extra or {}).get("ext") or ""
    return f"{node.sha256}{ext}"
