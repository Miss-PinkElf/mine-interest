package com.mineinterest.media.core.provider

import com.mineinterest.media.core.model.Platform

/**
 * 按平台查找 [DownloadProvider]。
 */
class ProviderRegistry(
    private val providers: List<DownloadProvider>,
) {
    fun forPlatform(platform: Platform): DownloadProvider? =
        providers.firstOrNull { it.platform == platform }
}
