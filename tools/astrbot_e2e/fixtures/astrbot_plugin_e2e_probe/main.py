"""端到端测试探针插件（Probe Plugin）。"""

from __future__ import annotations

import asyncio

from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

LOG_PREFIX = "[e2e_probe]"


def _argument(event: AstrMessageEvent, command: str) -> str:
    text = str(getattr(event, "message_str", "") or "").strip()
    for prefix in ("/" + command, command):
        if text.startswith(prefix):
            return text[len(prefix):].strip()
    return text


@register("astrbot_plugin_e2e_probe", "Claude", "端到端测试探针插件", "0.1.0")
class E2EProbe(Star):
    def __init__(self, context: Context, config=None):
        super().__init__(context, config)

    @filter.command("e2e_echo")
    async def e2e_echo(self, event: AstrMessageEvent):
        text = _argument(event, "e2e_echo")
        self.logger.info("%s echo %s", LOG_PREFIX, text)
        yield event.plain_result("e2e_echo:{}".format(text))

    @filter.command("e2e_sleep")
    async def e2e_sleep(self, event: AstrMessageEvent):
        raw = _argument(event, "e2e_sleep") or "0"
        try:
            milliseconds = int(raw)
        except ValueError:
            self.logger.info("%s sleep invalid %s", LOG_PREFIX, raw)
            yield event.plain_result("e2e_sleep:invalid")
            return
        await asyncio.sleep(milliseconds / 1000)
        self.logger.info("%s sleep %s", LOG_PREFIX, milliseconds)
        yield event.plain_result("e2e_sleep:{}".format(milliseconds))

    @filter.command("e2e_log")
    async def e2e_log(self, event: AstrMessageEvent):
        text = _argument(event, "e2e_log")
        self.logger.info("%s log %s", LOG_PREFIX, text)
        yield event.plain_result("e2e_log:ok")
