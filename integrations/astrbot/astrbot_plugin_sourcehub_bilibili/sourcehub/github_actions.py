"""GitHub 自动化（GitHub Automation）：star、fork 与 fork 同步工作流。"""

from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_GITHUB_PROXY = "http://127.0.0.1:7897"
GH_TIMEOUT_SECONDS = 30
MAX_REPOSITORIES_PER_MESSAGE = 5
MAX_ACTION_RECORDS = 50
WORKFLOW_FILE = ".github/workflows/sourcehub-fork-sync.yml"
WORKFLOW_MARKER = "# Managed by SourceHub"
WORKFLOW_CRON = "17 */6 * * *"

GH_CANDIDATE_PATHS = (
    "/opt/homebrew/bin/gh",
    "/usr/local/bin/gh",
    str(Path.home() / ".local/bin/gh"),
)

PROXY_ENV_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)

NETWORK_ERROR_MARKERS = (
    "could not resolve host",
    "no such host",
    "connection refused",
    "connection reset",
    "connection timed out",
    "dial tcp",
    "unexpected eof",
    "failed to connect",
    "http2:",
    "i/o timeout",
    "network is unreachable",
    "proxyconnect",
    "tls handshake",
    "timeout",
    "timed out",
    "error connecting to api.github.com",
    "check your internet connection",
)

AUTH_ERROR_MARKERS = (
    "http 401",
    "http 403",
    "bad credentials",
    "authentication failed",
    "forbidden",
    "gh auth login",
    "insufficient scope",
    "not logged in",
    "requires authentication",
    "resource not accessible",
    "workflow scope",
)

RATE_LIMIT_MARKERS = ("api rate limit", "rate limit exceeded")

NOT_FOUND_MARKERS = ("http 404", "not found")

FORK_NAME_PATTERNS = (
    re.compile(r"https://github\.com/([\w.-]+/[\w.-]+)"),
    re.compile(r"(?i)created fork ([\w.-]+/[\w.-]+)"),
)


@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    via_proxy: bool = False

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    @property
    def output(self) -> str:
        return "\n".join(part for part in (self.stdout, self.stderr) if part).strip()


@dataclass(frozen=True)
class ActionResult:
    repository: str
    action: str
    ok: bool
    message: str
    via_proxy: bool = False


@dataclass(frozen=True)
class WorkflowResult:
    ok: bool
    message: str
    via_proxy: bool = False


def resolve_gh_path(configured: str = "") -> str:
    """按配置、PATH、常见安装位置依次查找 gh。"""
    configured = str(configured or "").strip()
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_file():
            return str(candidate)
        found = shutil.which(configured)
        return found or ""
    found = shutil.which("gh")
    if found:
        return found
    for path in GH_CANDIDATE_PATHS:
        if Path(path).is_file():
            return path
    return ""


def _lower_output(result: CommandResult) -> str:
    return result.output.lower()


def is_network_error(result: CommandResult) -> bool:
    text = _lower_output(result)
    return any(marker in text for marker in NETWORK_ERROR_MARKERS)


def is_auth_error(result: CommandResult) -> bool:
    text = _lower_output(result)
    return any(marker in text for marker in AUTH_ERROR_MARKERS)


def is_rate_limit_error(result: CommandResult) -> bool:
    text = _lower_output(result)
    return any(marker in text for marker in RATE_LIMIT_MARKERS)


def is_not_found_error(result: CommandResult) -> bool:
    text = _lower_output(result)
    return any(marker in text for marker in NOT_FOUND_MARKERS)


def describe_failure(result: CommandResult, proxy_url: str = "") -> str:
    """把 gh 失败翻译成可直接展示给人看的中文说明。"""
    if "gh_not_found" in _lower_output(result):
        return "找不到 gh 命令，请安装 GitHub CLI，或在插件配置里填写 gh 路径。"
    if is_rate_limit_error(result):
        return "GitHub API 触发限流，请稍后重试。"
    if is_auth_error(result):
        return "GitHub 权限不足或 gh 未登录，请在本机执行 gh auth status 检查。"
    if is_not_found_error(result):
        return "仓库不存在，或当前账号无权访问。"
    if is_network_error(result):
        proxy_hint = proxy_url or DEFAULT_GITHUB_PROXY
        if result.via_proxy:
            return f"无法连接 GitHub（直连和代理 {proxy_hint} 均失败），请检查 ClashVerge 或网络。"
        return f"无法连接 GitHub，请检查网络，或确认本机代理 {proxy_hint} 可用。"
    line = next((item.strip() for item in result.output.splitlines() if item.strip()), "")
    return f"gh 执行失败：{line[:160]}" if line else "gh 执行失败。"


