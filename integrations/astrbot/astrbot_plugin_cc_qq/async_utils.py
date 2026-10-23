"""异步上下文兼容（Async Compatibility）。"""

from __future__ import annotations

from contextlib import asynccontextmanager

try:  # Python 3.10+
    from contextlib import aclosing
except ImportError:  # Python 3.9 兼容

    @asynccontextmanager
    async def aclosing(thing):
        try:
            yield thing
        finally:
            await thing.aclose()


__all__ = ["aclosing"]
