package com.mineinterest.media.core.task

import com.mineinterest.media.core.model.MediaTask
import com.mineinterest.media.core.model.TaskStatus
import kotlinx.coroutines.flow.Flow

/**
 * 任务仓库接口。MVP 可用内存实现，进程结束后可丢失。
 */
interface TaskRepository {
    fun observeTasks(): Flow<List<MediaTask>>
    fun get(id: String): MediaTask?
    fun upsert(task: MediaTask)
    fun updateStatus(
        id: String,
        status: TaskStatus,
        percent: Int,
        message: String?,
        outputPath: String?,
    )
}
