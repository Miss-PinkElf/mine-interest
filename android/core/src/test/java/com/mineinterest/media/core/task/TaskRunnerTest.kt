package com.mineinterest.media.core.task

import com.mineinterest.media.core.link.LinkParser
import com.mineinterest.media.core.model.BiliTaskOptions
import com.mineinterest.media.core.model.FanqieTaskOptions
import com.mineinterest.media.core.model.ParsedLink
import com.mineinterest.media.core.model.Platform
import com.mineinterest.media.core.model.TaskStatus
import com.mineinterest.media.core.provider.DownloadProvider
import com.mineinterest.media.core.provider.ProgressCallback
import com.mineinterest.media.core.provider.ProviderRegistry
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class TaskRunnerTest {

    private class FakeBiliProvider : DownloadProvider {
        override val platform: Platform = Platform.BILIBILI

        override suspend fun download(
            parsed: ParsedLink,
            taskId: String,
            biliOptions: BiliTaskOptions?,
            fanqieOptions: FanqieTaskOptions?,
            onProgress: ProgressCallback,
        ): Result<String> {
            onProgress.onProgress(100, "ok")
            return Result.success(FAKE_BILI_OUTPUT)
        }
    }

    private class FakeFanqieProvider : DownloadProvider {
        override val platform: Platform = Platform.FANQIE

        override suspend fun download(
            parsed: ParsedLink,
            taskId: String,
            biliOptions: BiliTaskOptions?,
            fanqieOptions: FanqieTaskOptions?,
            onProgress: ProgressCallback,
        ): Result<String> {
            onProgress.onProgress(100, "ok")
            return Result.success(FAKE_FANQIE_OUTPUT)
        }
    }

    @Test
    fun enqueue_bili_link_marks_success() = runTest(UnconfinedTestDispatcher()) {
        val repo = InMemoryTaskRepository()
        val runner = TaskRunner(
            parser = LinkParser(),
            registry = ProviderRegistry(listOf(FakeBiliProvider())),
            repo = repo,
            scope = this,
        )
        val id = runner.enqueue(
            sourceText = "https://www.bilibili.com/video/BV1xx411c7mD",
            biliOptions = BiliTaskOptions(saveDirUri = "file:///tmp"),
            fanqieOptions = null,
        )
        advanceUntilIdle()
        assertEquals(TaskStatus.SUCCESS, repo.get(id)?.status)
        assertEquals(FAKE_BILI_OUTPUT, repo.get(id)?.outputPath)
    }

    @Test
    fun enqueueBatch_two_valid_one_garbage() = runTest(UnconfinedTestDispatcher()) {
        val repo = InMemoryTaskRepository()
        val runner = TaskRunner(
            parser = LinkParser(),
            registry = ProviderRegistry(
                listOf(FakeBiliProvider(), FakeFanqieProvider()),
            ),
            repo = repo,
            scope = this,
        )
        val raw = """
            https://www.bilibili.com/video/BV1xx411c7mD
            垃圾行
            https://fanqienovel.com/page/7318247498772674083
        """.trimIndent()
        val result = runner.enqueueBatch(
            rawText = raw,
            biliOptions = BiliTaskOptions(saveDirUri = "file:///tmp"),
            fanqieOptions = FanqieTaskOptions(saveDirUri = "file:///tmp"),
        )
        advanceUntilIdle()
        assertEquals(2, result.taskIds.size)
        assertTrue(result.skippedLines.isNotEmpty())
        assertTrue(result.taskIds.all { repo.get(it)?.status == TaskStatus.SUCCESS })
    }

    companion object {
        private const val FAKE_BILI_OUTPUT = "/tmp/a.mp3"
        private const val FAKE_FANQIE_OUTPUT = "/tmp/book.txt"
    }
}
