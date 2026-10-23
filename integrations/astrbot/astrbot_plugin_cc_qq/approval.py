"""本机危险操作审批服务（Approval Broker）。

审批 hook 与插件之间只使用 127.0.0.1 上的单行 JSON 协议，
不引入额外的 Web 依赖，也不把 token 写进任何日志。
"""

from __future__ import annotations

import asyncio
import json
import secrets
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Optional

from .constants import (
    APPROVAL_APPROVED_REPLY,
    APPROVAL_APPROVED_STATUS,
    APPROVAL_BROKER_ERROR_REPLY,
    APPROVAL_BROKER_HOST,
    APPROVAL_DENIED_REPLY,
    APPROVAL_DENIED_STATUS,
    APPROVAL_DISABLED_REPLY,
    APPROVAL_ENV_HOST,
    APPROVAL_ENV_PORT,
    APPROVAL_ENV_TIMEOUT,
    APPROVAL_ENV_TOKEN,
    APPROVAL_NOT_FOUND_REPLY,
    APPROVAL_PENDING_STATUS,
    APPROVAL_REQUEST_TEMPLATE,
    APPROVAL_SUMMARY_MAX_CHARS,
    APPROVAL_TIMEOUT_REPLY,
    APPROVAL_TIMEOUT_STATUS,
    DANGER_APPROVAL_ENABLED_KEY,
    DANGER_APPROVAL_TIMEOUT_SECONDS_KEY,
    DEFAULT_DANGER_APPROVAL_TIMEOUT_SECONDS,
    LOG_PREFIX,
    MAX_DANGER_APPROVAL_TIMEOUT_SECONDS,
    MIN_DANGER_APPROVAL_TIMEOUT_SECONDS,
)
from .permissions import clamp_approval_timeout

Notifier = Callable[[str, str], Awaitable[None]]


def approval_targets(origin: str, admin_origins) -> list[str]:
    """审批卡片发回来源会话，并尽量私聊已见过的 owner/管理员。"""
    targets: list[str] = []
    for value in (origin, *(admin_origins or ())):
        text = str(value or "").strip()
        if text and text not in targets:
            targets.append(text)
    return targets


BROKER_READ_TIMEOUT_SECONDS = 10
BROKER_MAX_LINE_BYTES = 65_536
APPROVAL_ID_BYTES = 3


@dataclass
class PendingApproval:
    id: str
    conversation_key: str
    origin: str
    sender_id: str
    role: str
    profile: str
    tool_name: str
    summary: str
    future: asyncio.Future
    approver_id: str = ""
    resolved: bool = field(default=False)


