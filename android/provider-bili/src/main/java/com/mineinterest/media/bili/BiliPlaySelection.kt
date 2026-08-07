package com.mineinterest.media.bili

/**
 * B站选流结果。
 *
 * @param videoUrl 视频轨（mp4 时优先）
 * @param audioUrl 音频轨（mp3/m4a 优先；mp4 合并时使用）
 * @param subtitleUrl 字幕源（可选）
 * @param messageHint 降级/提示信息
 */
data class BiliPlaySelection(
    val bvid: String,
    val title: String,
    val cid: Long,
    val videoUrl: String?,
    val audioUrl: String?,
    val subtitleUrl: String?,
    val messageHint: String? = null,
)
