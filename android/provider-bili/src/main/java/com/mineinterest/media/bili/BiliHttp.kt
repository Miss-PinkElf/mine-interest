package com.mineinterest.media.bili

import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.UUID
import java.util.concurrent.TimeUnit

/**
 * B站请求公共头与客户端工厂。
 * 非官方稳定 API，失效时优先改 [BiliStreamClient] / CDN 下载头。
 */
object BiliHttp {

    /** 桌面 Chrome UA，部分 CDN 对移动 UA 更严 */
    const val USER_AGENT =
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    /** yt-dlp 经验：Referer 需带 www，否则 CDN 可能 403 */
    const val REFERER_WWW = "https://www.bilibili.com"
    const val ORIGIN = "https://www.bilibili.com"

    /** 进程内固定 buvid3，降低匿名风控 */
    val BUVID3: String = UUID.randomUUID().toString().uppercase() + "infoc"

    fun createClient(): OkHttpClient =
        OkHttpClient.Builder()
            .followRedirects(true)
            .followSslRedirects(true)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(120, TimeUnit.SECONDS)
            .build()

    fun apiGet(client: OkHttpClient, url: String): String {
        val request = Request.Builder()
            .url(url)
            .headers(apiHeaders())
            .get()
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                error("接口 HTTP ${response.code}: ${shortUrl(url)}")
            }
            return response.body?.string().orEmpty()
        }
    }

    /** 兼容旧调用 */
    fun get(client: OkHttpClient, url: String): String = apiGet(client, url)

    fun apiHeaders(): okhttp3.Headers {
        return okhttp3.Headers.Builder()
            .add("User-Agent", USER_AGENT)
            .add("Referer", REFERER_WWW)
            .add("Origin", ORIGIN)
            .add("Accept", "application/json, text/plain, */*")
            .add("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8")
            .add("Cookie", "buvid3=$BUVID3")
            .build()
    }

    /**
     * CDN 媒体下载头。Referer 尽量指向具体视频页。
     */
    fun mediaHeaders(bvid: String?): okhttp3.Headers {
        val referer = if (!bvid.isNullOrBlank()) {
            "https://www.bilibili.com/video/$bvid"
        } else {
            REFERER_WWW
        }
        return okhttp3.Headers.Builder()
            .add("User-Agent", USER_AGENT)
            .add("Referer", referer)
            .add("Origin", ORIGIN)
            .add("Accept", "*/*")
            .add("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8")
            .add("Connection", "keep-alive")
            .add("Cookie", "buvid3=$BUVID3")
            .build()
    }

    fun shortUrl(url: String): String {
        return if (url.length <= 96) url else url.take(96) + "…"
    }
}
