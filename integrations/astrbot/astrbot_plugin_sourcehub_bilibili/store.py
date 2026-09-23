"""本地归档（Local Archive）：先存通知，完成条目保持不变。"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .sourcehub.bili_ingest import record_to_fragment
from .sourcehub.bili_merge import merge_work_envelope
from .sourcehub.constants import NODE_FILE, NODE_IMAGE
from .sourcehub.envelope import ContentNode
from .sourcehub.media import hash_name, image_extension

from .client import FetchError
from .collector import numeric_id
from .content import EXISTING_BODY_GAPS
from .constants import (
    COLLECTION_GAP_PREFIX, COMPLETE, CONTENT_FILE, CONTENT_GAPS_HEADING,
    CONTENT_STATUS_PREFIX, CURSOR_FILE, IMAGE_GAP_PREFIX,
    ITEM_DIR, MEDIA_DIR, NOTIFICATION_DIR, OBJECT_GAP_PREFIX, PARENT_GAP_PREFIX,
    PARENT_MISSING_GAP, PARTIAL, RECORD_FILE, ROOT_GAP_PREFIX, ROOT_MISSING_GAP,
    TRIGGER_GAP_PREFIX,
)

MERGE_SKIP_KEYS = {
    "objects", "comments", "media", "gaps", "status", "attempted_at",
}
FETCH_FAILURE_GAP_PREFIXES = (
    COLLECTION_GAP_PREFIX, OBJECT_GAP_PREFIX, TRIGGER_GAP_PREFIX,
)
VIDEO_EXTENSIONS = {".mp4", ".flv"}
MP4_BRANDS = {b"isom", b"iso2", b"mp41", b"mp42", b"avc1", b"dash"}


def markdown_body(text: str) -> str:
    if text.startswith(CONTENT_STATUS_PREFIX):
        text = text.split("\n", 1)[1].lstrip("\n") if "\n" in text else ""
    heading = "\n" + CONTENT_GAPS_HEADING
    index = text.find(heading)
    if index >= 0:
        text = text[:index]
    return text.strip("\n")


def merge_media(previous: list, incoming: list) -> list:
    merged = []
    seen = set()
    recovered = {
        item.get("source_url"): item
        for item in previous
        if item.get("source_url") and item.get("local_path")
    }
    for item in incoming:
        url = item.get("source_url")
        if item.get("local_path"):
            merged.append(item)
        elif url in recovered:
            merged.append(recovered[url])
        else:
            merged.append(item)
        if url:
            seen.add(url)
    for url, item in recovered.items():
        if url not in seen:
            merged.append(item)
    return merged


def merge_raw(previous: dict, incoming: dict, media: list) -> dict:
    if not previous:
        merged = dict(incoming)
        merged["media"] = media
        return merged
    merged = dict(previous)
    for key, value in incoming.items():
        if key in MERGE_SKIP_KEYS or value in (None, "", [], {}):
            continue
        merged[key] = value
    if incoming.get("objects"):
        merged["objects"] = incoming["objects"]
    comments = dict(previous.get("comments") or {})
    comments.update(incoming.get("comments") or {})
    if comments:
        merged["comments"] = comments
    if incoming.get("notification"):
        merged["notification"] = incoming["notification"]
    merged["media"] = merge_media(previous.get("media") or [], media)
    return merged


def gap_recovered(gap: str, merged: dict) -> bool:
    comments = merged.get("comments") or {}
    media = merged.get("media") or []
    if gap.startswith(OBJECT_GAP_PREFIX):
        return bool(merged.get("objects"))
    if gap.startswith(COLLECTION_GAP_PREFIX):
        return bool(merged.get("objects") or comments)
    if gap.startswith(TRIGGER_GAP_PREFIX):
        return bool(comments.get("trigger"))
    if gap == PARENT_MISSING_GAP or gap.startswith(PARENT_GAP_PREFIX):
        return "parent" in comments
    if gap == ROOT_MISSING_GAP or gap.startswith(ROOT_GAP_PREFIX):
        return "root" in comments
    if gap.startswith(IMAGE_GAP_PREFIX):
        return bool(media) and all(item.get("local_path") for item in media)
    return False


def drop_recovered_gaps(gaps: list, merged: dict) -> list:
    return [gap for gap in gaps if not gap_recovered(gap, merged)]


def should_clear_empty_body(doc) -> bool:
    """本轮内容层仍报空正文，或本轮采集失败时，保留旧缺口。"""
    if any(gap in EXISTING_BODY_GAPS for gap in doc.gaps):
        return False
    return not any(
        gap.startswith(prefix)
        for gap in doc.gaps
        for prefix in FETCH_FAILURE_GAP_PREFIXES
    )


def image_extension(data: bytes) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    if data[4:8] == b"ftyp" and data[8:12] in {b"avif", b"avis"}:
        return ".avif"
    if data[4:8] == b"ftyp" and data[8:12] in MP4_BRANDS:
        return ".mp4"
    if data.startswith(b"FLV\x01"):
        return ".flv"
    raise FetchError("unsupported_image_content")


def atomic_write(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def write_json(path: Path, value):
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8"))


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


class Store:
    def __init__(self, path: Path, vault=None):
        self.path = path
        self.vault = vault
        self.notifications = path / NOTIFICATION_DIR
        self.notifications.mkdir(parents=True, exist_ok=True)

    def item_path(self, notification_id: str):
        return self.path / ITEM_DIR / numeric_id(notification_id)

    def record(self, notification_id: str):
        return read_json(self.item_path(notification_id) / RECORD_FILE, {})

    def receive(self, notification: dict):
        identity = numeric_id(notification.get("id"))
        path = self.notifications / f"{identity}.json"
        if not path.exists():
            write_json(path, notification)

    def pending(self):
        notifications = []
        for path in self.notifications.glob("*.json"):
            record = self.record(path.stem)
            if record.get("status") != COMPLETE:
                notifications.append((record.get("attempted_at", ""), path))
        # 重复失败的旧条目移到队尾，不能饿死新的通知。
        return [read_json(path, {}) for _, path in sorted(notifications)]

    def cursor(self):
        return read_json(self.path / CURSOR_FILE, {})

    def save_cursor(self, value: dict):
        write_json(self.path / CURSOR_FILE, value)

    async def save(self, notification: dict, raw: dict, doc, client):
        identity = numeric_id(notification.get("id"))
        previous = self.record(identity)
        if previous.get("status") == COMPLETE:
            self._export_vault(previous, self.item_path(identity))
            return
        folder = self.item_path(identity)
        media = []
        for url in dict.fromkeys(doc.downloads or doc.images):
            try:
                content = await client.image(url)
                name = hashlib.sha256(content).hexdigest() + image_extension(content)
                relative = f"{MEDIA_DIR}/{name}"
                atomic_write(folder / relative, content)
                doc.text = doc.text.replace(url, relative)
                media.append({"source_url": url, "local_path": relative})
                if relative not in doc.text:
                    doc.text += f"\n\n[附件]({relative})"
            except FetchError as exc:
                doc.gaps.append(f"{IMAGE_GAP_PREFIX}{exc}")
                media.append({"source_url": url, "error": str(exc)})
        merged = merge_raw(previous, raw, media)
        body = doc.text
        content_path = folder / CONTENT_FILE
        if previous and not body.strip() and content_path.exists():
            body = markdown_body(content_path.read_text(encoding="utf-8"))
        gaps = list(doc.gaps)
        for gap in previous.get("gaps") or []:
            if gap not in gaps:
                gaps.append(gap)
        gaps = drop_recovered_gaps(gaps, merged)
        if should_clear_empty_body(doc):
            gaps = [gap for gap in gaps if gap not in EXISTING_BODY_GAPS]
        status = PARTIAL if gaps else COMPLETE
        merged["status"] = status
        merged["gaps"] = gaps
        merged["attempted_at"] = datetime.now(timezone.utc).isoformat()
        text = f"{CONTENT_STATUS_PREFIX}{status}\n\n" + body
        if gaps:
            text += f"\n\n{CONTENT_GAPS_HEADING}\n\n" + "\n".join(f"- {gap}" for gap in gaps)
        atomic_write(folder / CONTENT_FILE, text.encode("utf-8"))
        # 最后提交成功状态：中途崩溃仍然可以重试。
        write_json(folder / RECORD_FILE, merged)
        self._export_vault(merged, folder)

    async def repair_failed_media(self, client) -> int:
        """重试已有记录里缺失的媒体；成功项不重复下载。"""
        repaired = 0
        for record_path in (self.path / ITEM_DIR).glob("*/" + RECORD_FILE):
            folder = record_path.parent
            record = read_json(record_path, {})
            content_path = folder / CONTENT_FILE
            if not content_path.exists():
                continue
            body = markdown_body(content_path.read_text(encoding="utf-8"))
            changed = False
            for media in record.get("media") or []:
                relative = media.get("local_path")
                if relative and (folder / relative).exists():
                    continue
                url = media.get("source_url")
                if not url:
                    continue
                try:
                    data = await client.image(url)
                    name = hashlib.sha256(data).hexdigest() + image_extension(data)
                    relative = f"{MEDIA_DIR}/{name}"
                    atomic_write(folder / relative, data)
                except FetchError as exc:
                    media["error"] = str(exc)
                    continue
                media["local_path"] = relative
                media.pop("error", None)
                body = body.replace(f"]({url})", f"]({relative})")
                repaired += 1
                changed = True
            if not changed:
                continue
            gaps = drop_recovered_gaps(record.get("gaps") or [], record)
            record["gaps"] = gaps
            record["status"] = PARTIAL if gaps else COMPLETE
            record["attempted_at"] = datetime.now(timezone.utc).isoformat()
            text = f"{CONTENT_STATUS_PREFIX}{record['status']}\n\n{body}"
            if gaps:
                text += f"\n\n{CONTENT_GAPS_HEADING}\n\n" + "\n".join(f"- {gap}" for gap in gaps)
            atomic_write(content_path, text.encode("utf-8"))
            write_json(record_path, record)
            self._export_vault(record, folder)
        return repaired

    def export_existing(self) -> int:
        if self.vault is None:
            return 0
        count = 0
        for path in (self.path / ITEM_DIR).glob("*/" + RECORD_FILE):
            record = read_json(path, {})
            if not record:
                continue
            try:
                self._export_vault(record, path.parent)
                count += 1
            except Exception:
                continue
        return count

    def _export_vault(self, merged: dict, folder: Path) -> None:
        if self.vault is None:
            return
        fragment = record_to_fragment(merged)
        if not fragment:
            return
        content_path = folder / CONTENT_FILE
        if content_path.exists():
            # 已采集档案的 content.md 是专栏/动态的完整可读正文；优先它而非摘要字段。
            archived_body = markdown_body(content_path.read_text(encoding="utf-8"))
            if archived_body:
                fragment["body"] = archived_body
        object_id = str(fragment.get("object_id") or "")
        existing_id = self.vault.lookup("bilibili", object_id) if object_id else None
        existing = self.vault.get(existing_id) if existing_id else None
        envelope = merge_work_envelope(existing, fragment)
        media_prefix = Path(os.path.relpath(
            self.vault.root / MEDIA_DIR, self.vault.item_dir_for(envelope)
        )).as_posix()
        for media in merged.get("media") or []:
            relative = media.get("local_path")
            if not relative:
                continue
            source = folder / relative
            if not source.exists():
                continue
            data = source.read_bytes()
            name = hash_name(data)
            self.vault.store_media(data, name)
            archived_link = f"]({relative})"
            vault_link = f"]({media_prefix}/{name})"
            for node in envelope.content:
                if (node.extra or {}).get("role") == "object" and node.text:
                    node.text = node.text.replace(archived_link, vault_link)
            digest = name.rsplit(".", 1)[0]
            known = {node.sha256 for node in envelope.content if node.sha256}
            if digest not in known:
                envelope.attachments.append(
                    {"sha256": digest, "filename": name, "url": media.get("source_url")}
                )
                envelope.content.append(
                    ContentNode(
                        type=NODE_FILE if Path(name).suffix in VIDEO_EXTENSIONS else NODE_IMAGE,
                        url=media.get("source_url"),
                        sha256=digest,
                        extra={"ext": image_extension(data)},
                    )
                )
        self.vault.upsert(envelope, object_key=object_id)
