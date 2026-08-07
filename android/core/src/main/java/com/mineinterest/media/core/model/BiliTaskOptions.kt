package com.mineinterest.media.core.model

import com.mineinterest.media.core.CoreMediaFormats

/**
 * B站下载导出选项。
 *
 * @param saveDirUri SAF tree URI 或绝对路径字符串
 */
data class BiliTaskOptions(
    val format: String = CoreMediaFormats.MP3,
    val audioBitrateKbps: Int = DEFAULT_AUDIO_BITRATE_KBPS,
    val videoQualityHeight: Int = DEFAULT_VIDEO_QUALITY_HEIGHT,
    val withSubtitle: Boolean = false,
    val saveDirUri: String,
) {
    companion object {
        const val DEFAULT_AUDIO_BITRATE_KBPS = 192
        const val DEFAULT_VIDEO_QUALITY_HEIGHT = 720
    }
}
