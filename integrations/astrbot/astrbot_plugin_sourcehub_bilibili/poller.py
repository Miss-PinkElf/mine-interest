"""通知轮询（Notification Polling），扫描进度与内容完成状态分离。"""

from __future__ import annotations

import asyncio

from .client import FetchError
from .constants import COLLECTION_GAP_PREFIX, MAX_ITEMS_PER_CYCLE, MAX_SCAN_PAGES
from .content import Document


class Poller:
    def __init__(self, client, collector, store):
        self.client = client
        self.collector = collector
        self.store = store

    async def scan(self):
        cursor = self.store.cursor()
        for _ in range(MAX_SCAN_PAGES):
            params = {"id": cursor["id"], "at_time": cursor["time"]} if cursor else {}
            data = await self.client.get("mentions", **params)
            if not isinstance(data.get("items"), list) or not isinstance(data.get("cursor"), dict):
                raise FetchError("notification_shape_changed")
            for item in data["items"]:
                self.store.receive(item)
            next_cursor = data["cursor"]
            if next_cursor.get("is_end") or not data["items"]:
                self.store.save_cursor({})
                return
            if not next_cursor.get("id") or "time" not in next_cursor:
                raise FetchError("notification_cursor_missing")
            next_cursor = {"id": next_cursor["id"], "time": next_cursor["time"]}
            if next_cursor == cursor:
                raise FetchError("notification_cursor_stalled")
            self.store.save_cursor(next_cursor)
            cursor = next_cursor

    async def process(self):
        for notification in self.store.pending()[:MAX_ITEMS_PER_CYCLE]:
            try:
                raw, doc = await self.collector.collect(notification)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                reason = str(exc) if isinstance(exc, FetchError) else type(exc).__name__
                raw = {"notification": notification}
                doc = Document(gaps=[f"{COLLECTION_GAP_PREFIX}{reason}"])
            await self.store.save(notification, raw, doc, self.client)

    async def cycle(self):
        # 扫描失败也处理已经安全保存的通知。
        try:
            await self.scan()
        finally:
            await self.process()
