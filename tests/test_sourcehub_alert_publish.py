"""独立私有 Git 告警发布（Alert Publisher Tests）。"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from sourcehub.alert_publish import AlertPublisher, AlertPublishError


class AlertPublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote.git"
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, capture_output=True)
        self.publisher = AlertPublisher(self.root / "alerts", str(self.remote), private_check=lambda: True)
        self.event = {"id": "00000001", "platform": "bilibili", "account": "尾号 3456", "status": "login_required", "time": "2026-09-28T00:00:00Z"}

    def test_single_event_single_commit_and_recovery(self):
        self.assertTrue(self.publisher.publish(self.event))
        self.assertFalse(self.publisher.publish(self.event))
        recovery = {**self.event, "id": "00000002", "status": "healthy"}
        self.assertTrue(self.publisher.publish(recovery))
        count = subprocess.run(["git", "--git-dir", str(self.remote), "rev-list", "--count", "main"], check=True, capture_output=True, text=True).stdout.strip()
        self.assertEqual(count, "2")
        files = subprocess.run(["git", "--git-dir", str(self.remote), "ls-tree", "-r", "--name-only", "main"], check=True, capture_output=True, text=True).stdout.splitlines()
        self.assertEqual(files, ["events/00000001.md", "events/00000002.md"])

    def test_private_check_failure_does_not_push(self):
        blocked = AlertPublisher(self.root / "alerts", str(self.remote), private_check=lambda: False)
        with self.assertRaisesRegex(AlertPublishError, "private_unverified"):
            blocked.publish(self.event)
        self.assertFalse((self.root / "alerts").exists())

    def test_stale_local_commit_is_never_pushed(self):
        local = self.root / "alerts"
        subprocess.run(["git", "init", str(local)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(local), "config", "user.name", "test"], check=True)
        subprocess.run(["git", "-C", str(local), "config", "user.email", "test@local"], check=True)
        (local / "private.txt").write_text("local only", encoding="utf-8")
        subprocess.run(["git", "-C", str(local), "add", "private.txt"], check=True)
        subprocess.run(["git", "-C", str(local), "commit", "-m", "旧本地提交"], check=True, capture_output=True)
        self.assertTrue(self.publisher.publish(self.event))
        files = subprocess.run(["git", "--git-dir", str(self.remote), "ls-tree", "-r", "--name-only", "main"], check=True, capture_output=True, text=True).stdout.splitlines()
        self.assertEqual(files, ["events/00000001.md"])


if __name__ == "__main__":
    unittest.main()
