"""长文本触发判定与长图切分的单元测试。"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image as PILImage

from astrbot_plugin_cc_qq.constants import (
    DEFAULT_LONG_TEXT_IMAGE_THRESHOLD,
    MAX_LONG_TEXT_IMAGE_THRESHOLD,
    MIN_LONG_TEXT_IMAGE_THRESHOLD,
)
from astrbot_plugin_cc_qq.render import (
    config_flag,
    should_render_image,
    split_long_image,
    threshold_from_config,
)


class ConfigFlagTests(unittest.TestCase):
    def test_missing_and_none_use_default(self):
        self.assertTrue(config_flag({}, "flag", True))
        self.assertFalse(config_flag({}, "flag", False))
        self.assertTrue(config_flag({"flag": None}, "flag", True))

    def test_explicit_values_win(self):
        self.assertFalse(config_flag({"flag": False}, "flag", True))
        self.assertTrue(config_flag({"flag": True}, "flag", False))


class ShouldRenderTests(unittest.TestCase):
    def test_threshold_is_360_by_default(self):
        self.assertEqual(DEFAULT_LONG_TEXT_IMAGE_THRESHOLD, 360)

    def test_short_text_does_not_render(self):
        self.assertFalse(should_render_image("短回复", True, 360))

    def test_long_text_renders(self):
        self.assertTrue(should_render_image("字" * 360, True, 360))

    def test_code_fence_renders(self):
        self.assertTrue(should_render_image("```diff\n-a\n+b\n```", True, 360))

    def test_disabled_never_renders(self):
        self.assertFalse(should_render_image("字" * 500, False, 360))

    def test_image_marker_takes_precedence(self):
        self.assertFalse(
            should_render_image("字" * 500 + "[[image:/work/a.png]]", True, 360)
        )


class ThresholdConfigTests(unittest.TestCase):
    def test_default_when_missing(self):
        self.assertEqual(threshold_from_config({}), DEFAULT_LONG_TEXT_IMAGE_THRESHOLD)

    def test_invalid_value_falls_back(self):
        self.assertEqual(
            threshold_from_config({"long_text_image_threshold": "abc"}),
            DEFAULT_LONG_TEXT_IMAGE_THRESHOLD,
        )
        self.assertEqual(
            threshold_from_config({"long_text_image_threshold": True}),
            DEFAULT_LONG_TEXT_IMAGE_THRESHOLD,
        )

    def test_value_is_clamped(self):
        self.assertEqual(
            threshold_from_config({"long_text_image_threshold": 1}),
            MIN_LONG_TEXT_IMAGE_THRESHOLD,
        )
        self.assertEqual(
            threshold_from_config({"long_text_image_threshold": 999999}),
            MAX_LONG_TEXT_IMAGE_THRESHOLD,
        )


class SplitImageTests(unittest.TestCase):
    def test_short_image_is_unchanged(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.png"
            PILImage.new("RGB", (100, 200), (0, 0, 0)).save(path)
            self.assertEqual(split_long_image(path, max_height=1000), [path])

    def test_long_image_is_split(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.png"
            PILImage.new("RGB", (100, 250), (0, 0, 0)).save(path)
            parts = split_long_image(path, max_height=100)
            self.assertEqual(len(parts), 3)
            for part in parts:
                self.assertTrue(part.is_file())


if __name__ == "__main__":
    unittest.main()
