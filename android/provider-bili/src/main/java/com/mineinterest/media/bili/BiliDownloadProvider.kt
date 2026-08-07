package com.mineinterest.media.bili

import com.mineinterest.media.core.model.BiliTaskOptions
import com.mineinterest.media.core.model.FanqieTaskOptions
import com.mineinterest.media.core.model.ParsedLink
import com.mineinterest.media.core.model.Platform
import com.mineinterest.media.core.provider.DownloadProvider
import com.mineinterest.media.core.provider.ProgressCallback

/**
 * B站一体式下载导出 Provider。
 *
 * 接口漂移时优先修改 [BiliStreamClient]，保持本类编排稳定。
 * 长期可替换为 yt-dlp 引擎而不改 [DownloadProvider] 形状。
 */
class BiliDownloadProvider(
    private val resolver: BiliIdResolver,
    private val streams: BiliStreamClient,
    private val exporter: BiliExporter,
) : DownloadProvider {

    override val platform: Platform = Platform.BILIBILI

    override suspend fun download(
        parsed: ParsedLink,
        taskId: String,
        biliOptions: BiliTaskOptions?,
        fanqieOptions: FanqieTaskOptions?,
        onProgress: ProgressCallback,
    ): Result<String> = runCatching {
        val options = biliOptions ?: error("缺少 B站选项")
        onProgress.onProgress(5, "解析视频 ID")
        val bvid = resolver.resolveToBvid(parsed)
        onProgress.onProgress(15, "获取媒体流")
        val selection = streams.fetchSelection(bvid, options).getOrThrow()
        onProgress.onProgress(30, "开始导出")
        exporter.export(selection, options, onProgress).getOrThrow()
    }
}
