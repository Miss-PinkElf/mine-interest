package com.mineinterest.media.core.task

/**
 * 批量入队结果。
 *
 * @param taskIds 成功创建的任务 id
 * @param skippedLines 解析阶段跳过的行（供 UI 提示）
 */
data class BatchEnqueueResult(
    val taskIds: List<String>,
    val skippedLines: List<String>,
)
