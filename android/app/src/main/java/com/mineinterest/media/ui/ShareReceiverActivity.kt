package com.mineinterest.media.ui

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

/**
 * 系统分享入口：接收 text/plain，转交主界面处理。
 */
class ShareReceiverActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val sharedText = intent?.getStringExtra(Intent.EXTRA_TEXT)
            ?: intent?.getCharSequenceExtra(Intent.EXTRA_TEXT)?.toString()
        val launch = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
            if (!sharedText.isNullOrBlank()) {
                putExtra(MainActivity.EXTRA_SHARED_TEXT, sharedText)
            }
        }
        startActivity(launch)
        finish()
    }
}
