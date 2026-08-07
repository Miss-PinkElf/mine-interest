package com.mineinterest.media.fanqie

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class FanqieBookIdResolverTest {

    @Test
    fun resolve_from_page_path() {
        assertEquals(
            "7318247498772674083",
            FanqieBookIdResolver.resolve("https://fanqienovel.com/page/7318247498772674083"),
        )
    }

    @Test
    fun resolve_plain_id() {
        assertEquals(
            "7318247498772674083",
            FanqieBookIdResolver.resolve("7318247498772674083"),
        )
    }

    @Test
    fun resolve_from_query() {
        assertEquals(
            "7318247498772674083",
            FanqieBookIdResolver.resolve("https://example.com/x?book_id=7318247498772674083&x=1"),
        )
    }

    @Test
    fun resolve_unknown_returns_null() {
        assertNull(FanqieBookIdResolver.resolve("hello novel"))
    }
}
