"""WebUI 登录与插件重载（Reloader）。"""

from __future__ import annotations

import aiohttp


async def _read_json(response, action: str) -> dict:
    status = response.status
    try:
        return await response.json()
    except (aiohttp.ContentTypeError, ValueError):
        raise RuntimeError("{}: HTTP {}，响应不是合法 JSON".format(action, status))


async def login_and_reload(
    base_url: str,
    username: str,
    password: str,
    plugin_id: str,
    timeout: float = 30.0,
) -> None:
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    # 本地 WebUI 常用 127.0.0.1，默认 CookieJar 会拒绝 IP 主机的 Cookie。
    cookie_jar = aiohttp.CookieJar(unsafe=True)
    async with aiohttp.ClientSession(
        timeout=client_timeout, cookie_jar=cookie_jar
    ) as session:
        async with session.post(
            "{}/api/v1/auth/login".format(base_url.rstrip("/")),
            json={"username": username, "password": password},
        ) as response:
            body = await _read_json(response, "WebUI 登录失败")
            if response.status != 200 or body.get("status") != "ok":
                raise RuntimeError(
                    "WebUI 登录失败: {} {}".format(response.status, body)
                )
        data = body.get("data") or {}
        token = data.get("token")
        headers = {"Authorization": "Bearer {}".format(token)} if token else {}
        async with session.post(
            "{}/api/v1/plugins/reload".format(base_url.rstrip("/")),
            json={"plugin_id": plugin_id},
            headers=headers,
        ) as response:
            body = await _read_json(response, "插件重载失败")
            if response.status != 200 or body.get("status") not in ("ok", "success"):
                raise RuntimeError(
                    "插件重载失败: {} {}".format(response.status, body)
                )
