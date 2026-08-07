package com.mineinterest.media.core.path

import com.mineinterest.media.core.CoreConstants
import com.mineinterest.media.core.model.Platform

/**
 * 保存路径与文件名策略（纯逻辑，无 Android 依赖）。
 */
object SavePathPolicy {

    private val ILLEGAL_FILE_NAME_CHARS = Regex("""[\\/:*?"<>|\n\r\t]""")

    fun sanitizeFileName(
        name: String,
        maxLen: Int = CoreConstants.MAX_SANITIZED_FILE_NAME_LENGTH,
    ): String {
        val cleaned = name.replace(ILLEGAL_FILE_NAME_CHARS, "_").trim()
            .ifEmpty { FALLBACK_FILE_NAME }
        return cleaned.take(maxLen)
    }

    fun defaultRelativeDir(platform: Platform): String = when (platform) {
        Platform.BILIBILI -> CoreConstants.DEFAULT_BILI_SUBDIR
        Platform.FANQIE -> CoreConstants.DEFAULT_FANQIE_SUBDIR
        Platform.UNKNOWN -> CoreConstants.DEFAULT_OTHER_SUBDIR
    }

    private const val FALLBACK_FILE_NAME = "untitled"
}
