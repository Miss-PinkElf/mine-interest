"""测试实例初始化、配置写入与插件同步（Bootstrap）。"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

PLATFORM_ID = "Test-E2E"


def ensure_test_root(cfg: Dict[str, Any]) -> Path:
    root = Path(cfg["test_root"]).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _run(argv: List[str], cwd: Path, input_text: Optional[str] = None) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        argv,
        cwd=str(cwd),
        input=input_text,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "命令失败: {}\nstdout:\n{}\nstderr:\n{}".format(argv, proc.stdout, proc.stderr)
        )
    return proc


def run_init(cfg: Dict[str, Any]) -> None:
    root = ensure_test_root(cfg)
    _run([str(cfg["astrbot"]["command"]), "init", "-y"], cwd=root)


def set_dashboard_password(cfg: Dict[str, Any]) -> None:
    root = ensure_test_root(cfg)
    password = str(cfg["webui"]["password"])
    _run(
        [str(cfg["astrbot"]["command"]), "password", "--username", str(cfg["webui"]["username"])],
        cwd=root,
        input_text="{}\n{}\n".format(password, password),
    )


def patch_config(cfg: Dict[str, Any]) -> None:
    root = ensure_test_root(cfg)
    path = root / "data" / "cmd_config.json"
    if not path.exists():
        raise RuntimeError("cmd_config.json 不存在，请先执行 astrbot init 与 password")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    data.setdefault("dashboard", {})
    data["dashboard"].update(
        {"enable": True, "host": "127.0.0.1", "port": int(cfg["webui"]["port"])}
    )
    data["platform"] = [
        {
            "id": PLATFORM_ID,
            "type": "aiocqhttp",
            "enable": True,
            "ws_reverse_host": cfg["astrbot"]["reverse_ws_host"],
            "ws_reverse_port": int(cfg["astrbot"]["reverse_ws_port"]),
            "ws_reverse_token": cfg["astrbot"]["reverse_ws_token"],
        }
    ]
    data["plugin_set"] = list(cfg["astrbot"]["plugins"])
    data["disable_builtin_commands"] = True
    data["log_level"] = "INFO"
    data["log_file_enable"] = True
    data["log_file_path"] = "logs/astrbot.log"
    data["wake_prefix"] = ["/"]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "data" / "logs").mkdir(parents=True, exist_ok=True)


def sync_plugins(cfg: Dict[str, Any], repo_root: Path, plugins: List[str]) -> None:
    target_base = ensure_test_root(cfg) / "data" / "plugins"
    target_base.mkdir(parents=True, exist_ok=True)
    for name in plugins:
        integration_source = Path(repo_root) / "integrations" / "astrbot" / name
        fixture_source = Path(repo_root) / "tools" / "astrbot_e2e" / "fixtures" / name
        source = integration_source if integration_source.exists() else fixture_source
        if not source.exists():
            raise RuntimeError(
                "插件源目录不存在，已尝试: {} 与 {}".format(
                    integration_source, fixture_source
                )
            )
        target = target_base / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "tests"),
        )


def write_cc_qq_config(cfg: Dict[str, Any], enabled: bool = True) -> None:
    root = ensure_test_root(cfg)
    config_dir = root / "data" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    work_dir = root / "workdir"
    work_dir.mkdir(exist_ok=True)
    enabled_groups = [str(cfg["group_id"])] if enabled else []
    rules = {str(cfg["group_id"]): {"work_dir": str(work_dir)}} if enabled else {}
    data = {
        "qq_platform_id": PLATFORM_ID,
        "enabled_group_ids": enabled_groups,
        "private_enabled": False,
        "owner_qq_id": str(cfg["sender"]["qq"]),
        "admin_qq_ids": [],
        "global_allowed_user_ids": [],
        "private_user_ids": [],
        "guest_permission_profile": "readonly",
        "member_permission_profile": "workspace",
        "owner_permission_profile": "full",
        "readonly_mcp_enabled": True,
        "danger_approval_enabled": True,
        "danger_approval_timeout_seconds": 60,
        "allowed_work_dirs": [],
        "private_work_dir": "",
        "group_rules_json": json.dumps(rules, ensure_ascii=False),
        "default_agent": "claude",
        "default_claude_model": "",
        "default_codex_model": "",
        "claude_command": "claude",
        "codex_command": "codex",
        "claude_setting_sources": "",
        "stale_message_max_age_seconds": 180,
    }
    (config_dir / "astrbot_plugin_cc_qq_config.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def prepare_instance(
    cfg: Dict[str, Any],
    active_plugin: Optional[str] = None,
    repo_root: Optional[Path] = None,
) -> None:
    root = ensure_test_root(cfg)
    if not (root / ".astrbot").exists():
        run_init(cfg)
    if not (root / "data" / "cmd_config.json").exists():
        set_dashboard_password(cfg)
    patch_config(cfg)
    repo = Path(repo_root) if repo_root else Path(__file__).resolve().parents[2]
    sync_plugins(cfg, repo, list(cfg["astrbot"]["plugins"]))
    write_cc_qq_config(cfg, enabled=active_plugin in (None, "astrbot_plugin_cc_qq"))