def parse_fork_name(output: str) -> str:
    """从 gh repo fork 的输出里取出 fork 全名。"""
    for pattern in FORK_NAME_PATTERNS:
        match = pattern.search(output or "")
        if match:
            return match.group(1).removesuffix(".git")
    return ""


def workflow_template(upstream: str, upstream_branch: str, fork_branch: str) -> str:
    """生成只同步默认分支、保留工作流文件的 GitHub Actions 工作流。"""
    return f"""# {WORKFLOW_MARKER}。请勿手工修改，插件会在需要时覆盖。
name: SourceHub Fork Sync

on:
  schedule:
    - cron: "{WORKFLOW_CRON}"
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: sourcehub-fork-sync
  cancel-in-progress: false

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout fork
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Merge upstream default branch
        env:
          UPSTREAM_REPOSITORY: "{upstream}"
          UPSTREAM_BRANCH: "{upstream_branch}"
          FORK_BRANCH: "{fork_branch}"
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git remote add upstream "https://github.com/${{UPSTREAM_REPOSITORY}}.git"
          git fetch upstream "${{UPSTREAM_BRANCH}}"
          git merge --no-edit "upstream/${{UPSTREAM_BRANCH}}"
          git push origin "HEAD:${{FORK_BRANCH}}"
"""


