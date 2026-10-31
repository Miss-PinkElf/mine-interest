"""回复媒体解析（Reply Media Parsing）。

把代理回复拆成有序的文本、图片与视频片段：

1. 显式协议 `[[image:<path>]]`，始终生效；
2. 自动识别（`auto_send_media` 开启时）：可信本地媒体路径与公网媒体链接。

本地文件只在 `work_dir` 与插件媒体目录内生效；图片必须通过 PIL 实检，
视频只做扩展名与大小校验。URL 只接受 http/https，并拦截回环与私网地址。
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from .constants import (
    AUTO_MEDIA_MAX_COUNT,
    IMAGE_MARKER_MAX_COUNT,
    IMAGE_MARKER_PATTERN,
    MAX_VIDEO_BYTES,
    MEDIA_IMAGE_EXTENSIONS,
    MEDIA_REPLY_EXTENSIONS,
    MEDIA_VIDEO_EXTENSIONS,
)
from .media import resolve_trusted_path, validate_image

IMAGE_MARKER = re.compile(IMAGE_MARKER_PATTERN)

MEDIA_KIND_IMAGE = "image"
MEDIA_KIND_VIDEO = "video"
MEDIA_KIND_TEXT = "text"

# 路径/URL 遇到这些字符即终止，避免把后随中文说明一起吞进媒体 token。
_TOKEN_STOP = r"\s`\"'<>()\[\]{}（）【】，。；！？、"
_EXTENSION_ALTERNATION = "|".join(
    sorted(ext.lstrip(".") for ext in MEDIA_REPLY_EXTENSIONS)
)
_URL_PATTERN = r"https?://[^" + _TOKEN_STOP + r"]+"
_PATH_PATTERN = (
    r"(?<![\w])(?:~|\.{1,2})?/[^"
    + _TOKEN_STOP
    + r"]*?\.(?:"
    + _EXTENSION_ALTERNATION
    + r")(?![A-Za-z0-9])"
)
URL_RE = re.compile(_URL_PATTERN, re.IGNORECASE)
PATH_RE = re.compile(_PATH_PATTERN, re.IGNORECASE)
MARKDOWN_MEDIA_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
CODE_FENCE_RE = re.compile(r"```.*?(?:```|$)", re.DOTALL)
URL_TRAILING_PUNCTUATION = ".,;:!?"


@dataclass(frozen=True)
class _Candidate:
    """自动识别命中的媒体候选；start/end 是原文本中的删除范围。"""

    start: int
    end: int
    kind: str
    value: str
    is_url: bool


def media_kind(suffix: str) -> str | None:
    """按扩展名判断媒体类型；非图片/视频返回 None。"""
    normalized = suffix.lower()
    if normalized in MEDIA_IMAGE_EXTENSIONS:
        return MEDIA_KIND_IMAGE
    if normalized in MEDIA_VIDEO_EXTENSIONS:
        return MEDIA_KIND_VIDEO
    return None


def has_reply_media(parts: list[tuple[str, str]]) -> bool:
    """回复片段中是否存在需要发往 QQ 的图片或视频。"""
    return any(kind != MEDIA_KIND_TEXT for kind, _ in parts)


def _resolve_local_media(
    raw: str, work_dir: str, media_root: Path | str | None
) -> tuple[str, str] | None:
    """本地媒体必须位于信任根内、真实存在且通过类型校验。"""
    resolved = resolve_trusted_path(raw, work_dir, media_root)
    if not resolved:
        return None
    path = Path(resolved)
    kind = media_kind(path.suffix)
    if kind is None or not path.is_file():
        return None
    if kind == MEDIA_KIND_IMAGE:
        if validate_image(path) is None:
            return None
        return kind, resolved
    try:
        too_large = path.stat().st_size > MAX_VIDEO_BYTES
    except OSError:
        return None
    return None if too_large else (kind, resolved)


def _is_public_media_url(url: str) -> bool:
    """只放行公网 http/https 媒体链接，拦截回环与私网地址（SSRF）。"""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme.lower() not in ("http", "https"):
        return False
    host = (parsed.hostname or "").lower()
    if not host or host == "localhost" or host.endswith(".localhost"):
        return False
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_reserved
        or address.is_multicast
        or address.is_unspecified
    ):
        return False
    return media_kind(Path(parsed.path).suffix) is not None


def _fenced_ranges(text: str) -> list[tuple[int, int]]:
    return [(match.start(), match.end()) for match in CODE_FENCE_RE.finditer(text)]


def _inside_any(position: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= position < end for start, end in ranges)


def _overlaps(span: tuple[int, int], ranges: list[tuple[int, int]]) -> bool:
    return any(span[0] < end and start < span[1] for start, end in ranges)


def _trim_url(url: str) -> str:
    return url.rstrip(URL_TRAILING_PUNCTUATION)


def _expand_backticks(text: str, start: int, end: int) -> tuple[int, int]:
    """把 `` `path` `` 两侧的反引号一起删掉，避免回复里留下空反引号。"""
    if start > 0 and end < len(text) and text[start - 1] == "`" and text[end] == "`":
        return start - 1, end + 1
    return start, end


def _scan_text(
    text: str, work_dir: str, media_root: Path | str | None
) -> list[_Candidate]:
    """扫描一段文本，返回按位置排序的媒体候选。"""
    fences = _fenced_ranges(text)
    candidates: list[_Candidate] = []
    occupied: list[tuple[int, int]] = []

    def add(candidate: _Candidate) -> None:
        candidates.append(candidate)
        occupied.append((candidate.start, candidate.end))

    for match in MARKDOWN_MEDIA_RE.finditer(text):
        if _inside_any(match.start(), fences):
            continue
        raw = match.group(1).strip()
        if raw.startswith(("http://", "https://")):
            if not _is_public_media_url(raw):
                continue
            kind = media_kind(Path(urlparse(raw).path).suffix)
            add(_Candidate(match.start(), match.end(), kind, raw, True))
        else:
            resolved = _resolve_local_media(raw, work_dir, media_root)
            if resolved is None:
                continue
            add(_Candidate(match.start(), match.end(), resolved[0], resolved[1], False))

    for pattern, is_url in ((URL_RE, True), (PATH_RE, False)):
        for match in pattern.finditer(text):
            if _inside_any(match.start(), fences) or _overlaps(match.span(), occupied):
                continue
            raw = _trim_url(match.group(0)) if is_url else match.group(0)
            start, end = _expand_backticks(text, match.start(), match.start() + len(raw))
            if is_url:
                if not _is_public_media_url(raw):
                    continue
                kind = media_kind(Path(urlparse(raw).path).suffix)
                add(_Candidate(start, end, kind, raw, True))
            else:
                resolved = _resolve_local_media(raw, work_dir, media_root)
                if resolved is None:
                    continue
                add(_Candidate(start, end, resolved[0], resolved[1], False))

    candidates.sort(key=lambda item: item.start)
    return candidates


def _dedupe_key(candidate: _Candidate) -> tuple[str, str]:
    if candidate.is_url:
        return ("url", candidate.value)
    return ("file", str(Path(candidate.value).resolve()))


def _tidy_text(text: str) -> str:
    """删除被清空的项目符号行，并收起多余空行；普通空行保留。"""
    lines = [
        line
        for line in text.splitlines()
        if line.strip() not in ("-", "*", "•")
    ]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _split_explicit(
    content: str, work_dir: str, media_root: Path | str | None
) -> tuple[list[tuple[str, str]], int]:
    """按显式 `[[image:<path>]]` 标记拆分，行为与旧实现一致。"""
    parts: list[tuple[str, str]] = []
    ignored = 0
    image_count = 0
    last = 0
    for match in IMAGE_MARKER.finditer(content):
        text = content[last:match.start()]
        if text:
            parts.append((MEDIA_KIND_TEXT, text))
        path = match.group(1).strip()
        resolved = (
            resolve_trusted_path(path, work_dir, media_root)
            if path and image_count < IMAGE_MARKER_MAX_COUNT
            else None
        )
        if resolved:
            parts.append((MEDIA_KIND_IMAGE, resolved))
            image_count += 1
        else:
            ignored += 1
        last = match.end()
    tail = content[last:]
    if tail:
        parts.append((MEDIA_KIND_TEXT, tail))
    return parts, ignored


def _rebuild_text_piece(
    text: str, chosen: list[_Candidate]
) -> list[tuple[str, str]]:
    """按命中位置把文本切成文本段与媒体段。"""
    pieces: list[tuple[str, str]] = []
    cursor = 0
    for candidate in chosen:
        before = text[cursor:candidate.start]
        if before:
            pieces.append((MEDIA_KIND_TEXT, before))
        pieces.append((candidate.kind, candidate.value))
        cursor = candidate.end
    tail = text[cursor:]
    if tail:
        pieces.append((MEDIA_KIND_TEXT, tail))
    return pieces


def parse_reply_parts(
    content: str,
    work_dir: str = "",
    media_root: Path | str | None = None,
    *,
    auto_send: bool = False,
) -> tuple[list[tuple[str, str]], int]:
    """把代理回复拆成文本段与媒体段；显式标记不可信时计入 ignored。

    `auto_send` 开启时，再对剩余文本自动识别本地媒体与公网媒体链接。
    自动识别失败的路径不计数，避免正文里普通描述触发告警。
    """
    parts, ignored = _split_explicit(content, work_dir, media_root)
    if not auto_send:
        return parts, ignored

    text_indexes = [
        index for index, (kind, _) in enumerate(parts) if kind == MEDIA_KIND_TEXT
    ]
    if not text_indexes:
        return parts, ignored

    scans = {
        index: _scan_text(parts[index][1], work_dir, media_root)
        for index in text_indexes
    }
    ordered = [
        (index, candidate)
        for index in text_indexes
        for candidate in scans[index]
    ]
    if not ordered:
        return parts, ignored

    explicit_media_count = len(parts) - len(text_indexes)
    budget = max(0, AUTO_MEDIA_MAX_COUNT - explicit_media_count)
    # 本地优先：同一回复里已识别到可信本地媒体时，丢弃 URL，避免重复发送同一张图。
    has_local = any(not candidate.is_url for _, candidate in ordered)
    seen: set[tuple[str, str]] = set()
    chosen: set[tuple[int, int]] = set()
    for index, candidate in ordered:
        if budget <= 0:
            break
        if candidate.is_url and has_local:
            continue
        key = _dedupe_key(candidate)
        if key in seen:
            continue
        seen.add(key)
        chosen.add((index, id(candidate)))
        budget -= 1

    rebuilt: list[tuple[str, str]] = []
    for index, (kind, value) in enumerate(parts):
        if kind != MEDIA_KIND_TEXT:
            rebuilt.append((kind, value))
            continue
        selected = [
            candidate for candidate in scans[index]
            if (index, id(candidate)) in chosen
        ]
        if not selected:
            rebuilt.append((kind, value))
            continue
        for piece_kind, piece_value in _rebuild_text_piece(value, selected):
            if piece_kind == MEDIA_KIND_TEXT:
                piece_value = _tidy_text(piece_value)
                if not piece_value:
                    continue
            rebuilt.append((piece_kind, piece_value))
    return rebuilt, ignored
