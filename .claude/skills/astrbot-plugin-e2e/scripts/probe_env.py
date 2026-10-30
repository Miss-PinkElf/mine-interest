"""探测本机 AstrBot 插件测试环境（Environment Probe）。"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

SCHEMA_VERSION = 1
QQ_APP = Path("/Applications/QQ.app")
DEFAULT_PORTS = {
    "production_webui": 6185,
    "production_onebot": 6199,
    "production_napcat": 6099,
    "test_webui": 6186,
    "test_onebot": 6198,
    "test_sender_napcat": 6098,
    "test_bot_onebot": 6200,
    "test_sender_onebot": 6201,
}


def _paths(home: Path) -> Dict[str, Path]:
    return {
        "qq_app": QQ_APP,
        "qq_container": home
        / "Library/Containers/com.tencent.qq/Data/Library/Application Support/QQ",
        "napcat_install": home
        / "Library/Containers/com.tencent.qq/Data/Documents/napcat",
        "astrbot_data": home / ".astrbot",
    }


def _run(argv, cwd=None, timeout=10.0) -> Optional[str]:
    try:
        proc = subprocess.run(
            argv,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def _port_open(host: str, port: int, timeout: float = 0.3) -> bool:
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


def astrbot_info(paths: Dict[str, Path]) -> Dict[str, Any]:
    exe = shutil.which("astrbot")
    if not exe:
        fallback = Path.home() / ".local/bin/astrbot"
        exe = str(fallback) if fallback.exists() else ""
    version = None
    if exe:
        output = _run([exe, "--version"], cwd=paths["astrbot_data"])
        if output and "version" in output.lower():
            version = output.split()[-1]
    data_root = paths["astrbot_data"]
    return {
        "command": exe or "astrbot",
        "available": bool(exe),
        "version": version,
        "data_root": str(data_root),
        "data_root_exists": data_root.exists(),
    }


def napcat_info(paths: Dict[str, Path]) -> Dict[str, Any]:
    install = paths["napcat_install"]
    version = None
    package = install / "package.json"
    if package.exists():
        try:
            version = json.loads(package.read_text(encoding="utf-8")).get("version")
        except (OSError, ValueError):
            version = None
    workdirs = []
    for name in ("NapCat", "NapCat-e2e"):
        workdir = paths["qq_container"] / name
        if workdir.exists():
            workdirs.append(str(workdir))
    return {
        "install_dir": str(install),
        "available": install.exists(),
        "version": version,
        "workdirs": workdirs,
    }


def qq_info(paths: Dict[str, Path]) -> Dict[str, Any]:
    output = _run(["ps", "-axo", "command="]) or ""
    running = "QQ.app/Contents/MacOS/QQ" in output
    app = paths["qq_app"]
    return {"app": str(app), "app_exists": app.exists(), "running": running}


def plugin_info(paths: Dict[str, Path]) -> Dict[str, Any]:
    directory = paths["astrbot_data"] / "data" / "plugins"
    available = []
    if directory.exists():
        available = sorted(item.name for item in directory.iterdir() if item.is_dir())
    return {"production_dir": str(directory), "available": available}


def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    config_path = Path(path).expanduser()
    try:
        data = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return {"_error": str(exc), "_path": str(config_path)}
    if not isinstance(data, dict):
        return {"_error": "配置顶层不是对象", "_path": str(config_path)}
    data["_path"] = str(config_path)
    return data


def config_info(cfg: Dict[str, Any]) -> Dict[str, Any]:
    if not cfg:
        return {}
    return {
        "path": cfg.get("_path"),
        "error": cfg.get("_error"),
        "test_root": cfg.get("test_root"),
        "bot_qq": (cfg.get("bot") or {}).get("qq"),
        "sender_qq": (cfg.get("sender") or {}).get("qq"),
        "group_id": cfg.get("group_id"),
        "webui_port": (cfg.get("webui") or {}).get("port"),
        "reverse_ws_port": (cfg.get("astrbot") or {}).get("reverse_ws_port"),
    }


def port_info(cfg: Dict[str, Any]) -> Dict[str, Any]:
    ports = dict(DEFAULT_PORTS)
    if cfg:
        ports["test_webui"] = int((cfg.get("webui") or {}).get("port", 6186))
        ports["test_onebot"] = int((cfg.get("astrbot") or {}).get("reverse_ws_port", 6198))
    return {
        name: {"port": port, "open": _port_open("127.0.0.1", port)}
        for name, port in ports.items()
    }


def build_profile(config_path: Optional[str], home: Path) -> Dict[str, Any]:
    paths = _paths(Path(home))
    cfg = load_config(config_path)
    return {
        "schema_version": SCHEMA_VERSION,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "is_macos": platform.system() == "Darwin",
        },
        "python": {
            "version": sys.version.split()[0],
            "executable": sys.executable,
        },
        "astrbot": astrbot_info(paths),
        "napcat": napcat_info(paths),
        "qq": qq_info(paths),
        "plugins": plugin_info(paths),
        "ports": port_info(cfg),
        "config": config_info(cfg),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="探测 AstrBot 插件测试环境")
    parser.add_argument("--config", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--home", default=None, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    home = Path(args.home) if args.home else Path.home()
    profile = build_profile(args.config, home)
    text = json.dumps(profile, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
