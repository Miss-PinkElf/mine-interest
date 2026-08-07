package com.mineinterest.media.fanqie

/**
 * 从分享文案 / URL / 纯数字解析番茄 book_id（纯函数，不访问网络）。
 * 短链解跳转由调用方用 OkHttp followRedirects 后再传入最终 URL。
 */
object FanqieBookIdResolver {

    fun resolve(raw: String): String? {
        val text = raw.trim()
        FanqieConstants.BOOK_ID_QUERY.find(text)?.groupValues?.get(1)?.let { return it }
        FanqieConstants.BOOK_ID_PATH.find(text)?.groupValues?.get(1)?.let { return it }
        if (FanqieConstants.BOOK_ID_PLAIN.matches(text)) {
            return text
        }
        return null
    }
}
