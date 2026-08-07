package com.mineinterest.media.fanqie

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request

/**
 * 个人配置的 HTTP 正文源。
 *
 * [endpointTemplates] 来自设置页多行文本，支持 `{item_id}` 占位符。
 * **禁止**在仓库硬编码第三方闭源 token。
 */
class ConfigurableHttpContentFetcher(
    private val http: OkHttpClient,
    private val endpointTemplates: List<String>,
) : FanqieContentFetcher {

    override suspend fun fetchChapterContent(itemId: String): String = withContext(Dispatchers.IO) {
        require(endpointTemplates.isNotEmpty()) { ERROR_ENDPOINTS_EMPTY }

        var lastError: Exception? = null
        for (template in endpointTemplates) {
            try {
                val url = template.replace(FanqieConstants.ITEM_ID_PLACEHOLDER, itemId)
                val body = httpGet(url)
                return@withContext extractContent(body)
            } catch (e: Exception) {
                lastError = e
            }
        }
        throw lastError ?: IllegalStateException(ERROR_CONTENT_FAILED)
    }

    private fun httpGet(url: String): String {
        val request = Request.Builder().url(url).get().build()
        http.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                error("HTTP ${response.code}")
            }
            return response.body?.string().orEmpty()
        }
    }

    /**
     * 兼容常见 JSON 字段 `content`（简单字符串提取，避免依赖 org.json 便于单测）。
     * 非 JSON 时原样返回。
     */
    internal fun extractContent(raw: String): String {
        val trimmed = raw.trim()
        if (trimmed.isEmpty()) {
            error(ERROR_EMPTY_BODY)
        }
        if (!trimmed.startsWith("{") && !trimmed.startsWith("[")) {
            return trimmed
        }
        val match = CONTENT_FIELD_REGEX.find(trimmed)
        if (match != null) {
            return unescapeJsonString(match.groupValues[1])
        }
        return trimmed
    }

    private fun unescapeJsonString(value: String): String {
        return value
            .replace("\\n", "\n")
            .replace("\\r", "\r")
            .replace("\\t", "\t")
            .replace("\\\"", "\"")
            .replace("\\\\", "\\")
    }

    companion object {
        private val CONTENT_FIELD_REGEX =
            Regex(""""content"\s*:\s*"((?:\\.|[^"\\])*)"""")
        private const val ERROR_ENDPOINTS_EMPTY =
            "未配置番茄正文 API 端点。请在设置中填写个人可用端点（含 {item_id}）。"
        private const val ERROR_CONTENT_FAILED = "正文获取失败"
        private const val ERROR_EMPTY_BODY = "正文响应为空"
    }
}
