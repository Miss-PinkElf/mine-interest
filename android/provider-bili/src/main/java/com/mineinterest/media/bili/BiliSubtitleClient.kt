package com.mineinterest.media.bili

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import java.io.File

/**
 * 下载字幕并尽量转为 SRT。
 */
class BiliSubtitleClient(
    private val http: OkHttpClient = BiliHttp.createClient(),
) {

    suspend fun downloadAsSrt(
        subtitleUrl: String,
        destFile: File,
    ): Result<File> = withContext(Dispatchers.IO) {
        runCatching {
            val body = BiliHttp.apiGet(http, subtitleUrl)
            val srt = if (body.contains("\"body\"") || body.contains("\"content\"")) {
                jsonSubtitleToSrt(body)
            } else {
                body
            }
            destFile.parentFile?.mkdirs()
            destFile.writeText(srt, Charsets.UTF_8)
            destFile
        }
    }

    /**
     * B站 JSON 字幕粗转 SRT（body 数组含 from/to/content）。
     */
    internal fun jsonSubtitleToSrt(json: String): String {
        val contents = BiliJson.allStringFields(json, "content")
        val froms = Regex(""""from"\s*:\s*([0-9.]+)""")
            .findAll(json)
            .map { it.groupValues[1].toDoubleOrNull() ?: 0.0 }
            .toList()
        val tos = Regex(""""to"\s*:\s*([0-9.]+)""")
            .findAll(json)
            .map { it.groupValues[1].toDoubleOrNull() ?: 0.0 }
            .toList()
        if (contents.isEmpty()) return json

        val sb = StringBuilder()
        contents.forEachIndexed { index, content ->
            val start = froms.getOrNull(index) ?: 0.0
            val end = tos.getOrNull(index) ?: (start + 2.0)
            sb.append(index + 1).append('\n')
            sb.append(formatSrtTime(start)).append(" --> ").append(formatSrtTime(end)).append('\n')
            sb.append(content).append("\n\n")
        }
        return sb.toString().trim() + "\n"
    }

    private fun formatSrtTime(seconds: Double): String {
        val totalMs = (seconds * 1000).toLong().coerceAtLeast(0)
        val h = totalMs / 3_600_000
        val m = (totalMs % 3_600_000) / 60_000
        val s = (totalMs % 60_000) / 1000
        val ms = totalMs % 1000
        return "%02d:%02d:%02d,%03d".format(h, m, s, ms)
    }
}
