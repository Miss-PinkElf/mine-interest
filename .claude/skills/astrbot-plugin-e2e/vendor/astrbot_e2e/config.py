"""本地配置加载、校验与脱敏（Config）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

PRODUCTION_ROOT = (Path.home() / ".astrbot").resolve()
PRODUCTION_PORTS = frozenset({6185, 6199, 6099})
SECRET_KEYS = frozenset({"password", "token", "api_key", "jwt_secret", "secret"})
SECRET_KEYWORDS = ("password", "token", "api_key", "secret", "jwt")


class ConfigError(ValueError):
    """配置缺失或非法。"""


def load_config(path: Any) -> Dict[str, Any]:
    config_path = Path(path).expanduser()
    if not config_path.exists():
        raise ConfigError("配置文件不存在: {}".format(config_path))
    try:
        text = config_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ConfigError("配置文件编码非法: {}".format(exc)) from exc
    except OSError as exc:
        raise ConfigError("配置文件读取失败: {}".format(exc)) from exc
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConfigError("配置文件不是合法 JSON: {}".format(exc)) from exc
    if not isinstance(raw, dict):
        raise ConfigError("配置文件顶层必须是对象")
    if not str(raw.get("test_root") or "").strip():
        raise ConfigError("缺少配置项: test_root")
    raw["test_root"] = str(Path(raw["test_root"]).expanduser().resolve())
    validate_config(raw)
    return raw


def _port(value: Any, label: str) -> int:
    if isinstance(value, bool) or isinstance(value, float):
        raise ConfigError("{} 必须是整数端口".format(label))
    try:
        port = int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError("{} 必须是整数端口".format(label)) from exc
    if not 1 <= port <= 65535:
        raise ConfigError("{} 端口超出范围: {}".format(label, port))
    return port


def _url_port(value: Any, label: str) -> int:
    parsed = urlparse(str(value or ""))
    if not parsed.hostname:
        raise ConfigError("{} 不是合法 WebSocket URL".format(label))
    try:
        port = parsed.port
    except ValueError as exc:
        raise ConfigError("{} 端口非法: {}".format(label, parsed.netloc)) from exc
    if port is None:
        raise ConfigError("{} 缺少端口".format(label))
    return _port(port, label)


def validate_config(cfg: Dict[str, Any]) -> None:
    for key in ("test_root", "webui", "astrbot", "bot", "sender", "group_id"):
        if not cfg.get(key):
            raise ConfigError("缺少配置项: {}".format(key))

    for key in ("webui", "astrbot", "bot", "sender"):
        if not isinstance(cfg[key], dict):
            raise ConfigError("{} 必须是对象".format(key))

    test_root = Path(cfg["test_root"]).expanduser().resolve()
    cfg["test_root"] = str(test_root)
    if test_root == PRODUCTION_ROOT:
        raise ConfigError("test_root 不能是生产数据根 ~/.astrbot")

    if not str(cfg["astrbot"].get("command") or "").strip():
        raise ConfigError("astrbot.command 必填")

    bot_qq = str(cfg["bot"].get("qq") or "").strip()
    sender_qq = str(cfg["sender"].get("qq") or "").strip()
    if not bot_qq or not sender_qq:
        raise ConfigError("bot.qq 与 sender.qq 必填")
    if bot_qq == sender_qq:
        raise ConfigError("bot.qq 与 sender.qq 必须不同")

    ports = {
        "webui.port": _port(cfg["webui"].get("port"), "webui.port"),
        "astrbot.reverse_ws_port": _port(cfg["astrbot"].get("reverse_ws_port"), "astrbot.reverse_ws_port"),
        "bot.onebot_ws": _url_port(cfg["bot"].get("onebot_ws"), "bot.onebot_ws"),
        "sender.onebot_ws": _url_port(cfg["sender"].get("onebot_ws"), "sender.onebot_ws"),
    }
    overlap = set(ports.values()) & PRODUCTION_PORTS
    if overlap:
        raise ConfigError("端口与生产端口冲突: {}".format(sorted(overlap)))

    group_id = str(cfg["group_id"]).strip()
    if not group_id.isdigit():
        raise ConfigError("group_id 必须是数字字符串")
    cfg["group_id"] = group_id
    sources = cfg.get("plugin_sources")
    if sources is not None:
        if not isinstance(sources, dict):
            raise ConfigError("plugin_sources 必须是对象")
        normalized: Dict[str, str] = {}
        for name, path in sources.items():
            if not str(path or "").strip():
                raise ConfigError("plugin_sources.{} 不能为空".format(name))
            normalized[str(name)] = str(Path(path).expanduser())
        cfg["plugin_sources"] = normalized
    cfg["bot"]["qq"] = bot_qq
    cfg["sender"]["qq"] = sender_qq


def _is_secret_key(key: Any) -> bool:
    lowered = str(key).lower()
    return lowered in SECRET_KEYS or any(word in lowered for word in SECRET_KEYWORDS)


def mask_config(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: ("***" if _is_secret_key(key) else mask_config(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [mask_config(item) for item in value]
    return value
