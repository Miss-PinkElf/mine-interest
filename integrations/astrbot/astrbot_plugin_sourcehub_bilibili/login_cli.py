"""本机管理员扫码入口（Local QR Login CLI）。"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from .auth import AuthError, BilibiliAuth, CredentialStore
from .constants import NETWORK_PROXY_KEY

QR_POLL_SECONDS = 3


async def login(credentials_path: Path, proxy_url: str = "") -> int:
    import qrcode

    async with BilibiliAuth(CredentialStore(credentials_path), {NETWORK_PROXY_KEY: proxy_url}) as auth:
        url, key = await auth.generate_qr()
        qr = qrcode.QRCode(border=2)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
        print("请用哔哩哔哩客户端扫描上方二维码。二维码仅显示在本机终端。")
        while True:
            await asyncio.sleep(QR_POLL_SECONDS)
            status = await auth.poll_qr(key)
            if status == "success":
                print("登录成功；凭据已保存在本机插件数据目录。")
                return 0
            if status == "expired":
                print("二维码已过期，请重新运行命令。")
                return 1
            if status == "scanned":
                print("已扫码，等待手机端确认。")


def main() -> int:
    parser = argparse.ArgumentParser(description="SourceHub B 站本机扫码登录")
    parser.add_argument("--credentials", type=Path, required=True, help="插件数据目录中的 credentials.json 路径")
    parser.add_argument("--proxy", default="", help="可选本机 HTTP 代理，例如 http://127.0.0.1:7897")
    args = parser.parse_args()
    try:
        return asyncio.run(login(args.credentials, args.proxy))
    except AuthError as exc:
        print(f"登录失败：{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
