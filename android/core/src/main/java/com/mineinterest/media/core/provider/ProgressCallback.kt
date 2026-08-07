package com.mineinterest.media.core.provider

fun interface ProgressCallback {
    fun onProgress(percent: Int, message: String?)
}
