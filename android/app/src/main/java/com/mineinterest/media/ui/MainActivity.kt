package com.mineinterest.media.ui

import android.Manifest
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.recyclerview.widget.LinearLayoutManager
import com.mineinterest.media.R
import com.mineinterest.media.core.CoreMediaFormats
import com.mineinterest.media.core.model.Platform
import com.mineinterest.media.databinding.ActivityMainBinding
import com.mineinterest.media.di.ServiceLocator
import kotlinx.coroutines.launch

/**
 * 主界面：手动批量解析、B站选项、番茄端点、任务列表；
 * 打开时可选检测剪贴板一次；接收分享文本。
 */
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: TaskListViewModel by viewModels()
    private val adapter = TaskListAdapter()

    private var clipboardCheckedThisSession = false

    private val pickBiliDir = registerForActivityResult(
        ActivityResultContracts.OpenDocumentTree(),
    ) { uri ->
        if (uri != null) {
            takePersistablePermission(uri)
            ServiceLocator.settings.setBiliDirUri(uri.toString())
            refreshPathHint()
        }
    }

    private val pickFanqieDir = registerForActivityResult(
        ActivityResultContracts.OpenDocumentTree(),
    ) { uri ->
        if (uri != null) {
            takePersistablePermission(uri)
            ServiceLocator.settings.setFanqieDirUri(uri.toString())
            refreshPathHint()
        }
    }

    private val requestNotificationPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { /* 忽略拒绝：仍可下载，仅无通知 */ }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupFormatSpinner()
        loadSettingsToUi()
        binding.taskList.layoutManager = LinearLayoutManager(this)
        binding.taskList.adapter = adapter

        binding.btnStartBatch.setOnClickListener { onStartBatch() }
        binding.btnPickBiliDir.setOnClickListener { pickBiliDir.launch(null) }
        binding.btnPickFanqieDir.setOnClickListener { pickFanqieDir.launch(null) }
        binding.btnSaveSettings.setOnClickListener {
            saveUiToSettings()
            Toast.makeText(this, R.string.toast_settings_saved, Toast.LENGTH_SHORT).show()
        }

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.tasks.collect { tasks ->
                    adapter.submitList(tasks)
                    binding.emptyHintText.visibility =
                        if (tasks.isEmpty()) android.view.View.VISIBLE else android.view.View.GONE
                }
            }
        }

        maybeRequestNotificationPermission()
        handleSharedIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleSharedIntent(intent)
    }

    override fun onResume() {
        super.onResume()
        maybeDetectClipboardOnce()
    }

    private fun setupFormatSpinner() {
        val formats = listOf(CoreMediaFormats.MP3, CoreMediaFormats.MP4)
        binding.spinnerFormat.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            formats,
        )
    }

    private fun loadSettingsToUi() {
        val settings = ServiceLocator.settings
        val format = settings.getBiliFormat()
        val formats = listOf(CoreMediaFormats.MP3, CoreMediaFormats.MP4)
        binding.spinnerFormat.setSelection(formats.indexOf(format).coerceAtLeast(0))
        binding.inputBitrate.setText(settings.getAudioBitrate().toString())
        binding.inputHeight.setText(settings.getVideoHeight().toString())
        binding.checkSubtitle.isChecked = settings.isWithSubtitle()
        binding.checkClipboard.isChecked = settings.isClipboardDetectEnabled()
        binding.inputEndpoints.setText(settings.getFanqieEndpointsText())
        refreshPathHint()
    }

    private fun saveUiToSettings() {
        val settings = ServiceLocator.settings
        val format = binding.spinnerFormat.selectedItem?.toString() ?: CoreMediaFormats.MP3
        settings.setBiliFormat(format)
        settings.setAudioBitrate(
            binding.inputBitrate.text?.toString()?.toIntOrNull()
                ?: settings.getAudioBitrate(),
        )
        settings.setVideoHeight(
            binding.inputHeight.text?.toString()?.toIntOrNull()
                ?: settings.getVideoHeight(),
        )
        settings.setWithSubtitle(binding.checkSubtitle.isChecked)
        settings.setClipboardDetectEnabled(binding.checkClipboard.isChecked)
        settings.setFanqieEndpointsText(binding.inputEndpoints.text?.toString().orEmpty())
    }

    private fun refreshPathHint() {
        val settings = ServiceLocator.settings
        binding.pathHint.text = getString(
            R.string.path_hint,
            settings.getBiliDirUri(),
            settings.getFanqieDirUri(),
        )
    }

    private fun onStartBatch() {
        saveUiToSettings()
        val text = binding.inputLinks.text?.toString().orEmpty().trim()
        if (text.isEmpty()) {
            Toast.makeText(this, R.string.toast_empty_input, Toast.LENGTH_SHORT).show()
            return
        }
        enqueueRaw(text)
    }

    private fun enqueueRaw(text: String) {
        val result = viewModel.enqueueBatch(text)
        Toast.makeText(
            this,
            getString(R.string.toast_enqueued, result.taskIds.size),
            Toast.LENGTH_SHORT,
        ).show()
        if (result.skippedLines.isNotEmpty()) {
            Toast.makeText(
                this,
                getString(R.string.toast_skipped, result.skippedLines.size),
                Toast.LENGTH_LONG,
            ).show()
        }
    }

    private fun handleSharedIntent(intent: Intent?) {
        val shared = intent?.getStringExtra(EXTRA_SHARED_TEXT)?.trim().orEmpty()
        if (shared.isNotEmpty()) {
            binding.inputLinks.setText(shared)
            // 分享进入后填充，用户确认选项再点开始；若只想自动开始可改
            intent?.removeExtra(EXTRA_SHARED_TEXT)
        }
    }

    private fun maybeDetectClipboardOnce() {
        if (clipboardCheckedThisSession) return
        if (!ServiceLocator.settings.isClipboardDetectEnabled()) return
        clipboardCheckedThisSession = true

        val clipboard = getSystemService(ClipboardManager::class.java) ?: return
        val clip: ClipData = clipboard.primaryClip ?: return
        if (clip.itemCount <= 0) return
        val text = clip.getItemAt(0).coerceToText(this)?.toString()?.trim().orEmpty()
        if (text.isEmpty()) return

        val parsed = ServiceLocator.linkParser.parse(text)
        val batch = ServiceLocator.linkParser.parseBatch(text)
        val hasKnown = parsed.platform != Platform.UNKNOWN || batch.items.isNotEmpty()
        if (!hasKnown) return

        AlertDialog.Builder(this)
            .setTitle(R.string.dialog_clipboard_title)
            .setMessage(getString(R.string.dialog_clipboard_message, text.take(200)))
            .setPositiveButton(R.string.dialog_yes) { _, _ ->
                binding.inputLinks.setText(text)
                enqueueRaw(text)
            }
            .setNegativeButton(R.string.dialog_no, null)
            .show()
    }

    private fun takePersistablePermission(uri: Uri) {
        val flags = Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION
        runCatching {
            contentResolver.takePersistableUriPermission(uri, flags)
        }
    }

    private fun maybeRequestNotificationPermission() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return
        val granted = ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.POST_NOTIFICATIONS,
        ) == PackageManager.PERMISSION_GRANTED
        if (!granted) {
            requestNotificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }

    companion object {
        const val EXTRA_SHARED_TEXT = "extra_shared_text"
    }
}
