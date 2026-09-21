"""AstrBot 生命周期（Lifecycle）：只采集，无消息发送入口。"""

from __future__ import annotations

import asyncio
from contextlib import suppress

from astrbot.api.star import Context, Star, StarTools, register

from .client import BilibiliClient, FetchError
from .collector import Collector, numeric_id
from .constants import (
    DEFAULT_POLL_SECONDS, LOG_PREFIX, MEDIA_MAX_BYTES, MIN_POLL_SECONDS,
    PLUGIN_NAME, PLUGIN_VERSION,
)
from .poller import Poller
from .store import Store


@register(PLUGIN_NAME, "Codex", "B 站 @ 原文只读采集", PLUGIN_VERSION)
class SourceHubBilibili(Star):
    def __init__(self, context: Context, config=None):
        super().__init__(context, config)
        self.config = config or {}
        self.task = None
        self.client = None

    async def initialize(self):
        if not self.config.get("enabled", False):
            self.logger.info("%s 未启用采集", LOG_PREFIX)
            return
        sessdata = str(self.config.get("sessdata", "")).strip()
        if not sessdata:
            self.logger.warning("%s 缺少本地登录配置，未启动", LOG_PREFIX)
            return
        self.client = BilibiliClient(
            sessdata, str(self.config.get("buvid3", "")),
            max(1, int(self.config.get("media_max_bytes", MEDIA_MAX_BYTES))),
        )
        self.task = asyncio.create_task(self.run())

    async def run(self):
        interval = max(MIN_POLL_SECONDS, int(self.config.get("poll_seconds", DEFAULT_POLL_SECONDS)))
        poller = None
        current_account = None
        while True:
            try:
                identity = await self.client.get("identity")
                if not identity.get("isLogin"):
                    raise FetchError("login_required")
                account = numeric_id(identity.get("mid"))
                if poller is None or account != current_account:
                    current_account = account
                    store = Store(StarTools.get_data_dir(PLUGIN_NAME) / account)
                    poller = Poller(self.client, Collector(self.client), store)
                await poller.cycle()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                reason = str(exc) if isinstance(exc, FetchError) else type(exc).__name__
                self.logger.warning("%s 本轮未完全成功：%s", LOG_PREFIX, reason)
            await asyncio.sleep(interval)

    async def terminate(self):
        if self.task:
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task
        if self.client:
            await self.client.close()
