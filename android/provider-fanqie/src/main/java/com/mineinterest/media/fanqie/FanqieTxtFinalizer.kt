package com.mineinterest.media.fanqie

/**
 * 将章节标题与正文合并为 TXT 内容。
 */
object FanqieTxtFinalizer {

    fun merge(chapters: List<Pair<String, String>>): String {
        return chapters.joinToString(CHAPTER_SEPARATOR) { (title, body) ->
            "$CHAPTER_TITLE_PREFIX$title\n\n${body.trim()}"
        }
    }

    private const val CHAPTER_SEPARATOR = "\n\n"
    private const val CHAPTER_TITLE_PREFIX = "第章 "
}
