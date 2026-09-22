"""媒体体积、魔数与内容哈希。"""

from __future__ import annotations

import hashlib

from .constants import GAP_MEDIA_TOO_LARGE


def image_extension(data: bytes) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    if len(data) >= 12 and data[4:8] == b"ftyp" and data[8:12] in {b"avif", b"avis"}:
        return ".avif"
    return ".bin"


def hash_name(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest() + image_extension(data)


def accept_media(data: bytes, max_bytes: int):
    if len(data) > max_bytes:
        return None, None, GAP_MEDIA_TOO_LARGE
    return data, hash_name(data), None


def walk_nodes(nodes):
    for node in nodes:
        yield node
        yield from walk_nodes(node.children)


def persist_media_nodes(envelope, vault, max_bytes, fetcher) -> None:
    """将图片、视频和文件节点统一写入公共哈希媒体库。"""
    from .constants import NODE_FILE, NODE_IMAGE

    for node in walk_nodes(envelope.content):
        if node.type not in {NODE_IMAGE, NODE_FILE} or not node.url or node.sha256:
            continue
        data, name, gap = fetcher(node.url, max_bytes)
        if gap:
            envelope.gaps.append(gap)
            continue
        if not data or not name:
            continue
        vault.store_media(data, name)
        node.sha256 = hashlib.sha256(data).hexdigest()
        node.extra["ext"] = image_extension(data)
        envelope.attachments.append(
            {"sha256": node.sha256, "filename": name, "url": node.url}
        )


# 兼容已发布插件内的旧调用名。
persist_image_nodes = persist_media_nodes
