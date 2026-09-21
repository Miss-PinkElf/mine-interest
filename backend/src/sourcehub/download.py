"""直连下载字节，不走代理。"""

from __future__ import annotations

import urllib.request

from .constants import GAP_MEDIA_FAILED, GAP_MEDIA_TOO_LARGE
from .media import accept_media

USER_AGENT = "Mozilla/5.0 SourceHub-Capture/0.1"


def fetch_bytes(url: str, max_bytes: int, timeout: int = 20):
    if not url:
        return None, None, GAP_MEDIA_FAILED
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=timeout) as response:
            data = response.read(max_bytes + 1)
    except Exception:
        return None, None, GAP_MEDIA_FAILED
    return accept_media(data, max_bytes)
