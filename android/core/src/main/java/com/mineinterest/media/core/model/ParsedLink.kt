package com.mineinterest.media.core.model

/**
 * 链接解析结果（单条）。
 *
 * @param platform 平台类型
 * @param rawText 原始输入片段
 * @param canonicalUrl 提取到的 URL（若有）
 * @param idHint BV 号 / av 号 / book_id 等提示 id
 */
data class ParsedLink(
    val platform: Platform,
    val rawText: String,
    val canonicalUrl: String?,
    val idHint: String?,
)
