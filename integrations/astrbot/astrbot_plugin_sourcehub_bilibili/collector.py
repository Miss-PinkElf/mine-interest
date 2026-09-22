"""提及采集器（Mention Collector）：评论关系与作品原文分别补全。"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from .client import FetchError
from .constants import (
    ARTICLE_COMMENT, DYNAMIC_COMMENTS, MAX_COMMENT_PAGES, MAX_FORWARD_DEPTH,
    NO_PARENT_ID, OPUS_FEATURES, PAGE_SIZE, PARENT_ID_KEYS, PARENT_MISSING_GAP,
    ROOT_ID_KEYS, ROOT_MISSING_GAP, SITE_BASE, VIDEO_COMMENT,
)
from .content import (
    Document, article_document, as_list, as_map, body_incomplete,
    has_visible_body, opus_document, opus_from_major,
)


def numeric_id(value) -> str:
    text = str(value or "")
    if not text.isdecimal() or int(text) <= 0:
        raise FetchError("invalid_identifier")
    return text


def dynamic_id(uri: str) -> str:
    parts = urlsplit("https:" + uri if uri.startswith("//") else uri)
    if parts.hostname not in {"t.bilibili.com", "www.bilibili.com", "m.bilibili.com"}:
        raise FetchError("dynamic_uri_missing")
    match = re.fullmatch(r"/(?:opus/|dynamic/)?([0-9]+)/?", parts.path)
    if not match:
        raise FetchError("dynamic_uri_missing")
    return numeric_id(match.group(1))


def relation_id(comment: dict, keys: tuple) -> tuple:
    """返回 (编号, 已知)。缺失或 null 不是明确的零值。"""
    for key in keys:
        if key not in comment:
            continue
        value = comment[key]
        if value is None or str(value) == "":
            continue
        return str(value), True
    return "", False


def find_comment(data: dict, rpid: str):
    """只匹配真实编号，不能把接口返回的根评论误认成目标子评论。"""
    if str(data.get("rpid_str") or data.get("rpid")) == rpid:
        return data
    for child in data.get("replies") or []:
        result = find_comment(child, rpid)
        if result:
            return result
    return None


class Collector:
    def __init__(self, client):
        self.client = client

    async def comment(self, oid, kind, rpid, root_hint=None):
        root_id = root_hint or rpid
        detail = await self.client.get("comment", oid=oid, type=kind, root=root_id)
        root = detail.get("root") or {}
        found = find_comment(root, rpid)
        if found:
            return found
        for page in range(1, MAX_COMMENT_PAGES + 1):
            data = await self.client.get(
                "replies", oid=oid, type=kind, root=root_id, pn=page, ps=PAGE_SIZE,
            )
            replies = data.get("replies") or []
            for reply in replies:
                found = find_comment(reply, rpid)
                if found:
                    return found
            count = as_map(data.get("page")).get("count") or 0
            if not replies or page * PAGE_SIZE >= int(count):
                break
        raise FetchError("comment_not_found_or_page_limit")

    async def collect(self, notification: dict):
        source = notification.get("item") or {}
        kind = int(source.get("business_id") or 0)
        oid = numeric_id(source.get("subject_id"))
        rpid = numeric_id(source.get("source_id"))
        raw = {"notification": notification, "comments": {}, "objects": []}
        doc = Document("# B 站采集\n\n" + str(source.get("source_content", "")))
        root_hint = str(source.get("root_id") or "")
        try:
            trigger = await self.comment(oid, kind, rpid, root_hint or None)
            raw["comments"]["trigger"] = trigger
            parent, parent_known = relation_id(trigger, PARENT_ID_KEYS)
            root, root_known = relation_id(trigger, ROOT_ID_KEYS)
            for role, target, known, missing_gap in (
                ("parent", parent, parent_known, PARENT_MISSING_GAP),
                ("root", root, root_known, ROOT_MISSING_GAP),
            ):
                if not known:
                    doc.gaps.append(missing_gap)
                    continue
                if target in {NO_PARENT_ID, rpid}:
                    raw["comments"][role] = None
                    continue
                try:
                    hint = None if root in {NO_PARENT_ID, ""} else root
                    raw["comments"][role] = await self.comment(oid, kind, numeric_id(target), hint)
                except FetchError as exc:
                    doc.gaps.append(f"{role}:{exc}")
            for role, comment in raw["comments"].items():
                if comment:
                    payload = as_map(comment.get("content"))
                    doc.text += f"\n\n## {role}\n\n{payload.get('message', '')}"
                    for image in as_list(payload.get("pictures")):
                        doc.picture(as_map(image).get("img_src", ""))
        except FetchError as exc:
            doc.gaps.append(f"trigger:{exc}")

        try:
            if kind == VIDEO_COMMENT:
                data = await self.client.get("video", aid=oid)
                raw["objects"].append(data)
                bvid = data.get("bvid")
                if not bvid or "desc" not in data:
                    raise FetchError("video_fields_missing")
                raw["source_url"] = f"{SITE_BASE}/video/{bvid}"
                doc.text += f"\n\n# {data.get('title', bvid)}\n\n{raw['source_url']}\n\n{data['desc']}"
                first_page = as_list(data.get("pages"))[0] if as_list(data.get("pages")) else {}
                cid = as_map(first_page).get("cid")
                if cid:
                    stream = await self.client.get(
                        "playurl", bvid=bvid, cid=cid, qn=64, fnval=0, fnver=0,
                    )
                    durl = as_list(stream.get("durl"))
                    stream_url = as_map(durl[0]).get("url") if durl else ""
                    if stream_url:
                        doc.download(str(stream_url))
                    else:
                        doc.gaps.append("video_stream_missing")
            elif kind == ARTICLE_COMMENT:
                data = await self.client.get("article", id=oid)
                raw["objects"].append(data)
                raw["source_url"] = f"{SITE_BASE}/read/cv{oid}"
                doc.text += f"\n\n# {data.get('title', '')}\n\n{raw['source_url']}"
                doc.append(article_document(data))
            elif kind in DYNAMIC_COMMENTS:
                target = dynamic_id(source.get("uri", ""))
                raw["source_url"] = f"{SITE_BASE}/opus/{target}"
                doc.text += "\n\n" + raw["source_url"]
                doc.append(await self.dynamic(target, raw["objects"], set()))
            else:
                raise FetchError("unsupported_comment_type")
        except FetchError as exc:
            doc.gaps.append(f"object:{exc}")
        return raw, doc

    async def dynamic(self, target: str, objects: list, visited: set) -> Document:
        if target in visited or len(visited) >= MAX_FORWARD_DEPTH:
            return Document(gaps=["dynamic_cycle_or_depth_limit"])
        visited.add(target)
        data = await self.client.get("dynamic", id=target, features=OPUS_FEATURES)
        objects.append(data)
        item = data.get("item") or {}
        module = as_map(as_map(item.get("modules")).get("module_dynamic"))
        doc = Document(as_map(module.get("desc")).get("text") or "")
        major = as_map(module.get("major"))
        if "opus" in major:
            detail = await self.client.get("opus", id=target, features=OPUS_FEATURES)
            objects.append(detail)
            fallback = as_map(detail.get("fallback"))
            opus_item = as_map(detail.get("item"))
            cv_id = None
            if fallback.get("type") == 2:
                cv_id = fallback.get("id")
            elif opus_item.get("type") == 1:
                cv_id = as_map(opus_item.get("basic")).get("rid_str")
            if cv_id:
                article = await self.client.get("article", id=numeric_id(cv_id))
                objects.append(article)
                doc.append(article_document(article))
            else:
                rendered = opus_document(detail)
                preview = opus_from_major(major)
                if rendered.text.strip() and not body_incomplete(rendered):
                    doc.append(rendered)
                elif has_visible_body(preview):
                    doc.append(preview)
                else:
                    doc.append(rendered)
        elif "draw" in major:
            for pic in as_list(as_map(major.get("draw")).get("items")):
                doc.picture(as_map(pic).get("src", ""))
        elif "archive" in major:
            video = as_map(major.get("archive"))
            doc.text += f"\n\n{video.get('title', '')}\n{SITE_BASE}/video/{video.get('bvid', '')}"
        elif major:
            doc.gaps.append("unsupported_dynamic_major")
        original = item.get("orig")
        if original:
            original_id = original.get("id_str")
            if original_id:
                doc.text += "\n\n## 转发原文"
                doc.append(await self.dynamic(numeric_id(original_id), objects, visited))
            else:
                doc.gaps.append("forward_original_unavailable")
        if not doc.text.strip():
            doc.gaps.append("dynamic_body_missing")
        return doc
