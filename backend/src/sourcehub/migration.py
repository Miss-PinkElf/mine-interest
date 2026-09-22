"""Vault 目录迁移（Vault Migration）：先预演，执行阶段另行显式调用。"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path

from .constants import ENVELOPE_FILE, ITEM_DIR
from .envelope import Envelope
from .paths import item_storage_path
from .vault import Vault


@dataclass(frozen=True)
class MigrationEntry:
    source: Path
    target: Path
    conflict: bool


def plan_migration(vault: Vault) -> list[MigrationEntry]:
    """仅列出旧路径到新路径的迁移计划；此函数绝不修改文件或 catalog。"""
    entries = []
    for envelope_path in (vault.root / ITEM_DIR).rglob(ENVELOPE_FILE):
        payload = json.loads(envelope_path.read_text(encoding="utf-8"))
        envelope = Envelope.from_dict(payload)
        source = envelope_path.parent
        target = vault.root / ITEM_DIR / item_storage_path(envelope)
        if source == target:
            continue
        entries.append(MigrationEntry(source=source, target=target, conflict=target.exists()))
    return sorted(entries, key=lambda entry: str(entry.source))


def execute_migration(vault: Vault, entries: list[MigrationEntry]) -> int:
    """执行已审阅的预演计划；存在目标冲突时拒绝整体执行，避免覆盖资料。"""
    if any(entry.conflict for entry in entries):
        raise ValueError("migration_target_conflict")
    migrated = 0
    affected_days: set[tuple[str, str]] = set()
    for entry in entries:
        envelope_path = entry.source / ENVELOPE_FILE
        envelope = Envelope.from_dict(json.loads(envelope_path.read_text(encoding="utf-8")))
        entry.target.parent.mkdir(parents=True, exist_ok=True)
        entry.source.replace(entry.target)
        relative = str(entry.target.relative_to(vault.root))
        with sqlite3.connect(vault.root / "catalog.sqlite3") as connection:
            connection.execute(
                """
                INSERT INTO items(item_id, platform, object_key, path, updated_at)
                VALUES (?, ?, NULL, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    platform = excluded.platform,
                    path = excluded.path,
                    updated_at = excluded.updated_at
                """,
                (envelope.item_id, envelope.platform, relative, datetime.now(timezone.utc).isoformat()),
            )
        path_parts = item_storage_path(envelope).split("/")
        affected_days.add((envelope.platform, path_parts[1]))
        migrated += 1
    for platform, day in affected_days:
        # 复用每日索引写入器；日期字符串在 received_at 为空的旧档案会映射 unknown。
        received_at = "" if day == "unknown" else f"{day}T00:00:00+08:00"
        vault._write_daily_index(platform, received_at)
    return migrated
