package com.mineinterest.media.bili

import com.mineinterest.media.core.CoreMediaFormats
import com.mineinterest.media.core.model.BiliTaskOptions
import com.mineinterest.media.core.path.SavePathPolicy
import com.mineinterest.media.core.provider.ProgressCallback
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File
import java.io.FileOutputStream

/**
 * 下载媒体流并导出到用户目录。
 *
 * - 多候选 URL 依次尝试（base + backup），缓解单链 CDN 403
 * - CDN 请求带 www 视频页 Referer + buvid3
 */
class BiliExporter(
    private val tempDir: File,
    private val fileWriter: MediaFileWriter,
    private val http: OkHttpClient = BiliHttp.createClient(),
    private val subtitleClient: BiliSubtitleClient = BiliSubtitleClient(http),
) {

    suspend fun export(
        selection: BiliPlaySelection,
        options: BiliTaskOptions,
        onProgress: ProgressCallback,
    ): Result<String> = withContext(Dispatchers.IO) {
        runCatching {
            tempDir.mkdirs()
            val safeTitle = SavePathPolicy.sanitizeFileName(selection.title)
            val baseName = "$safeTitle-${selection.bvid}"

            val isAudioOnly = options.format == CoreMediaFormats.MP3
            val primaryCandidates = if (isAudioOnly) {
                selection.audioUrls.ifEmpty { selection.videoUrls }
            } else {
                selection.videoUrls.ifEmpty { selection.audioUrls }
            }
            if (primaryCandidates.isEmpty()) {
                error("无可用音频/视频流")
            }

            onProgress.onProgress(35, "下载媒体（${primaryCandidates.size} 个候选）")
            val sampleUrl = primaryCandidates.first()
            val ext = when {
                isAudioOnly -> EXT_M4A
                sampleUrl.contains(".m4s") -> EXT_MP4
                sampleUrl.contains(".flv") -> EXT_FLV
                else -> EXT_MP4
            }
            val tempMedia = File(tempDir, "$baseName-primary$ext")
            downloadWithFallback(
                urls = primaryCandidates,
                dest = tempMedia,
                bvid = selection.bvid,
                stageLabel = "主媒体",
            ) { percent ->
                val mapped = 35 + (percent * 0.45).toInt()
                onProgress.onProgress(mapped.coerceIn(35, 80), "下载中 $percent%")
            }

            if (!isAudioOnly &&
                selection.audioUrls.isNotEmpty() &&
                selection.videoUrls.isNotEmpty()
            ) {
                onProgress.onProgress(82, "下载音轨旁路")
                val tempAudio = File(tempDir, "$baseName-audio$EXT_M4A")
                runCatching {
                    downloadWithFallback(
                        urls = selection.audioUrls,
                        dest = tempAudio,
                        bvid = selection.bvid,
                        stageLabel = "音轨",
                    ) {}
                    fileWriter.writeFile(
                        options.saveDirUri,
                        "$baseName-audio$EXT_M4A",
                        tempAudio,
                    )
                }
            }

            var finalName = "$baseName$ext"
            if (isAudioOnly && options.format == CoreMediaFormats.MP3) {
                finalName = "$baseName$EXT_M4A"
            }

            onProgress.onProgress(88, "写入保存目录")
            val outputPath = fileWriter.writeFile(options.saveDirUri, finalName, tempMedia)

            if (options.withSubtitle && !selection.subtitleUrl.isNullOrBlank()) {
                onProgress.onProgress(92, "下载字幕")
                val tempSrt = File(tempDir, "$baseName$EXT_SRT")
                subtitleClient.downloadAsSrt(selection.subtitleUrl, tempSrt).onSuccess {
                    fileWriter.writeFile(options.saveDirUri, "$baseName$EXT_SRT", it)
                }
            }

            val hint = buildString {
                if (isAudioOnly) append("音频已导出为 m4a（mp3 选项降级）")
                selection.messageHint?.let {
                    if (isNotEmpty()) append("；")
                    append(it)
                }
            }
            if (hint.isNotEmpty()) {
                onProgress.onProgress(98, hint)
            }
            outputPath
        }
    }

    private fun downloadWithFallback(
        urls: List<String>,
        dest: File,
        bvid: String,
        stageLabel: String,
        onPercent: (Int) -> Unit,
    ) {
        var lastError: Exception? = null
        for (url in urls) {
            try {
                downloadToFile(url, dest, bvid, onPercent)
                return
            } catch (e: Exception) {
                lastError = e
            }
        }
        val detail = lastError?.message ?: "未知错误"
        error("$stageLabel 下载失败（已试 ${urls.size} 个地址）: $detail")
    }

    private fun downloadToFile(
        url: String,
        dest: File,
        bvid: String,
        onPercent: (Int) -> Unit,
    ) {
        val request = Request.Builder()
            .url(url)
            .headers(BiliHttp.mediaHeaders(bvid))
            .get()
            .build()
        http.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                error(
                    "CDN HTTP ${response.code} ${BiliHttp.shortUrl(url)}",
                )
            }
            val body = response.body ?: error("空响应体")
            val total = body.contentLength()
            dest.parentFile?.mkdirs()
            FileOutputStream(dest).use { out ->
                val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
                var readTotal = 0L
                var lastPercent = -1
                body.byteStream().use { input ->
                    while (true) {
                        val n = input.read(buffer)
                        if (n <= 0) break
                        out.write(buffer, 0, n)
                        readTotal += n
                        if (total > 0) {
                            val percent = ((readTotal * 100) / total).toInt().coerceIn(0, 100)
                            if (percent != lastPercent) {
                                lastPercent = percent
                                onPercent(percent)
                            }
                        }
                    }
                }
            }
        }
        onPercent(100)
    }

    companion object {
        private const val EXT_MP4 = ".mp4"
        private const val EXT_M4A = ".m4a"
        private const val EXT_FLV = ".flv"
        private const val EXT_SRT = ".srt"
        private const val DEFAULT_BUFFER_SIZE = 64 * 1024
    }
}
