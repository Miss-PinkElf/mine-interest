"""GitHub 仓库链接解析测试（GitHub Link Tests）。"""

from __future__ import annotations

import unittest

from sourcehub.github_links import extract_repository_links, fork_requested


class GithubLinkTests(unittest.TestCase):
    def test_extracts_repository_from_common_urls(self):
        text = (
            "看这个 https://github.com/openai/codex 和 "
            "https://www.github.com/astrbot/AstrBot.git?tab=readme#install"
        )
        self.assertEqual(
            extract_repository_links(text),
            ["openai/codex", "astrbot/AstrBot"],
        )

    def test_extracts_repository_from_subpaths_and_scheme_less_links(self):
        text = "github.com/owner/repo/tree/main/src 和 https://github.com/owner/repo/blob/dev/a.py"
        self.assertEqual(extract_repository_links(text), ["owner/repo"])

    def test_deduplicates_case_insensitively(self):
        text = "https://github.com/Owner/Repo 与 https://github.com/owner/repo"
        self.assertEqual(extract_repository_links(text), ["Owner/Repo"])

    def test_ignores_non_repository_paths_and_gist(self):
        text = (
            "https://github.com/features/copilot "
            "https://github.com/sponsors/someone "
            "https://gist.github.com/someone/abc123"
        )
        self.assertEqual(extract_repository_links(text), [])

    def test_fork_command_must_be_a_separate_token(self):
        self.assertTrue(fork_requested("请 /fork 这个仓库"))
        self.assertTrue(fork_requested("/FORK"))
        self.assertFalse(fork_requested("fork 这个仓库"))
        self.assertFalse(fork_requested("/forked"))
        self.assertFalse(fork_requested("https://example.com//fork"))


if __name__ == "__main__":
    unittest.main()
