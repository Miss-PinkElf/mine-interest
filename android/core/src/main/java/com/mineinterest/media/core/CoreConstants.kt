package com.mineinterest.media.core

/**
 * core 模块配置与路径相关常量（避免魔法字符串散落）。
 */
object CoreConstants {
    const val DEFAULT_BILI_SUBDIR = "MineMedia/bilibili"
    const val DEFAULT_FANQIE_SUBDIR = "MineMedia/fanqie"
    const val DEFAULT_OTHER_SUBDIR = "MineMedia/other"
    const val PREFS_NAME = "mine_media_settings"
    const val KEY_DEFAULT_BILI_DIR = "default_bili_dir"
    const val KEY_DEFAULT_FANQIE_DIR = "default_fanqie_dir"
    const val KEY_FANQIE_API_ENDPOINTS = "fanqie_api_endpoints"
    const val MAX_SANITIZED_FILE_NAME_LENGTH = 120
}
