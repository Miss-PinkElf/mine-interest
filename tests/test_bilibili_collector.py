"""B 站采集契约测试（Collection Contract Tests），只用合成数据。"""

from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.client import BilibiliClient, FetchError, media_url
from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.collector import Collector, dynamic_id
from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.constants import (
    ARTICLE_COMMENT, COMPLETE, EMPTY_BODY_GAP, OBJECT_GAP_PREFIX,
    PARENT_MISSING_GAP, PARTIAL, ROOT_MISSING_GAP,
)
from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.content import (
    Document, article_document, opus_document,
)
from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.poller import Poller
from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.store import Store, image_extension
from sourcehub.vault import Vault

UNIQUE_BODY_MARKER = "UNIQUE_BODY_MARKER_xyz"
SYNTHETIC_IMAGE_URL = "https://i0.hdslb.com/a.jpg"


def notification(identity=1, source_id=30, root_id=10):
    return {"id": identity, "item": {
        "source_id": source_id, "root_id": root_id, "subject_id": 99,
        "business_id": 1, "source_content": "@机器人 收藏",
    }}


def comment(identity, parent=0, root=0):
    return {"rpid": identity, "parent": parent, "root": root,
            "content": {"message": f"评论 {identity}"}}


class FakeClient:
    def __init__(self):
        self.calls = []
        self.image_calls = 0
        self.image_fail = False
        self.comments = {10: comment(10), 20: comment(20, 10, 10), 30: comment(30, 20, 10)}

    async def get(self, endpoint, **params):
        self.calls.append((endpoint, params))
        if endpoint == "comment":
            root = dict(self.comments[10])
            root["replies"] = list(self.comments.values())[1:]
            return {"root": root}
        if endpoint == "replies":
            return {"replies": [], "page": {"count": 0}}
        if endpoint == "video":
            return {"bvid": "BVsynthetic", "title": "测试视频", "desc": "长简介" * 1000, "pages": [{"cid": 1}]}
        if endpoint == "playurl":
            return {"durl": [{"url": SYNTHETIC_IMAGE_URL}]}
        raise FetchError("test_endpoint_missing")

    async def image(self, url):
        self.image_calls += 1
        if self.image_fail:
            raise FetchError("test_image_failure")
        return b"GIF89a" + b"synthetic-image"


