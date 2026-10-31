"""回复媒体自动识别的单元测试（Auto-send Reply Media）。"""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from astrbot_plugin_cc_qq.constants import AUTO_MEDIA_MAX_COUNT
from astrbot_plugin_cc_qq.reply_media import has_reply_media, parse_reply_parts


def _write_image(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (2, 2), (255, 0, 0)).save(path)
    return path


def _real(path) -> str:
    return os.path.realpath(str(path))


def _media_values(parts):
    return [value for kind, value in parts if kind != "text"]


class AutoMediaDetectionTests(unittest.TestCase):
    def test_absolute_image_path_is_sent(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            image = _write_image(work_dir / "shot.png")
            parts, ignored = parse_reply_parts(
                f"图片在这里：{image}", str(work_dir), auto_send=True
            )
            self.assertEqual(_media_values(parts), [_real(image)])
            self.assertEqual(ignored, 0)

    def test_relative_path_resolves_under_work_dir(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            image = _write_image(work_dir / "shot.png")
            parts, _ = parse_reply_parts(
                "见 ./shot.png", str(work_dir), auto_send=True
            )
            self.assertEqual(_media_values(parts), [_real(image)])

    def test_backtick_wrapped_path_is_sent_without_backticks(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            image = _write_image(work_dir / "shot.png")
            parts, _ = parse_reply_parts(
                f"本地文件：`{image}`（2×2）", str(work_dir), auto_send=True
            )
            self.assertEqual(_media_values(parts), [_real(image)])
            texts = "".join(value for kind, value in parts if kind == "text")
            self.assertNotIn("`", texts)
            self.assertIn("本地文件", texts)

    def test_markdown_image_is_sent(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            image = _write_image(work_dir / "shot.png")
            parts, _ = parse_reply_parts(
                f"![预览]({image})", str(work_dir), auto_send=True
            )
            self.assertEqual(_media_values(parts), [_real(image)])

    def test_public_image_url_is_sent(self):
        parts, _ = parse_reply_parts(
            "图：https://cdn.example.com/a.png?token=1",
            auto_send=True,
        )
        self.assertEqual(
            _media_values(parts), ["https://cdn.example.com/a.png?token=1"]
        )

    def test_public_video_url_is_sent(self):
        parts, _ = parse_reply_parts(
            "视频：https://cdn.example.com/a.mp4", auto_send=True
        )
        kinds = [kind for kind, _ in parts if kind != "text"]
        self.assertEqual(kinds, ["video"])

    def test_private_urls_are_rejected(self):
        for url in (
            "http://127.0.0.1/a.png",
            "http://localhost/a.png",
            "http://192.168.1.2/a.png",
            "http://10.0.0.5/a.png",
            "http://[::1]/a.png",
        ):
            with self.subTest(url=url):
                parts, ignored = parse_reply_parts(f"图：{url}", auto_send=True)
                self.assertFalse(has_reply_media(parts))
                self.assertEqual(ignored, 0)

    def test_local_file_outside_roots_is_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_dir = root / "work"
            work_dir.mkdir()
            outside = _write_image(root / "outside.png")
            parts, ignored = parse_reply_parts(
                f"图：{outside}", str(work_dir), auto_send=True
            )
            self.assertFalse(has_reply_media(parts))
            self.assertEqual(ignored, 0)

    def test_fake_image_is_rejected(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            fake = work_dir / "fake.png"
            fake.write_text("not an image", encoding="utf-8")
            parts, _ = parse_reply_parts(
                f"图：{fake}", str(work_dir), auto_send=True
            )
            self.assertFalse(has_reply_media(parts))

    def test_fenced_code_block_is_not_scanned(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            outside = _write_image(work_dir / "inside.png")
            content = f"```\n{outside}\n```\n```\n{outside}\n```"
            parts, _ = parse_reply_parts(content, str(work_dir), auto_send=True)
            self.assertFalse(has_reply_media(parts))

    def test_explicit_marker_and_auto_media_keep_order(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            first = _write_image(work_dir / "first.png")
            second = _write_image(work_dir / "second.png")
            parts, _ = parse_reply_parts(
                f"前[[image:{first}]]中 {second} 后",
                str(work_dir),
                auto_send=True,
            )
            self.assertEqual(_media_values(parts), [_real(first), _real(second)])

    def test_local_media_wins_over_url(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            image = _write_image(work_dir / "shot.png")
            parts, _ = parse_reply_parts(
                f"本地：{image}\n在线：https://cdn.example.com/same.png",
                str(work_dir),
                auto_send=True,
            )
            self.assertEqual(_media_values(parts), [_real(image)])

    def test_media_count_is_capped(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            paths = [
                _write_image(work_dir / f"{index}.png")
                for index in range(AUTO_MEDIA_MAX_COUNT + 2)
            ]
            content = "\n".join(str(path) for path in paths)
            parts, _ = parse_reply_parts(content, str(work_dir), auto_send=True)
            self.assertEqual(len(_media_values(parts)), AUTO_MEDIA_MAX_COUNT)

    def test_video_path_is_sent(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            video = work_dir / "clip.mp4"
            video.write_bytes(b"fake video bytes")
            parts, _ = parse_reply_parts(
                f"视频：{video}", str(work_dir), auto_send=True
            )
            kinds = [kind for kind, _ in parts if kind != "text"]
            self.assertEqual(kinds, ["video"])

    def test_auto_send_disabled_keeps_plain_text(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            image = _write_image(work_dir / "shot.png")
            parts, _ = parse_reply_parts(f"图：{image}", str(work_dir))
            self.assertFalse(has_reply_media(parts))
            texts = "".join(value for kind, value in parts if kind == "text")
            self.assertIn(str(image), texts)

    def test_duplicate_path_is_sent_once(self):
        with TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            image = _write_image(work_dir / "shot.png")
            parts, _ = parse_reply_parts(
                f"{image}\n\n{image}", str(work_dir), auto_send=True
            )
            self.assertEqual(_media_values(parts), [_real(image)])


if __name__ == "__main__":
    unittest.main()
