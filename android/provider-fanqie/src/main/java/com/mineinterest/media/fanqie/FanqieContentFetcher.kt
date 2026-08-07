package com.mineinterest.media.fanqie

/**
 * 可插拔番茄章节正文源。
 */
interface FanqieContentFetcher {
    suspend fun fetchChapterContent(itemId: String): String
}
