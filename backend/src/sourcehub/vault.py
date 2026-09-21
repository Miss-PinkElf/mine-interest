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
        return self.root / ITEM_DIR / item_relpath(item_id)

    def upsert(self, envelope: Envelope, object_key: Optional[str] = None) -> None:
        folder = self.item_dir(envelope.item_id)
        folder.mkdir(parents=True, exist_ok=True)
        atomic_write(
            folder / ENVELOPE_FILE,
            json.dumps(envelope.to_dict(), ensure_ascii=False, indent=2).encode("utf-8"),
        )
        atomic_write(folder / CONTENT_FILE, render_content_md(envelope).encode("utf-8"))
        self._index(envelope, object_key)
        if self.git_enabled:
            relpath = f"{ITEM_DIR}/{item_relpath(envelope.item_id)}"
            try:
                commit_item(self.root, envelope.item_id, relpath)
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

    def _index(self, envelope: Envelope, object_key: Optional[str]) -> None:
        path = f"{ITEM_DIR}/{item_relpath(envelope.item_id)}"
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
