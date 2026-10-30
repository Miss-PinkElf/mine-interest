"""`[[image:<path>]]` 标记解析的单元测试。"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from astrbot_plugin_cc_qq.constants import IMAGE_MARKER_MAX_COUNT
from astrbot_plugin_cc_qq.media import parse_reply_parts


class ParseReplyPartsTests(unittest.TestCase):
    def test_plain_text_has_no_images(self):
        parts, ignored = parse_reply_parts("普通回复", "/work")
        self.assertEqual(parts, [("text", "普通回复")])
        self.assertEqual(ignored, 0)

    def test_trusted_image_is_kept_in_order(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            parts, ignored = parse_reply_parts(
                "前文[[image:shot.png]]后文", str(work_dir)
            )
            self.assertEqual(len(parts), 3)
            self.assertEqual(parts[0], ("text", "前文"))
            self.assertEqual(parts[1][0], "image")
            self.assertTrue(Path(parts[1][1]).is_absolute())
            self.assertEqual(Path(parts[1][1]).name, "shot.png")
            self.assertEqual(parts[2], ("text", "后文"))
            self.assertEqual(ignored, 0)

    def test_untrusted_image_is_ignored(self):
        with TemporaryDirectory() as tmp:
            parts, ignored = parse_reply_parts(
                "前文[[image:/etc/passwd]]后文", str(Path(tmp) / "work")
            )
            self.assertEqual(parts, [("text", "前文"), ("text", "后文")])
            self.assertEqual(ignored, 1)

    def test_empty_path_is_ignored(self):
        parts, ignored = parse_reply_parts("[[image: ]]", "/work")
        self.assertEqual(parts, [])
        self.assertEqual(ignored, 1)

    def test_image_count_is_capped(self):
        markers = "".join(f"[[image:{index}.png]]" for index in range(IMAGE_MARKER_MAX_COUNT + 3))
        with TemporaryDirectory() as tmp:
            parts, ignored = parse_reply_parts(markers, tmp)
        images = [value for kind, value in parts if kind == "image"]
        self.assertEqual(len(images), IMAGE_MARKER_MAX_COUNT)
        self.assertEqual(ignored, 3)

    def test_without_work_dir_all_images_ignored(self):
        parts, ignored = parse_reply_parts("[[image:a.png]]", "")
        self.assertEqual(parts, [])
        self.assertEqual(ignored, 1)


if __name__ == "__main__":
    unittest.main()
