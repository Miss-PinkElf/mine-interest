"""AstrBot 生命周期（Lifecycle）：只采集，无消息发送入口。"""

from __future__ import annotations

import asyncio
from contextlib import suppress

from astrbot.api.star import Context, Star, StarTools, register

from pathlib import Path

from .sourcehub.vault import Vault
from .sourcehub.publish import Publisher, PublishError, PUBLISH_INTERVAL_SECONDS
from .sourcehub.alerts import AlertLedger, HEALTHY, LOGIN_REQUIRED, UNKNOWN
from .sourcehub.alert_publish import ALERT_DIR_SUFFIX, AlertPublisher, AlertPublishError

from .auth import BilibiliAuth, CredentialStore
from .client import BilibiliClient, FetchError
from .collector import Collector, numeric_id
from .constants import (
    ALERT_ENABLED_KEY, ALERT_POLL_SECONDS, ALERT_REMOTE_KEY, DEFAULT_POLL_SECONDS, LOG_PREFIX, MEDIA_MAX_BYTES, MIN_POLL_SECONDS, NETWORK_PROXY_KEY,
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
        self.publish_task = None
        self.client = None
        vault_dir = Path(str(self.config.get("vault_dir") or "data/sourcehub"))
        self.vault = Vault(vault_dir, git_enabled=True)
        self.publisher = Publisher(vault_dir) if self.config.get("publish_enabled", True) else None
        self.credential_store = CredentialStore(StarTools.get_data_dir(PLUGIN_NAME) / "credentials.json")
        self.alert_ledger = AlertLedger(vault_dir / "spool" / "alerts.json")
        alert_remote = str(self.config.get(ALERT_REMOTE_KEY) or "").strip()
        self.alert_publisher = AlertPublisher(
            vault_dir.with_name(vault_dir.name + ALERT_DIR_SUFFIX), alert_remote,
        ) if self.config.get(ALERT_ENABLED_KEY, False) and alert_remote else None
        self.alert_task = None

    async def initialize(self):
        if not self.config.get("enabled", False):
            self.logger.info("%s 未启用采集", LOG_PREFIX)
            return
        if self.publisher is not None:
            self.publish_task = asyncio.create_task(self._publish_loop())
        if self.alert_publisher is not None:
            self.alert_task = asyncio.create_task(self._alert_loop())
        self.task = asyncio.create_task(self.run())

    async def _alert_loop(self):
        while True:
            for event in self.alert_ledger.pending():
                try:
                    await asyncio.to_thread(self.alert_publisher.publish, event)
                    self.alert_ledger.mark_delivered(event["id"])
                except AlertPublishError as exc:
                    self.logger.warning("%s 告警待推送：%s", LOG_PREFIX, exc)
                    break
            await asyncio.sleep(ALERT_POLL_SECONDS)

    async def _publish_loop(self):
        while True:
            try:
                await asyncio.to_thread(self.publisher.sync_once)
            except asyncio.CancelledError:
                raise
            except PublishError as exc:
                self.logger.warning("%s 资料待推送：%s", LOG_PREFIX, exc)
            await asyncio.sleep(PUBLISH_INTERVAL_SECONDS)

    async def run(self):
        interval = max(MIN_POLL_SECONDS, int(self.config.get("poll_seconds", DEFAULT_POLL_SECONDS)))
        poller = None
        current_account = None
        while True:
            try:
                credentials = self.credential_store.load(self.config)
                async with BilibiliAuth(self.credential_store, self.config) as auth:
                    auth_status = await auth.check(credentials)
                    if auth_status == HEALTHY:
                        refresh_status, updated = await auth.refresh_if_needed(credentials)
                        if refresh_status == HEALTHY:
                            credentials = updated
                        elif refresh_status == LOGIN_REQUIRED:
                            auth_status = LOGIN_REQUIRED
                    if auth_status == LOGIN_REQUIRED:
                        account_hint = str(credentials.get("account_id") or current_account or "")
                        if account_hint.isdecimal():
                            self.alert_ledger.observe("bilibili", account_hint, LOGIN_REQUIRED)
                        self.logger.warning("%s 登录失效，请运行本地扫码登录工具", LOG_PREFIX)
                        await asyncio.sleep(interval)
                        continue
                    if auth_status == UNKNOWN:
                        self.logger.warning("%s 登录状态暂不可确认，本轮保留旧状态", LOG_PREFIX)
                        await asyncio.sleep(interval)
                        continue
                if self.client is None or credentials["SESSDATA"] != getattr(self, "_client_sessdata", ""):
                    if self.client:
                        await self.client.close()
                    self.client = BilibiliClient(
                        credentials["SESSDATA"], str(credentials.get("buvid3") or ""),
                        max(1, int(self.config.get("media_max_bytes", MEDIA_MAX_BYTES))),
                        str(self.config.get(NETWORK_PROXY_KEY) or ""),
                    )
                    self._client_sessdata = credentials["SESSDATA"]
                    poller = None
                identity = await self.client.get("identity")
                if identity.get("isLogin") is False:
                    raise FetchError("login_required")
                if identity.get("isLogin") is not True:
                    raise FetchError("identity_unknown")
                account = numeric_id(identity.get("mid"))
                self.alert_ledger.observe("bilibili", account, HEALTHY)
                if credentials.get("account_id") != account:
                    credentials["account_id"] = account
                    self.credential_store.save(credentials)
                if poller is None or account != current_account:
                    current_account = account
                    store = Store(StarTools.get_data_dir(PLUGIN_NAME) / account, vault=self.vault)
                    poller = Poller(self.client, Collector(self.client), store)
                await poller.cycle()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                if isinstance(exc, FetchError) and str(exc) == "login_required":
                    account_hint = str(current_account or self.credential_store.load(self.config).get("account_id") or "")
                    if account_hint.isdecimal():
                        self.alert_ledger.observe("bilibili", account_hint, LOGIN_REQUIRED)
                reason = str(exc) if isinstance(exc, FetchError) else type(exc).__name__
                self.logger.warning("%s 本轮未完全成功：%s", LOG_PREFIX, reason)
            await asyncio.sleep(interval)

    async def terminate(self):
        if self.alert_task:
            self.alert_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.alert_task
        if self.publish_task:
            self.publish_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.publish_task
        if self.task:
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task
        if self.client:
            await self.client.close()
