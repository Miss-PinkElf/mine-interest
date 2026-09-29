"""插件专属 SQLite 会话、历史与消息回执（Plugin Storage）。"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

from .constants import (
    DATABASE_NAME,
    RECEIPT_PROCESSING,
    RECEIPT_QUEUED,
    SESSION_ACTIVE,
    SESSION_ENDED,
)
from .contracts import (
    ConversationKey,
    ConversationKind,
    IncomingMessage,
    SessionRecord,
    SessionSettings,
)


SESSION_TABLE = "sessions"
MESSAGE_RECEIPT_TABLE = "message_receipts"
TURN_TABLE = "turns"


class SessionStore:
    """所有记录均以平台实例、会话类别和 QQ ID 的复合键为边界。"""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.database_path = self.data_dir / DATABASE_NAME
        self._initialize_schema()

    @contextmanager
    def _connection(self):
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            with connection:
                yield connection

    def _initialize_schema(self) -> None:
        with self._connection() as connection:
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
                    sender_id TEXT NOT NULL DEFAULT '',
                    text TEXT NOT NULL DEFAULT '',
                    origin TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT '{RECEIPT_QUEUED}',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (platform_id, message_id)
                )"""
            )
            columns = {
                row["name"]
                for row in connection.execute(f"PRAGMA table_info({MESSAGE_RECEIPT_TABLE})")
            }
            for name, definition in (
                ("status", f"TEXT NOT NULL DEFAULT '{RECEIPT_PROCESSING}'"),
                ("sender_id", "TEXT NOT NULL DEFAULT ''"),
                ("text", "TEXT NOT NULL DEFAULT ''"),
                ("origin", "TEXT NOT NULL DEFAULT ''"),
            ):
                if name not in columns:
                    connection.execute(
                        f"ALTER TABLE {MESSAGE_RECEIPT_TABLE} ADD COLUMN {name} {definition}"
                    )
            connection.execute(
                f"""CREATE TABLE IF NOT EXISTS {TURN_TABLE} (
                    id INTEGER PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    message_id TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )

    @staticmethod
    def _record(row: sqlite3.Row | None, conversation: ConversationKey) -> SessionRecord | None:
        if row is None:
            return None
        return SessionRecord(
            id=row["id"],
            conversation=conversation,
            agent_type=row["agent_type"],
            work_dir=row["work_dir"],
            status=row["status"],
            agent_session_id=row["agent_session_id"],
        )

    def active(self, conversation: ConversationKey) -> SessionRecord | None:
        with self._connection() as connection:
            row = connection.execute(
                f"SELECT * FROM {SESSION_TABLE} WHERE conversation_key=? AND status=? "
                "ORDER BY id DESC LIMIT 1",
                (conversation.storage_key(), SESSION_ACTIVE),
            ).fetchone()
        return self._record(row, conversation)

    def create(self, conversation: ConversationKey, settings: SessionSettings) -> SessionRecord:
        key = conversation.storage_key()
        with self._connection() as connection:
            connection.execute(
                f"UPDATE {SESSION_TABLE} SET status=?, updated_at=CURRENT_TIMESTAMP "
                "WHERE conversation_key=? AND status=?",
                (SESSION_ENDED, key, SESSION_ACTIVE),
            )
            cursor = connection.execute(
                f"INSERT INTO {SESSION_TABLE} "
                "(conversation_key, agent_type, work_dir, status) VALUES (?, ?, ?, ?)",
                (key, settings.agent_type, settings.work_dir, SESSION_ACTIVE),
            )
            session_id = cursor.lastrowid
        return SessionRecord(session_id, conversation, settings.agent_type, settings.work_dir, SESSION_ACTIVE)

    def resume(self, conversation: ConversationKey, identifier: str = "") -> SessionRecord | None:
        key = conversation.storage_key()
        with self._connection() as connection:
            if identifier:
                row = connection.execute(
                    f"SELECT * FROM {SESSION_TABLE} WHERE conversation_key=? "
                    "AND (CAST(id AS TEXT)=? OR agent_session_id=?) ORDER BY id DESC LIMIT 1",
                    (key, identifier, identifier),
                ).fetchone()
            else:
                row = connection.execute(
                    f"SELECT * FROM {SESSION_TABLE} WHERE conversation_key=? "
                    "AND status=? ORDER BY id DESC LIMIT 1",
                    (key, SESSION_ENDED),
                ).fetchone()
            if row is None:
                return None
            connection.execute(
                f"UPDATE {SESSION_TABLE} SET status=?, updated_at=CURRENT_TIMESTAMP "
                "WHERE conversation_key=? AND status=?",
                (SESSION_ENDED, key, SESSION_ACTIVE),
            )
            connection.execute(
                f"UPDATE {SESSION_TABLE} SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (SESSION_ACTIVE, row["id"]),
            )
        return self.active(conversation)

    def end(self, conversation: ConversationKey) -> bool:
        with self._connection() as connection:
            cursor = connection.execute(
                f"UPDATE {SESSION_TABLE} SET status=?, updated_at=CURRENT_TIMESTAMP "
                "WHERE conversation_key=? AND status=?",
                (SESSION_ENDED, conversation.storage_key(), SESSION_ACTIVE),
            )
        return cursor.rowcount > 0

    def set_agent_session_id(self, session_id: int, agent_session_id: str) -> None:
        with self._connection() as connection:
            connection.execute(
                f"UPDATE {SESSION_TABLE} SET agent_session_id=?, updated_at=CURRENT_TIMESTAMP "
                "WHERE id=?",
                (agent_session_id, session_id),
            )

    def claim_message(self, message: IncomingMessage) -> bool:
        if not message.message_id:
            return True
        with self._connection() as connection:
            cursor = connection.execute(
                f"INSERT OR IGNORE INTO {MESSAGE_RECEIPT_TABLE} "
                "(platform_id, message_id, conversation_key, sender_id, text, origin, status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    message.conversation.platform_id,
                    message.message_id,
                    message.conversation.storage_key(),
                    message.sender_id,
                    message.text,
                    message.origin,
                    RECEIPT_QUEUED,
                ),
            )
        return cursor.rowcount > 0

    def message_status(self, conversation: ConversationKey, message_id: str) -> str | None:
        if not message_id:
            return None
        with self._connection() as connection:
            row = connection.execute(
                f"SELECT status FROM {MESSAGE_RECEIPT_TABLE} "
                "WHERE platform_id=? AND message_id=?",
                (conversation.platform_id, message_id),
            ).fetchone()
        return row["status"] if row else None

    def queued_messages(self) -> list[IncomingMessage]:
        return self._messages_by_status(RECEIPT_QUEUED)

    def processing_messages(self) -> list[IncomingMessage]:
        return self._messages_by_status(RECEIPT_PROCESSING)

    def _messages_by_status(self, status: str) -> list[IncomingMessage]:
        with self._connection() as connection:
            rows = connection.execute(
                f"SELECT * FROM {MESSAGE_RECEIPT_TABLE} WHERE status=? ORDER BY created_at",
                (status,),
            ).fetchall()
        pending = []
        for row in rows:
            platform_id, kind, conversation_id = json.loads(row["conversation_key"])
            conversation = ConversationKey(
                platform_id, ConversationKind(kind), conversation_id
            )
            pending.append(IncomingMessage(
                conversation=conversation,
                sender_id=row["sender_id"],
                sender_name=row["sender_id"],
                message_id=row["message_id"],
                text=row["text"],
                origin=row["origin"],
                mentions_bot=conversation.kind is ConversationKind.GROUP,
            ))
        return pending

    def mark_message(self, conversation: ConversationKey, message_id: str, status: str) -> None:
        if not message_id:
            return
        with self._connection() as connection:
            connection.execute(
                f"UPDATE {MESSAGE_RECEIPT_TABLE} SET status=? WHERE platform_id=? AND message_id=?",
                (status, conversation.platform_id, message_id),
            )

    def record_turn(
        self, session_id: int, message_id: str, prompt: str, response: str, status: str
    ) -> None:
        with self._connection() as connection:
            connection.execute(
                f"INSERT INTO {TURN_TABLE} (session_id, message_id, prompt, response, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (session_id, message_id, prompt, response, status),
            )
