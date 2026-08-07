package com.mineinterest.media.core.model

/**
 * 番茄 TXT 下载选项。
 *
 * @param saveDirUri SAF tree URI 或绝对路径字符串
 * @param resume 是否断点续传（跳过已下载章节）
 */
data class FanqieTaskOptions(
    val saveDirUri: String,
    val resume: Boolean = true,
)
