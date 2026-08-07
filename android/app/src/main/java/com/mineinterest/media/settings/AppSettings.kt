package com.mineinterest.media.settings

import android.content.Context
import com.mineinterest.media.core.CoreConstants
import com.mineinterest.media.core.CoreMediaFormats
import com.mineinterest.media.core.model.BiliTaskOptions
import com.mineinterest.media.core.model.FanqieTaskOptions
import java.io.File

/**
 * 设置读写（SharedPreferences）。
 */
class AppSettings(context: Context) {

    private val prefs = context.getSharedPreferences(CoreConstants.PREFS_NAME, Context.MODE_PRIVATE)
    private val defaultFilesDir = context.getExternalFilesDir(null) ?: context.filesDir

    fun getBiliDirUri(): String {
        return prefs.getString(CoreConstants.KEY_DEFAULT_BILI_DIR, null)
            ?: File(defaultFilesDir, CoreConstants.DEFAULT_BILI_SUBDIR).absolutePath
    }

    fun setBiliDirUri(uri: String) {
        prefs.edit().putString(CoreConstants.KEY_DEFAULT_BILI_DIR, uri).apply()
    }

    fun getFanqieDirUri(): String {
        return prefs.getString(CoreConstants.KEY_DEFAULT_FANQIE_DIR, null)
            ?: File(defaultFilesDir, CoreConstants.DEFAULT_FANQIE_SUBDIR).absolutePath
    }

    fun setFanqieDirUri(uri: String) {
        prefs.edit().putString(CoreConstants.KEY_DEFAULT_FANQIE_DIR, uri).apply()
    }

    fun getFanqieEndpoints(): List<String> {
        val raw = prefs.getString(CoreConstants.KEY_FANQIE_API_ENDPOINTS, "").orEmpty()
        return raw.lines().map { it.trim() }.filter { it.isNotEmpty() }
    }

    fun setFanqieEndpointsText(text: String) {
        prefs.edit().putString(CoreConstants.KEY_FANQIE_API_ENDPOINTS, text).apply()
    }

    fun getFanqieEndpointsText(): String =
        prefs.getString(CoreConstants.KEY_FANQIE_API_ENDPOINTS, "").orEmpty()

    fun getBiliFormat(): String =
        prefs.getString(KEY_BILI_FORMAT, CoreMediaFormats.MP3) ?: CoreMediaFormats.MP3

    fun setBiliFormat(format: String) {
        prefs.edit().putString(KEY_BILI_FORMAT, format).apply()
    }

    fun getAudioBitrate(): Int =
        prefs.getInt(KEY_BILI_BITRATE, BiliTaskOptions.DEFAULT_AUDIO_BITRATE_KBPS)

    fun setAudioBitrate(value: Int) {
        prefs.edit().putInt(KEY_BILI_BITRATE, value).apply()
    }

    fun getVideoHeight(): Int =
        prefs.getInt(KEY_BILI_HEIGHT, BiliTaskOptions.DEFAULT_VIDEO_QUALITY_HEIGHT)

    fun setVideoHeight(value: Int) {
        prefs.edit().putInt(KEY_BILI_HEIGHT, value).apply()
    }

    fun isWithSubtitle(): Boolean = prefs.getBoolean(KEY_BILI_SUBTITLE, false)

    fun setWithSubtitle(value: Boolean) {
        prefs.edit().putBoolean(KEY_BILI_SUBTITLE, value).apply()
    }

    fun isClipboardDetectEnabled(): Boolean =
        prefs.getBoolean(KEY_CLIPBOARD_DETECT, true)

    fun setClipboardDetectEnabled(value: Boolean) {
        prefs.edit().putBoolean(KEY_CLIPBOARD_DETECT, value).apply()
    }

    fun currentBiliOptions(): BiliTaskOptions = BiliTaskOptions(
        format = getBiliFormat(),
        audioBitrateKbps = getAudioBitrate(),
        videoQualityHeight = getVideoHeight(),
        withSubtitle = isWithSubtitle(),
        saveDirUri = getBiliDirUri(),
    )

    fun currentFanqieOptions(): FanqieTaskOptions = FanqieTaskOptions(
        saveDirUri = getFanqieDirUri(),
        resume = true,
    )

    companion object {
        private const val KEY_BILI_FORMAT = "bili_format"
        private const val KEY_BILI_BITRATE = "bili_bitrate"
        private const val KEY_BILI_HEIGHT = "bili_height"
        private const val KEY_BILI_SUBTITLE = "bili_subtitle"
        private const val KEY_CLIPBOARD_DETECT = "clipboard_detect"
    }
}
