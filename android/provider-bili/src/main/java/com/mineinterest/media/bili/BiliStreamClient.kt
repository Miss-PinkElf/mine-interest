package com.mineinterest.media.bili

import com.mineinterest.media.core.CoreMediaFormats
import com.mineinterest.media.core.model.BiliTaskOptions
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient

/**
 * B站播放信息与流地址获取（单点实现，接口漂移时只改本类）。
 *
 * 使用公开接口：
 * - view: `api.bilibili.com/x/web-interface/view`
 * - playurl: `api.bilibili.com/x/player/playurl`（fnval=16 拿 DASH）
 * - 字幕: `api.bilibili.com/x/player/v2`
 *
 * **风险：** 非官方稳定 API，可能需登录/风控；个人自用 MVP 接受失败与后续修补。
 */
class BiliStreamClient(
    private val http: OkHttpClient = BiliHttp.createClient(),
) {

    suspend fun fetchSelection(
        bvid: String,
        options: BiliTaskOptions,
    ): Result<BiliPlaySelection> = withContext(Dispatchers.IO) {
        runCatching {
            val viewJson = BiliHttp.get(http, "$VIEW_API?bvid=$bvid")
            val code = BiliJson.intField(viewJson, "code")
            if (code != null && code != 0) {
                error(BiliJson.stringField(viewJson, "message") ?: "获取视频信息失败 code=$code")
            }
            val title = BiliJson.stringField(viewJson, "title") ?: bvid
            val cid = BiliJson.longField(viewJson, "cid")
                ?: error("无法解析 cid，视频可能需登录或接口变更")

            val qn = qualityToQn(options.videoQualityHeight)
            val playUrl =
                "$PLAYURL_API?bvid=$bvid&cid=$cid&qn=$qn&fnval=$FNVAL_DASH&fourk=1&fnver=0"
            val playJson = BiliHttp.get(http, playUrl)
            val playCode = BiliJson.intField(playJson, "code")
            if (playCode != null && playCode != 0) {
                error(BiliJson.stringField(playJson, "message") ?: "获取播放地址失败 code=$playCode")
            }

            val dashBlock = extractObjectBlock(playJson, "dash")
            val (videoUrl, audioUrl) = if (dashBlock != null) {
                selectDashStreams(dashBlock, options)
            } else {
                val durl = BiliJson.allStringFields(playJson, "url").firstOrNull()
                durl to null
            }

            if (videoUrl.isNullOrBlank() && audioUrl.isNullOrBlank()) {
                error("未找到可用媒体流，可能需要登录或清晰度受限")
            }

            var subtitleUrl: String? = null
            var hint: String? = null
            if (options.withSubtitle) {
                subtitleUrl = fetchSubtitleUrl(bvid, cid)
                if (subtitleUrl == null) {
                    hint = "未找到字幕"
                }
            }

            if (options.format == CoreMediaFormats.MP3 && audioUrl == null && videoUrl != null) {
                hint = listOfNotNull(hint, "无独立音频轨，将尝试从视频导出").joinToString("；")
            }

            BiliPlaySelection(
                bvid = bvid,
                title = title,
                cid = cid,
                videoUrl = videoUrl,
                audioUrl = audioUrl,
                subtitleUrl = subtitleUrl,
                messageHint = hint,
            )
        }
    }

    private fun selectDashStreams(
        dashJson: String,
        options: BiliTaskOptions,
    ): Pair<String?, String?> {
        val videoUrls = extractStreamBaseUrls(extractArrayBlock(dashJson, "video") ?: "")
        val audioUrls = extractStreamBaseUrls(extractArrayBlock(dashJson, "audio") ?: "")
        val heights = BiliJson.allIntFields(dashJson, "height")

        val videoUrl = when {
            options.format == CoreMediaFormats.MP3 -> null
            videoUrls.isEmpty() -> null
            else -> pickClosestVideo(videoUrls, heights, options.videoQualityHeight)
        }
        val audioUrl = audioUrls.lastOrNull() // 通常码率升序，取较高

        return videoUrl to audioUrl
    }

    private fun pickClosestVideo(
        urls: List<String>,
        heights: List<Int>,
        targetHeight: Int,
    ): String {
        if (heights.isEmpty() || heights.size != urls.size) {
            return urls.last()
        }
        val indexed = heights.indices.minByOrNull { idx ->
            kotlin.math.abs(heights[idx] - targetHeight)
        } ?: (urls.size - 1)
        return urls[indexed]
    }

    private fun extractStreamBaseUrls(arrayJson: String): List<String> {
        if (arrayJson.isBlank()) return emptyList()
        // baseUrl 优先，其次 base_url
        val baseUrls = BiliJson.allStringFields(arrayJson, "baseUrl")
        if (baseUrls.isNotEmpty()) return baseUrls
        return BiliJson.allStringFields(arrayJson, "base_url")
    }

    private fun fetchSubtitleUrl(bvid: String, cid: Long): String? {
        return runCatching {
            val json = BiliHttp.get(http, "$PLAYER_V2_API?bvid=$bvid&cid=$cid")
            // subtitle.subtitles[].subtitle_url
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

    /**
     * 粗提取 `"key":{...}` 对象块（括号匹配）。
     */
    private fun extractObjectBlock(json: String, key: String): String? {
        val startMarker = Regex(""""$key"\s*:\s*\{""").find(json) ?: return null
        val start = startMarker.range.last // points to '{'
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
                    if (depth == 0) {
                        return text.substring(start, i + 1)
                    }
                }
            }
        }
        return null
    }

    companion object {
        private const val VIEW_API = "https://api.bilibili.com/x/web-interface/view"
        private const val PLAYURL_API = "https://api.bilibili.com/x/player/playurl"
        private const val PLAYER_V2_API = "https://api.bilibili.com/x/player/v2"
        private const val FNVAL_DASH = 16
        private const val QN_360 = 16
        private const val QN_480 = 32
        private const val QN_720 = 64
        private const val QN_1080 = 80
    }
}
