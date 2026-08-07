package com.mineinterest.media.fanqie

import java.io.File

/**
 * 章节断点与缓存（借鉴 status.json + jsonl 思路的简化版）。
 */
class FanqieChapterStore(
    private val bookCacheDir: File,
) {

    private val journalFile = File(bookCacheDir, FanqieConstants.CHAPTER_JOURNAL)
    private val chapterDir = File(bookCacheDir, CHAPTER_DIR_NAME)

    init {
        bookCacheDir.mkdirs()
        chapterDir.mkdirs()
    }

    fun loadDownloadedIds(): Set<String> {
        if (!journalFile.exists()) return emptySet()
        return journalFile.readLines()
            .map { it.trim() }
            .filter { it.isNotEmpty() }
            .map { line -> line.substringBefore('\t') }
            .toSet()
    }

    fun markDownloaded(itemId: String, title: String) {
        journalFile.appendText("$itemId\t$title\n")
    }

    fun writeChapterText(itemId: String, title: String, body: String) {
        val file = chapterFile(itemId)
        file.writeText("$title\n\n$body", Charsets.UTF_8)
        markDownloaded(itemId, title)
    }

    fun readChapter(itemId: String): Pair<String, String>? {
        val file = chapterFile(itemId)
        if (!file.exists()) return null
        val text = file.readText(Charsets.UTF_8)
        val parts = text.split("\n\n", limit = 2)
        return if (parts.size == 2) parts[0] to parts[1] else file.name to text
    }

    fun listOrderedChapters(refs: List<com.mineinterest.media.fanqie.model.FanqieChapterRef>): List<Pair<String, String>> {
        return refs.mapNotNull { ref ->
            readChapter(ref.itemId)?.let { (title, body) ->
                (title.ifBlank { ref.title }) to body
            }
        }
    }

    private fun chapterFile(itemId: String): File = File(chapterDir, "$itemId.txt")

    companion object {
        private const val CHAPTER_DIR_NAME = "chapters"
    }
}
