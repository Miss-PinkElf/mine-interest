"""只读网络客户端（Read-only Client），不提供平台写接口。"""

from __future__ import annotations

import asyncio
from urllib.parse import urlsplit

import aiohttp

from .constants import (
    API_BASE, ENDPOINTS, MAX_MEDIA_ATTEMPTS, MEDIA_CHUNK_BYTES,
    MEDIA_HOST_SUFFIXES, MEDIA_MAX_BYTES, MEDIA_RETRY_BASE_DELAY_SECONDS,
    REQUEST_TIMEOUT_SECONDS, RETRYABLE_MEDIA_STATUSES, SITE_BASE, USER_AGENT,
)


class FetchError(Exception):
    """错误仅包含类别/业务码，避免日志泄漏凭证或媒体鉴权链接。"""


def media_url(url: str) -> str:
    url = "https:" + url if url.startswith("//") else url
    parts = urlsplit(url)
    if (
        parts.scheme not in {"http", "https"}
        or not any((parts.hostname or "").endswith(suffix) for suffix in MEDIA_HOST_SUFFIXES)
        or parts.username or parts.password or parts.port not in {None, 80, 443}
    ):
        raise FetchError("media_host_not_allowed")
    return url


class BilibiliClient:
    def __init__(self, sessdata: str, buvid3: str = "", media_limit: int = MEDIA_MAX_BYTES):
        headers = {"User-Agent": USER_AGENT, "Referer": SITE_BASE + "/"}
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
        self.api = aiohttp.ClientSession(
            headers=headers, cookies={"SESSDATA": sessdata, "buvid3": buvid3},
            timeout=timeout, trust_env=False,
        )
        # 图片会话没有账号凭证，也不接收服务端 Cookie。
        self.media = aiohttp.ClientSession(
            headers=headers, timeout=timeout, trust_env=False,
            cookie_jar=aiohttp.DummyCookieJar(),
        )
        self.media_limit = media_limit

    async def get(self, endpoint: str, **params) -> dict:
        try:
            async with self.api.get(
                API_BASE + ENDPOINTS[endpoint], params=params, allow_redirects=False,
            ) as response:
                if response.status != 200:
                    raise FetchError(f"http_{response.status}")
                payload = await response.json(content_type=None)
                if payload.get("code") != 0:
                    raise FetchError(f"api_{payload.get('code', 'missing_code')}")
                data = payload.get("data")
                if not isinstance(data, dict):
                    raise FetchError("invalid_data_shape")
                return data
        except (aiohttp.ClientError, ValueError, TimeoutError) as exc:
            raise FetchError(type(exc).__name__) from None

    async def image(self, url: str) -> bytes:
        checked_url = media_url(url)
        last_error = FetchError("media_download_failed")
        for attempt in range(MAX_MEDIA_ATTEMPTS):
            try:
                async with self.media.get(checked_url, allow_redirects=False) as response:
                    if response.status != 200:
                        error = FetchError(f"media_http_{response.status}")
                        if response.status not in RETRYABLE_MEDIA_STATUSES and not 500 <= response.status < 600:
                            raise error
                        last_error = error
                    else:
                        data = bytearray()
                        async for chunk in response.content.iter_chunked(MEDIA_CHUNK_BYTES):
                            data.extend(chunk)
                            if len(data) > self.media_limit:
                                raise FetchError("media_size_limit")
                        return bytes(data)
            except (aiohttp.ClientError, TimeoutError) as exc:
                last_error = FetchError(type(exc).__name__)
            if attempt + 1 < MAX_MEDIA_ATTEMPTS:
                await asyncio.sleep(MEDIA_RETRY_BASE_DELAY_SECONDS * (attempt + 1))
        raise last_error

    async def close(self):
        await self.api.close()
        await self.media.close()
