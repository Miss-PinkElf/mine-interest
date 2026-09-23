"""由捕获封套生成可读原文 Markdown。"""

from __future__ import annotations

from .envelope import ContentNode, Envelope
from .paths import item_storage_path

ROLE_HEADINGS = {
    "object": "作品",
    "trigger": "评论",
    "parent": "上一级评论",
    "root": "根评论",
}
FILE_LABEL = "文件"


def media_href(envelope: Envelope, filename: str) -> str:
    relpath = item_storage_path(envelope)
    depth = 1 + len([part for part in relpath.split("/") if part])
    return ("../" * depth) + f"media/{filename}"


def render_content_md(envelope: Envelope) -> str:
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
