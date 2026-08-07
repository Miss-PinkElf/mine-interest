package com.mineinterest.media.bili

import com.mineinterest.media.core.CoreMediaFormats
import com.mineinterest.media.core.model.BiliTaskOptions
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient

/**
 * B站播放信息与流地址获取（单点实现）。
 *
 * 流程：
 * 1. view 拿 title/cid
 * 2. WBI 签名后请求 wbi/playurl（失败则回退普通 playurl）
 * 3. 解析 dash baseUrl + backupUrl，或 durl
 *
 * **风险：** 非官方 API；高清/部分稿件仍可能需登录 Cookie。
 */
class BiliStreamClient(
    private val http: OkHttpClient = BiliHttp.createClient(),
    private val wbi: BiliWbiSigner = BiliWbiSigner(http),
) {

    suspend fun fetchSelection(
        bvid: String,
        options: BiliTaskOptions,
    ): Result<BiliPlaySelection> = withContext(Dispatchers.IO) {
        runCatching {
            val viewJson = BiliHttp.apiGet(http, "$VIEW_API?bvid=$bvid")
            val code = BiliJson.intField(viewJson, "code")
            if (code != null && code != 0) {
                error(
                    "获取视频信息失败 code=$code " +
                        (BiliJson.stringField(viewJson, "message") ?: ""),
                )
            }
            val title = BiliJson.stringField(viewJson, "title") ?: bvid
            val cid = BiliJson.longField(viewJson, "cid")
                ?: error("无法解析 cid（视频可能需登录或接口变更）")

            val qn = qualityToQn(options.videoQualityHeight)
            val playJson = fetchPlayJson(bvid, cid, qn)
            val playCode = BiliJson.intField(playJson, "code")
            if (playCode != null && playCode != 0) {
                error(
                    "获取播放地址失败 code=$playCode " +
                        (BiliJson.stringField(playJson, "message") ?: "（可能需登录/地区限制）"),
                )
            }

            val dashBlock = extractObjectBlock(playJson, "dash")
            val (videoUrls, audioUrls) = if (dashBlock != null) {
                selectDashStreams(dashBlock, options)
            } else {
                val durl = BiliJson.allStringFields(playJson, "url")
                durl to emptyList()
            }

            if (videoUrls.isEmpty() && audioUrls.isEmpty()) {
                error("未找到可用媒体流（可能需要登录 SESSDATA 或清晰度受限）")
            }

            var subtitleUrl: String? = null
            var hint: String? = null
            if (options.withSubtitle) {
                subtitleUrl = fetchSubtitleUrl(bvid, cid)
                if (subtitleUrl == null) {
                    hint = "未找到字幕"
                }
            }

            if (options.format == CoreMediaFormats.MP3 && audioUrls.isEmpty() && videoUrls.isNotEmpty()) {
                hint = listOfNotNull(hint, "无独立音频轨，将尝试从视频轨导出").joinToString("；")
            }

            BiliPlaySelection(
                bvid = bvid,
                title = title,
                cid = cid,
                videoUrls = videoUrls,
                audioUrls = audioUrls,
                subtitleUrl = subtitleUrl,
                messageHint = hint,
            )
        }
    }

    private fun fetchPlayJson(bvid: String, cid: Long, qn: Int): String {
        val baseParams = mapOf(
            "bvid" to bvid,
            "cid" to cid.toString(),
            "qn" to qn.toString(),
            "fnval" to FNVAL_DASH.toString(),
            "fnver" to "0",
            "fourk" to "1",
            "platform" to "html5",
            "high_quality" to "1",
        )
        // 优先 WBI 签名接口
        try {
            val signed = wbi.signUrl(WBI_PLAYURL_API, baseParams)
            val body = BiliHttp.apiGet(http, signed)
            val code = BiliJson.intField(body, "code")
            if (code == null || code == 0) return body
            // 签名过期等，刷新一次
            if (code == -352 || code == -403) {
                wbi.invalidate()
                val retry = wbi.signUrl(WBI_PLAYURL_API, baseParams)
                val retryBody = BiliHttp.apiGet(http, retry)
                val retryCode = BiliJson.intField(retryBody, "code")
                if (retryCode == null || retryCode == 0) return retryBody
            }
        } catch (_: Exception) {
            // fall through to legacy
        }

        val legacy = buildString {
            append(LEGACY_PLAYURL_API)
            append("?bvid=").append(bvid)
            append("&cid=").append(cid)
            append("&qn=").append(qn)
            append("&fnval=").append(FNVAL_DASH)
            append("&fnver=0&fourk=1&platform=html5&high_quality=1")
        }
        return BiliHttp.apiGet(http, legacy)
    }

    private fun selectDashStreams(
        dashJson: String,
        options: BiliTaskOptions,
    ): Pair<List<String>, List<String>> {
        val videoBlock = extractArrayBlock(dashJson, "video").orEmpty()
        val audioBlock = extractArrayBlock(dashJson, "audio").orEmpty()
        val videoUrls = extractStreamUrls(videoBlock)
        val audioUrls = extractStreamUrls(audioBlock)
        val heights = BiliJson.allIntFields(videoBlock, "height")

        val selectedVideo = when {
            options.format == CoreMediaFormats.MP3 -> emptyList()
            videoUrls.isEmpty() -> emptyList()
            else -> pickClosestVideoUrls(videoUrls, heights, options.videoQualityHeight)
        }
        // 音频取码率较高的若干候选（列表末尾通常更高）
        val selectedAudio = if (audioUrls.isEmpty()) {
            emptyList()
        } else {
            audioUrls.takeLast(3).reversed()
        }
        return selectedVideo to selectedAudio
    }

    /**
     * 返回主选清晰度的 baseUrl + 其 backup，再附带相邻清晰度作回退。
     */
    private fun pickClosestVideoUrls(
        urls: List<String>,
        heights: List<Int>,
        targetHeight: Int,
    ): List<String> {
        if (urls.isEmpty()) return emptyList()
        if (heights.isEmpty() || heights.size != urls.size) {
            return urls.takeLast(2).reversed()
        }
        val bestIdx = heights.indices.minByOrNull { idx ->
            kotlin.math.abs(heights[idx] - targetHeight)
        } ?: (urls.size - 1)
        val ordered = linkedSetOf<String>()
        ordered.add(urls[bestIdx])
        // 邻近清晰度
        if (bestIdx + 1 < urls.size) ordered.add(urls[bestIdx + 1])
        if (bestIdx - 1 >= 0) ordered.add(urls[bestIdx - 1])
        urls.lastOrNull()?.let { ordered.add(it) }
        return ordered.toList()
    }

    private fun extractStreamUrls(arrayJson: String): List<String> {
        if (arrayJson.isBlank()) return emptyList()
        val base = BiliJson.allStringFields(arrayJson, "baseUrl")
            .ifEmpty { BiliJson.allStringFields(arrayJson, "base_url") }
        val backup = BiliJson.allStringFields(arrayJson, "backupUrl")
            .ifEmpty { BiliJson.allStringFields(arrayJson, "backup_url") }
        // 保持「每个 base 后跟其 backup 段」的近似顺序：先全部 base，再 backup
        return (base + backup).distinct().filter { it.startsWith("http") }
    }

    private fun fetchSubtitleUrl(bvid: String, cid: Long): String? {
        return runCatching {
            val json = BiliHttp.apiGet(http, "$PLAYER_V2_API?bvid=$bvid&cid=$cid")
            val urls = BiliJson.allStringFields(json, "subtitle_url")
            val first = urls.firstOrNull() ?: return null
            if (first.startsWith("//")) "https:$first" else first
        }.getOrNull()
    }

    private fun qualityToQn(height: Int): Int = when {
        height >= 1080 -> QN_1080
        height >= 720 -> QN_720
        height >= 480 -> QN_480
        else -> QN_360
    }

    private fun extractObjectBlock(json: String, key: String): String? {
        val startMarker = Regex(""""$key"\s*:\s*\{""").find(json) ?: return null
        val start = startMarker.range.last
        return sliceBalanced(json, start, '{', '}')
    }

    private fun extractArrayBlock(json: String, key: String): String? {
        val startMarker = Regex(""""$key"\s*:\s*\[""").find(json) ?: return null
        val start = startMarker.range.last
        return sliceBalanced(json, start, '[', ']')
    }

    private fun sliceBalanced(
        text: String,
        start: Int,
        open: Char,
        close: Char,
    ): String? {
        var depth = 0
        var inString = false
        var escape = false
        for (i in start until text.length) {
            val c = text[i]
            if (inString) {
                when {
                    escape -> escape = false
                    c == '\\' -> escape = true
                    c == '"' -> inString = false
                }
                continue
            }
            when (c) {
                '"' -> inString = true
                open -> depth++
                close -> {
                    depth--
                    if (depth == 0) return text.substring(start, i + 1)
                }
            }
        }
        return null
    }

    companion object {
        private const val VIEW_API = "https://api.bilibili.com/x/web-interface/view"
        private const val WBI_PLAYURL_API = "https://api.bilibili.com/x/player/wbi/playurl"
        private const val LEGACY_PLAYURL_API = "https://api.bilibili.com/x/player/playurl"
        private const val PLAYER_V2_API = "https://api.bilibili.com/x/player/v2"
        /** dash + 部分额外能力 */
        private const val FNVAL_DASH = 16
        private const val QN_360 = 16
        private const val QN_480 = 32
        private const val QN_720 = 64
        private const val QN_1080 = 80
    }
}
