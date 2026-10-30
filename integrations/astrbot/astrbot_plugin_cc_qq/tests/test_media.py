"""媒体展开、落盘、提示组装与只读媒体根的单元测试。"""

import os
import time
import unittest
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, patch

from PIL import Image as PILImage

from astrbot_plugin_cc_qq.contracts import (
    ConversationKey,
    ConversationKind,
    IncomingMessage,
)
from astrbot_plugin_cc_qq.media import (
    agent_images,
    build_agent_prompt,
    cleanup_old_media,
    conversation_media_dir,
    copy_verified_image,
    is_trusted_path,
    materialize,
    validate_image,
)
from astrbot_plugin_cc_qq.permissions import (
    DECISION_DENY,
    DECISION_NONE,
    PROFILE_READONLY,
    classify_tool_call,
)


def make_message(**overrides) -> IncomingMessage:
    base = IncomingMessage(
        conversation=ConversationKey("platform", ConversationKind.GROUP, "group"),
        sender_id="10001",
        sender_name="用户",
        message_id="msg-1",
        text="",
        origin="origin",
    )
    return replace(base, **overrides)


def write_png(path: Path, size=(4, 4)) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    PILImage.new("RGB", size, (255, 0, 0)).save(path, "PNG")
    return path


class TrustedPathTests(unittest.TestCase):
    def test_work_dir_and_media_root_are_trusted(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_dir = root / "work"
            media_root = root / "media"
            work_dir.mkdir()
            media_root.mkdir()
            image = write_png(media_root / "a.png")
            self.assertTrue(is_trusted_path(str(image), str(work_dir), media_root))
            self.assertTrue(is_trusted_path("notes.txt", str(work_dir), media_root))

    def test_outside_path_is_not_trusted(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = write_png(root / "outside.png")
            self.assertFalse(
                is_trusted_path(str(outside), str(root / "work"), root / "media")
            )
            self.assertFalse(is_trusted_path("", str(root / "work"), root / "media"))


class ImageValidationTests(unittest.TestCase):
    def test_png_is_accepted(self):
        with TemporaryDirectory() as tmp:
            image = write_png(Path(tmp) / "a.png")
            self.assertEqual(validate_image(image), ".png")

    def test_non_image_is_rejected(self):
        with TemporaryDirectory() as tmp:
            text_file = Path(tmp) / "a.png"
            text_file.write_text("not an image", encoding="utf-8")
            self.assertIsNone(validate_image(text_file))

    def test_oversized_image_is_rejected(self):
        with TemporaryDirectory() as tmp:
            image = write_png(Path(tmp) / "a.png")
            self.assertIsNone(validate_image(image, max_bytes=1))

    def test_copy_verified_image(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_png(root / "source.png")
            stored = copy_verified_image(source, root / "media", 1)
            self.assertIsNotNone(stored)
            self.assertTrue(Path(stored).is_file())
            self.assertTrue(Path(stored).name.startswith("01"))


class CleanupTests(unittest.TestCase):
    def test_expired_date_directory_is_removed(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_dir = root / "abc" / "20200101"
            old_dir.mkdir(parents=True)
            (old_dir / "a.png").write_bytes(b"x")
            stale = time.time() - 30 * 86400
            os.utime(old_dir, (stale, stale))
            removed = cleanup_old_media(root, retention_days=7)
            self.assertEqual(removed, 1)
            self.assertFalse(old_dir.exists())

    def test_fresh_directory_is_kept(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fresh = conversation_media_dir(root, "key", "msg")
            fresh.mkdir(parents=True)
            self.assertEqual(cleanup_old_media(root, retention_days=7), 0)
            self.assertTrue(fresh.is_dir())


class PromptTests(unittest.TestCase):
    def test_text_only_prompt(self):
        self.assertEqual(build_agent_prompt(make_message(text="你好")), "你好")

    def test_image_only_prompt_uses_hint(self):
        message = make_message(
            text="", images=("/media/1.jpg",), image_refs=("https://x/1.jpg",)
        )
        prompt = build_agent_prompt(message)
        self.assertIn("用户只发送了图片", prompt)
        self.assertIn("/media/1.jpg", prompt)
        self.assertIn("Read 工具", prompt)

    def test_quoted_text_without_images_does_not_use_image_hint(self):
        message = make_message(text="", quoted_text="被引用原文")
        prompt = build_agent_prompt(message)
        self.assertNotIn("用户只发送了图片", prompt)
        self.assertIn("被引用原文", prompt)

    def test_quoted_and_forward_sections(self):
        message = make_message(
            text="看看这个",
            quoted_text="被引用原文",
            quoted_images=("/media/q.jpg",),
            forward_text="转发原文",
            forward_images=("/media/f.jpg",),
        )
        prompt = build_agent_prompt(message)
        self.assertIn("[被引用的消息]", prompt)
        self.assertIn("被引用原文", prompt)
        self.assertIn("[转发的消息]", prompt)
        self.assertIn("转发原文", prompt)

    def test_agent_images_combines_groups(self):
        message = make_message(
            images=("/a.jpg",),
            quoted_images=("/b.jpg",),
            forward_images=("/c.jpg",),
        )
        self.assertEqual(agent_images(message), ("/a.jpg", "/b.jpg", "/c.jpg"))


class MaterializeTests(unittest.IsolatedAsyncioTestCase):
    async def test_image_groups_are_replaced_with_local_paths(self):
        message = make_message(
            image_refs=("direct",),
            quoted_image_refs=("quoted",),
            forward_ids=("forward-id",),
        )

        async def fake_store(ref, target_dir, index, resolver=None):
            return f"/media/{index}-{ref}.jpg"

        with TemporaryDirectory() as tmp, patch(
            "astrbot_plugin_cc_qq.media._store_image", side_effect=fake_store
        ), patch(
            "astrbot_plugin_cc_qq.media._expand_forward_ids",
            new=AsyncMock(return_value=("转发文本", ["forward"])),
        ):
            result = await materialize(None, message, Path(tmp))

        self.assertEqual(result.message.images, ("/media/1-direct.jpg",))
        self.assertEqual(result.message.quoted_images, ("/media/2-quoted.jpg",))
        self.assertEqual(result.message.forward_images, ("/media/3-forward.jpg",))
        self.assertEqual(result.message.forward_text, "转发文本")
        self.assertEqual((result.failed, result.truncated), (0, 0))

    async def test_failed_images_counted(self):
        message = make_message(image_refs=("bad", "good"))

        async def fake_store(ref, target_dir, index, resolver=None):
            return None if ref == "bad" else f"/media/{index}.jpg"

        with TemporaryDirectory() as tmp, patch(
            "astrbot_plugin_cc_qq.media._store_image", side_effect=fake_store
        ), patch(
            "astrbot_plugin_cc_qq.media._expand_forward_ids",
            new=AsyncMock(return_value=("", [])),
        ):
            result = await materialize(None, message, Path(tmp))

        self.assertEqual(result.failed, 1)
        self.assertEqual(result.message.images, ("/media/2.jpg",))

    async def test_max_images_truncates(self):
        message = make_message(image_refs=("a", "b", "c"))

        async def fake_store(ref, target_dir, index, resolver=None):
            return f"/media/{index}.jpg"

        with TemporaryDirectory() as tmp, patch(
            "astrbot_plugin_cc_qq.media._store_image", side_effect=fake_store
        ), patch(
            "astrbot_plugin_cc_qq.media._expand_forward_ids",
            new=AsyncMock(return_value=("", [])),
        ):
            result = await materialize(None, message, Path(tmp), max_images=2)

        self.assertEqual(len(result.message.images), 2)
        self.assertEqual(result.truncated, 1)

    async def test_media_disabled_keeps_message(self):
        message = make_message(image_refs=("a",))
        result = await materialize(None, message, Path("/tmp"), enabled=False)
        self.assertEqual(result.message, message)


class ReadonlyMediaRootTests(unittest.TestCase):
    def test_media_root_read_is_allowed(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_dir = root / "work"
            media_root = root / "media"
            work_dir.mkdir()
            media_root.mkdir()
            image = write_png(media_root / "a.png")
            decision = classify_tool_call(
                "Read",
                {"file_path": str(image)},
                PROFILE_READONLY,
                str(work_dir),
                (str(media_root),),
            )
            self.assertEqual(decision.outcome, DECISION_NONE)

    def test_outside_media_root_is_denied(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_dir = root / "work"
            media_root = root / "media"
            work_dir.mkdir()
            media_root.mkdir()
            outside = write_png(root / "outside.png")
            decision = classify_tool_call(
                "Read",
                {"file_path": str(outside)},
                PROFILE_READONLY,
                str(work_dir),
                (str(media_root),),
            )
            self.assertEqual(decision.outcome, DECISION_DENY)

    def test_write_still_denied_with_media_root(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_dir = root / "work"
            media_root = root / "media"
            work_dir.mkdir()
            media_root.mkdir()
            decision = classify_tool_call(
                "Write",
                {"file_path": str(media_root / "x.txt")},
                PROFILE_READONLY,
                str(work_dir),
                (str(media_root),),
            )
            self.assertEqual(decision.outcome, DECISION_DENY)


if __name__ == "__main__":
    unittest.main()
