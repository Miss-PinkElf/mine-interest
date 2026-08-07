package com.mineinterest.media.core.link

import com.mineinterest.media.core.model.ParsedLink
import com.mineinterest.media.core.model.Platform

/**
 * 链接分类与批量拆分。
 *
 * - 单条：[parse]
 * - 批量：[parseBatch] 按行拆分；同行多 URL 再拆；UNKNOWN 跳过；platform+idHint+canonicalUrl 去重
 * - 短链解跳转不在本类（Provider 内完成）
 */
class LinkParser {

    fun parse(raw: String): ParsedLink {
        val text = raw.trim()
        val url = URL_REGEX.find(text)?.value
        val lower = text.lowercase()

        val isBili = BILI_HOST_MARKERS.any { lower.contains(it) } ||
            BV_REGEX.containsMatchIn(text) ||
            AV_REGEX.containsMatchIn(text)
        if (isBili) {
            val bv = BV_REGEX.find(text)?.value
            val av = AV_REGEX.find(text)?.groupValues?.getOrNull(1)
            return ParsedLink(
                platform = Platform.BILIBILI,
                rawText = text,
                canonicalUrl = url,
                idHint = bv ?: av?.let { "av$it" },
            )
        }

        // 含番茄/常读分享域（含 changdunovel.com/t/ 短链）；book_id 可为空，下载时再解跳
        val isFanqie = FANQIE_HOST_MARKERS.any { lower.contains(it) } ||
            BOOK_ID_QUERY.containsMatchIn(text) ||
            BOOK_ID_PATH.containsMatchIn(text) ||
            isFanqieShortShareUrl(url) ||
            (url == null && BOOK_ID_PLAIN.matches(text))
        if (isFanqie) {
            val id = BOOK_ID_QUERY.find(text)?.groupValues?.get(1)
                ?: BOOK_ID_PATH.find(text)?.groupValues?.get(1)
                ?: text.takeIf { BOOK_ID_PLAIN.matches(it) }
            return ParsedLink(
                platform = Platform.FANQIE,
                rawText = text,
                canonicalUrl = url,
                idHint = id,
            )
        }

        return ParsedLink(
            platform = Platform.UNKNOWN,
            rawText = text,
            canonicalUrl = url,
            idHint = null,
        )
    }

    /**
     * 手动批量解析：按行拆分；若单行含多个 URL 则再拆。
     * 跳过 UNKNOWN；按 platform + idHint + canonicalUrl 去重。
     */
    fun parseBatch(raw: String): BatchParseResult {
        val candidates = mutableListOf<String>()
        val skipped = mutableListOf<String>()

        raw.lines()
            .map { it.trim() }
            .filter { it.isNotEmpty() }
            .forEach { line ->
                val urls = URL_REGEX.findAll(line).map { it.value }.toList()
                when {
                    urls.size >= 2 -> candidates.addAll(urls)
                    urls.size == 1 -> candidates.add(line)
                    BOOK_ID_PLAIN.matches(line) -> candidates.add(line)
                    else -> skipped.add(line)
                }
            }

        val seen = linkedSetOf<String>()
        val items = mutableListOf<ParsedLink>()
        for (candidate in candidates) {
            val parsed = parse(candidate)
            if (parsed.platform == Platform.UNKNOWN) {
                skipped.add(candidate)
                continue
            }
            val key = listOf(
                parsed.platform.name,
                parsed.idHint.orEmpty(),
                parsed.canonicalUrl.orEmpty(),
            ).joinToString(DEDUPE_KEY_SEPARATOR)
            if (seen.add(key)) {
                items.add(parsed)
            }
        }
        return BatchParseResult(items = items, skippedLines = skipped)
    }

    /**
     * 番茄分享短链：`https://changdunovel.com/t/<token>/` 等。
     * 仅做形态识别；book_id 在 Provider 内跟跳转解析。
     */
    private fun isFanqieShortShareUrl(url: String?): Boolean {
        if (url.isNullOrBlank()) return false
        if (!FANQIE_SHORT_LINK_PATH.matches(url)) return false
        val host = urlHost(url) ?: return false
        return FANQIE_SHORT_LINK_HOSTS.any { host == it || host.endsWith(".$it") }
    }

    private fun urlHost(url: String): String? {
        val afterScheme = when {
            url.startsWith("https://", ignoreCase = true) -> url.substring(8)
            url.startsWith("http://", ignoreCase = true) -> url.substring(7)
            else -> return null
        }
        return afterScheme.substringBefore('/').substringBefore(':').lowercase()
    }

    companion object {
        private const val DEDUPE_KEY_SEPARATOR = "|"

        private val URL_REGEX = Regex("""https?://[^\s]+""")
        private val BILI_HOST_MARKERS = listOf("bilibili.com", "b23.tv", "bili2233.cn")
        /** 与 provider-fanqie 短链白名单对齐（core 不依赖 fanqie 模块） */
        private val FANQIE_HOST_MARKERS = listOf(
            "fanqienovel.com",
            "fqnovel.com",
            "novelfm.com",
            "changdunovel.com",
        )
        private val FANQIE_SHORT_LINK_HOSTS = listOf(
            "changdunovel.com",
            "fanqienovel.com",
            "fqnovel.com",
        )
        private val FANQIE_SHORT_LINK_PATH = Regex(
            """(?i)^https?://[^/\s]+/t/[A-Za-z0-9_-]+/?(?:[?#][^\s]*)?$""",
        )
        private val BV_REGEX = Regex("""BV[0-9A-Za-z]+""")
        private val AV_REGEX = Regex("""av(\d+)""", RegexOption.IGNORE_CASE)
        private val BOOK_ID_QUERY = Regex("""(?i)[?&](?:book_id|bookId)=(\d{5,})""")
        private val BOOK_ID_PATH = Regex("""/page/(\d{5,})""")
        private val BOOK_ID_PLAIN = Regex("""^\d{5,}$""")
    }
}
