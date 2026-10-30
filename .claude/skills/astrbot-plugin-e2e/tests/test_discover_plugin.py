import json
import tempfile
import unittest
from pathlib import Path

from scripts.discover_plugin import build_features


class DiscoverPluginTest(unittest.TestCase):
    def _make_plugin(self, home: Path) -> Path:
        plugin = home / "demo_plugin"
        plugin.mkdir()
        (plugin / "metadata.yaml").write_text(
            "name: demo_plugin\n"
            "display_name: 演示插件\n"
            "desc: 用于测试\n"
            "version: 0.1.0\n"
            "author: tester\n"
            "support_platforms:\n"
            "  - aiocqhttp\n",
            encoding="utf-8",
        )
        (plugin / "_conf_schema.json").write_text(
            json.dumps({"enabled": {"type": "bool", "default": True}}),
            encoding="utf-8",
        )
        (plugin / "main.py").write_text(
            "from astrbot.api.event import filter\n"
            "@filter.command('help')\n"
            "async def help_cmd(event):\n"
            "    pass\n"
            "@filter.event_message_type(filter.EventMessageType.ALL)\n"
            "async def on_message(event):\n"
            "    pass\n",
            encoding="utf-8",
        )
        (plugin / "README.md").write_text(
            "# demo\n\n- `/info` 查看信息\n- `/pwd` 查看目录\n",
            encoding="utf-8",
        )
        return plugin

    def test_extracts_commands_events_and_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = self._make_plugin(Path(tmp))
            result = build_features(plugin)
        self.assertEqual(result["plugin"], "demo_plugin")
        commands = {
            item["trigger"] for item in result["features"] if item["kind"] == "command"
        }
        self.assertTrue({"/help", "/info", "/pwd"}.issubset(commands))
        kinds = {item["kind"] for item in result["features"]}
        self.assertIn("event", kinds)
        self.assertIn("config", kinds)
        self.assertEqual(result["metadata"]["version"], "0.1.0")

    def test_marks_event_features_as_manual(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = self._make_plugin(Path(tmp))
            result = build_features(plugin)
        event = next(
            item for item in result["features"] if item["kind"] == "event"
        )
        self.assertEqual(event["testability"], "manual")

    def test_rejects_missing_plugin_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "插件目录不存在"):
                build_features(Path(tmp) / "missing")

    def test_reads_explicit_command_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = self._make_plugin(Path(tmp))
            (plugin / "README.md").write_text("# demo\n", encoding="utf-8")
            (plugin / "registry.py").write_text(
                'COMMANDS = (Command("/cc", "/cc <消息>", "透传"),)\n',
                encoding="utf-8",
            )
            result = build_features(plugin)
        commands = {
            item["trigger"] for item in result["features"] if item["kind"] == "command"
        }
        self.assertIn("/cc", commands)

    def test_keeps_chinese_commands_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = self._make_plugin(Path(tmp))
            (plugin / "README.md").write_text(
                "# demo\n\n- `/整理` 整理\n- `/总结` 总结\n",
                encoding="utf-8",
            )
            result = build_features(plugin)
        ids = [
            item["id"]
            for item in result["features"]
            if item["kind"] == "command" and item["trigger"] in ("/整理", "/总结")
        ]
        self.assertEqual(len(set(ids)), 2)
        self.assertTrue(all("feature" not in item for item in ids))

    def test_ignores_system_paths_and_supports_arguments(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = self._make_plugin(Path(tmp))
            (plugin / "README.md").write_text(
                "# demo\n\n- `/info` 查看信息\n- `/cc <代理消息>` 透传\n- 禁止访问 `/etc` 与 `/tmp`\n",
                encoding="utf-8",
            )
            result = build_features(plugin)
        commands = {
            item["trigger"] for item in result["features"] if item["kind"] == "command"
        }
        self.assertIn("/cc", commands)
        self.assertIn("/info", commands)
        self.assertNotIn("/etc", commands)
        self.assertNotIn("/tmp", commands)

    def test_deduplicates_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = self._make_plugin(Path(tmp))
            readme = plugin / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8") + "\n- `/help` 再写一次\n",
                encoding="utf-8",
            )
            result = build_features(plugin)
        helps = [
            item
            for item in result["features"]
            if item["kind"] == "command" and item["trigger"] == "/help"
        ]
        self.assertEqual(len(helps), 1)
