"""LLM 语义判定（LLM-as-a-Judge）测试。"""

import json
import socket
import unittest

from aiohttp import web
from aiohttp.test_utils import TestServer

from astrbot_e2e.llm_judge import JudgeError, judge


def _llm_response(content):
    """构造 OpenAI 兼容响应体。"""
    return web.json_response({"choices": [{"message": {"content": content}}]})


class JudgeTest(unittest.IsolatedAsyncioTestCase):
    async def _serve(self, handler):
        """启动临时服务并返回基地址（不含 /v1）。"""
        app = web.Application()
        app.router.add_post("/{tail:.*}", handler)
        server = TestServer(app)
        await server.start_server()
        self.addAsyncCleanup(server.close)
        return str(server.make_url("")).rstrip("/")

    async def test_judge_returns_pass(self):
        async def chat(request):
            return _llm_response(json.dumps({"pass": True, "reason": "符合"}))

        base = await self._serve(chat)
        result = await judge(base, "key", "model", "必须是命令列表", "可用命令：/new /info")
        self.assertTrue(result["pass"])
        self.assertEqual(result["reason"], "符合")

    async def test_missing_config_raises(self):
        with self.assertRaisesRegex(JudgeError, "未配置"):
            await judge("", "", "", "criteria", "actual")

    async def test_judge_accepts_code_fence(self):
        fenced = '```json\n{}\n```'.format(json.dumps({"pass": True, "reason": "符合"}))

        async def chat(request):
            return _llm_response(fenced)

        base = await self._serve(chat)
        result = await judge(base, "key", "model", "criteria", "actual")
        self.assertTrue(result["pass"])
        self.assertEqual(result["reason"], "符合")

    async def test_judge_extracts_json_from_extra_text(self):
        content = '判定结果如下：{"pass": true, "reason": "符合"} 完毕'

        async def chat(request):
            return _llm_response(content)

        base = await self._serve(chat)
        result = await judge(base, "key", "model", "criteria", "actual")
        self.assertTrue(result["pass"])

    async def test_non_200_raises(self):
        async def chat(request):
            return web.Response(status=500, text="boom")

        base = await self._serve(chat)
        with self.assertRaisesRegex(JudgeError, "HTTP 500"):
            await judge(base, "key", "model", "criteria", "actual")

    async def test_non_json_response_raises(self):
        async def chat(request):
            return web.Response(text="not json", content_type="text/plain")

        base = await self._serve(chat)
        with self.assertRaisesRegex(JudgeError, "不是合法 JSON"):
            await judge(base, "key", "model", "criteria", "actual")

    async def test_json_array_content_raises(self):
        async def chat(request):
            return _llm_response(json.dumps(["pass", True]))

        base = await self._serve(chat)
        with self.assertRaisesRegex(JudgeError, "不是对象"):
            await judge(base, "key", "model", "criteria", "actual")

    async def test_connection_error_raises(self):
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        sock.close()
        with self.assertRaisesRegex(JudgeError, "请求失败"):
            await judge(
                "http://127.0.0.1:{}".format(port), "", "model", "criteria", "actual"
            )

    async def test_reason_none_returns_empty(self):
        async def chat(request):
            return _llm_response(json.dumps({"pass": False, "reason": None}))

        base = await self._serve(chat)
        result = await judge(base, "key", "model", "criteria", "actual")
        self.assertFalse(result["pass"])
        self.assertEqual(result["reason"], "")

    async def test_endpoint_with_v1_base(self):
        paths = []

        async def chat(request):
            paths.append(request.path)
            return _llm_response(json.dumps({"pass": True, "reason": "ok"}))

        base = await self._serve(chat)
        result = await judge(base + "/v1", "key", "model", "criteria", "actual")
        self.assertTrue(result["pass"])
        self.assertEqual(paths, ["/v1/chat/completions"])

    async def test_endpoint_with_v1_trailing_slash(self):
        paths = []

        async def chat(request):
            paths.append(request.path)
            return _llm_response(json.dumps({"pass": True, "reason": "ok"}))

        base = await self._serve(chat)
        result = await judge(base + "/v1/", "key", "model", "criteria", "actual")
        self.assertTrue(result["pass"])
        self.assertEqual(paths, ["/v1/chat/completions"])


    async def test_custom_headers_are_sent(self):
        captured = {}

        async def chat(request):
            captured.update({key.lower(): value for key, value in request.headers.items()})
            return _llm_response(json.dumps({"pass": True, "reason": "ok"}))

        base = await self._serve(chat)
        await judge(
            base,
            "key",
            "model",
            "criteria",
            "actual",
            headers={
                "x-opencode-session": "astrbot-e2e",
                "Authorization": "Bearer override",
            },
        )
        self.assertEqual(captured["x-opencode-session"], "astrbot-e2e")
        self.assertEqual(captured["authorization"], "Bearer override")
        self.assertEqual(captured["content-type"], "application/json")


if __name__ == "__main__":
    unittest.main()
