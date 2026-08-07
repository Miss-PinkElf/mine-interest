package com.mineinterest.media.fanqie

import com.mineinterest.media.fanqie.model.FanqieBookMeta
import com.mineinterest.media.fanqie.model.FanqieChapterRef

/**
 * 番茄书信息与章节目录客户端。
 */
interface FanqieCatalogClient {
    suspend fun fetchMeta(bookId: String): FanqieBookMeta
    suspend fun fetchChapters(bookId: String): List<FanqieChapterRef>
}
