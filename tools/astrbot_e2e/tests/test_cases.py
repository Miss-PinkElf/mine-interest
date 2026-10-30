import json
import tempfile
import unittest
from pathlib import Path

from astrbot_e2e.cases import CaseError, case_steps, load_case, render_case


class CaseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "case.json"

    def write(self, data):
        self.path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def write_case(self, **overrides):
        data = {
            "name": "probe",
            "plugin": "astrbot_plugin_e2e_probe",
            "send": {"group_id": "{{group_id}}", "text": "/e2e_echo hello", "at_bot": True},
            "expect": {"messages": [{"contains": ["e2e_echo:hello"]}]},
        }
        data.update(overrides)
        self.write(data)
        return data

    def test_loads_and_renders_group_id(self):
        self.write_case()
        case = load_case(self.path)
        rendered = render_case(case, {"group_id": "123456789"})
        self.assertEqual(rendered["send"]["group_id"], "123456789")

    def test_rejects_missing_expectation(self):
        self.write_case(expect={})
        with self.assertRaisesRegex(CaseError, "至少包含"):
            load_case(self.path)

    def test_rejects_unknown_key(self):
        self.write_case(expect={"steps": []})
        with self.assertRaisesRegex(CaseError, "未知字段"):
            load_case(self.path)

    def test_rejects_unknown_top_key(self):
        self.write_case(extra=True)
        with self.assertRaisesRegex(CaseError, "未知字段"):
            load_case(self.path)

    def test_rejects_missing_file(self):
        with self.assertRaisesRegex(CaseError, "不存在"):
            load_case(Path(self.tmp.name) / "missing.json")

    def test_rejects_directory_path(self):
        with self.assertRaisesRegex(CaseError, "读取失败"):
            load_case(Path(self.tmp.name))

    def test_rejects_non_utf8_file(self):
        self.path.write_bytes(b"\xff\xfe\x00\x00")
        with self.assertRaisesRegex(CaseError, "编码非法"):
            load_case(self.path)

    def test_rejects_invalid_json(self):
        self.path.write_text("{not json", encoding="utf-8")
        with self.assertRaisesRegex(CaseError, "不是合法 JSON"):
            load_case(self.path)

    def test_rejects_empty_assertion_lists(self):
        for key in ("messages", "logs"):
            with self.subTest(key=key):
                self.write_case(expect={key: []})
                with self.assertRaisesRegex(CaseError, "非空数组"):
                    load_case(self.path)

    def test_rejects_non_object_semantic(self):
        self.write_case(expect={"semantic": "yes"})
        with self.assertRaisesRegex(CaseError, "semantic 必须是对象"):
            load_case(self.path)

    def test_render_does_not_mutate_case(self):
        self.write_case()
        case = load_case(self.path)
        render_case(case, {"group_id": "123456789"})
        self.assertEqual(case["send"]["group_id"], "{{group_id}}")

    def test_render_keeps_non_placeholder_group_id(self):
        self.write_case(send={"group_id": "987654321", "text": "/e2e_echo hello"})
        case = load_case(self.path)
        rendered = render_case(case, {"group_id": "123456789"})
        self.assertEqual(rendered["send"]["group_id"], "987654321")

    def test_render_requires_config_group_id(self):
        self.write_case()
        case = load_case(self.path)
        with self.assertRaisesRegex(CaseError, "group_id"):
            render_case(case, {})

    def test_accepts_multi_step_case(self):
        self.write(
            {
                "name": "multi",
                "plugin": "astrbot_plugin_e2e_probe",
                "steps": [
                    {
                        "send": {"group_id": "{{group_id}}", "text": "/help"},
                        "expect": {"messages": [{"contains": ["帮助"]}]},
                    },
                    {
                        "send": {"group_id": "{{group_id}}", "text": "/info"},
                        "expect": {"messages": [{"regex": r"\S"}]},
                    },
                ],
            }
        )
        case = load_case(self.path)
        rendered = render_case(case, {"group_id": "123456789"})
        self.assertEqual(rendered["steps"][0]["send"]["group_id"], "123456789")
        self.assertEqual(rendered["steps"][1]["send"]["group_id"], "123456789")

    def test_rejects_steps_with_top_level_send(self):
        self.write_case(
            steps=[
                {
                    "send": {"group_id": "{{group_id}}", "text": "/help"},
                    "expect": {"messages": [{"contains": ["帮助"]}]},
                }
            ]
        )
        with self.assertRaisesRegex(CaseError, "不能同时出现"):
            load_case(self.path)

    def test_rejects_empty_steps(self):
        self.write(
            {
                "name": "multi",
                "plugin": "astrbot_plugin_e2e_probe",
                "steps": [],
            }
        )
        with self.assertRaisesRegex(CaseError, "steps 必须是非空数组"):
            load_case(self.path)

    def test_rejects_step_without_expect(self):
        self.write(
            {
                "name": "multi",
                "plugin": "astrbot_plugin_e2e_probe",
                "steps": [{"send": {"group_id": "{{group_id}}", "text": "/help"}}],
            }
        )
        with self.assertRaisesRegex(CaseError, "send 与 expect"):
            load_case(self.path)

    def test_rejects_unknown_step_key(self):
        self.write(
            {
                "name": "multi",
                "plugin": "astrbot_plugin_e2e_probe",
                "steps": [
                    {
                        "send": {"group_id": "{{group_id}}", "text": "/help"},
                        "expect": {"messages": [{"contains": ["帮助"]}]},
                        "sleep": 1,
                    }
                ],
            }
        )
        with self.assertRaisesRegex(CaseError, "未知字段"):
            load_case(self.path)

    def test_case_steps_returns_legacy_as_single_step(self):
        self.write_case()
        case = load_case(self.path)
        steps = case_steps(case)
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0]["send"]["text"], "/e2e_echo hello")
