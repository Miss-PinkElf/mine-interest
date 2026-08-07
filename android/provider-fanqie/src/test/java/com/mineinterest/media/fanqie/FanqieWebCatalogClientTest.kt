package com.mineinterest.media.fanqie

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class FanqieWebCatalogClientTest {

    private val client = FanqieWebCatalogClient()

    @Test
    fun parseChapterList_from_fixture() {
        val json = """
            {
              "data": {
                "chapterListWithVolume": [
                  [
                    {"item_id":"1111111111","title":"第一章"},
                    {"item_id":"2222222222","title":"第二章"}
                  ]
                ]
              }
            }
        """.trimIndent()
        val list = client.parseChapterList(json)
        assertEquals(2, list.size)
        assertEquals("1111111111", list[0].itemId)
        assertTrue(list[0].title.contains("第一") || list[0].title.isNotBlank())
    }
}
