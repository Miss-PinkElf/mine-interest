"""插件数据目录与 SQLite 建表（Plugin Storage）。"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .constants import DATABASE_NAME


SESSION_TABLE = "sessions"
MESSAGE_RECEIPT_TABLE = "message_receipts"


class SessionStore:
    """会话和消息处理状态的持久化入口。"""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.database_path = self.data_dir / DATABASE_NAME
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                f"""CREATE TABLE IF NOT EXISTS {SESSION_TABLE} (
                    id INTEGER PRIMARY KEY,
                    conversation_key TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    work_dir TEXT NOT NULL,
                    status TEXT NOT NULL,
                    agent_session_id TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            connection.execute(
                f"""CREATE INDEX IF NOT EXISTS sessions_by_conversation
                ON {SESSION_TABLE} (conversation_key, id DESC)"""
            )
            connection.execute(
                f"""CREATE TABLE IF NOT EXISTS {MESSAGE_RECEIPT_TABLE} (
                    platform_id TEXT NOT NULL,
                    message_id TEXT NOT NULL,
                    conversation_key TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (platform_id, message_id)
                )"""
            )
