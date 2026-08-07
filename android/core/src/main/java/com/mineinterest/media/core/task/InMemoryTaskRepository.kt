package com.mineinterest.media.core.task

import com.mineinterest.media.core.model.MediaTask
import com.mineinterest.media.core.model.TaskStatus
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.concurrent.ConcurrentHashMap

/**
 * MVP 内存任务仓库：杀进程后丢失可接受。
 */
class InMemoryTaskRepository : TaskRepository {

    private val tasksById = ConcurrentHashMap<String, MediaTask>()
    private val tasksFlow = MutableStateFlow<List<MediaTask>>(emptyList())

    override fun observeTasks(): Flow<List<MediaTask>> = tasksFlow.asStateFlow()

    override fun get(id: String): MediaTask? = tasksById[id]

    override fun upsert(task: MediaTask) {
        tasksById[task.id] = task
        publish()
    }

    override fun updateStatus(
        id: String,
        status: TaskStatus,
        percent: Int,
        message: String?,
        outputPath: String?,
    ) {
        val existing = tasksById[id] ?: return
        tasksById[id] = existing.copy(
            status = status,
            progressPercent = percent,
            message = message,
            outputPath = outputPath ?: existing.outputPath,
            updatedAtEpochMs = System.currentTimeMillis(),
        )
        publish()
    }

    private fun publish() {
        tasksFlow.value = tasksById.values
            .sortedByDescending { it.createdAtEpochMs }
            .toList()
    }
}
