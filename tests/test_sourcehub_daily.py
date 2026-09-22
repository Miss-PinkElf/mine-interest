"""QQ 日收集账本（Daily Ledger）行为测试。"""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from sourcehub.daily import DailyLedger
from sourcehub.grouping import IncomingMessage


def message(event_id: str, text: str = "普通消息") -> IncomingMessage:
    return IncomingMessage(
        platform="qq",
        conversation_id="group-1",
        event_id=event_id,
        sender_id="sender-1",
        source_time="2026-09-21T16:00:00Z",
        received_at="2026-09-21T16:00:00Z",
        text=text,
        nodes=[],
    )


class DailyLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ledger = DailyLedger(Path(self.temp.name), timezone_name="Asia/Shanghai")

    def test_append_uses_shanghai_day_and_deduplicates_event(self):
        day = self.ledger.append(message("1"), datetime(2026, 9, 21, 16, tzinfo=timezone.utc))
        self.ledger.append(message("1"), datetime(2026, 9, 21, 16, tzinfo=timezone.utc))

        self.assertEqual(day, "2026-09-22")
        self.assertEqual([item.event_id for item in self.ledger.pending("group-1", day)], ["1"])

    def test_mark_finalized_survives_restart(self):
        day = "2026-09-22"
        self.ledger.append(message("1"), datetime(2026, 9, 21, 16, tzinfo=timezone.utc))
        self.ledger.mark_finalized("group-1", day, ["1"])

        restored = DailyLedger(Path(self.temp.name), timezone_name="Asia/Shanghai")
        self.assertEqual(restored.pending("group-1", day), [])


if __name__ == "__main__":
    unittest.main()
