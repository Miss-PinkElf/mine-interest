package com.mineinterest.media.core.link

import com.mineinterest.media.core.model.Platform
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class LinkParserTest {

    private val parser = LinkParser()

    @Test
    fun parse_bilibili_bv_from_share_text() {
        val text = "【标题】https://www.bilibili.com/video/BV1xx411c7mD/?spm=1 完整放送"
        val result = parser.parse(text)
        assertEquals(Platform.BILIBILI, result.platform)
        assertEquals("BV1xx411c7mD", result.idHint)
    }

    @Test
    fun parse_bilibili_short_link_host() {
        val result = parser.parse("https://b23.tv/abcdefg")
        assertEquals(Platform.BILIBILI, result.platform)
        assertTrue(result.canonicalUrl!!.contains("b23.tv"))
    }

    @Test
    fun parse_fanqie_book_id_path() {
        val result = parser.parse("https://fanqienovel.com/page/1234567890123456789")
        assertEquals(Platform.FANQIE, result.platform)
        assertEquals("1234567890123456789", result.idHint)
    }

    @Test
    fun parse_unknown() {
        val result = parser.parse("hello world")
        assertEquals(Platform.UNKNOWN, result.platform)
    }

    @Test
    fun parseBatch_multiline_mixed_platforms() {
        val text = """
            https://www.bilibili.com/video/BV1xx411c7mD
            垃圾行没有链接
            https://fanqienovel.com/page/7318247498772674083
            https://www.bilibili.com/video/BV1xx411c7mD
        """.trimIndent()
        val batch = parser.parseBatch(text)
        assertEquals(2, batch.items.size)
        assertTrue(batch.skippedLines.isNotEmpty())
        assertEquals(1, batch.items.count { it.platform == Platform.BILIBILI })
        assertEquals(1, batch.items.count { it.platform == Platform.FANQIE })
    }

    @Test
    fun parseBatch_multiple_urls_in_one_line() {
        val text =
            "看这个 https://www.bilibili.com/video/BV1aa411c7mD 还有 https://b23.tv/xxxxxx"
        val batch = parser.parseBatch(text)
        assertTrue(
            batch.items.size >= 2 || batch.items.any { it.platform == Platform.BILIBILI },
        )
    }
}
