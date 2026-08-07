package com.mineinterest.media.bili

import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.OkHttpClient
import java.security.MessageDigest
import java.util.TreeMap
import java.util.concurrent.atomic.AtomicReference

/**
 * B站 WBI 签名（用于 playurl 等接口，降低 403/风控概率）。
 * 算法对齐 bilibili-API-collect 公开说明。
 */
class BiliWbiSigner(
    private val http: OkHttpClient,
) {

    private val cachedMixin = AtomicReference<String?>(null)

    fun signUrl(baseUrl: String, params: Map<String, String>): String {
        val mixin = cachedMixin.get() ?: refreshMixinKey().also { cachedMixin.set(it) }
        val signed = signParams(params, mixin)
        val builder = baseUrl.toHttpUrl().newBuilder()
        signed.forEach { (k, v) -> builder.addQueryParameter(k, v) }
        return builder.build().toString()
    }

    fun invalidate() {
        cachedMixin.set(null)
    }

    private fun refreshMixinKey(): String {
        val json = BiliHttp.apiGet(http, NAV_API)
        val imgUrl = BiliJson.stringField(json, "img_url")
            ?: error("WBI: 无法获取 img_url")
        val subUrl = BiliJson.stringField(json, "sub_url")
            ?: error("WBI: 无法获取 sub_url")
        val imgKey = imgUrl.substringAfterLast('/').substringBefore('.')
        val subKey = subUrl.substringAfterLast('/').substringBefore('.')
        return mixinKey(imgKey, subKey)
    }

    private fun signParams(
        params: Map<String, String>,
        mixinKey: String,
    ): Map<String, String> {
        val sorted = TreeMap<String, String>()
        params.forEach { (k, v) -> sorted[k] = filterValue(v) }
        val wts = (System.currentTimeMillis() / 1000L).toString()
        sorted["wts"] = wts
        val query = sorted.entries.joinToString("&") { "${it.key}=${it.value}" }
        val wRid = md5Hex(query + mixinKey)
        sorted["w_rid"] = wRid
        return sorted
    }

    private fun filterValue(value: String): String {
        return value.replace(FILTER_CHARS, "")
    }

    private fun mixinKey(imgKey: String, subKey: String): String {
        val raw = imgKey + subKey
        return buildString {
            for (i in 0 until 32) {
                append(raw[MIXIN_KEY_ENC_TAB[i]])
            }
        }
    }

    private fun md5Hex(text: String): String {
        val digest = MessageDigest.getInstance("MD5").digest(text.toByteArray(Charsets.UTF_8))
        return digest.joinToString("") { "%02x".format(it) }
    }

    companion object {
        private const val NAV_API = "https://api.bilibili.com/x/web-interface/nav"
        private val FILTER_CHARS = Regex("""[!'()*]""")

        /**
         * 官方公开混淆表（固定）。
         */
        private val MIXIN_KEY_ENC_TAB = intArrayOf(
            46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
            27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
            37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
            22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
        )
    }
}
