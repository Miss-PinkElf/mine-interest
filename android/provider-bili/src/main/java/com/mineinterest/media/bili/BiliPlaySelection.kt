package com.mineinterest.media.bili

/**
 * B站选流结果。
 *
 * @param videoUrls 视频轨候选（主链 + backup，按优先级）
 * @param audioUrls 音频轨候选
 * @param subtitleUrl 字幕源（可选）
 * @param messageHint 降级/提示信息
 */
data class BiliPlaySelection(
    val bvid: String,
    val title: String,
    val cid: Long,
    val videoUrls: List<String>,
    val audioUrls: List<String>,
    val subtitleUrl: String?,
    val messageHint: String? = null,
) {
    val videoUrl: String? get() = videoUrls.firstOrNull()
    val audioUrl: String? get() = audioUrls.firstOrNull()
}
