"""私聊短窗口去重的单元测试。"""

import unittest

from astrbot_plugin_cc_qq.constants import PRIVATE_DUPLICATE_WINDOW_SECONDS
from astrbot_plugin_cc_qq.platform.duplicates import is_recent_duplicate


class DuplicateGuardTest(unittest.TestCase):
    def test_first_event_is_not_duplicate(self):
        seen: dict[tuple[str, ...], int] = {}
        self.assertFalse(
            is_recent_duplicate(seen, ("private", "10001", "hi"), 100, PRIVATE_DUPLICATE_WINDOW_SECONDS)
        )

    def test_same_text_within_window_is_duplicate(self):
        seen: dict[tuple[str, ...], int] = {}
        key = ("private", "10001", "hi")
        is_recent_duplicate(seen, key, 100, PRIVATE_DUPLICATE_WINDOW_SECONDS)
        self.assertTrue(is_recent_duplicate(seen, key, 101, PRIVATE_DUPLICATE_WINDOW_SECONDS))
        self.assertTrue(
            is_recent_duplicate(
                seen, key, 100 + PRIVATE_DUPLICATE_WINDOW_SECONDS, PRIVATE_DUPLICATE_WINDOW_SECONDS
            )
        )

    def test_same_text_after_window_is_new(self):
        seen: dict[tuple[str, ...], int] = {}
        key = ("private", "10001", "hi")
        is_recent_duplicate(seen, key, 100, PRIVATE_DUPLICATE_WINDOW_SECONDS)
        self.assertFalse(
            is_recent_duplicate(
                seen, key, 101 + PRIVATE_DUPLICATE_WINDOW_SECONDS, PRIVATE_DUPLICATE_WINDOW_SECONDS
            )
        )

    def test_empty_burst_is_duplicate(self):
        seen: dict[tuple[str, ...], int] = {}
        key = ("private", "10001", "")
        is_recent_duplicate(seen, key, 100, PRIVATE_DUPLICATE_WINDOW_SECONDS)
        self.assertTrue(is_recent_duplicate(seen, key, 100, PRIVATE_DUPLICATE_WINDOW_SECONDS))

    def test_different_text_is_not_duplicate(self):
        seen: dict[tuple[str, ...], int] = {}
        is_recent_duplicate(seen, ("private", "10001", "a"), 100, PRIVATE_DUPLICATE_WINDOW_SECONDS)
        self.assertFalse(
            is_recent_duplicate(seen, ("private", "10001", "b"), 100, PRIVATE_DUPLICATE_WINDOW_SECONDS)
        )

    def test_zero_window_disables_dedup(self):
        seen: dict[tuple[str, ...], int] = {}
        key = ("private", "10001", "hi")
        self.assertFalse(is_recent_duplicate(seen, key, 100, 0))
        self.assertFalse(is_recent_duplicate(seen, key, 100, 0))


if __name__ == "__main__":
    unittest.main()
