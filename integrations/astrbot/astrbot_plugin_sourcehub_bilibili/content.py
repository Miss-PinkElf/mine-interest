"""正文转换（Content Rendering）；未知节点保留并报告，不冒充全文。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from markdownify import markdownify

from .constants import EMPTY_BODY_GAP

EXISTING_BODY_GAPS = {"body_missing", "article_body_missing", "opus_body_missing", EMPTY_BODY_GAP}


def as_map(value) -> dict:
    return value if isinstance(value, dict) else {}


def as_list(value) -> list:
    return value if isinstance(value, list) else []


@dataclass
class Document:
    text: str = ""
    images: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)

    def append(self, other: Document):
        self.text += "\n\n" + other.text
        self.images.extend(other.images)
        self.gaps.extend(other.gaps)

    def picture(self, url: str):
        if not url:
            self.gaps.append("image_url_missing")
            return
        self.images.append(url)
        self.text += f"\n\n![图片]({url})"


def has_visible_body(doc: Document) -> bool:
    return bool(doc.text.strip() or doc.images)


def body_incomplete(doc: Document) -> bool:
    return (not has_visible_body(doc)) or any(gap in EXISTING_BODY_GAPS for gap in doc.gaps)


def finalize_document(doc: Document) -> Document:
    if has_visible_body(doc) or any(gap in EXISTING_BODY_GAPS for gap in doc.gaps):
        return doc
    doc.gaps.append(EMPTY_BODY_GAP)
    return doc


def nodes_text(nodes: list, doc: Document) -> str:
    parts = []
    for node in as_list(nodes):
        if not isinstance(node, dict):
            doc.gaps.append("unknown_text_node")
            parts.append(json.dumps(node, ensure_ascii=False))
            continue
        if "word" in node:
            parts.append(str(as_map(node.get("word")).get("words", "")))
        elif "rich" in node:
            rich = as_map(node.get("rich"))
            parts.append(str(rich.get("text", "")))
            if rich.get("jump_url"):
                parts.append(f" ({rich['jump_url']})")
            icon = as_map(rich.get("emoji")).get("icon_url")
            if icon:
                doc.images.append(icon)
        elif isinstance(node.get("text"), str):
            parts.append(node["text"])
        else:
            doc.gaps.append("unknown_text_node")
            parts.append(json.dumps(node, ensure_ascii=False))
    return "".join(parts)


def paragraphs_document(paragraphs: list) -> Document:
    doc = Document()
    for paragraph in as_list(paragraphs):
        pics = as_map(paragraph.get("pic")).get("pics")
        if pics:
            for pic in as_list(pics):
                doc.picture(as_map(pic).get("url", ""))
        elif "text" in paragraph:
            doc.text += "\n\n" + nodes_text(as_map(paragraph.get("text")).get("nodes", []), doc)
        elif "code" in paragraph:
            code = as_map(paragraph.get("code"))
            text = code.get("content") or code.get("code")
            if isinstance(text, str):
                doc.text += "\n\n```\n" + text + "\n```"
            else:
                doc.gaps.append("unknown_code_node")
        elif "line" in paragraph:
            pic = as_map(paragraph.get("line")).get("pic")
            if pic:
                doc.picture(as_map(pic).get("url", ""))
            else:
                doc.text += "\n\n---"
        else:
            doc.gaps.append("unknown_paragraph")
            doc.text += "\n\n```json\n" + json.dumps(paragraph, ensure_ascii=False) + "\n```"
    if not paragraphs:
        doc.gaps.append("body_missing")
    return finalize_document(doc)


def article_document(data: dict) -> Document:
    paragraphs = as_map(as_map(data.get("opus")).get("content")).get("paragraphs")
    if paragraphs:
        return paragraphs_document(paragraphs)
    content = data.get("content")
    if not isinstance(content, str) or not content.strip():
        return Document(gaps=["article_body_missing"])
    if content.lstrip().startswith("{"):
        doc = Document()
        try:
            for op in json.loads(content)["ops"]:
                insert = op.get("insert")
                if isinstance(insert, str):
                    doc.text += insert
                elif isinstance(insert, dict) and isinstance(insert.get("image"), str):
                    doc.picture(insert["image"])
                else:
                    doc.gaps.append("unknown_delta_insert")
        except (ValueError, KeyError, TypeError):
            doc.gaps.append("invalid_delta_body")
        return finalize_document(doc)
    soup = BeautifulSoup(content, "html.parser")
    images = []
    for image in soup.find_all("img"):
        url = image.get("data-src") or image.get("src")
        if url:
            image["src"] = url
            images.append(url)
    return finalize_document(Document(markdownify(str(soup), heading_style="ATX"), images))


def filled_list(value) -> list:
    return value if isinstance(value, list) and value else []


def opus_from_major(major: dict) -> Document:
    opus = as_map(major.get("opus"))
    doc = Document()
    title = opus.get("title")
    if isinstance(title, str) and title.strip():
        doc.text += f"\n\n# {title}"
    summary = as_map(opus.get("summary")).get("text") or ""
    if str(summary).strip():
        doc.text += "\n\n" + str(summary)
    for pic in as_list(opus.get("pics")):
        doc.picture(as_map(pic).get("url") or as_map(pic).get("live_url") or "")
    if not str(summary).strip() and not doc.images:
        doc.gaps.append("opus_body_missing")
    return finalize_document(doc)


def opus_document(data: dict) -> Document:
    modules = as_map(data.get("item")).get("modules")
    if isinstance(modules, dict):
        return opus_from_major(as_map(as_map(modules.get("module_dynamic")).get("major")))
    doc = Document()
    found_body = False
    for module in as_list(modules):
        module = as_map(module)
        title = as_map(module.get("module_title")).get("text")
        if isinstance(title, str) and title.strip():
            doc.text += f"\n\n# {title}"
        paragraphs = as_map(module.get("module_content")).get("paragraphs")
        if filled_list(paragraphs):
            found_body = True
            doc.append(paragraphs_document(paragraphs))
        pics = as_map(as_map(as_map(module.get("module_top")).get("display")).get("album")).get("pics")
        for pic in filled_list(pics):
            doc.picture(as_map(pic).get("url", ""))
    if not found_body and not doc.images:
        doc.gaps.append("opus_body_missing")
    return finalize_document(doc)
