package com.mineinterest.media.fanqie

import java.io.File

/**
 * 将最终 TXT 写入用户保存目录。
 */
interface FanqieFileWriter {
    fun writeText(saveDirUri: String, fileName: String, content: String): String
}
