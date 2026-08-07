package com.mineinterest.media.core.task

import com.mineinterest.media.core.link.LinkParser
import com.mineinterest.media.core.model.BiliTaskOptions
import com.mineinterest.media.core.model.FanqieTaskOptions
import com.mineinterest.media.core.model.MediaTask
import com.mineinterest.media.core.model.ParsedLink
import com.mineinterest.media.core.model.Platform
import com.mineinterest.media.core.model.TaskStatus
import com.mineinterest.media.core.provider.ProviderRegistry
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch
import java.util.UUID

/**
 * 任务编排：解析 → 选 Provider → 更新状态。
 *
 * 批量入口 [enqueueBatch] 将多条有效链接分别入队，单条失败不阻断其它条。
 */
class TaskRunner(
    private val parser: LinkParser,
    private val registry: ProviderRegistry,
    private val repo: TaskRepository,
    private val scope: CoroutineScope,
) {

    fun enqueue(
        sourceText: String,
        biliOptions: BiliTaskOptions?,
        fanqieOptions: FanqieTaskOptions?,
    ): String {
        val parsed = parser.parse(sourceText)
        return enqueueParsed(parsed, sourceText, biliOptions, fanqieOptions)
    }

    /**
     * 手动批量：解析多条 → 分别入队。
     */
    fun enqueueBatch(
        rawText: String,
        biliOptions: BiliTaskOptions?,
        fanqieOptions: FanqieTaskOptions?,
    ): BatchEnqueueResult {
        val batch = parser.parseBatch(rawText)
        val ids = batch.items.map { parsed ->
            enqueueParsed(parsed, parsed.rawText, biliOptions, fanqieOptions)
        }
        return BatchEnqueueResult(
            taskIds = ids,
            skippedLines = batch.skippedLines,
        )
    }

    private fun enqueueParsed(
        parsed: ParsedLink,
        sourceText: String,
        biliOptions: BiliTaskOptions?,
        fanqieOptions: FanqieTaskOptions?,
    ): String {
        val id = UUID.randomUUID().toString()
        val now = System.currentTimeMillis()
        val task = MediaTask(
            id = id,
            platform = parsed.platform,
            sourceText = sourceText,
            displayTitle = parsed.idHint,
            status = TaskStatus.QUEUED,
            progressPercent = 0,
            message = null,
            outputPath = null,
            createdAtEpochMs = now,
            updatedAtEpochMs = now,
            biliOptions = biliOptions,
            fanqieOptions = fanqieOptions,
        )
        repo.upsert(task)

        scope.launch {
            repo.updateStatus(id, TaskStatus.RUNNING, 0, MESSAGE_START, null)
            if (parsed.platform == Platform.UNKNOWN) {
                repo.updateStatus(id, TaskStatus.FAILED, 0, MESSAGE_UNRECOGNIZED_LINK, null)
                return@launch
            }
            val provider = registry.forPlatform(parsed.platform)
            if (provider == null) {
                repo.updateStatus(id, TaskStatus.FAILED, 0, MESSAGE_PROVIDER_MISSING, null)
                return@launch
            }
            val optsBili = if (parsed.platform == Platform.BILIBILI) biliOptions else null
            val optsFq = if (parsed.platform == Platform.FANQIE) fanqieOptions else null
            val result = provider.download(parsed, id, optsBili, optsFq) { percent, message ->
                repo.updateStatus(id, TaskStatus.RUNNING, percent, message, null)
            }
            result.fold(
                onSuccess = { path ->
                    repo.updateStatus(id, TaskStatus.SUCCESS, 100, MESSAGE_DONE, path)
                },
                onFailure = { error ->
                    repo.updateStatus(
                        id,
                        TaskStatus.FAILED,
                        0,
                        error.message ?: MESSAGE_FAILED,
                        null,
                    )
                },
            )
        }
        return id
    }

    companion object {
        private const val MESSAGE_START = "开始"
        private const val MESSAGE_UNRECOGNIZED_LINK = "无法识别链接"
        private const val MESSAGE_PROVIDER_MISSING = "未注册 Provider"
        private const val MESSAGE_DONE = "完成"
        private const val MESSAGE_FAILED = "失败"
    }
}
