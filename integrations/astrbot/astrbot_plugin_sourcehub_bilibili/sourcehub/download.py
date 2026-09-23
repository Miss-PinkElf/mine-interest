"""直连下载字节，不走代理。"""

from __future__ import annotations

import urllib.request
import time
from urllib.error import HTTPError, URLError

from .constants import GAP_MEDIA_FAILED, GAP_MEDIA_TOO_LARGE
from .media import accept_media

USER_AGENT = "Mozilla/5.0 SourceHub-Capture/0.1"
MAX_MEDIA_ATTEMPTS = 5
MEDIA_RETRY_BASE_DELAY_SECONDS = 0.25
RETRYABLE_HTTP_STATUS = {429}


def fetch_bytes(url: str, max_bytes: int, timeout: int = 20):
    if not url:
        return None, None, GAP_MEDIA_FAILED
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for attempt in range(MAX_MEDIA_ATTEMPTS):
        try:
            with opener.open(request, timeout=timeout) as response:
                data = response.read(max_bytes + 1)
            return accept_media(data, max_bytes)
        except HTTPError as exc:
            if exc.code not in RETRYABLE_HTTP_STATUS and not 500 <= exc.code < 600:
                break
        except (URLError, TimeoutError, ConnectionError):
            pass
        except Exception:
            break
        if attempt + 1 < MAX_MEDIA_ATTEMPTS:
            time.sleep(MEDIA_RETRY_BASE_DELAY_SECONDS * (attempt + 1))
    return None, None, GAP_MEDIA_FAILED
