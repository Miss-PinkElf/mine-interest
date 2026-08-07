package com.mineinterest.media.fanqie

import com.mineinterest.media.fanqie.model.FanqieBookMeta
import com.mineinterest.media.fanqie.model.FanqieChapterRef
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit

/**
 * 通过番茄网页/公开目录接口获取书信息与章节列表。
 *
 * 借鉴 Tomato `FanqieWebNetwork`：
 * - 书页 HTML：`https://fanqienovel.com/page/{bookId}`
 * - 目录 API：`https://fanqienovel.com/api/reader/directory/detail?bookId=`
 *
 * **可能失效**：页面结构与接口变更时需单点修改本类。
 */
class FanqieWebCatalogClient(
    private val http: OkHttpClient = defaultClient(),
) : FanqieCatalogClient {

    override suspend fun fetchMeta(bookId: String): FanqieBookMeta = withContext(Dispatchers.IO) {
        val html = get(BOOK_PAGE_URL.format(bookId), htmlHeaders(bookId))
        val title = extractTitle(html) ?: "book_$bookId"
        val author = extractAuthor(html)
        FanqieBookMeta(bookId = bookId, title = title, author = author)
    }

    override suspend fun fetchChapters(bookId: String): List<FanqieChapterRef> =
        withContext(Dispatchers.IO) {
            val json = get(DIRECTORY_API.format(bookId), jsonHeaders(bookId))
            val chapters = parseChapterList(json)
            if (chapters.isEmpty()) {
                error("目录获取失败：未解析到章节（接口可能变更或需登录）")
            }
            chapters
        }

    internal fun parseChapterList(json: String): List<FanqieChapterRef> {
        // 匹配 item_id / itemId / chapter_id 与 title 的粗解析
        val itemIds = Regex(""""(?:item_id|itemId|chapter_id|chapterId)"\s*:\s*"?(\d{5,})"?""")
            .findAll(json)
            .map { it.groupValues[1] }
            .distinct()
            .toList()
        val titles = Regex(""""(?:title|chapter_title|chapterName)"\s*:\s*"((?:\\.|[^"\\])*)"""")
            .findAll(json)
            .map { unescape(it.groupValues[1]) }
            .toList()

        if (itemIds.isEmpty()) return emptyList()

        return itemIds.mapIndexed { index, id ->
            FanqieChapterRef(
                itemId = id,
                title = titles.getOrNull(index) ?: "第${index + 1}章",
                index = index,
            )
        }
    }

    private fun extractTitle(html: String): String? {
        Regex("""<title>([^<]+)</title>""", RegexOption.IGNORE_CASE)
            .find(html)
            ?.groupValues
            ?.get(1)
            ?.substringBefore('_')
            ?.substringBefore('-')
            ?.trim()
            ?.takeIf { it.isNotEmpty() }
            ?.let { return it }
        return Regex(""""bookName"\s*:\s*"((?:\\.|[^"\\])*)"""")
            .find(html)
            ?.groupValues
            ?.get(1)
            ?.let { unescape(it) }
    }

    private fun extractAuthor(html: String): String? {
        return Regex(""""author(?:Name)?"\s*:\s*"((?:\\.|[^"\\])*)"""")
            .find(html)
            ?.groupValues
            ?.get(1)
            ?.let { unescape(it) }
    }

    private fun get(url: String, headers: Map<String, String>): String {
        val builder = Request.Builder().url(url).get()
        headers.forEach { (k, v) -> builder.header(k, v) }
        http.newCall(builder.build()).execute().use { response ->
            if (!response.isSuccessful) {
                error("目录请求失败 HTTP ${response.code}")
            }
            return response.body?.string().orEmpty()
        }
    }

    private fun htmlHeaders(bookId: String): Map<String, String> = mapOf(
        "User-Agent" to USER_AGENT,
        "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer" to BOOK_PAGE_URL.format(bookId),
    )

    private fun jsonHeaders(bookId: String): Map<String, String> = mapOf(
        "User-Agent" to USER_AGENT,
        "Accept" to "application/json, text/plain, */*",
        "Referer" to BOOK_PAGE_URL.format(bookId),
    )

    private fun unescape(value: String): String =
        value
            .replace("\\n", "\n")
            .replace("\\\"", "\"")
            .replace("\\\\", "\\")
            .replace("\\/", "/")

    companion object {
        private const val BOOK_PAGE_URL = "https://fanqienovel.com/page/%s"
        private const val DIRECTORY_API =
            "https://fanqienovel.com/api/reader/directory/detail?bookId=%s"
        private const val USER_AGENT =
            "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 " +
                "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"

        fun defaultClient(): OkHttpClient =
            OkHttpClient.Builder()
                .followRedirects(true)
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(60, TimeUnit.SECONDS)
                .build()
    }
}