class ContentTests(unittest.TestCase):
    def test_article_body_not_summary_and_lazy_images(self):
        doc = article_document({
            "summary": "摘要不能代替正文",
            "content": '<h1>全文</h1><p>末尾段落</p><img data-src="//i0.hdslb.com/a.jpg">',
        })
        self.assertIn("末尾段落", doc.text)
        self.assertEqual(doc.images, ["//i0.hdslb.com/a.jpg"])
        self.assertNotIn("摘要不能代替正文", doc.text)

    def test_opus_unknown_paragraph_marks_partial(self):
        doc = opus_document({"item": {"modules": [{"module_content": {
            "paragraphs": [{"future_node": "不能丢"}],
        }}]}})
        self.assertIn("不能丢", doc.text)
        self.assertIn("unknown_paragraph", doc.gaps)

    def test_opus_skips_protobuf_empty_modules(self):
        empty = {
            "module_author": {}, "module_content": {}, "module_title": {},
            "module_top": {"display": {}}, "module_type": 0,
        }
        filled = {
            **empty,
            "module_title": {"text": "唉"},
            "module_content": {"paragraphs": [
                {"text": {"nodes": [{"word": {"words": "心有点疼"}}]}},
            ]},
            "module_top": {"display": {"album": {"pics": [{"url": SYNTHETIC_IMAGE_URL}]}}},
        }
        doc = opus_document({"item": {"modules": [empty, empty, filled, empty]}})
        self.assertIn("心有点疼", doc.text)
        self.assertEqual(doc.images, [SYNTHETIC_IMAGE_URL])
        self.assertEqual(doc.gaps, [])

    def test_article_structured_body(self):
        doc = article_document({"opus": {"content": {"paragraphs": [
            {"text": {"nodes": [{"word": {"words": "完整正文"}}]}},
            {"pic": {"pics": [{"url": "https://i0.hdslb.com/a.jpg"}]}},
        ]}}})
        self.assertIn("完整正文", doc.text)
        self.assertEqual(len(doc.images), 1)
        self.assertEqual(doc.gaps, [])

    def test_delta_embedded_unknown_not_silently_dropped(self):
        doc = article_document({"content": json.dumps({"ops": [{"insert": {"unknown": "x"}}]})})
        self.assertIn("unknown_delta_insert", doc.gaps)

    def test_empty_delta_ops_marks_partial(self):
        doc = article_document({"content": json.dumps({"ops": []})})
        self.assertFalse(doc.text.strip())
        self.assertEqual(doc.images, [])
        self.assertIn(EMPTY_BODY_GAP, doc.gaps)

    def test_empty_paragraph_nodes_marks_partial(self):
        doc = article_document({"opus": {"content": {"paragraphs": [
            {"text": {"nodes": []}},
        ]}}})
        self.assertFalse(doc.text.strip())
        self.assertEqual(doc.images, [])
        self.assertIn(EMPTY_BODY_GAP, doc.gaps)

    def test_empty_html_marks_partial(self):
        doc = article_document({"content": "<div></div>"})
        self.assertFalse(doc.text.strip())
        self.assertEqual(doc.images, [])
        self.assertIn(EMPTY_BODY_GAP, doc.gaps)

    def test_image_only_body_is_not_empty(self):
        doc = article_document({"content": json.dumps({
            "ops": [{"insert": {"image": SYNTHETIC_IMAGE_URL}}],
        })})
        self.assertEqual(doc.images, [SYNTHETIC_IMAGE_URL])
        self.assertNotIn(EMPTY_BODY_GAP, doc.gaps)

    def test_dynamic_uses_page_identifier(self):
        self.assertEqual(dynamic_id("https://www.bilibili.com/opus/12345?x=1"), "12345")
        with self.assertRaises(FetchError):
            dynamic_id("https://example.com/12345")

    def test_image_magic_not_suffix(self):
        self.assertEqual(image_extension(b"GIF89a"), ".gif")
        self.assertEqual(image_extension(b"\x00\x00\x00\x18ftypisom"), ".mp4")
        self.assertEqual(image_extension(b"FLV\x01"), ".flv")
        with self.assertRaises(FetchError):
            image_extension(b"<html>error</html>")

    def test_media_url_rejects_other_hosts_and_credentials(self):
        self.assertEqual(media_url("//i0.hdslb.com/a.jpg"), "https://i0.hdslb.com/a.jpg")
        self.assertEqual(
            media_url("https://upos-sz-mirrorcoso1.bilivideo.com/a.mp4"),
            "https://upos-sz-mirrorcoso1.bilivideo.com/a.mp4",
        )
        for url in ["https://evil.example/a.jpg", "http://127.0.0.1/a.jpg", "https://i0.hdslb.com.evil/a", "https://u:p@i0.hdslb.com/a"]:
            with self.assertRaises(FetchError):
                media_url(url)


class MediaRetryTests(unittest.IsolatedAsyncioTestCase):
    async def test_media_recovers_on_fifth_attempt(self):
        class Response:
            status = 200

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_):
                return False

            class content:
                @staticmethod
                async def iter_chunked(_size):
                    yield b"GIF89a-image"

        class Media:
            calls = 0

            def get(self, *_args, **_kwargs):
                self.calls += 1
                if self.calls < 5:
                    raise TimeoutError("timeout")
                return Response()

        client = BilibiliClient.__new__(BilibiliClient)
        client.media = Media()
        client.media_limit = 100
        from unittest.mock import patch
        with patch("integrations.astrbot.astrbot_plugin_sourcehub_bilibili.client.asyncio.sleep"):
            result = await client.image(SYNTHETIC_IMAGE_URL)
        self.assertEqual(result, b"GIF89a-image")
        self.assertEqual(client.media.calls, 5)


