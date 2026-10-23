"""通知轮询（Notification Polling），扫描进度与内容完成状态分离。"""

from __future__ import annotations

import asyncio

from .client import FetchError
from .constants import COLLECTION_GAP_PREFIX, LOG_PREFIX, MAX_ITEMS_PER_CYCLE, MAX_SCAN_PAGES
from .content import Document
from .sourcehub.github_actions import MAX_REPOSITORIES_PER_MESSAGE
from .sourcehub.github_links import extract_repository_links, fork_requested

#: 通知日志里标题的最大展示长度，避免把整条视频标题刷进日志。
NOTIFICATION_TITLE_LOG_MAX_CHARS = 40


def notification_label(notification: dict) -> str:
    """把通知压成一行可读标签：业务类型｜发送者｜标题。"""
    item = notification.get("item") or {}
    user = notification.get("user") or {}
    business = str(item.get("business") or item.get("type") or "通知").strip()
    nickname = str(user.get("nickname") or user.get("mid") or "").strip()
    title = str(item.get("title") or "").strip().replace("\n", " ")
    if len(title) > NOTIFICATION_TITLE_LOG_MAX_CHARS:
        title = title[:NOTIFICATION_TITLE_LOG_MAX_CHARS] + "…"
    parts = [part for part in (business, nickname, title) if part]
    return "｜".join(parts) if parts else "未命名通知"


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
            if data["items"]:
                self._log("收到 %s 条 B 站通知" % len(data["items"]))
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
            label = notification_label(notification)
            self._log("开始采集 B 站通知：%s" % label)
            try:
                raw, doc = await self.collector.collect(notification)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                reason = str(exc) if isinstance(exc, FetchError) else type(exc).__name__
                raw = {"notification": notification}
                doc = Document(gaps=[f"{COLLECTION_GAP_PREFIX}{reason}"])
                self._log("采集未完成：%s（%s）" % (label, reason), warning=True)
            await self.store.save(notification, raw, doc, self.client)
            self._log("已保存 B 站条目：%s" % label)
            await self._run_github(notification, raw, doc)

    async def _run_github(self, notification: dict, raw: dict, doc: Document) -> None:
        """B 站不回复消息；结果写入 AstrBot 日志，插件页可查看最近动作。"""
        repositories = extract_repository_links(doc.text)
        if not repositories:
            return
        if self.github is None:
            self._log("检测到 GitHub 链接，但 GitHub 自动化未启用，跳过")
            return
        if len(repositories) > MAX_REPOSITORIES_PER_MESSAGE:
            self._log(
                "GitHub 链接超过单条上限 %s，只处理前 %s 个"
                % (MAX_REPOSITORIES_PER_MESSAGE, MAX_REPOSITORIES_PER_MESSAGE),
                warning=True,
            )
        fork = fork_requested(trigger_message(notification, raw))
        self._log(
            "GitHub 自动化开始：%s 个仓库，fork=%s"
            % (len(repositories), "是" if fork else "否")
        )
        try:
            results = await asyncio.to_thread(
                self.github.handle,
                repositories,
                fork,
                "bilibili",
            )
        except Exception as exc:
            self._log(
                "GitHub 自动化异常：%s：%s" % (type(exc).__name__, exc), warning=True
            )
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
            self.logger.warning("%s %s", LOG_PREFIX, message)
        else:
            self.logger.info("%s %s", LOG_PREFIX, message)

    async def cycle(self):
        # 扫描失败也处理已经安全保存的通知。
        try:
            await self.scan()
        finally:
            await self.process()
