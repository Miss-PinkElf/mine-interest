package com.mineinterest.media.core.model

/**
 * 下载任务领域模型（UI 与编排层共用）。
 */
data class MediaTask(
    val id: String,
    val platform: Platform,
    val sourceText: String,
    val displayTitle: String?,
    val status: TaskStatus,
    val progressPercent: Int,
    val message: String?,
    val outputPath: String?,
    val createdAtEpochMs: Long,
    val updatedAtEpochMs: Long,
    val biliOptions: BiliTaskOptions? = null,
    val fanqieOptions: FanqieTaskOptions? = null,
)
