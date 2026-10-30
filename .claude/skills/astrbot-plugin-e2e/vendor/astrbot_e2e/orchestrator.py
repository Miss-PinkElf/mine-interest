"""AstrBot 测试实例的启动、停止与健康检查（Orchestrator）。"""

from __future__ import annotations

import asyncio
import os
import signal
import socket
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .log_capture import LogCapture

PID_NAME = "astrbot-e2e.pid"
START_PORT_WAIT_SECONDS = 5.0
STOP_PORT_WAIT_SECONDS = 10.0
PORT_POLL_INTERVAL_SECONDS = 0.2


def port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


def _wait_ports_free(endpoints, timeout, interval=PORT_POLL_INTERVAL_SECONDS, probe=None):
    """等待所有端口释放，返回超时后仍被占用的端口列表。"""
    check = probe or port_open
    endpoints = list(endpoints)
    deadline = time.monotonic() + timeout
    while True:
        busy = [(host, port) for host, port in endpoints if check(host, port)]
        if not busy or time.monotonic() >= deadline:
            return busy
        time.sleep(interval)


def pid_is_astrbot(pid: int) -> bool:
    try:
        output = subprocess.check_output(
            ["ps", "-p", str(pid), "-o", "command="],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return "astrbot" in output.lower()


def _process_cwd(pid: int) -> Optional[str]:
    try:
        output = subprocess.check_output(
            ["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        # Linux 可在缺少 lsof 时退回 /proc；macOS 无 /proc，返回 None。
        try:
            return str((Path("/proc") / str(pid) / "cwd").resolve(strict=True))
        except OSError:
            return None
    except (subprocess.CalledProcessError, OSError):
        return None
    for line in output.splitlines():
        if line.startswith("n"):
            return line[1:]
    return None


def pid_belongs_to_instance(pid: int, test_root: Path) -> bool:
    if not pid_is_astrbot(pid):
        return False
    cwd = _process_cwd(pid)
    if not cwd:
        return False
    try:
        return Path(cwd).resolve() == Path(test_root).resolve()
    except OSError:
        return False


class AstrBotInstance:
    def __init__(self, cfg: Dict[str, Any], run_dir: Path):
        self.cfg = cfg
        self.root = Path(cfg["test_root"]).expanduser().resolve()
        self.run_dir = Path(run_dir)
        self.proc: Optional[subprocess.Popen] = None
        self.log_handle = None
        self._log_mark: Optional[int] = None

    def pid_file(self) -> Path:
        return self.root / PID_NAME

    def is_running(self) -> bool:
        path = self.pid_file()
        if not path.exists():
            return False
        try:
            pid = int(path.read_text(encoding="utf-8").strip())
        except ValueError:
            return False
        return pid_belongs_to_instance(pid, self.root)

    def port_endpoints(self):
        webui = self.cfg.get("webui") or {}
        reverse_host = str(self.cfg["astrbot"].get("reverse_ws_host", "127.0.0.1"))
        return [
            ("WebUI", "127.0.0.1", int(webui.get("port", 6186))),
            ("OneBot 反向 WS", reverse_host, int(self.cfg["astrbot"].get("reverse_ws_port", 6198))),
        ]

    def _port_endpoints(self):
        return self.port_endpoints()

    def start(self) -> subprocess.Popen:
        self.root.mkdir(parents=True, exist_ok=True)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        endpoints = self._port_endpoints()
        busy = _wait_ports_free(
            [(host, port) for _, host, port in endpoints],
            timeout=START_PORT_WAIT_SECONDS,
        )
        if busy:
            labels = {(host, port): label for label, host, port in endpoints}
            host, port = busy[0]
            raise RuntimeError(
                "端口已被占用: {} {}；请先停止旧的测试实例".format(
                    labels[(host, port)], port
                )
            )
        log_path = self.run_dir / "astrbot.log"
        self._log_mark = LogCapture(
            Path(self.cfg["test_root"]) / "data" / "logs" / "astrbot.log"
        ).mark()
        self.log_handle = log_path.open("ab")
        env = os.environ.copy()
        env["ASTRBOT_ROOT"] = str(self.root)
        try:
            self.proc = subprocess.Popen(
                [str(self.cfg["astrbot"]["command"]), "run"],
                cwd=str(self.root),
                env=env,
                stdout=self.log_handle,
                stderr=subprocess.STDOUT,
            )
            self.pid_file().write_text(str(self.proc.pid), encoding="utf-8")
            time.sleep(0.2)
            if self.proc.poll() is not None:
                raise RuntimeError(
                    "AstrBot 测试实例启动后立即退出，请查看 {}".format(log_path)
                )
        except Exception:
            self._log_mark = None
            if self.proc is not None:
                if self.proc.poll() is None:
                    try:
                        self.proc.kill()
                    except OSError:
                        pass
                try:
                    self.proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
                self.proc = None
            self.pid_file().unlink(missing_ok=True)
            self._close_log()
            raise
        return self.proc

    async def wait_ready(
        self,
        bot_client,
        timeout: Optional[float] = None,
        require_platform_log: bool = True,
    ) -> None:
        limit = float(
            timeout
            if timeout is not None
            else self.cfg["astrbot"].get("startup_timeout_seconds", 120)
        )
        deadline = time.monotonic() + limit
        webui = self.cfg.get("webui") or {}
        bot_qq = str(self.cfg.get("bot", {}).get("qq", ""))
        log = LogCapture(Path(self.cfg["test_root"]) / "data" / "logs" / "astrbot.log")
        current_size = log.mark()
        if self._log_mark is not None and current_size < self._log_mark:
            # 日志被截断或轮转，旧 mark 失效。
            self._log_mark = 0
        log_mark = self._log_mark if self._log_mark is not None else current_size
        while time.monotonic() < deadline:
            if self.proc and self.proc.poll() is not None:
                raise RuntimeError("AstrBot 测试实例提前退出")
            if port_open(str(webui.get("host", "127.0.0.1")), int(webui.get("port", 6186))):
                try:
                    info = await bot_client.call("get_login_info", {})
                    if str(info.get("user_id")) == bot_qq:
                        if not require_platform_log:
                            return
                        if "适配器已连接" in log.read_since(log_mark):
                            return
                except Exception:
                    pass
            await asyncio.sleep(1)
        raise TimeoutError("等待 AstrBot 测试实例就绪超时")

    def _close_log(self) -> None:
        if self.log_handle:
            self.log_handle.close()
            self.log_handle = None

    def _wait_for_ports_released(self) -> None:
        _wait_ports_free(
            [(host, port) for _, host, port in self._port_endpoints()],
            timeout=STOP_PORT_WAIT_SECONDS,
        )

    def stop(self) -> None:
        path = self.pid_file()
        if not path.exists():
            return
        try:
            pid = int(path.read_text(encoding="utf-8").strip())
        except ValueError:
            path.unlink(missing_ok=True)
            return
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            self._wait_for_ports_released()
            path.unlink(missing_ok=True)
            self.proc = None
            self._close_log()
            return
        except OSError as exc:
            raise RuntimeError("无法确认 PID {} 的状态: {}".format(pid, exc))
        if not pid_belongs_to_instance(pid, self.root):
            raise RuntimeError(
                "PID {} 不属于当前测试实例，拒绝终止（需通过 lsof 或 /proc 校验工作目录）".format(pid)
            )
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if not pid_is_astrbot(pid):
                break
            time.sleep(0.2)
        else:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if self.proc is not None:
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            self.proc = None
        self._wait_for_ports_released()
        path.unlink(missing_ok=True)
        self._close_log()
