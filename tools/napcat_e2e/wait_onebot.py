#!/usr/bin/env python3
"""等待 NapCat 的 OneBot 账号真正就绪。

用途：
  - 只检查端口是否监听不够：容器刚启动/重连时端口可能已开，但账号还没登录，
    `start-instance` 连接会瞬时失败（Server disconnected）。
  - 本脚本连接 OneBot WS 并调用 get_login_info，确认返回的 user_id 与预期一致。

退出码：
  0  账号已就绪
  1  连接失败 / 调用失败 / user_id 不匹配

用法（由 common.sh 调用）：
  PYTHONPATH=<repo>/tools <venv>/python wait_onebot.py <port> <token> <expected_qq>
"""

from __future__ import annotations

import asyncio
import sys

from astrbot_e2e.onebot import OneBotClient


async def check(port: str, token: str, expected_qq: str) -> bool:
    client = OneBotClient(f"ws://127.0.0.1:{port}/onebot/v11/ws", token)
    try:
        await client.connect()
        info = await client.call("get_login_info", {})
        return str(info.get("user_id")) == str(expected_qq)
    except Exception:
        return False
    finally:
        await client.close()


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: wait_onebot.py <port> <token> <expected_qq>", file=sys.stderr)
        return 2
    port, token, expected_qq = sys.argv[1], sys.argv[2], sys.argv[3]
    return 0 if asyncio.run(check(port, token, expected_qq)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