class CollectorTests(unittest.IsolatedAsyncioTestCase):
    async def test_parent_and_root_are_distinct_and_video_not_truncated(self):
        raw, doc = await Collector(FakeClient()).collect(notification())
        self.assertEqual(raw["comments"]["trigger"]["rpid"], 30)
        self.assertEqual(raw["comments"]["parent"]["rpid"], 20)
        self.assertEqual(raw["comments"]["root"]["rpid"], 10)
        self.assertIn("长简介" * 1000, doc.text)
        self.assertIn(SYNTHETIC_IMAGE_URL, doc.downloads)
        self.assertEqual(doc.gaps, [])

    async def test_deleted_parent_not_confused_with_root(self):
        client = FakeClient()
        del client.comments[20]
        raw, doc = await Collector(client).collect(notification())
        self.assertNotIn("parent", raw["comments"])
        self.assertTrue(any(gap.startswith("parent:") for gap in doc.gaps))
        self.assertEqual(raw["comments"]["root"]["rpid"], 10)

    async def test_forward_dynamic_keeps_caption_and_original(self):
        class DynamicClient:
            async def get(self, endpoint, **params):
                original = params["id"] == "200"
                item = {"modules": {"module_dynamic": {"desc": {"text": "原文" if original else "转发附言"}}}}
                if not original:
                    item["orig"] = {"id_str": "200"}
                return {"item": item}
        objects = []
        doc = await Collector(DynamicClient()).dynamic("100", objects, set())
        self.assertIn("转发附言", doc.text)
        self.assertIn("原文", doc.text)
        self.assertEqual(len(objects), 2)

    async def test_missing_parent_and_root_fields_are_partial(self):
        client = FakeClient()
        client.comments[30] = {"rpid": 30, "content": {"message": "评论 30"}}
        raw, doc = await Collector(client).collect(notification())
        self.assertNotIn("parent", raw["comments"])
        self.assertNotIn("root", raw["comments"])
        self.assertIn(PARENT_MISSING_GAP, doc.gaps)
        self.assertIn(ROOT_MISSING_GAP, doc.gaps)

    async def test_null_parent_and_root_fields_are_partial(self):
        client = FakeClient()
        client.comments[30] = {
            "rpid": 30, "parent": None, "root": None,
            "parent_str": None, "root_str": None,
            "content": {"message": "评论 30"},
        }
        raw, doc = await Collector(client).collect(notification())
        self.assertNotIn("parent", raw["comments"])
        self.assertNotIn("root", raw["comments"])
        self.assertIn(PARENT_MISSING_GAP, doc.gaps)
        self.assertIn(ROOT_MISSING_GAP, doc.gaps)

    async def test_explicit_zero_parent_is_complete_top_level(self):
        client = FakeClient()
        client.comments = {10: comment(10, parent=0, root=0)}
        raw, doc = await Collector(client).collect(notification(source_id=10, root_id=10))
        self.assertIsNone(raw["comments"]["parent"])
        self.assertIsNone(raw["comments"]["root"])
        self.assertEqual(doc.gaps, [])

    async def test_string_parent_and_root_ids_are_distinct(self):
        client = FakeClient()
        client.comments[30] = {
            "rpid": 30, "parent": "20", "root": "10",
            "content": {"message": "评论 30"},
        }
        raw, doc = await Collector(client).collect(notification())
        self.assertEqual(raw["comments"]["parent"]["rpid"], 20)
        self.assertEqual(raw["comments"]["root"]["rpid"], 10)
        self.assertEqual(doc.gaps, [])

    async def test_dynamic_null_desc_does_not_raise(self):
        class NullDescClient:
            async def get(self, endpoint, **params):
                return {"item": {"modules": {"module_dynamic": {"desc": None, "major": {}}}}}
        doc = await Collector(NullDescClient()).dynamic("100", [], set())
        self.assertIn("dynamic_body_missing", doc.gaps)

    async def test_opus_major_summary_used_when_detail_modules_empty(self):
        class OpusClient:
            async def get(self, endpoint, **params):
                if endpoint == "dynamic":
                    return {"item": {"modules": {"module_dynamic": {"desc": None, "major": {
                        "opus": {
                            "title": "唉",
                            "summary": {"text": "心有点疼"},
                            "pics": [{"url": SYNTHETIC_IMAGE_URL}],
                        },
                    }}}}}
                if endpoint == "opus":
                    return {"item": {"modules": [
                        {"module_content": {}, "module_top": {}, "module_title": {}},
                    ]}}
                raise FetchError("unexpected")
        doc = await Collector(OpusClient()).dynamic("300", [], set())
        self.assertIn("心有点疼", doc.text)
        self.assertEqual(doc.images, [SYNTHETIC_IMAGE_URL])
        self.assertNotIn("body_missing", doc.gaps)
        self.assertNotIn("opus_body_missing", doc.gaps)


class StorageTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(Path(self.temp.name))

    async def test_retry_image_failure_and_restart_dedup(self):
        item = notification()
        self.store.receive(item)
        client = FakeClient()
        client.image_fail = True
        doc = Document("正文", ["https://i0.hdslb.com/a.jpg"])
        await self.store.save(item, {}, doc, client)
        self.assertEqual(self.store.record("1")["status"], PARTIAL)
        self.assertEqual(len(Store(self.store.path).pending()), 1)
        client.image_fail = False
        await self.store.save(item, {}, Document("正文", ["https://i0.hdslb.com/a.jpg"]), client)
        self.assertEqual(self.store.record("1")["status"], COMPLETE)
        self.store.receive(item)
        self.assertEqual(Store(self.store.path).pending(), [])
        self.assertTrue(list(self.store.item_path("1").glob("media/*.gif")))

    async def test_complete_document_not_overwritten(self):
        await self.store.save(notification(), {}, Document("原文"), FakeClient())
        path = self.store.item_path("1") / "content.md"
        path.write_text("用户修改", encoding="utf-8")
        await self.store.save(notification(), {}, Document("重采"), FakeClient())
        self.assertEqual(path.read_text(encoding="utf-8"), "用户修改")

    async def test_export_existing_uses_readable_article_body_for_vault(self):
        vault = Vault(Path(self.temp.name) / "vault", git_enabled=False)
        store = Store(Path(self.temp.name) / "archive", vault=vault)
        folder = store.item_path("1")
        folder.mkdir(parents=True)
        (folder / "content.md").write_text(
            "# 正文标题\n\n第一段正文\n\n![图片](media/a.jpg)", encoding="utf-8"
        )
        (folder / "media").mkdir()
        (folder / "media/a.jpg").write_bytes(b"\xff\xd8\xff" + b"synthetic-image")
        from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.store import write_json
        write_json(folder / "record.json", {
            "notification": {"item": {"source_id": 1, "uri": "https://www.bilibili.com/read/cv99"}},
            "source_url": "https://www.bilibili.com/read/cv99",
            "objects": [{"title": "专栏标题", "summary": "错误摘要"}],
            "comments": {"trigger": {"rpid": 1, "content": {"message": "@机器人"}}},
            "media": [{"source_url": SYNTHETIC_IMAGE_URL, "local_path": "media/a.jpg"}],
        })

        self.assertEqual(store.export_existing(), 1)
        content = (vault.item_dir("bilibili:article:99") / "content.md").read_text(encoding="utf-8")
        self.assertIn("第一段正文", content)
        self.assertNotIn("错误摘要", content)
        self.assertNotIn("](media/a.jpg)", content)
        self.assertIn("](../../../../../media/", content)

    async def test_repair_failed_media_is_idempotent_and_preserves_body(self):
        vault = Vault(Path(self.temp.name) / "vault", git_enabled=False)
        store = Store(Path(self.temp.name) / "archive", vault=vault)
        folder = store.item_path("1")
        folder.mkdir(parents=True)
        (folder / "content.md").write_text(
            "采集状态（Collection Status）：partial\n\n正文原文\n\n![图片](https://i0.hdslb.com/a.jpg)\n\n## 未完成项\n\n- image:timeout",
            encoding="utf-8",
        )
        from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.store import write_json
        write_json(folder / "record.json", {
            "notification": {"item": {"source_id": 1, "uri": "https://www.bilibili.com/read/cv99"}},
            "source_url": "https://www.bilibili.com/read/cv99",
            "objects": [{"title": "专栏标题", "summary": "摘要"}],
            "comments": {"trigger": {"rpid": 1, "content": {"message": "@机器人"}}},
            "media": [{"source_url": SYNTHETIC_IMAGE_URL, "error": "timeout"}],
            "gaps": ["image:timeout"],
            "status": PARTIAL,
        })
        client = FakeClient()

        self.assertEqual(await store.repair_failed_media(client), 1)
        self.assertEqual(await store.repair_failed_media(client), 0)
        self.assertEqual(client.image_calls, 1)
        record = store.record("1")
        self.assertEqual(record["status"], COMPLETE)
        self.assertTrue((folder / record["media"][0]["local_path"]).exists())
        content = (vault.item_dir("bilibili:article:99") / "content.md").read_text(encoding="utf-8")
        self.assertIn("正文原文", content)
        self.assertIn("](../../../../../media/", content)

    async def test_scan_paginates_and_persists_before_cursor(self):
        class PagingClient:
            async def get(self, endpoint, **params):
                if not params:
                    return {"items": [notification(2)], "cursor": {"id": 2, "time": 100, "is_end": False}}
                self_params = {"id": 2, "at_time": 100}
                if params != self_params:
                    raise AssertionError(params)
                return {"items": [notification(1)], "cursor": {"is_end": True}}
        await Poller(PagingClient(), None, self.store).scan()
        self.assertEqual(len(self.store.pending()), 2)
        self.assertEqual(self.store.cursor(), {})

    async def test_scan_failure_retains_resume_cursor_and_notifications(self):
        class BrokenClient:
            async def get(self, endpoint, **params):
                if params:
                    raise FetchError("temporary_failure")
                return {"items": [notification()], "cursor": {"id": 1, "time": 100, "is_end": False}}
        with self.assertRaises(FetchError):
            await Poller(BrokenClient(), None, self.store).scan()
        self.assertEqual(self.store.cursor(), {"id": 1, "time": 100})
        self.assertEqual(len(self.store.pending()), 1)

    async def test_failed_collection_does_not_lose_notification(self):
        class BrokenCollector:
            async def collect(self, item):
                raise FetchError("temporary_failure")
        self.store.receive(notification())
        await Poller(FakeClient(), BrokenCollector(), self.store).process()
        self.assertEqual(self.store.record("1")["status"], PARTIAL)
        self.assertEqual(len(self.store.pending()), 1)

    async def test_partial_retry_keeps_body_when_object_refetch_fails(self):
        item = notification()
        first_raw = {
            "notification": item,
            "objects": [{"bvid": "BVsynthetic", "desc": UNIQUE_BODY_MARKER}],
            "source_url": "https://www.bilibili.com/video/BVsynthetic",
        }
        client = FakeClient()
        client.image_fail = True
        await self.store.save(
            item, first_raw,
            Document(UNIQUE_BODY_MARKER, [SYNTHETIC_IMAGE_URL]),
            client,
        )
        self.assertEqual(self.store.record("1")["status"], PARTIAL)
        failed_raw = {"notification": item, "objects": []}
        await self.store.save(item, failed_raw, Document(gaps=["object:api_error"]), client)
        record = self.store.record("1")
        self.assertEqual(record["status"], PARTIAL)
        self.assertEqual(record["objects"][0]["desc"], UNIQUE_BODY_MARKER)
        content = (self.store.item_path("1") / "content.md").read_text(encoding="utf-8")
        self.assertIn(UNIQUE_BODY_MARKER, content)
        client.image_fail = False
        success_raw = {
            "notification": item,
            "objects": [{"bvid": "BVsynthetic", "desc": UNIQUE_BODY_MARKER}],
            "source_url": "https://www.bilibili.com/video/BVsynthetic",
        }
        await self.store.save(
            item, success_raw,
            Document(UNIQUE_BODY_MARKER, [SYNTHETIC_IMAGE_URL]),
            client,
        )
        self.assertEqual(self.store.record("1")["status"], COMPLETE)
        self.assertIn(UNIQUE_BODY_MARKER, (self.store.item_path("1") / "content.md").read_text(encoding="utf-8"))
        self.assertTrue(list(self.store.item_path("1").glob("media/*.gif")))

    async def test_attribute_error_does_not_block_later_notifications(self):
        class MixedCollector:
            async def collect(self, item):
                if item["id"] == 1:
                    None.get("text")
                return {}, Document("ok")
        self.store.receive(notification(1))
        self.store.receive(notification(2))
        await Poller(FakeClient(), MixedCollector(), self.store).process()
        self.assertEqual(self.store.record("2")["status"], COMPLETE)
        self.assertEqual(self.store.record("1")["status"], PARTIAL)
        self.assertTrue(self.store.record("1").get("attempted_at"))
        self.assertEqual([item["id"] for item in self.store.pending()], [1])

    async def test_cancelled_error_propagates_from_process(self):
        class CancelCollector:
            async def collect(self, item):
                raise asyncio.CancelledError()
        self.store.receive(notification())
        with self.assertRaises(asyncio.CancelledError):
            await Poller(FakeClient(), CancelCollector(), self.store).process()

    async def test_image_only_body_completes_when_download_succeeds(self):
        doc = article_document({"content": json.dumps({
            "ops": [{"insert": {"image": SYNTHETIC_IMAGE_URL}}],
        })})
        await self.store.save(notification(), {"objects": [{}]}, doc, FakeClient())
        self.assertEqual(self.store.record("1")["status"], COMPLETE)

    async def test_empty_article_stays_partial_despite_title_and_notice(self):
        class ArticleClient(FakeClient):
            async def get(self, endpoint, **params):
                if endpoint == "article":
                    return {"title": "标题不能证明全文", "content": json.dumps({"ops": []})}
                return await super().get(endpoint, **params)
        item = notification()
        item["item"]["business_id"] = ARTICLE_COMMENT
        raw, doc = await Collector(ArticleClient()).collect(item)
        self.assertIn(EMPTY_BODY_GAP, doc.gaps)
        await self.store.save(item, raw, doc, ArticleClient())
        record = self.store.record("1")
        self.assertEqual(record["status"], PARTIAL)
        self.assertIn(EMPTY_BODY_GAP, record["gaps"])

    async def test_recovered_opus_text_clears_stale_body_missing(self):
        item = notification()
        first = Document("# 通知标题\n\n链接", gaps=["body_missing"])
        await self.store.save(item, {"notification": item, "objects": [{"title": "动态"}]}, first, FakeClient())
        self.assertEqual(self.store.record("1")["status"], PARTIAL)
        await self.store.save(
            item,
            {"notification": item, "objects": [{"title": "动态"}]},
            Document("心有点疼", [SYNTHETIC_IMAGE_URL]),
            FakeClient(),
        )
        record = self.store.record("1")
        self.assertEqual(record["status"], COMPLETE)
        self.assertEqual(record["gaps"], [])
        self.assertIn("心有点疼", (self.store.item_path("1") / "content.md").read_text(encoding="utf-8"))

    async def test_empty_body_gap_survives_failed_object_retry(self):
        item = notification()
        first = Document("# 通知标题\n\n链接", gaps=[EMPTY_BODY_GAP])
        await self.store.save(item, {"notification": item, "objects": [{"title": "空文"}]}, first, FakeClient())
        self.assertEqual(self.store.record("1")["status"], PARTIAL)
        await self.store.save(
            item,
            {"notification": item, "objects": []},
            Document(gaps=[f"{OBJECT_GAP_PREFIX}api_error"]),
            FakeClient(),
        )
        record = self.store.record("1")
        self.assertEqual(record["status"], PARTIAL)
        self.assertIn(EMPTY_BODY_GAP, record["gaps"])
        self.assertEqual(record["objects"][0]["title"], "空文")


if __name__ == "__main__":
    unittest.main()
