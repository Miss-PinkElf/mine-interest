"""状态变化与待送重试（Alert Ledger Tests）。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sourcehub.alerts import AlertLedger, DISCONNECTED, HEALTHY, LOGIN_REQUIRED, UNKNOWN


class AlertLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "alerts.json"
        self.ledger = AlertLedger(self.path)

    def test_fault_recovery_and_restart_are_deduplicated(self):
        self.assertIsNone(self.ledger.observe("bilibili", "123456", HEALTHY))
        fault = self.ledger.observe("bilibili", "123456", LOGIN_REQUIRED, "t1")
        self.assertEqual(fault["account"], "尾号 3456")
        self.assertIsNone(self.ledger.observe("bilibili", "123456", LOGIN_REQUIRED, "t2"))
        self.assertIsNone(self.ledger.observe("bilibili", "123456", UNKNOWN, "t3"))
        self.ledger.mark_delivered(fault["id"])
        restarted = AlertLedger(self.path)
        self.assertEqual(restarted.pending(), [])
        recovered = restarted.observe("bilibili", "123456", HEALTHY, "t4")
        self.assertEqual(recovered["status"], HEALTHY)
        self.assertEqual(len(restarted.pending()), 1)

    def test_failed_delivery_remains_pending(self):
        self.ledger.observe("qq", "987654", DISCONNECTED, "t1")
        self.assertEqual(len(AlertLedger(self.path).pending()), 1)

    def test_unknown_never_implies_login_failure(self):
        self.assertIsNone(self.ledger.observe("qq", "987654", UNKNOWN))
        self.assertEqual(self.ledger.pending(), [])


if __name__ == "__main__":
    unittest.main()
