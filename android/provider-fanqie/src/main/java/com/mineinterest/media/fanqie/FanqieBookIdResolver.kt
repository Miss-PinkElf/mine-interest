package com.mineinterest.media.fanqie

import com.mineinterest.media.core.model.ParsedLink
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request

/**
 * 从分享文案 / URL / 纯数字解析番茄 book_id。
 *
 * - [parseBookId]：纯本地，不访问网络
 * - [resolveBookId]：必要时跟随 `/t/<token>` 短链重定向（仅允许白名单 host）
 *
 * 短链形态示例：`https://changdunovel.com/t/sZ-unSSoOow/`
 * 对齐 Tomato `base_system/book_id.rs`。
 */
object FanqieBookIdResolver {

    /**
     * 本地解析：纯数字、query book_id/bookId、`/page/{id}`。
     * 会先从文本中提取 URL 再解析。
     */
    fun parseBookId(input: String): String? {
        val trimmed = input.trim()
        if (trimmed.isEmpty()) return null

        if (FanqieConstants.BOOK_ID_PLAIN.matches(trimmed)) {
            return trimmed
        }

        val target = FanqieConstants.URL_IN_TEXT.find(trimmed)?.value ?: trimmed

        FanqieConstants.BOOK_ID_QUERY.find(target)?.groupValues?.get(1)?.let { return it }
        FanqieConstants.BOOK_ID_PATH.find(target)?.groupValues?.get(1)?.let { return it }

        // 兼容旧调用点命名
        return null
    }

    /** 兼容旧 API：等同 [parseBookId]。 */
    fun resolve(raw: String): String? = parseBookId(raw)

    /**
     * 是否为白名单域名上的 `/t/token` 短链。
     */
    fun isShortLink(input: String): Boolean {
        val trimmed = input.trim()
        val target = FanqieConstants.URL_IN_TEXT.find(trimmed)?.value ?: trimmed
        if (!FanqieConstants.SHORT_LINK_PATH.matches(target)) {
            return false
        }
        val host = urlHost(target) ?: return false
        return host in FanqieConstants.ALLOWED_SHORT_LINK_HOSTS
    }

    /**
     * 从 [ParsedLink] 解析 book_id；短链会发起网络请求跟随重定向。
     */
    suspend fun resolveFromParsed(
        parsed: ParsedLink,
        http: OkHttpClient,
    ): String = withContext(Dispatchers.IO) {
        parseBookId(parsed.idHint.orEmpty())
            ?: parseBookId(parsed.canonicalUrl.orEmpty())
            ?: parseBookId(parsed.rawText)
            ?: resolveShortLinkFromTexts(
                listOfNotNull(parsed.canonicalUrl, parsed.rawText),
                http,
            )
            ?: error(ERROR_CANNOT_RESOLVE_BOOK_ID)
    }

    /**
     * 完整解析：本地失败后，若输入含白名单短链则跟跳转再 parse。
     */
    suspend fun resolveBookId(
        input: String,
        http: OkHttpClient,
    ): String? = withContext(Dispatchers.IO) {
        parseBookId(input) ?: resolveShortLinkFromTexts(listOf(input), http)
    }

    private fun resolveShortLinkFromTexts(
        texts: List<String>,
        http: OkHttpClient,
    ): String? {
        for (text in texts) {
            val url = FanqieConstants.URL_IN_TEXT.find(text.trim())?.value ?: continue
            if (!isShortLink(url)) continue
            val finalUrl = followRedirects(url, http) ?: continue
            parseBookId(finalUrl)?.let { return it }
        }
        return null
    }

    private fun followRedirects(url: String, http: OkHttpClient): String? {
        return try {
            val request = Request.Builder()
                .url(url)
                .header("User-Agent", USER_AGENT)
                .get()
                .build()
            http.newCall(request).execute().use { response ->
                response.request.url.toString()
            }
        } catch (_: Exception) {
            null
        }
    }

    private fun urlHost(url: String): String? {
        val afterScheme = when {
            url.startsWith("https://", ignoreCase = true) -> url.substring(8)
            url.startsWith("http://", ignoreCase = true) -> url.substring(7)
            else -> return null
        }
        val hostPort = afterScheme.substringBefore('/')
        return hostPort.substringBefore(':').lowercase()
    }

    private const val USER_AGENT =
        "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 " +
            "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    private const val ERROR_CANNOT_RESOLVE_BOOK_ID =
        "无法解析番茄 book_id（请使用 fanqienovel.com/page/… 或 changdunovel.com/t/… 分享链）"
}
