package com.mineinterest.media.core.provider

import com.mineinterest.media.core.model.BiliTaskOptions
import com.mineinterest.media.core.model.FanqieTaskOptions
import com.mineinterest.media.core.model.ParsedLink
import com.mineinterest.media.core.model.Platform

/**
 * 可替换的下载导出 Provider 接口。
 * 成功时 [Result] 值为输出文件路径字符串。
 */
interface DownloadProvider {
    val platform: Platform

    suspend fun download(
        parsed: ParsedLink,
        taskId: String,
        biliOptions: BiliTaskOptions?,
        fanqieOptions: FanqieTaskOptions?,
        onProgress: ProgressCallback,
    ): Result<String>
}
