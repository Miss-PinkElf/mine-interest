package com.mineinterest.media.bili

/**
 * B站 Provider 常量（主机标记、正则、默认码率等）。
 */
object BiliConstants {
    val HOST_MARKERS = listOf("bilibili.com", "b23.tv", "bili2233.cn")
    val BV_REGEX = Regex("""BV[0-9A-Za-z]+""")
    val AV_REGEX = Regex("""av(\d+)""", RegexOption.IGNORE_CASE)
    const val DEFAULT_AUDIO_BITRATE_KBPS = 192
    const val FORMAT_MP3 = "mp3"
    const val FORMAT_MP4 = "mp4"
    const val SHORT_LINK_HOST = "b23.tv"
}
