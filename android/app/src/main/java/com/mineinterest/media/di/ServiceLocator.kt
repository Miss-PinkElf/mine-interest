package com.mineinterest.media.di

import android.app.Application
import com.mineinterest.media.bili.BiliDownloadProvider
import com.mineinterest.media.bili.BiliExporter
import com.mineinterest.media.bili.BiliHttp
import com.mineinterest.media.bili.BiliIdResolver
import com.mineinterest.media.bili.BiliStreamClient
import com.mineinterest.media.core.link.LinkParser
import com.mineinterest.media.core.provider.ProviderRegistry
import com.mineinterest.media.core.task.InMemoryTaskRepository
import com.mineinterest.media.core.task.TaskRepository
import com.mineinterest.media.core.task.TaskRunner
import com.mineinterest.media.fanqie.ConfigurableHttpContentFetcher
import com.mineinterest.media.fanqie.FanqieDownloadProvider
import com.mineinterest.media.fanqie.FanqieWebCatalogClient
import com.mineinterest.media.io.AppFileWriter
import com.mineinterest.media.settings.AppSettings
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import java.io.File

/**
 * 手动组装依赖（YAGNI：无 Hilt）。
 */
object ServiceLocator {

    lateinit var application: Application
        private set
    lateinit var settings: AppSettings
        private set
    lateinit var taskRepository: TaskRepository
        private set
    lateinit var taskRunner: TaskRunner
        private set
    lateinit var linkParser: LinkParser
        private set
    lateinit var appScope: CoroutineScope
        private set

    private var initialized = false

    fun init(app: Application) {
        if (initialized) return
        application = app
        appScope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
        settings = AppSettings(app)
        linkParser = LinkParser()
        taskRepository = InMemoryTaskRepository()

        val http = BiliHttp.createClient()
        val fileWriter = AppFileWriter(app)
        val tempDir = File(app.cacheDir, TEMP_DIR_NAME)
        val fanqieCache = File(app.filesDir, FANQIE_CACHE_DIR)

        val biliProvider = BiliDownloadProvider(
            resolver = BiliIdResolver(http),
            streams = BiliStreamClient(http),
            exporter = BiliExporter(
                tempDir = tempDir,
                fileWriter = fileWriter,
                http = http,
            ),
        )

        // 端点可在设置中更新；每次下载时 ContentFetcher 使用当前 settings 值需可刷新
        val fanqieProvider = FanqieDownloadProvider(
            catalogClient = FanqieWebCatalogClient(http),
            contentFetcher = SettingsBackedContentFetcher(settings, http),
            cacheRootDir = fanqieCache,
            fileWriter = fileWriter,
        )

        val registry = ProviderRegistry(listOf(biliProvider, fanqieProvider))
        taskRunner = TaskRunner(
            parser = linkParser,
            registry = registry,
            repo = taskRepository,
            scope = CoroutineScope(SupervisorJob() + Dispatchers.Default),
        )
        initialized = true
    }

    private const val TEMP_DIR_NAME = "media_temp"
    private const val FANQIE_CACHE_DIR = "fanqie_cache"
}

/**
 * 每次请求时读取最新端点配置，避免必须重启 App。
 */
private class SettingsBackedContentFetcher(
    private val settings: AppSettings,
    private val http: okhttp3.OkHttpClient,
) : com.mineinterest.media.fanqie.FanqieContentFetcher {
    override suspend fun fetchChapterContent(itemId: String): String {
        val fetcher = ConfigurableHttpContentFetcher(
            http = http,
            endpointTemplates = settings.getFanqieEndpoints(),
        )
        return fetcher.fetchChapterContent(itemId)
    }
}
