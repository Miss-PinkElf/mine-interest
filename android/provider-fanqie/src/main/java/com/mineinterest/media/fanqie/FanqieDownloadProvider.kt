package com.mineinterest.media.fanqie

import com.mineinterest.media.core.model.BiliTaskOptions
import com.mineinterest.media.core.model.FanqieTaskOptions
import com.mineinterest.media.core.model.ParsedLink
import com.mineinterest.media.core.model.Platform
import com.mineinterest.media.core.path.SavePathPolicy
import com.mineinterest.media.core.provider.DownloadProvider
import com.mineinterest.media.core.provider.ProgressCallback
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import java.io.File
import java.util.concurrent.atomic.AtomicInteger

/**
 * 番茄 TXT 下载主流程：
 * book_id（含 changdunovel /t/ 短链解跳）→ 目录 → 分章正文（可配置）→ 断点 → finalize TXT
 */
class FanqieDownloadProvider(
    private val catalogClient: FanqieCatalogClient,
    private val contentFetcher: FanqieContentFetcher,
    private val cacheRootDir: File,
    private val fileWriter: FanqieFileWriter,
    private val http: OkHttpClient,
    private val concurrency: Int = FanqieConstants.DEFAULT_CONCURRENCY,
) : DownloadProvider {

    override val platform: Platform = Platform.FANQIE

    override suspend fun download(
        parsed: ParsedLink,
        taskId: String,
        biliOptions: BiliTaskOptions?,
        fanqieOptions: FanqieTaskOptions?,
        onProgress: ProgressCallback,
    ): Result<String> = runCatching {
        val options = fanqieOptions ?: error("缺少番茄选项")
        onProgress.onProgress(3, "解析 book_id")
        val bookId = FanqieBookIdResolver.resolveFromParsed(parsed, http)

        onProgress.onProgress(8, "获取书信息")
        val meta = catalogClient.fetchMeta(bookId)
        onProgress.onProgress(15, "获取目录")
        val chapters = catalogClient.fetchChapters(bookId)
        if (chapters.isEmpty()) {
            error("章节列表为空")
        }

        val store = FanqieChapterStore(File(cacheRootDir, bookId))
        val downloaded = if (options.resume) store.loadDownloadedIds() else emptySet()
        val pending = chapters.filter { it.itemId !in downloaded }

        onProgress.onProgress(20, "下载章节 ${pending.size}/${chapters.size}")
        downloadChapters(pending, store, onProgress)

        onProgress.onProgress(90, "合并 TXT")
        val ordered = store.listOrderedChapters(chapters)
        if (ordered.isEmpty()) {
            error("无可用章节正文，请检查正文 API 端点配置")
        }
        val txt = FanqieTxtFinalizer.merge(ordered)
        val fileName = SavePathPolicy.sanitizeFileName(meta.title) + EXT_TXT
        withContext(Dispatchers.IO) {
            fileWriter.writeText(options.saveDirUri, fileName, txt)
        }
    }

    private suspend fun downloadChapters(
        pending: List<com.mineinterest.media.fanqie.model.FanqieChapterRef>,
        store: FanqieChapterStore,
        onProgress: ProgressCallback,
    ) {
        if (pending.isEmpty()) return
        val semaphore = Semaphore(concurrency.coerceAtLeast(1))
        val done = AtomicInteger(0)
        val total = pending.size
        coroutineScope {
            pending.map { chapter ->
                async(Dispatchers.IO) {
                    semaphore.withPermit {
                        val body = contentFetcher.fetchChapterContent(chapter.itemId)
                        store.writeChapterText(chapter.itemId, chapter.title, body)
                        val finished = done.incrementAndGet()
                        val percent = 20 + ((finished * 65) / total)
                        onProgress.onProgress(
                            percent.coerceIn(20, 85),
                            "章节 $finished/$total ${chapter.title}",
                        )
                    }
                }
            }.awaitAll()
        }
    }

    companion object {
        private const val EXT_TXT = ".txt"
    }
}
