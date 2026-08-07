package com.mineinterest.media.bili

/**
 * 轻量 JSON 字段提取（避免 org.json，便于 JVM 单测）。
 */
object BiliJson {

    fun intField(json: String, key: String): Int? {
        val match = Regex(""""$key"\s*:\s*(-?\d+)""").find(json) ?: return null
        return match.groupValues[1].toIntOrNull()
    }

    fun longField(json: String, key: String): Long? {
        val match = Regex(""""$key"\s*:\s*(-?\d+)""").find(json) ?: return null
        return match.groupValues[1].toLongOrNull()
    }

    fun stringField(json: String, key: String): String? {
        val match = Regex(""""$key"\s*:\s*"((?:\\.|[^"\\])*)"""").find(json) ?: return null
        return unescape(match.groupValues[1])
    }

    fun allStringFields(json: String, key: String): List<String> {
        return Regex(""""$key"\s*:\s*"((?:\\.|[^"\\])*)"""")
            .findAll(json)
            .map { unescape(it.groupValues[1]) }
            .toList()
    }

    fun allIntFields(json: String, key: String): List<Int> {
        return Regex(""""$key"\s*:\s*(-?\d+)""")
            .findAll(json)
            .mapNotNull { it.groupValues[1].toIntOrNull() }
            .toList()
    }

    fun unescape(value: String): String {
        return value
            .replace("\\/", "/")
            .replace("\\n", "\n")
            .replace("\\r", "\r")
            .replace("\\t", "\t")
            .replace("\\\"", "\"")
            .replace("\\\\", "\\")
            .replace("\\u0026", "&")
    }
}
