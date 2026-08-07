package com.mineinterest.media.bili

import org.junit.Assert.assertTrue
import org.junit.Test

class BiliSubtitleClientTest {

    @Test
    fun jsonSubtitleToSrt_contains_cues() {
        val client = BiliSubtitleClient()
        val json = """
            {"body":[
              {"from":0.0,"to":1.5,"content":"你好"},
              {"from":1.5,"to":3.0,"content":"世界"}
            ]}
        """.trimIndent()
        val srt = client.jsonSubtitleToSrt(json)
        assertTrue(srt.contains("你好"))
        assertTrue(srt.contains("-->"))
        assertTrue(srt.contains("世界"))
    }
}