class GithubRunner:
    """执行 gh 命令；直连失败且属于网络错误时，用本机代理重试一次。"""

    def __init__(
        self,
        gh_path: str = "",
        proxy_url: str = DEFAULT_GITHUB_PROXY,
        timeout: int = GH_TIMEOUT_SECONDS,
        run=subprocess.run,
    ):
        self.gh_path = resolve_gh_path(gh_path)
        self.proxy_url = str(proxy_url or "").strip()
        self.timeout = timeout
        self._run_command = run

    def _environment(self, use_proxy: bool) -> dict:
        """直连时清掉系统代理；只有显式重试时才设置插件代理。"""
        environment = dict(os.environ)
        for key in PROXY_ENV_KEYS:
            environment.pop(key, None)
        if use_proxy and self.proxy_url:
            for key in PROXY_ENV_KEYS:
                environment[key] = self.proxy_url
            environment["NO_PROXY"] = "localhost,127.0.0.1,::1"
            environment["no_proxy"] = environment["NO_PROXY"]
        return environment

    def run(self, args: list[str], use_proxy: bool = False) -> CommandResult:
        if not self.gh_path:
            return CommandResult(-1, "", "gh_not_found")
        try:
            completed = self._run_command(
                [self.gh_path, *args],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=self._environment(use_proxy),
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return CommandResult(-1, "", f"{type(exc).__name__}: {exc}", via_proxy=use_proxy)
        return CommandResult(
            completed.returncode,
            completed.stdout or "",
            completed.stderr or "",
            via_proxy=use_proxy,
        )

    def run_with_fallback(self, args: list[str]) -> CommandResult:
        direct = self.run(args)
        if direct.ok or not is_network_error(direct) or not self.proxy_url:
            return direct
        return self.run(args, use_proxy=True)


class GithubAutomation:
    """对采集内容执行 star/fork，并把结果记录到本机状态文件。"""

    def __init__(self, state_path: Path, runner: GithubRunner):
        self.state_path = Path(state_path)
        self.runner = runner
        self._lock = threading.Lock()
        self._state = self._load_state()

    def handle(self, repositories, fork: bool, source: str) -> list[ActionResult]:
        """按顺序处理仓库列表；同一仓库重复出现只处理一次。"""
        selected = list(dict.fromkeys(repositories))[:MAX_REPOSITORIES_PER_MESSAGE]
        results: list[ActionResult] = []
        with self._lock:
            try:
                for repository in selected:
                    try:
                        results.append(self._star(repository, source))
                        if fork:
                            results.append(self._fork(repository, source))
                    except Exception as exc:  # 单仓库失败不能拖垮其它仓库
                        result = ActionResult(
                            repository, "error", False, f"内部错误：{type(exc).__name__}"
                        )
                        self._record(source, result)
                        results.append(result)
            finally:
                self._save_state()
        return results

    def recent_actions(self, limit: int = 10) -> list[dict]:
        with self._lock:
            return list(self._state["actions"][-limit:])

    def _load_state(self) -> dict:
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        if not isinstance(data, dict):
            data = {}
        repositories = data.get("repos")
        actions = data.get("actions")
        return {
            "version": 1,
            "login": str(data.get("login") or ""),
            "repos": repositories if isinstance(repositories, dict) else {},
            "actions": actions if isinstance(actions, list) else [],
        }

    def _save_state(self) -> None:
        self._state["updated_at"] = _now()
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.state_path.with_suffix(self.state_path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(self._state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        temporary.replace(self.state_path)

    def _repo_state(self, repository: str) -> dict:
        state = self._state["repos"].get(repository)
        if not isinstance(state, dict):
            state = {}
            self._state["repos"][repository] = state
        return state

    def _record(self, source: str, result: ActionResult) -> None:
        self._state["actions"].append(
            {
                "at": _now(),
                "source": source,
                "repository": result.repository,
                "action": result.action,
                "ok": result.ok,
                "via_proxy": result.via_proxy,
                "message": result.message,
            }
        )
        del self._state["actions"][:-MAX_ACTION_RECORDS]

    def _login(self) -> tuple[str, CommandResult | None]:
        cached = str(self._state.get("login") or "")
        if cached:
            return cached, None
        result = self.runner.run_with_fallback(["api", "user", "--jq", ".login"])
        if result.ok and result.stdout.strip():
            self._state["login"] = result.stdout.strip()
        return str(self._state.get("login") or ""), result

    def _api_json(self, endpoint: str) -> tuple[dict | None, CommandResult]:
        result = self.runner.run_with_fallback(["api", endpoint])
        if not result.ok:
            return None, result
        try:
            payload = json.loads(result.stdout)
        except (TypeError, ValueError):
            return None, CommandResult(1, result.stdout, "api_response_not_json", result.via_proxy)
        return (payload if isinstance(payload, dict) else None), result

    def _star(self, repository: str, source: str) -> ActionResult:
        state = self._repo_state(repository)
        if state.get("starred_at"):
            return ActionResult(repository, "star", True, "已经 star，跳过")
        result = self.runner.run_with_fallback(
            ["api", "--method", "PUT", f"/user/starred/{repository}"]
        )
        if result.ok:
            state["starred_at"] = _now()
            action = ActionResult(repository, "star", True, "已 star", result.via_proxy)
        else:
            action = ActionResult(
                repository, "star", False, describe_failure(result, self.runner.proxy_url), result.via_proxy
            )
        self._record(source, action)
        return action

    def _fork(self, repository: str, source: str) -> ActionResult:
        login, login_result = self._login()
        if not login:
            detail = (
                describe_failure(login_result, self.runner.proxy_url)
                if login_result is not None
                else "拿不到当前 GitHub 账号，请检查 gh 登录。"
            )
            result = ActionResult(repository, "fork", False, detail)
            self._record(source, result)
            return result

        owner, separator, name = repository.partition("/")
        if not separator or not name:
            result = ActionResult(repository, "fork", False, "仓库全名不完整。")
            self._record(source, result)
            return result
        if owner.lower() == login.lower():
            result = ActionResult(repository, "fork", True, "这是你自己的仓库，不需要 fork。")
            self._record(source, result)
            return result

        upstream, upstream_result = self._api_json(f"repos/{repository}")
        if upstream is None:
            result = ActionResult(
                repository, "fork", False, describe_failure(upstream_result, self.runner.proxy_url), upstream_result.via_proxy
            )
            self._record(source, result)
            return result
        upstream_name = str(upstream.get("name") or name)
        upstream_branch = str(upstream.get("default_branch") or "master")

        fork_data = self._existing_fork(login, upstream_name, repository)
        via_proxy = upstream_result.via_proxy
        if fork_data is None:
            created = self.runner.run_with_fallback(
                ["repo", "fork", repository, "--clone=false", "--remote=false", "--default-branch-only"]
            )
            via_proxy = created.via_proxy
            if not created.ok:
                result = ActionResult(
                    repository, "fork", False, describe_failure(created, self.runner.proxy_url), created.via_proxy
                )
                self._record(source, result)
                return result
            fork_full = parse_fork_name(created.stdout) or f"{login}/{upstream_name}"
            fork_data, _ = self._api_json(f"repos/{fork_full}")
            if fork_data is None:
                fork_data = {"full_name": fork_full, "default_branch": upstream_branch}
        else:
            fork_full = str(fork_data.get("full_name") or f"{login}/{upstream_name}")
        fork_full = str(fork_data.get("full_name") or fork_full)
        fork_branch = str(fork_data.get("default_branch") or upstream_branch)

        workflow = self._ensure_workflow(fork_full, repository, upstream_branch, fork_branch)
        state = self._repo_state(repository)
        state["fork"] = {
            "full_name": fork_full,
            "default_branch": fork_branch,
            "installed_at": _now(),
            "workflow_file": WORKFLOW_FILE,
        }
        if workflow.ok:
            message = (
                f"已 fork 到 {fork_full}；自动同步工作流{workflow.message}"
                f"（每 6 小时，只同步 {fork_branch} 分支）"
            )
        else:
            message = f"已 fork 到 {fork_full}，但自动同步工作流安装失败：{workflow.message}"
        action = ActionResult(repository, "fork", True, message, via_proxy or workflow.via_proxy)
        self._record(source, action)
        return action

    def _existing_fork(self, login: str, upstream_name: str, upstream_repository: str) -> dict | None:
        payload, _ = self._api_json(f"repos/{login}/{upstream_name}")
        if not payload or not payload.get("fork"):
            return None
        parent = str(((payload.get("parent") or {}).get("full_name")) or "")
        if parent.lower() != upstream_repository.lower():
            return None
        return payload

    def _ensure_workflow(
        self, fork: str, upstream: str, upstream_branch: str, fork_branch: str
    ) -> WorkflowResult:
        content = workflow_template(upstream, upstream_branch, fork_branch)
        endpoint = f"repos/{fork}/contents/{WORKFLOW_FILE}?ref={fork_branch}"
        existing = self.runner.run_with_fallback(["api", endpoint])
        existing_sha = ""
        if existing.ok:
            try:
                payload = json.loads(existing.stdout)
                decoded = base64.b64decode(str(payload.get("content") or "")).decode(
                    "utf-8", errors="replace"
                )
            except (TypeError, ValueError):
                return WorkflowResult(False, "读取现有工作流失败。", existing.via_proxy)
            if WORKFLOW_MARKER not in decoded:
                return WorkflowResult(
                    False, "同名工作流已存在且不是 SourceHub 托管，未覆盖。", existing.via_proxy
                )
            if decoded.strip() == content.strip():
                self._enable_workflow(fork)
                return WorkflowResult(True, "已存在", existing.via_proxy)
            existing_sha = str(payload.get("sha") or "")
        elif not is_not_found_error(existing):
            return WorkflowResult(False, describe_failure(existing, self.runner.proxy_url), existing.via_proxy)

        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        arguments = [
            "api",
            "--method",
            "PUT",
            f"repos/{fork}/contents/{WORKFLOW_FILE}",
            "-f",
            "message=chore: add SourceHub fork sync workflow",
            "-f",
            f"content={encoded}",
            "-f",
            f"branch={fork_branch}",
        ]
        if existing_sha:
            arguments.extend(["-f", f"sha={existing_sha}"])
        written = self.runner.run_with_fallback(arguments)
        if not written.ok:
            return WorkflowResult(False, describe_failure(written, self.runner.proxy_url), written.via_proxy)
        enabled = self._enable_workflow(fork)
        message = "已安装"
        if not enabled.ok:
            message += "；请在 fork 的 Actions 页面确认工作流已启用"
        return WorkflowResult(True, message, written.via_proxy or enabled.via_proxy)

    def _enable_workflow(self, fork: str) -> CommandResult:
        return self.runner.run_with_fallback(
            ["workflow", "enable", Path(WORKFLOW_FILE).name, "-R", fork]
        )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
