package com.mineinterest.media

import android.app.Application
import com.mineinterest.media.di.ServiceLocator

/**
 * Application 入口：初始化 [ServiceLocator]。
 */
class MediaApp : Application() {
    override fun onCreate() {
        super.onCreate()
        ServiceLocator.init(this)
    }
}
