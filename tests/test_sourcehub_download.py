"""直连媒体下载与有限重试（Direct Media Retry）测试。"""

from __future__ import annotations

import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from sourcehub.constants import GAP_MEDIA_FAILED, GAP_MEDIA_TOO_LARGE
from sourcehub.download import fetch_bytes


class _Response:
    def __init__(self, content: bytes):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, size: int) -> bytes:
        return self.content[:size]


class _Opener:
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.calls = 0

    def open(self, *_args, **_kwargs):
        self.calls += 1
        outcome = next(self.outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return _Response(outcome)


class DownloadTests(unittest.TestCase):
    def test_transient_error_succeeds_on_fifth_direct_attempt(self):
        opener = _Opener([URLError("offline")] * 4 + [b"GIF89a-image"])
        with patch("sourcehub.download.urllib.request.build_opener", return_value=opener) as build, patch("sourcehub.download.time.sleep"):
            data, name, gap = fetch_bytes("https://example.test/image", 100)
        self.assertEqual(data, b"GIF89a-image")
        self.assertIsNone(gap)
        self.assertEqual(opener.calls, 5)
        self.assertTrue(name.endswith(".gif"))
        self.assertEqual(build.call_args.args[0].proxies, {})

    def test_http_404_does_not_retry(self):
        opener = _Opener([HTTPError("https://example.test/image", 404, "missing", None, None)])
        with patch("sourcehub.download.urllib.request.build_opener", return_value=opener):
            _data, _name, gap = fetch_bytes("https://example.test/image", 100)
        self.assertEqual(gap, GAP_MEDIA_FAILED)
        self.assertEqual(opener.calls, 1)

    def test_oversize_does_not_retry(self):
        opener = _Opener([b"GIF89a-image"])
        with patch("sourcehub.download.urllib.request.build_opener", return_value=opener):
            _data, _name, gap = fetch_bytes("https://example.test/image", 3)
        self.assertEqual(gap, GAP_MEDIA_TOO_LARGE)
        self.assertEqual(opener.calls, 1)
