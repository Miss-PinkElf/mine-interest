package com.mineinterest.media.bili

import java.io.File

/**
 * 将临时文件写入用户选择的保存目录（路径或 SAF tree URI）。
 * @return 可读的输出路径/URI 字符串
 */
interface MediaFileWriter {
    fun writeFile(saveDirUri: String, fileName: String, sourceFile: File): String
}
