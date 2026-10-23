"""通知轮询（Notification Polling），扫描进度与内容完成状态分离。"""

from __future__ import annotations

import asyncio

from .client import FetchError
from .constants import COLLECTION_GAP_PREFIX, MAX_ITEMS_PER_CYCLE, MAX_SCAN_PAGES
from .content import Document
from .sourcehub.github_actions import MAX_REPOSITORIES_PER_MESSAGE
from .sourcehub.github_links import extract_repository_links, fork_requested


def trigger_message(notification: dict, raw: dict) -> str:
    """取本次触发评论的正文；取不到时退回通知自带的 source_content。"""
    comments = raw.get("comments") or {}
    trigger = comments.get("trigger") or {}
    message = str(((trigger.get("content") or {}).get("message")) or "")
    if not message:
        message = str(((notification.get("item") or {}).get("source_content")) or "")
    return message


class Poller:
    def __init__(self, client, collector, store, github=None, logger=None):
        self.client = client
        self.collector = collector
        self.store = store
        self.github = github
        self.logger = logger

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
            await self._run_github(notification, raw, doc)

    async def _run_github(self, notification: dict, raw: dict, doc: Document) -> None:
        """B 站不回复消息；结果写入日志，插件页可查看最近动作。"""
        if self.github is None:
            return
        repositories = extract_repository_links(doc.text)
        if not repositories:
            return
        if len(repositories) > MAX_REPOSITORIES_PER_MESSAGE:
            self._log(
                "GitHub 链接超过单条上限 %s，只处理前 %s 个"
                % (MAX_REPOSITORIES_PER_MESSAGE, MAX_REPOSITORIES_PER_MESSAGE),
                warning=True,
            )
        try:
            results = await asyncio.to_thread(
                self.github.handle,
                repositories,
                fork_requested(trigger_message(notification, raw)),
                "bilibili",
            )
        except Exception as exc:
            self._log("GitHub 自动化异常：%s" % type(exc).__name__, warning=True)
            return
        for result in results:
            self._log(
                "GitHub %s %s：%s" % (result.action, result.repository, result.message),
                warning=not result.ok,
            )

    def _log(self, message: str, warning: bool = False) -> None:
        if self.logger is None:
            return
        if warning:
            self.logger.warning(message)
        else:
            self.logger.info(message)

    async def cycle(self):
        # 扫描失败也处理已经安全保存的通知。
        try:
            await self.scan()
        finally:
            await self.process()
