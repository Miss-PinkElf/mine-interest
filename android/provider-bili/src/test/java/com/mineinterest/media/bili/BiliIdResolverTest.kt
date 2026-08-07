package com.mineinterest.media.bili

import com.mineinterest.media.core.model.ParsedLink
import com.mineinterest.media.core.model.Platform
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class BiliIdResolverTest {

    private val resolver = BiliIdResolver()

    @Test
    fun resolve_bv_from_url() {
        val id = resolver.extractFromParsed(
            ParsedLink(
                platform = Platform.BILIBILI,
                rawText = "",
                canonicalUrl = "https://www.bilibili.com/video/BV1xx411c7mD",
                idHint = "BV1xx411c7mD",
            ),
        )
        assertEquals("BV1xx411c7mD", id)
    }

    @Test
    fun extract_bv_from_text_only() {
        val id = resolver.extractBvidFromText("see BV1aa411c7mD now")
        assertEquals("BV1aa411c7mD", id)
    }

    @Test
    fun extract_from_parsed_without_hint_uses_url() {
        val id = resolver.extractFromParsed(
            ParsedLink(
                platform = Platform.BILIBILI,
                rawText = "share",
                canonicalUrl = "https://www.bilibili.com/video/BV1bb411c7mD/?spm=1",
                idHint = null,
            ),
        )
        assertEquals("BV1bb411c7mD", id)
    }

    @Test
    fun extract_av_hint_without_bv_returns_null() {
        val id = resolver.extractFromParsed(
            ParsedLink(
                platform = Platform.BILIBILI,
                rawText = "av170001",
                canonicalUrl = null,
                idHint = "av170001",
            ),
        )
        assertNull(id)
    }
}
