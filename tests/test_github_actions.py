"""GitHub 自动化服务测试（GitHub Automation Tests）。"""

from __future__ import annotations

import base64
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from sourcehub.github_actions import (
    DEFAULT_GITHUB_PROXY,
    WORKFLOW_FILE,
    WORKFLOW_MARKER,
    CommandResult,
    GithubAutomation,
    GithubRunner,
    describe_failure,
    parse_fork_name,
    workflow_template,
)


class RecordingSubprocess:
    """记录每次子进程调用，并按顺序返回预设结果。"""

    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs["env"]))
        code, stdout, stderr = self.results[len(self.calls) - 1]
        return subprocess.CompletedProcess(command, code, stdout, stderr)


class GithubRunnerTests(unittest.TestCase):
    def test_direct_success_does_not_use_proxy(self):
        recorder = RecordingSubprocess([(0, "ok", "")])
        runner = GithubRunner(gh_path="/bin/echo", run=recorder)
        result = runner.run_with_fallback(["api", "user"])
        self.assertTrue(result.ok)
        self.assertFalse(result.via_proxy)
        self.assertEqual(len(recorder.calls), 1)
        self.assertNotIn("HTTPS_PROXY", recorder.calls[0][1])

    def test_network_failure_retries_with_local_proxy(self):
        recorder = RecordingSubprocess(
            [
                (1, "", "Could not resolve host: api.github.com"),
                (0, "logged-in", ""),
            ]
        )
        runner = GithubRunner(gh_path="/bin/echo", run=recorder)
        result = runner.run_with_fallback(["api", "user"])
        self.assertTrue(result.ok)
        self.assertTrue(result.via_proxy)
        self.assertEqual(len(recorder.calls), 2)
        self.assertEqual(recorder.calls[1][1]["HTTPS_PROXY"], DEFAULT_GITHUB_PROXY)

    def test_permission_failure_is_not_retried(self):
        recorder = RecordingSubprocess([(1, "", "HTTP 403: Resource not accessible")])
        runner = GithubRunner(gh_path="/bin/echo", run=recorder)
        result = runner.run_with_fallback(["api", "user"])
        self.assertFalse(result.ok)
        self.assertEqual(len(recorder.calls), 1)

    def test_missing_gh_is_reported(self):
        runner = GithubRunner(gh_path="/definitely/not/installed")
        result = runner.run_with_fallback(["api", "user"])
        self.assertFalse(result.ok)
        self.assertIn("gh 命令", describe_failure(result))


class GithubAutomationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state_path = Path(self.temp.name) / "github_actions.json"

    def _runner(
        self,
        existing_workflow: str | None = None,
        existing_fork: bool = True,
        login_fails: bool = False,
    ):
        class StubRunner:
            proxy_url = DEFAULT_GITHUB_PROXY

            def __init__(self):
                self.calls = []
                self.existing_workflow = existing_workflow
                self.existing_fork = existing_fork
                self.login_fails = login_fails
                self.fork_created = False
                self.graphql_fails = False
                self.graphql_data = {
                    "repository": {"id": "R_demo"},
                    "viewer": {
                        "lists": {"pageInfo": {"hasNextPage": False}, "nodes": []}
                    },
                }

            def run_with_fallback(self, args):
                self.calls.append(list(args))
                if args[:2] == ["api", "user"]:
                    if self.login_fails:
                        return CommandResult(1, "", "Could not resolve host: api.github.com")
                    return CommandResult(0, "tester", "")
                if args[:2] == ["api", "graphql"]:
                    if self.graphql_fails:
                        return CommandResult(1, "", "graphql_error: boom")
                    query = next(
                        (argument for argument in args if argument.startswith("query=")),
                        "",
                    )
                    if "updateUserListsForItem" in query:
                        return CommandResult(
                            0,
                            json.dumps(
                                {"data": {"updateUserListsForItem": {"list": None}}}
                            ),
                            "",
                        )
                    return CommandResult(
                        0, json.dumps({"data": self.graphql_data}), ""
                    )
                if args[:2] == ["workflow", "enable"]:
                    return CommandResult(0, "", "")
                if args[:2] == ["repo", "fork"]:
                    self.fork_created = True
                    return CommandResult(0, "✓ Created fork tester/demo", "")
                if args[:2] == ["api", "--method"]:
                    endpoint = args[3] if len(args) > 3 else ""
                    if endpoint.startswith("/user/starred/"):
                        return CommandResult(0, "", "")
                    if "contents" in endpoint:
                        return CommandResult(0, "{}", "")
                    return CommandResult(0, "{}", "")
                endpoint = args[1] if len(args) > 1 else ""
                if endpoint == "repos/owner/demo":
                    return CommandResult(
                        0,
                        json.dumps({"name": "demo", "default_branch": "master"}),
                        "",
                    )
                if endpoint == "repos/tester/demo":
                    if not self.existing_fork and not self.fork_created:
                        return CommandResult(1, "", "gh: Not Found (HTTP 404)")
                    return CommandResult(
                        0,
                        json.dumps(
                            {
                                "full_name": "tester/demo",
                                "default_branch": "master",
                                "fork": True,
                                "parent": {"full_name": "owner/demo"},
                            }
                        ),
                        "",
                    )
                if endpoint.startswith(f"repos/tester/demo/contents/{WORKFLOW_FILE}"):
                    if self.existing_workflow is None:
                        return CommandResult(1, "", "gh: Not Found (HTTP 404)")
                    encoded = base64.b64encode(self.existing_workflow.encode()).decode()
                    return CommandResult(
                        0, json.dumps({"content": encoded, "sha": "abc"}), ""
                    )
                return CommandResult(0, "{}", "")

        return StubRunner()

    def test_star_is_recorded_once(self):
        runner = self._runner()
        automation = GithubAutomation(self.state_path, runner)
        automation.handle(["owner/demo"], fork=False, source="qq")
        automation.handle(["owner/demo"], fork=False, source="qq")
        star_calls = [
            call
            for call in runner.calls
            if call[:2] == ["api", "--method"] and "/user/starred/" in call[3]
        ]
        self.assertEqual(len(star_calls), 1)
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertIn("starred_at", state["repos"]["owner/demo"])

    def test_fork_installs_default_branch_sync_workflow(self):
        runner = self._runner()
        automation = GithubAutomation(self.state_path, runner)
        results = automation.handle(["owner/demo"], fork=True, source="bilibili")
        self.assertTrue(all(result.ok for result in results))
        put_calls = [
            call
            for call in runner.calls
            if call[:2] == ["api", "--method"] and "contents" in call[3]
        ]
        self.assertEqual(len(put_calls), 1)
        content_argument = next(
            argument for argument in put_calls[0] if argument.startswith("content=")
        )
        decoded = base64.b64decode(content_argument.removeprefix("content=")).decode()
        self.assertIn(WORKFLOW_MARKER, decoded)
        self.assertIn('UPSTREAM_REPOSITORY: "owner/demo"', decoded)
        self.assertIn('UPSTREAM_BRANCH: "master"', decoded)
        self.assertIn('FORK_BRANCH: "master"', decoded)
        self.assertIn("17 */6 * * *", decoded)

    def test_new_fork_only_includes_default_branch(self):
        runner = self._runner(existing_fork=False)
        automation = GithubAutomation(self.state_path, runner)
        results = automation.handle(["owner/demo"], fork=True, source="qq")
        self.assertTrue(all(result.ok for result in results))
        fork_calls = [call for call in runner.calls if call[:2] == ["repo", "fork"]]
        self.assertEqual(len(fork_calls), 1)
        self.assertIn("--default-branch-only", fork_calls[0])
        self.assertIn("--clone=false", fork_calls[0])
        # `gh repo fork <repository>` 不接受 --remote（即使显式传 false 也会报错）：
        # the `--remote` flag is unsupported when a repository argument is provided
        self.assertNotIn("--remote=false", fork_calls[0])

    def test_unmanaged_existing_workflow_is_not_overwritten(self):
        runner = self._runner(existing_workflow="name: Someone Else\n")
        automation = GithubAutomation(self.state_path, runner)
        results = automation.handle(["owner/demo"], fork=True, source="qq")
        self.assertTrue(results[-1].ok)
        self.assertIn("未覆盖", results[-1].message)
        put_calls = [
            call
            for call in runner.calls
            if call[:2] == ["api", "--method"] and "contents" in call[3]
        ]
        self.assertEqual(put_calls, [])

    def test_login_failure_mentions_proxy_in_fork_result(self):
        runner = self._runner(login_fails=True)
        automation = GithubAutomation(self.state_path, runner)
        results = automation.handle(["owner/demo"], fork=True, source="qq")
        fork_result = next(result for result in results if result.action == "fork")
        self.assertFalse(fork_result.ok)
        self.assertIn("代理", fork_result.message)

    def test_recent_actions_are_recorded(self):
        runner = self._runner()
        automation = GithubAutomation(self.state_path, runner)
        automation.handle(["owner/demo"], fork=True, source="qq")
        actions = automation.recent_actions()
        self.assertEqual([action["action"] for action in actions], ["star", "fork"])


    def _list_node(self, list_id, name, repositories=(), truncated=False):
        return {
            "id": list_id,
            "name": name,
            "items": {
                "pageInfo": {"hasNextPage": truncated},
                "nodes": [{"nameWithOwner": repository} for repository in repositories],
            },
        }

    def _set_lists(self, runner, nodes):
        runner.graphql_data["viewer"]["lists"] = {
            "pageInfo": {"hasNextPage": False},
            "nodes": nodes,
        }

    def _mutations(self, runner):
        return [
            call
            for call in runner.calls
            if call[:2] == ["api", "graphql"]
            and any("updateUserListsForItem" in argument for argument in call)
        ]

    def test_new_star_joins_configured_list(self):
        runner = self._runner()
        self._set_lists(runner, [self._list_node("UL_ai", "AI相关")])
        automation = GithubAutomation(self.state_path, runner, star_list="AI相关")

        results = automation.handle(["owner/demo"], fork=False, source="qq")

        self.assertTrue(results[0].ok)
        self.assertIn("已加入列表「AI相关」", results[0].message)
        mutations = self._mutations(runner)
        self.assertEqual(len(mutations), 1)
        self.assertIn('"UL_ai"', " ".join(mutations[0]))

    def test_star_list_preserves_existing_lists(self):
        runner = self._runner()
        self._set_lists(
            runner,
            [
                self._list_node("UL_ai", "AI相关"),
                self._list_node("UL_useful", "Useful", ["owner/demo"]),
            ],
        )
        automation = GithubAutomation(self.state_path, runner, star_list="AI相关")

        results = automation.handle(["owner/demo"], fork=False, source="qq")

        self.assertTrue(results[0].ok)
        mutation = " ".join(self._mutations(runner)[0])
        self.assertIn('"UL_ai"', mutation)
        self.assertIn('"UL_useful"', mutation)

    def test_missing_list_falls_back_to_default_star(self):
        runner = self._runner()
        self._set_lists(runner, [self._list_node("UL_other", "其他")])
        automation = GithubAutomation(self.state_path, runner, star_list="不存在")

        results = automation.handle(["owner/demo"], fork=False, source="qq")

        self.assertTrue(results[0].ok)
        self.assertIn("不存在，放入默认位置", results[0].message)
        self.assertEqual(self._mutations(runner), [])

    def test_already_starred_does_not_query_lists(self):
        runner = self._runner()
        self._set_lists(runner, [self._list_node("UL_ai", "AI相关")])
        automation = GithubAutomation(self.state_path, runner, star_list="AI相关")
        automation.handle(["owner/demo"], fork=False, source="qq")
        runner.calls.clear()

        results = automation.handle(["owner/demo"], fork=False, source="qq")

        self.assertEqual(results[0].message, "已经 star，跳过")
        self.assertFalse(
            any(call[:2] == ["api", "graphql"] for call in runner.calls)
        )

    def test_truncated_list_skips_assignment(self):
        runner = self._runner()
        self._set_lists(
            runner, [self._list_node("UL_ai", "AI相关", truncated=True)]
        )
        automation = GithubAutomation(self.state_path, runner, star_list="AI相关")

        results = automation.handle(["owner/demo"], fork=False, source="qq")

        self.assertFalse(results[0].ok)
        self.assertIn("超过 100", results[0].message)
        self.assertEqual(self._mutations(runner), [])

    def test_graphql_failure_keeps_star_recorded(self):
        runner = self._runner()
        runner.graphql_fails = True
        automation = GithubAutomation(self.state_path, runner, star_list="AI相关")

        results = automation.handle(["owner/demo"], fork=False, source="qq")

        self.assertFalse(results[0].ok)
        self.assertIn("已 star，但加入列表", results[0].message)
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertTrue(state["repos"]["owner/demo"].get("starred_at"))


class GithubHelpersTests(unittest.TestCase):
    def test_parse_fork_name_from_creation_output(self):
        output = "✓ Created fork tester/demo\nhttps://github.com/tester/demo"
        self.assertEqual(parse_fork_name(output), "tester/demo")

    def test_workflow_template_mentions_merge_not_force_sync(self):
        template = workflow_template("owner/demo", "master", "master")
        self.assertIn("git merge --no-edit", template)
        self.assertNotIn("repo sync --force", template)

    def test_describe_network_failure_mentions_proxy(self):
        result = CommandResult(1, "", "dial tcp: i/o timeout", via_proxy=True)
        self.assertIn("代理", describe_failure(result))

    def test_describe_permission_failure(self):
        result = CommandResult(1, "", "HTTP 403: Forbidden")
        self.assertIn("权限", describe_failure(result))


if __name__ == "__main__":
    unittest.main()
