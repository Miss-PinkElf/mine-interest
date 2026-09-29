"""QQ 会话准入与代理设置（QQ Admission Policy）。"""

from __future__ import annotations

import json
from pathlib import Path

from .constants import (
    ADMIN_QQ_IDS_KEY,
    DEFAULT_AGENT,
    DEFAULT_AGENT_KEY,
    DEFAULT_GROUP_RULES_JSON,
    DEFAULT_MODEL_KEY,
    ENABLED_GROUP_IDS_KEY,
    GLOBAL_ALLOWED_USER_IDS_KEY,
    GROUP_RULES_JSON_KEY,
    OWNER_QQ_ID_KEY,
    PLATFORM_ID_KEY,
    PRIVATE_ENABLED_KEY,
    PRIVATE_USER_IDS_KEY,
    PRIVATE_WORK_DIR_KEY,
    REASON_CONFIGURATION_INVALID,
    REASON_NOT_ALLOWED,
    REASON_OUT_OF_SCOPE,
    REASON_WORK_DIR_MISSING,
    SUPPORTED_AGENTS,
)
from .contracts import AuthorizationDecision, ConversationKind, IncomingMessage, SessionSettings


def _id_set(values) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {str(value).strip() for value in values if str(value).strip()}


def _group_rules(config: dict) -> dict:
    raw = config.get(GROUP_RULES_JSON_KEY) or DEFAULT_GROUP_RULES_JSON
    if isinstance(raw, dict):
        return raw
    parsed = json.loads(str(raw))
    if not isinstance(parsed, dict):
        raise ValueError("群配置必须是 JSON 对象")
    return parsed


def _session_settings(rule: dict, config: dict) -> SessionSettings | None:
    work_dir = str(rule.get("work_dir") or "").strip()
    if not work_dir:
        return None
    agent_type = str(rule.get("agent") or config.get(DEFAULT_AGENT_KEY) or DEFAULT_AGENT).strip()
    if agent_type not in SUPPORTED_AGENTS:
        raise ValueError("不支持的代理类型")
    model = str(rule.get("model") or config.get(DEFAULT_MODEL_KEY) or "").strip()
    return SessionSettings(work_dir=str(Path(work_dir).expanduser()), agent_type=agent_type, model=model)


def authorize(message: IncomingMessage, config: dict) -> AuthorizationDecision:
    """先定会话范围，再判断角色和白名单；拒绝结果不得启动代理。"""
    if message.conversation.platform_id != str(config.get(PLATFORM_ID_KEY) or "").strip():
        return AuthorizationDecision(False, "none", REASON_OUT_OF_SCOPE)

    sender_id = message.sender_id
    owner_id = str(config.get(OWNER_QQ_ID_KEY) or "").strip()
    admin_ids = _id_set(config.get(ADMIN_QQ_IDS_KEY))
    role = "owner" if owner_id and sender_id == owner_id else "admin" if sender_id in admin_ids else "member"

    if message.conversation.kind is ConversationKind.GROUP:
        group_id = message.conversation.conversation_id
        if group_id not in _id_set(config.get(ENABLED_GROUP_IDS_KEY)):
            return AuthorizationDecision(False, role, REASON_OUT_OF_SCOPE)
        try:
            rule = _group_rules(config).get(group_id)
        except (TypeError, ValueError, json.JSONDecodeError):
            return AuthorizationDecision(False, role, REASON_CONFIGURATION_INVALID)
        if not isinstance(rule, dict):
            return AuthorizationDecision(False, role, REASON_CONFIGURATION_INVALID)
        allowed_ids = _id_set(rule.get("allowed_user_ids")) or _id_set(
            config.get(GLOBAL_ALLOWED_USER_IDS_KEY)
        )
    else:
        if not bool(config.get(PRIVATE_ENABLED_KEY, False)):
            return AuthorizationDecision(False, role, REASON_OUT_OF_SCOPE)
        allowed_ids = _id_set(config.get(PRIVATE_USER_IDS_KEY))
        private_root = str(config.get(PRIVATE_WORK_DIR_KEY) or "").strip()
        rule = {"work_dir": str(Path(private_root).expanduser() / sender_id)} if private_root else {}

    if role == "member" and sender_id not in allowed_ids:
        return AuthorizationDecision(False, role, REASON_NOT_ALLOWED)

    try:
        settings = _session_settings(rule, config)
    except (TypeError, ValueError):
        return AuthorizationDecision(False, role, REASON_CONFIGURATION_INVALID)
    if settings is None:
        return AuthorizationDecision(False, role, REASON_WORK_DIR_MISSING)
    return AuthorizationDecision(True, role, settings=settings)
