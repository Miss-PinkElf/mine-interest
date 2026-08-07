package com.mineinterest.media.fanqie

/**
 * 番茄 Provider 常量。
 */
object FanqieConstants {
    val HOST_MARKERS = listOf("fanqienovel.com", "fqnovel.com", "novelfm.com")
    val BOOK_ID_QUERY = Regex("""[?&]book_id=(\d{10,})""")
    val BOOK_ID_PATH = Regex("""/page/(\d{10,})""")
    val BOOK_ID_PLAIN = Regex("""^\d{10,}$""")
    const val STATUS_JSON = "status.json"
    const val CHAPTER_JOURNAL = "downloaded_chapters.jsonl"
    const val DEFAULT_CONCURRENCY = 2
    const val ITEM_ID_PLACEHOLDER = "{item_id}"
}
