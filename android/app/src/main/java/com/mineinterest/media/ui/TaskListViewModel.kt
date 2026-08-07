package com.mineinterest.media.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mineinterest.media.core.model.MediaTask
import com.mineinterest.media.core.task.BatchEnqueueResult
import com.mineinterest.media.di.ServiceLocator
import com.mineinterest.media.download.DownloadForegroundService
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn

class TaskListViewModel : ViewModel() {

    val tasks: StateFlow<List<MediaTask>> =
        ServiceLocator.taskRepository.observeTasks()
            .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    fun enqueueBatch(rawText: String): BatchEnqueueResult {
        val settings = ServiceLocator.settings
        val result = ServiceLocator.taskRunner.enqueueBatch(
            rawText = rawText,
            biliOptions = settings.currentBiliOptions(),
            fanqieOptions = settings.currentFanqieOptions(),
        )
        if (result.taskIds.isNotEmpty()) {
            DownloadForegroundService.start(ServiceLocator.application)
        }
        return result
    }
}
