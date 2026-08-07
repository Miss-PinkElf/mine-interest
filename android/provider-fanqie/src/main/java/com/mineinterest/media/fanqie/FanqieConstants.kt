package com.mineinterest.media.fanqie

/**
 * 番茄 Provider 常量。
 * 短链域名列表对齐 Tomato `ALLOWED_SHORT_LINK_HOSTS`，仅跟跳这些 host 以防 SSRF。
 */
object FanqieConstants {
    /** 用于平台识别（LinkParser 可含不带 www 的后缀匹配） */
    val HOST_MARKERS = listOf(
        "fanqienovel.com",
        "fqnovel.com",
        "novelfm.com",
        "changdunovel.com",
    )

    /**
     * 允许跟随重定向的短链完整 host（小写）。
     * 仅这些域名可被 [FanqieBookIdResolver] 发起网络请求。
     */
    val ALLOWED_SHORT_LINK_HOSTS = setOf(
        "changdunovel.com",
        "www.changdunovel.com",
        "fanqienovel.com",
        "www.fanqienovel.com",
        "fqnovel.com",
        "www.fqnovel.com",
    )

    /** `/t/<token>` 分享短链（token 可含 _ -） */
    val SHORT_LINK_PATH = Regex(
        """(?i)^https?://[^/\s]+/t/[A-Za-z0-9_-]+/?(?:[?#][^\s]*)?$""",
    )

    val BOOK_ID_QUERY = Regex(
        """(?i)(?:book_id|bookId)=(\d{5,})""",
    )
    val BOOK_ID_PATH = Regex("""/page/(\d{5,})""")
    val BOOK_ID_PLAIN = Regex("""^\d{5,}$""")
    val URL_IN_TEXT = Regex("""https?://[^\s]+""")

    const val STATUS_JSON = "status.json"
    const val CHAPTER_JOURNAL = "downloaded_chapters.jsonl"
    const val DEFAULT_CONCURRENCY = 2
    const val ITEM_ID_PLACEHOLDER = "{item_id}"
}
