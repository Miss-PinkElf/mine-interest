package com.mineinterest.media.core.link

import com.mineinterest.media.core.model.ParsedLink

/**
 * 手动批量解析结果。
 *
 * @param items 有效且已去重的链接
 * @param skippedLines 无法识别或被跳过的行/片段（供 UI 提示）
 */
data class BatchParseResult(
    val items: List<ParsedLink>,
    val skippedLines: List<String>,
)
