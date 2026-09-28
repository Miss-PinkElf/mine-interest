"""独立 B 站登录（Bilibili Authentication）：扫码、检查与刷新。"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import aiohttp

from .constants import NETWORK_PROXY_KEY, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from .client import local_proxy_url
from .sourcehub.alerts import HEALTHY, LOGIN_REQUIRED, UNKNOWN

NAV_URL = "https://api.bilibili.com/x/web-interface/nav"
COOKIE_INFO_URL = "https://passport.bilibili.com/x/passport-login/web/cookie/info"
COOKIE_REFRESH_URL = "https://passport.bilibili.com/x/passport-login/web/cookie/refresh"
COOKIE_CONFIRM_URL = "https://passport.bilibili.com/x/passport-login/web/confirm/refresh"
QR_GENERATE_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
QR_POLL_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
CORRESPOND_URL = "https://www.bilibili.com/correspond/1/"
QR_SUCCESS = 0
QR_EXPIRED = 86038
QR_SCANNED = 86090
QR_WAITING = 86101
RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDLgd2OAkcGVtoE3ThUREbio0Eg
Uc/prcajMKXvkCKFCWhJYJcLkcM2DKKcSeFpD/j6Boy538YXnR6VhcuUJOhH2x71
nzPjfdTcqMz7djHum0qSZA0AyCBDABUqCrfNgCiJ00Ra7GmRj+YCK1NJEuewlb40
JNrRuoEUXpabUzGB8QIDAQAB
-----END PUBLIC KEY-----"""


class AuthError(Exception):
    """只包含类别，不携带 Cookie 或鉴权 URL。"""


class CredentialStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self, config: dict | None = None) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        config = config or {}
        return {
            "SESSDATA": str(config.get("sessdata") or ""),
            "buvid3": str(config.get("buvid3") or ""),
            "bili_jct": str(config.get("bili_jct") or ""),
            "refresh_token": str(config.get("refresh_token") or ""),
            "account_id": str(config.get("account_id") or ""),
        }

    def save(self, credentials: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(credentials, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(self.path)


class BilibiliAuth:
    def __init__(self, credentials: CredentialStore, config: dict | None = None):
        self.credentials = credentials
        self.config = config or {}
        self.proxy_url = local_proxy_url(str(self.config.get(NETWORK_PROXY_KEY) or ""))
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": USER_AGENT},
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS),
            trust_env=False,
        )
        return self

    async def __aexit__(self, *_):
        await self.session.close()

    async def _request(self, method: str, url: str, credentials: dict | None = None, **kwargs):
        cookies = {key: value for key, value in (credentials or {}).items() if key in {"SESSDATA", "bili_jct", "buvid3"} and value}
        try:
            async with self.session.request(method, url, cookies=cookies, allow_redirects=False, proxy=self.proxy_url or None, **kwargs) as response:
                if response.status != 200:
                    raise AuthError(f"auth_http_{response.status}")
                payload = await response.json(content_type=None)
                return payload, {key: value.value for key, value in response.cookies.items()}
        except (aiohttp.ClientError, TimeoutError, ValueError) as exc:
            raise AuthError(type(exc).__name__) from None

    async def check(self, credentials: dict) -> str:
        if not credentials.get("SESSDATA"):
            return LOGIN_REQUIRED
        try:
            payload, _ = await self._request("GET", NAV_URL, credentials)
        except AuthError:
            return UNKNOWN
        if payload.get("code") != 0:
            return LOGIN_REQUIRED if payload.get("code") in {-101, -111} else UNKNOWN
        data = payload.get("data") or {}
        if data.get("isLogin") is True:
            return HEALTHY
        return LOGIN_REQUIRED if data.get("isLogin") is False else UNKNOWN

    async def refresh_if_needed(self, credentials: dict) -> tuple[str, dict]:
        """网络与接口不确定时保持旧凭据并返回 unknown。"""
        if not credentials.get("SESSDATA"):
            return LOGIN_REQUIRED, credentials
        try:
            payload, _ = await self._request("GET", COOKIE_INFO_URL, credentials, params={"csrf": credentials.get("bili_jct") or ""})
            if payload.get("code") != 0:
                return UNKNOWN, credentials
            if not (payload.get("data") or {}).get("refresh"):
                return HEALTHY, credentials
            if not credentials.get("refresh_token") or not credentials.get("bili_jct"):
                return UNKNOWN, credentials
            updated = await self._refresh(credentials)
        except (AuthError, ImportError):
            return UNKNOWN, credentials
        self.credentials.save(updated)
        return HEALTHY, updated

    async def _refresh(self, credentials: dict) -> dict:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        public_key = serialization.load_pem_public_key(RSA_PUBLIC_KEY.encode("ascii"))
        timestamp = int(time.time() * 1000)
        encrypted = public_key.encrypt(
            f"refresh_{timestamp}".encode("ascii"),
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        ).hex()
        try:
            async with self.session.get(CORRESPOND_URL + encrypted, cookies={"SESSDATA": credentials["SESSDATA"]}, allow_redirects=False, proxy=self.proxy_url or None) as response:
                if response.status != 200:
                    raise AuthError("refresh_csrf_unavailable")
                html = await response.text()
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise AuthError(type(exc).__name__) from None
        match = re.search(r'<div\s+id="1-name"\s*>([^<]+)</div>', html)
        if not match:
            raise AuthError("refresh_csrf_missing")
        payload, cookies = await self._request(
            "POST", COOKIE_REFRESH_URL, credentials,
            data={
                "csrf": credentials["bili_jct"],
                "refresh_csrf": match.group(1).strip(),
                "source": "main_web",
                "refresh_token": credentials["refresh_token"],
            },
        )
        if payload.get("code") != 0 or not cookies.get("SESSDATA"):
            raise AuthError("refresh_failed")
        updated = dict(credentials)
        updated.update({
            "SESSDATA": cookies["SESSDATA"],
            "bili_jct": cookies.get("bili_jct") or credentials["bili_jct"],
            "refresh_token": str((payload.get("data") or {}).get("refresh_token") or credentials["refresh_token"]),
        })
        try:
            await self._request("POST", COOKIE_CONFIRM_URL, updated, data={"csrf": updated["bili_jct"], "refresh_token": credentials["refresh_token"]})
        except AuthError:
            pass
        return updated

    async def generate_qr(self) -> tuple[str, str]:
        payload, _ = await self._request("GET", QR_GENERATE_URL)
        data = payload.get("data") or {}
        if payload.get("code") != 0 or not data.get("url") or not data.get("qrcode_key"):
            raise AuthError("qr_generate_failed")
        return str(data["url"]), str(data["qrcode_key"])

    async def poll_qr(self, key: str) -> str:
        payload, cookies = await self._request("GET", QR_POLL_URL, params={"qrcode_key": key})
        data = payload.get("data") or {}
        code = data.get("code")
        if code == QR_SUCCESS:
            params = parse_qs(urlsplit(str(data.get("url") or "")).query)
            credentials = {
                "SESSDATA": cookies.get("SESSDATA") or (params.get("SESSDATA") or [""])[0],
                "bili_jct": cookies.get("bili_jct") or (params.get("bili_jct") or [""])[0],
                "refresh_token": str(data.get("refresh_token") or ""),
                "account_id": str(cookies.get("DedeUserID") or (params.get("DedeUserID") or [""])[0]),
            }
            if not credentials["SESSDATA"]:
                raise AuthError("qr_cookie_missing")
            self.credentials.save(credentials)
            return "success"
        return {QR_WAITING: "waiting", QR_SCANNED: "scanned", QR_EXPIRED: "expired"}.get(code, "unknown")
