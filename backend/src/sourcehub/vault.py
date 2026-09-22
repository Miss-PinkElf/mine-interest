"""资料目录（Vault）：封套、Markdown、catalog、可选本地 Git。"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .constants import CATALOG_FILE, CONTENT_FILE, ENVELOPE_FILE, ITEM_DIR, MEDIA_DIR, SPOOL_DIR
from .envelope import Envelope, item_relpath
from .gitstore import commit_item
from .markdown import render_content_md
from .paths import item_storage_path

DAILY_MESSAGES_HEADING = "## 实时消息（Live Messages）"


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


class Vault:
    def __init__(self, root: Path, git_enabled: bool = True):
        self.root = root
        self.git_enabled = git_enabled
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / ITEM_DIR).mkdir(exist_ok=True)
        (self.root / MEDIA_DIR).mkdir(exist_ok=True)
        (self.root / SPOOL_DIR).mkdir(exist_ok=True)
        self._init_catalog()

    def item_dir(self, item_id: str) -> Path:
        """优先从 catalog 解析已迁移路径；未入库时保留旧路径兼容。"""
        with sqlite3.connect(self.root / CATALOG_FILE) as connection:
            row = connection.execute(
                "SELECT path FROM items WHERE item_id = ?", (item_id,)
            ).fetchone()
        if row:
            return self.root / row[0]
        return self.root / ITEM_DIR / item_relpath(item_id)

    def item_dir_for(self, envelope: Envelope) -> Path:
        return self.root / ITEM_DIR / item_storage_path(envelope)

    def upsert(self, envelope: Envelope, object_key: Optional[str] = None) -> None:
        folder = self.item_dir_for(envelope)
        folder.mkdir(parents=True, exist_ok=True)
        atomic_write(
            folder / ENVELOPE_FILE,
            json.dumps(envelope.to_dict(), ensure_ascii=False, indent=2).encode("utf-8"),
        )
        atomic_write(folder / CONTENT_FILE, render_content_md(envelope).encode("utf-8"))
        relative_path = f"{ITEM_DIR}/{item_storage_path(envelope)}"
        self._index(envelope, object_key, relative_path)
        self._write_daily_index(envelope.platform, envelope.received_at)
        if self.git_enabled:
            try:
                commit_item(self.root, envelope.item_id, relative_path)
            except Exception:
                pass

    def get(self, item_id: str) -> Optional[Envelope]:
        path = self.item_dir(item_id) / ENVELOPE_FILE
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        return Envelope.from_dict(payload)

    def lookup(self, platform: str, object_key: str) -> Optional[str]:
        with sqlite3.connect(self.root / CATALOG_FILE) as connection:
            row = connection.execute(
                "SELECT item_id FROM items WHERE platform = ? AND object_key = ?",
                (platform, object_key),
            ).fetchone()
        return row[0] if row else None

    def store_media(self, data: bytes, filename: str) -> Path:
        path = self.root / MEDIA_DIR / filename
        if not path.exists():
            atomic_write(path, data)
        return path

    def append_daily_message(self, envelope: Envelope) -> None:
        """普通 QQ 消息到达即写入当天总文档，整理 Item 前也可直接阅读。"""
        path_parts = item_storage_path(envelope).split("/")
        day_root = self.root / ITEM_DIR / "qq" / path_parts[1]
        index_path = day_root / CONTENT_FILE
        current = index_path.read_text(encoding="utf-8") if index_path.exists() else f"# qq {path_parts[1]}\n\n"
        if DAILY_MESSAGES_HEADING not in current:
            current = current.rstrip() + f"\n\n{DAILY_MESSAGES_HEADING}\n"
        current += f"\n- `{envelope.event_id}` {render_content_md(envelope).splitlines()[-1]}\n"
        atomic_write(index_path, current.encode("utf-8"))

    def _init_catalog(self) -> None:
        with sqlite3.connect(self.root / CATALOG_FILE) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    item_id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    object_key TEXT,
                    path TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_items_object ON items(platform, object_key)"
            )

    def _index(self, envelope: Envelope, object_key: Optional[str], path: str) -> None:
        stamp = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.root / CATALOG_FILE) as connection:
            connection.execute(
                """
                INSERT INTO items(item_id, platform, object_key, path, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    platform = excluded.platform,
                    object_key = excluded.object_key,
                    path = excluded.path,
                    updated_at = excluded.updated_at
                """,
                (envelope.item_id, envelope.platform, object_key, path, stamp),
            )

    def _write_daily_index(self, platform: str, received_at: str) -> None:
        """每日总文档仅作索引，实际原文仍以每个 Item 的 content.md 为准。"""
        day_path = item_storage_path(
            Envelope(
                schema_version="1", platform=platform, conversation_id="", item_id=(
                    "qq:message:index" if platform == "qq" else "bilibili:video:index"
                ), event_id="", sender_id="", source_time=None, received_at=received_at,
                content=[], attachments=[], gaps=[], grouping={},
            )
        ).split("/")
        day_root = self.root / ITEM_DIR / platform / day_path[1]
        prefix = f"{ITEM_DIR}/{platform}/{day_path[1]}/%"
        with sqlite3.connect(self.root / CATALOG_FILE) as connection:
            rows = connection.execute(
                "SELECT item_id, path FROM items WHERE platform = ? AND path LIKE ? ORDER BY updated_at",
                (platform, prefix),
            ).fetchall()
        index_path = day_root / CONTENT_FILE
        previous = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
        messages = ""
        if DAILY_MESSAGES_HEADING in previous:
            messages = previous[previous.index(DAILY_MESSAGES_HEADING):].strip()
        lines = [f"# {platform} {day_path[1]}", ""]
        for item_id, path in rows:
            target = self.root / path / CONTENT_FILE
            lines.append(f"- [{item_id}]({target.relative_to(day_root)})")
        if messages:
            lines.extend(["", messages])
        atomic_write(day_root / CONTENT_FILE, ("\n".join(lines) + "\n").encode("utf-8"))