class ApprovalBroker:
    def __init__(self, store, logger, config: dict):
        self.store = store
        self.logger = logger
        self.enabled = bool(config.get(DANGER_APPROVAL_ENABLED_KEY, True))
        self.timeout_seconds = clamp_approval_timeout(
            config.get(DANGER_APPROVAL_TIMEOUT_SECONDS_KEY),
            DEFAULT_DANGER_APPROVAL_TIMEOUT_SECONDS,
            MIN_DANGER_APPROVAL_TIMEOUT_SECONDS,
            MAX_DANGER_APPROVAL_TIMEOUT_SECONDS,
        )
        self._server: Optional[asyncio.AbstractServer] = None
        self._token = ""
        self._port = 0
        self._notifier: Optional[Notifier] = None
        self._pending: dict[str, PendingApproval] = {}
        self._dedupe: dict[tuple[str, ...], str] = {}

    @property
    def is_running(self) -> bool:
        return self._server is not None

    def hook_env(self) -> dict[str, str]:
        if not self._token:
            return {}
        return {
            APPROVAL_ENV_HOST: APPROVAL_BROKER_HOST,
            APPROVAL_ENV_PORT: str(self._port),
            APPROVAL_ENV_TOKEN: self._token,
            APPROVAL_ENV_TIMEOUT: str(self.timeout_seconds),
        }

    async def start(self, notifier: Notifier) -> None:
        if not self.enabled or self._server is not None:
            return
        self._notifier = notifier
        self._token = secrets.token_urlsafe(24)
        self._server = await asyncio.start_server(
            self._handle_client, APPROVAL_BROKER_HOST, 0
        )
        socket = self._server.sockets[0]
        self._port = int(socket.getsockname()[1])
        self.logger.info("%s 审批服务已启动，端口 %s", LOG_PREFIX, self._port)

    async def stop(self) -> None:
        for pending in list(self._pending.values()):
            if not pending.future.done():
                pending.future.set_result((False, APPROVAL_BROKER_ERROR_REPLY))
        self._pending.clear()
        self._dedupe.clear()
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        self._token = ""

    async def request(self, payload: dict) -> tuple[bool, str]:
        """返回 (是否批准, 给 hook 的原因)；任何异常或超时都按拒绝。"""
        if not self.enabled:
            return False, APPROVAL_DISABLED_REPLY

        conversation_key = str(payload.get("conversation_key") or "")
        sender_id = str(payload.get("sender_id") or "")
        origin = str(payload.get("origin") or "")
        role = str(payload.get("role") or "")
        profile = str(payload.get("profile") or "")
        tool_name = str(payload.get("tool_name") or "")
        summary = str(payload.get("summary") or "")[:APPROVAL_SUMMARY_MAX_CHARS]

        dedupe_key = (conversation_key, sender_id, tool_name, summary)
        existing_id = self._dedupe.get(dedupe_key)
        if existing_id and existing_id in self._pending:
            pending = self._pending[existing_id]
            return await self._wait(pending)

        approval_id = self._new_id()
        loop = asyncio.get_running_loop()
        pending = PendingApproval(
            id=approval_id,
            conversation_key=conversation_key,
            origin=origin,
            sender_id=sender_id,
            role=role,
            profile=profile,
            tool_name=tool_name,
            summary=summary,
            future=loop.create_future(),
        )
        self._pending[approval_id] = pending
        self._dedupe[dedupe_key] = approval_id
        self.store.record_permission_event(
            conversation_key, sender_id, role, profile, tool_name, summary,
            APPROVAL_PENDING_STATUS,
        )

        if not origin or self._notifier is None:
            self._finish(pending, False, APPROVAL_BROKER_ERROR_REPLY, APPROVAL_BROKER_ERROR_REPLY)
            return False, APPROVAL_BROKER_ERROR_REPLY

        message = APPROVAL_REQUEST_TEMPLATE.format(
            approval_id=approval_id,
            sender_id=sender_id or "未知",
            tool_name=tool_name or "未知",
            summary=summary or "无摘要",
            timeout=self.timeout_seconds,
        )
        try:
            await self._notifier(origin, message)
        except Exception:
            self.logger.error("%s 审批卡片发送失败", LOG_PREFIX)
            self._finish(pending, False, APPROVAL_BROKER_ERROR_REPLY, APPROVAL_BROKER_ERROR_REPLY)
            return False, APPROVAL_BROKER_ERROR_REPLY

        return await self._wait(pending)

    async def _wait(self, pending: PendingApproval) -> tuple[bool, str]:
        try:
            approved, reason = await asyncio.wait_for(
                asyncio.shield(pending.future), timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            self._finish(
                pending, False, APPROVAL_TIMEOUT_REPLY, APPROVAL_TIMEOUT_REPLY,
                status=APPROVAL_TIMEOUT_STATUS,
            )
            return False, APPROVAL_TIMEOUT_REPLY
        return bool(approved), str(reason)

    def _finish(
        self,
        pending: PendingApproval,
        approved: bool,
        hook_reason: str,
        audit_reason: str,
        status: str | None = None,
        approver_id: str = "",
    ) -> None:
        if pending.resolved:
            return
        pending.resolved = True
        pending.approver_id = approver_id
        if not pending.future.done():
            pending.future.set_result((approved, hook_reason))
        self._pending.pop(pending.id, None)
        for key, value in list(self._dedupe.items()):
            if value == pending.id:
                self._dedupe.pop(key, None)
        decision = status or (APPROVAL_APPROVED_STATUS if approved else APPROVAL_DENIED_STATUS)
        self.store.record_permission_event(
            pending.conversation_key,
            pending.sender_id,
            pending.role,
            pending.profile,
            pending.tool_name,
            pending.summary,
            decision,
            audit_reason,
            approver_id,
        )

    def resolve(self, approval_id: str, approved: bool, approver_id: str) -> str:
        """owner/管理员回复 /approve 或 /deny 时调用。"""
        pending = self._pending.get(approval_id)
        if pending is None or pending.resolved:
            return APPROVAL_NOT_FOUND_REPLY
        if approved:
            self._finish(
                pending, True, "管理员批准", "管理员批准",
                status=APPROVAL_APPROVED_STATUS, approver_id=approver_id,
            )
            return APPROVAL_APPROVED_REPLY.format(approval_id=approval_id)
        self._finish(
            pending, False, "管理员拒绝", "管理员拒绝",
            status=APPROVAL_DENIED_STATUS, approver_id=approver_id,
        )
        return APPROVAL_DENIED_REPLY.format(approval_id=approval_id)

    def pending_count(self) -> int:
        return len(self._pending)

    def pending_ids(self) -> list[str]:
        return list(self._pending)

    def _new_id(self) -> str:
        while True:
            candidate = secrets.token_hex(APPROVAL_ID_BYTES)
            if candidate not in self._pending:
                return candidate

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            raw = await asyncio.wait_for(
                reader.readline(), timeout=BROKER_READ_TIMEOUT_SECONDS
            )
            if not raw or len(raw) > BROKER_MAX_LINE_BYTES:
                await self._write_response(writer, False, APPROVAL_BROKER_ERROR_REPLY)
                return
            payload = json.loads(raw.decode("utf-8"))
            token = str(payload.get("token") or "")
            if not secrets.compare_digest(token, self._token):
                await self._write_response(writer, False, APPROVAL_BROKER_ERROR_REPLY)
                return
            approved, reason = await self.request(payload)
            await self._write_response(writer, approved, reason)
        except (asyncio.TimeoutError, json.JSONDecodeError, UnicodeDecodeError):
            await self._write_response(writer, False, APPROVAL_BROKER_ERROR_REPLY)
        except Exception:
            self.logger.error("%s 审批请求处理失败", LOG_PREFIX)
            await self._write_response(writer, False, APPROVAL_BROKER_ERROR_REPLY)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    @staticmethod
    async def _write_response(
        writer: asyncio.StreamWriter, approved: bool, reason: str
    ) -> None:
        response = json.dumps(
            {"decision": "allow" if approved else "deny", "reason": str(reason)},
            ensure_ascii=False,
        )
        writer.write((response + "\n").encode("utf-8"))
        try:
            await writer.drain()
        except Exception:
            pass
