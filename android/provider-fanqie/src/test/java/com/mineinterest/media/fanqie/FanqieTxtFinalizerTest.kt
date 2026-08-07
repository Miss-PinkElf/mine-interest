package com.mineinterest.media.fanqie

import org.junit.Assert.assertTrue
import org.junit.Test

class FanqieTxtFinalizerTest {

    @Test
    fun merge_includes_titles_and_bodies() {
        val text = FanqieTxtFinalizer.merge(
            listOf(
                "开篇" to "正文一",
                "转折" to "正文二",
            ),
        )
        assertTrue(text.contains("开篇"))
        assertTrue(text.contains("正文一"))
        assertTrue(text.contains("转折"))
        assertTrue(text.contains("正文二"))
    }
}
