"""代理标准输入被对端关闭时必须变成代理错误。"""

import unittest

from astrbot_plugin_cc_qq.agents.process import AgentProcessError, deliver_prompt


class _Stdin:
    def write(self, data):
        return len(data)

    async def drain(self):
        raise ConnectionResetError("Connection lost")

    def close(self):
        raise AssertionError("drain 失败后不应再 close")


class _Process:
    def __init__(self, returncode):
        self.returncode = returncode
        self.wait_calls = 0

    async def wait(self):
        self.wait_calls += 1
        self.returncode = 3


class DeliverPromptTest(unittest.IsolatedAsyncioTestCase):
    async def test_connection_reset_becomes_agent_process_error(self):
        process = _Process(returncode=None)
        with self.assertRaises(AgentProcessError) as caught:
            await deliver_prompt(_Stdin(), "hi", process)
        self.assertEqual(str(caught.exception), "代理进程在接收消息前退出，退出码 3")
        self.assertEqual(process.wait_calls, 1)

    async def test_known_return_code_skips_wait(self):
        process = _Process(returncode=1)
        with self.assertRaises(AgentProcessError) as caught:
            await deliver_prompt(_Stdin(), "hi", process)
        self.assertIn("退出码 1", str(caught.exception))
        self.assertEqual(process.wait_calls, 0)


if __name__ == "__main__":
    unittest.main()
