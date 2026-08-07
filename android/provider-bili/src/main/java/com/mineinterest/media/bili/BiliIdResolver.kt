package com.mineinterest.media.bili

import com.mineinterest.media.core.model.ParsedLink
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request

/**
 * 从 [ParsedLink] 解析 bvid；短链在本类内跟随重定向。
 */
class BiliIdResolver(
    private val http: OkHttpClient = defaultClient(),
) {

    /**
     * 同步抽取：优先 idHint 中的 BV，其次从 URL/文本正则提取（不访问网络）。
     */
    fun extractFromParsed(parsed: ParsedLink): String? {
        val hint = parsed.idHint
        if (hint != null && hint.startsWith(BV_PREFIX)) {
            return hint
        }
        if (hint != null && hint.startsWith(AV_PREFIX, ignoreCase = true)) {
            return null // av 需后续接口转 bvid，MVP 先要求 BV 或短链解跳
        }
        return extractBvidFromText(parsed.canonicalUrl.orEmpty() + " " + parsed.rawText)
    }

    /**
     * 解析到 bvid：含 b23.tv 时发起请求跟随重定向。
     */
    suspend fun resolveToBvid(parsed: ParsedLink): String = withContext(Dispatchers.IO) {
        extractFromParsed(parsed)?.let { return@withContext it }

        val url = parsed.canonicalUrl
            ?: error(ERROR_NO_URL)
        if (!url.contains(BiliConstants.SHORT_LINK_HOST)) {
            return@withContext extractBvidFromText(url)
                ?: error(ERROR_NO_BVID)
        }

        val request = Request.Builder().url(url).get().build()
        http.newCall(request).execute().use { response ->
            val finalUrl = response.request.url.toString()
            extractBvidFromText(finalUrl) ?: error(ERROR_SHORT_LINK_NO_BVID)
        }
    }

    fun extractBvidFromText(text: String): String? =
        BiliConstants.BV_REGEX.find(text)?.value

    companion object {
        private const val BV_PREFIX = "BV"
        private const val AV_PREFIX = "av"
        private const val ERROR_NO_URL = "无 URL，无法解析 bvid"
        private const val ERROR_NO_BVID = "无法解析 bvid"
        private const val ERROR_SHORT_LINK_NO_BVID = "短链未解析到 BV"

        fun defaultClient(): OkHttpClient =
            OkHttpClient.Builder()
                .followRedirects(true)
                .followSslRedirects(true)
                .build()
    }
}
