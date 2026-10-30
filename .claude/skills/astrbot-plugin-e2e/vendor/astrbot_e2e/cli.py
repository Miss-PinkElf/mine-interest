"""命令行入口（CLI）。"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .bootstrap import prepare_instance, resolve_plugin_source
from .cases import load_case
from .config import ConfigError, load_config
from .onebot import OneBotClient
from .orchestrator import AstrBotInstance, port_open
from .runner import run_case
from .suite import run_suite

DEFAULT_CONFIG = "tools/astrbot_e2e/config.local.json"


def _add_subcommand(sub, name: str):
    parser = sub.add_parser(name)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    return parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="astrbot-e2e")
    sub = parser.add_subparsers(dest="command", required=True)
    _add_subcommand(sub, "doctor")
    init = _add_subcommand(sub, "init-instance")
    init.add_argument("--plugin", default=None)
    start = _add_subcommand(sub, "start-instance")
    start.add_argument("--plugin", default=None)
    _add_subcommand(sub, "stop-instance")
    run = _add_subcommand(sub, "run")
    run.add_argument("--case", required=True)
    run.add_argument("--reload", action="store_true")
    run.add_argument("--attach", action="store_true")
    suite = _add_subcommand(sub, "run-suite")
    suite.add_argument("--cases-dir", required=True)
    suite.add_argument("--plugin", default=None)
    suite.add_argument("--reload", action="store_true")
    suite.add_argument("--attach", action="store_true")
    suite.add_argument("--keep-running", action="store_true")
    suite.add_argument("--no-redact", action="store_true")
    return parser


async def _check_login(name: str, section: Dict[str, Any]) -> int:
    client = OneBotClient(section["onebot_ws"], section["token"])
    try:
        await client.connect()
        info = await client.call("get_login_info", {})
    except Exception as exc:
        print("{} OneBot 不可用: {}".format(name, exc))
        return 2
    finally:
        await client.close()
    if str(info.get("user_id")) != str(section["qq"]):
        print("{} 不匹配: 期望 {} 实际 {}".format(name, section["qq"], info.get("user_id")))
        return 2
    return 0


def _check_plugin_sources(cfg: Dict[str, Any]) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    for name in cfg["astrbot"]["plugins"]:
        try:
            source = resolve_plugin_source(cfg, repo_root, name)
        except RuntimeError as exc:
            print("插件源不可用: {}".format(exc))
            return 2
        print("插件源 OK: {} -> {}".format(name, source))
    return 0


def _check_test_ports(cfg: Dict[str, Any]) -> int:
    instance = AstrBotInstance(cfg, Path(cfg["test_root"]) / "bootstrap-run")
    running = instance.is_running()
    for label, host, port in instance.port_endpoints():
        if port_open(host, port):
            if running:
                print("{} {} 由测试实例占用（已运行）".format(label, port))
            else:
                print("{} {} 被未知进程占用；请先排查，不自动终止".format(label, port))
                return 2
    return 0


async def _doctor(cfg: Dict[str, Any]) -> int:
    code = await _check_login("机器人号", cfg["bot"])
    if code:
        return code
    code = await _check_login("发送者号", cfg["sender"])
    if code:
        return code
    code = _check_plugin_sources(cfg)
    if code:
        return code
    code = _check_test_ports(cfg)
    if code:
        return code
    root = Path(cfg["test_root"])
    if not (root / ".astrbot").exists():
        print("测试实例未初始化: {}".format(root))
        return 2
    print(
        "doctor OK: bot={} sender={} test_root={}".format(
            cfg["bot"]["qq"], cfg["sender"]["qq"], root
        )
    )
    return 0


async def _wait_instance(cfg: Dict[str, Any], instance: AstrBotInstance) -> None:
    client = OneBotClient(cfg["bot"]["onebot_ws"], cfg["bot"]["token"])
    try:
        await client.connect()
        await instance.wait_ready(client)
    finally:
        await client.close()


async def _run(cfg: Dict[str, Any], case_path: str, reload: bool, attach: bool) -> int:
    try:
        summary = await run_case(cfg, case_path, reload=reload, attach=attach)
    except Exception as exc:
        # run_case 已统一兜底；这里再兜一层，确保任何初始化异常都映射为 ERROR。
        print("用例执行异常: {}".format(exc), file=sys.stderr)
        return 2
    print("{}: {} ({})".format(summary["case"], summary["status"], summary.get("run_dir")))
    if summary["status"] == "PASSED":
        return 0
    if summary["status"] == "ERROR":
        return 2
    if summary["status"] == "SKIPPED":
        return 3
    return 1


def _case_paths(cases_dir: str, plugin: Optional[str]) -> List[str]:
    directory = Path(cases_dir).expanduser()
    if not directory.is_dir():
        raise ValueError("用例目录不存在: {}".format(directory))
    paths = sorted(
        str(path)
        for path in directory.glob("*.json")
        if not path.name.startswith("_")
    )
    if not paths:
        raise ValueError("用例目录为空: {}".format(directory))
    if plugin:
        keep = []
        for path in paths:
            if load_case(path)["plugin"] != plugin:
                raise ValueError(
                    "用例 {} 的插件不是 {}".format(path, plugin)
                )
            keep.append(path)
        paths = keep
    return paths


async def _run_suite(args: argparse.Namespace, cfg: Dict[str, Any]) -> int:
    try:
        paths = _case_paths(args.cases_dir, args.plugin)
        suite = await run_suite(
            cfg,
            paths,
            reload=args.reload,
            attach=args.attach,
            keep_running=args.keep_running,
            redact=not args.no_redact,
        )
    except Exception as exc:
        print("批量执行异常: {}".format(exc), file=sys.stderr)
        return 2
    print(
        "{}: {} ({})".format(
            suite["plugin"], suite["status"], suite["suite_dir"]
        )
    )
    if suite["status"] == "PASSED":
        return 0
    if suite["status"] == "ERROR":
        return 2
    if suite["status"] == "SKIPPED":
        return 3
    return 1


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print("配置错误: {}".format(exc), file=sys.stderr)
        return 2
    if args.command == "doctor":
        return asyncio.run(_doctor(cfg))
    if args.command == "init-instance":
        prepare_instance(cfg, args.plugin)
        return 0
    if args.command == "start-instance":
        prepare_instance(cfg, args.plugin)
        instance = AstrBotInstance(cfg, Path(cfg["test_root"]) / "bootstrap-run")
        try:
            instance.start()
            asyncio.run(_wait_instance(cfg, instance))
        except Exception as exc:
            print("测试实例未就绪: {}".format(exc), file=sys.stderr)
            # 启动或等待失败时必须停掉实例，避免留下半启动的孤儿进程。
            try:
                instance.stop()
            except Exception:
                pass
            return 2
        print(instance.proc.pid)
        return 0
    if args.command == "stop-instance":
        try:
            AstrBotInstance(cfg, Path(cfg["test_root"]) / "bootstrap-run").stop()
        except RuntimeError as exc:
            print("停止测试实例失败: {}".format(exc), file=sys.stderr)
            return 2
        return 0
    if args.command == "run":
        return asyncio.run(_run(cfg, args.case, args.reload, args.attach))
    if args.command == "run-suite":
        return asyncio.run(_run_suite(args, cfg))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
