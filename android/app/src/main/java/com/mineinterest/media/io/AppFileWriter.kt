package com.mineinterest.media.io

import android.content.Context
import android.net.Uri
import androidx.documentfile.provider.DocumentFile
import com.mineinterest.media.bili.MediaFileWriter
import com.mineinterest.media.fanqie.FanqieFileWriter
import java.io.File
import java.io.FileInputStream

/**
 * 统一写盘：支持绝对路径目录与 SAF tree URI。
 */
class AppFileWriter(
    private val context: Context,
) : MediaFileWriter, FanqieFileWriter {

    override fun writeFile(saveDirUri: String, fileName: String, sourceFile: File): String {
        return when {
            saveDirUri.startsWith(CONTENT_SCHEME) -> writeFileToSaf(saveDirUri, fileName, sourceFile)
            else -> writeFileToPath(saveDirUri, fileName, sourceFile)
        }
    }

    override fun writeText(saveDirUri: String, fileName: String, content: String): String {
        val temp = File(context.cacheDir, "write-$fileName")
        temp.writeText(content, Charsets.UTF_8)
        return writeFile(saveDirUri, fileName, temp).also {
            temp.delete()
        }
    }

    private fun writeFileToPath(dirPath: String, fileName: String, sourceFile: File): String {
        val dir = File(resolvePath(dirPath))
        if (!dir.exists()) {
            dir.mkdirs()
        }
        val dest = File(dir, fileName)
        sourceFile.copyTo(dest, overwrite = true)
        return dest.absolutePath
    }

    private fun writeFileToSaf(treeUri: String, fileName: String, sourceFile: File): String {
        val tree = DocumentFile.fromTreeUri(context, Uri.parse(treeUri))
            ?: error("无法打开保存目录")
        val existing = tree.findFile(fileName)
        existing?.delete()
        val target = tree.createFile(guessMime(fileName), fileName)
            ?: error("无法在保存目录创建文件: $fileName")
        context.contentResolver.openOutputStream(target.uri)?.use { out ->
            FileInputStream(sourceFile).use { input -> input.copyTo(out) }
        } ?: error("无法写入 SAF 文件")
        return target.uri.toString()
    }

    private fun resolvePath(raw: String): String {
        return when {
            raw.startsWith(FILE_SCHEME) -> Uri.parse(raw).path ?: raw.removePrefix(FILE_SCHEME)
            else -> raw
        }
    }

    private fun guessMime(fileName: String): String = when {
        fileName.endsWith(".mp4", true) -> "video/mp4"
        fileName.endsWith(".m4a", true) -> "audio/mp4"
        fileName.endsWith(".mp3", true) -> "audio/mpeg"
        fileName.endsWith(".srt", true) -> "application/x-subrip"
        fileName.endsWith(".txt", true) -> "text/plain"
        else -> "application/octet-stream"
    }

    companion object {
        private const val CONTENT_SCHEME = "content:"
        private const val FILE_SCHEME = "file://"
    }
}
