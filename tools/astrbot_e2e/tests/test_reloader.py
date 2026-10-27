import unittest

from aiohttp import web
from aiohttp.test_utils import TestServer

from astrbot_e2e.reloader import login_and_reload


class ReloaderTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.logged_in = False
        self.reloaded = None
        self.bearer = None

        async def login(request):
            body = await request.json()
            self.logged_in = body["username"] == "e2e" and body["password"] == "pass"
            if not self.logged_in:
                return web.json_response({"status": "error", "data": {}}, status=401)
            response = web.json_response(
                {"status": "ok", "data": {"token": "fake-token"}}
            )
            response.set_cookie(
                "astrbot_dashboard_jwt", "fake-token", secure=True, httponly=True
            )
            return response

        async def reload(request):
            self.bearer = request.headers.get("Authorization")
            cookie_token = request.cookies.get("astrbot_dashboard_jwt")
            if self.bearer != "Bearer fake-token" and cookie_token != "fake-token":
                return web.json_response({"status": "error", "data": {}}, status=401)
            body = await request.json()
            self.reloaded = body["plugin_id"]
            return web.json_response({"status": "ok", "data": {}})

        app = web.Application()
        app.router.add_post("/api/v1/auth/login", login)
        app.router.add_post("/api/v1/plugins/reload", reload)
        self.server = TestServer(app)
        await self.server.start_server()

    async def asyncTearDown(self):
        await self.server.close()

    async def test_login_and_reload(self):
        base = str(self.server.make_url("")).rstrip("/")
        await login_and_reload(base, "e2e", "pass", "astrbot_plugin_cc_qq")
        self.assertTrue(self.logged_in)
        self.assertEqual(self.bearer, "Bearer fake-token")
        self.assertEqual(self.reloaded, "astrbot_plugin_cc_qq")

    async def test_reload_rejects_wrong_password(self):
        base = str(self.server.make_url("")).rstrip("/")
        with self.assertRaisesRegex(RuntimeError, "登录失败"):
            await login_and_reload(base, "e2e", "wrong", "x")
