"""媒体哈希与体积（Media Policy Tests）。"""

from __future__ import annotations

import unittest

from sourcehub.constants import GAP_MEDIA_TOO_LARGE
from sourcehub.media import accept_media, hash_name, image_extension

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
JPEG = b"\xff\xd8\xff" + b"\x00" * 16


class MediaTests(unittest.TestCase):
    def test_png_magic_maps_to_png_extension(self):
        self.assertEqual(image_extension(PNG), ".png")
        self.assertEqual(image_extension(JPEG), ".jpg")

    def test_identical_bytes_share_hash_name(self):
        self.assertEqual(hash_name(PNG), hash_name(PNG))
        self.assertTrue(hash_name(PNG).endswith(".png"))

    def test_oversize_bytes_are_rejected_with_gap(self):
        data, name, gap = accept_media(PNG, max_bytes=8)
        self.assertIsNone(data)
        self.assertIsNone(name)
        self.assertEqual(gap, GAP_MEDIA_TOO_LARGE)

    def test_accepted_bytes_keep_content_and_name(self):
        data, name, gap = accept_media(PNG, max_bytes=1024)
        self.assertEqual(data, PNG)
        self.assertTrue(name.endswith(".png"))
        self.assertIsNone(gap)


if __name__ == "__main__":
    unittest.main()
