package com.mineinterest.media.fanqie.model

data class FanqieBookMeta(
    val bookId: String,
    val title: String,
    val author: String?,
)

data class FanqieChapterRef(
    val itemId: String,
    val title: String,
    val index: Int,
)
