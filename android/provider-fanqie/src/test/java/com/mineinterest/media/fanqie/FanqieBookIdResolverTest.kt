package com.mineinterest.media.fanqie

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class FanqieBookIdResolverTest {

    @Test
    fun resolve_from_page_path() {
        assertEquals(
            "7318247498772674083",
            FanqieBookIdResolver.parseBookId("https://fanqienovel.com/page/7318247498772674083"),
        )
    }

    @Test
    fun resolve_plain_id() {
        assertEquals(
            "7318247498772674083",
            FanqieBookIdResolver.parseBookId("7318247498772674083"),
        )
    }

    @Test
    fun resolve_from_query() {
        assertEquals(
            "7318247498772674083",
            FanqieBookIdResolver.parseBookId(
                "https://example.com/x?book_id=7318247498772674083&x=1",
            ),
        )
    }

    @Test
    fun parse_book_id_from_changdunovel_share_query() {
        val url =
            "https://changdunovel.com/ug/pages/book-share?share_type=11&aid=1967&book_id=7423591956359416856"
        assertEquals("7423591956359416856", FanqieBookIdResolver.parseBookId(url))
    }

    @Test
    fun parse_book_id_from_share_text_with_url() {
        val text =
            "变身灾厄萝莉，我发动了诸神黄昏https://fanqienovel.com/page/7423591956359416856"
        assertEquals("7423591956359416856", FanqieBookIdResolver.parseBookId(text))
    }

    @Test
    fun is_short_link_changdunovel() {
        assertTrue(FanqieBookIdResolver.isShortLink("https://changdunovel.com/t/sZ-unSSoOow/"))
        assertTrue(FanqieBookIdResolver.isShortLink("https://changdunovel.com/t/E_HDbOHpMJA/"))
        assertTrue(FanqieBookIdResolver.isShortLink("https://changdunovel.com/t/AbC-Def_123/"))
    }

    @Test
    fun reject_short_link_unknown_host() {
        assertFalse(FanqieBookIdResolver.isShortLink("https://example.com/t/E_HDbOHpMJA/"))
    }

    @Test
    fun short_link_has_no_local_book_id() {
        assertNull(FanqieBookIdResolver.parseBookId("https://changdunovel.com/t/sZ-unSSoOow/"))
    }

    @Test
    fun resolve_unknown_returns_null() {
        assertNull(FanqieBookIdResolver.parseBookId("hello novel"))
    }

    @Test
    fun legacy_resolve_alias() {
        assertEquals(
            "7318247498772674083",
            FanqieBookIdResolver.resolve("7318247498772674083"),
        )
    }
}
