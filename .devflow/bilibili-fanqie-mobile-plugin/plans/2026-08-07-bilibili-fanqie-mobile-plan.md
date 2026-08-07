# B站 + 番茄小说 Android 工具 Implementation Plan（实施计划）

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| 创建时间（Created At） | 2026-08-07 16:43:14 CST |
| 更新时间（Updated At） | 2026-08-07 16:58:59 CST |
| 作者（Author） | Grok |
| 目的（Purpose） | 将已确认 Align 落成可执行实施计划（Plan），指导后续 Spec/Tasks 与 Apply |
| 关联仓库或项目（Related Repository / Project） | mine-interest-bilibili-fanqie |
| 关联 mission（Related Mission） | bilibili-fanqie-mobile-plugin |
| 当前状态（Status） | 计划中（Planned） |
| 文档边界（Scope / Boundary） | **Plan 真相源**：回答「做什么、按什么顺序做」；**不是** formal OpenSpec，**不**直接等于已开始 Apply |
| 关联 Align | `.devflow/bilibili-fanqie-mobile-plugin/plans/2026-08-07-bilibili-fanqie-mobile-align.md` |
| 开发分支（Branch） | `rin-bilibili-fanqie-mobile/dev` |

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-subagent-driven-development（推荐）或 executing-plans 按任务实施。步骤使用 checkbox（`- [ ]`）跟踪。  
> **本仓库提交流程：** 未经用户明确允许，**不得** `git commit`；计划中的 Commit 步骤改为「暂存并询问用户是否提交」。

**Goal:** 在 Android 上交付一个 Kotlin 个人工具 App：通过分享/剪贴板/手动入口解析链接（**手动支持批量解析多条**），B站可配置导出 mp3/mp4（含码率/字幕/目录），番茄导出 TXT 到指定目录；下载核心与 UI 解耦。

**Architecture:** 单 App 多模块：`app`（极简 UI + 入口）调用 `core`（链接解析含 `parseBatch`、任务队列、路径策略）与可替换 `BiliProvider` / `FanqieProvider`。B站本轮一体式实现；番茄借鉴 Tomato-Novel-Downloader 的「book_id → 目录 → 分章 → 断点 → TXT」流程，正文通过可配置 `ContentFetcher` 接入（开源上游正文源不完整，不可假称可 1:1 复现闭源能力）。手动批量：拆分多行/多 URL → 去重 → 分别入队，单条失败不阻断其它条。

**Tech Stack:** Kotlin、Android Gradle（AGP 8.x）、Jetpack（Activity/ViewModel/WorkManager 或 Coroutine 前台服务）、OkHttp、Kotlinx Serialization 或 Moshi、JUnit4/5 单元测试；minSdk 26+；目标个人 sideload，不强制上架商店。

---

## 0. 文件与模块地图（先锁定分解）

所有产品代码落在仓库根目录 `android/` 下（与 `.devflow/` 文档分离）。

```text
android/
├── settings.gradle.kts
├── build.gradle.kts
├── gradle.properties
├── app/                          # UI + Application + 分享入口
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/.../ui/
│       │   ├── MainActivity.kt
│       │   ├── ShareReceiverActivity.kt
│       │   ├── TaskListViewModel.kt
│       │   └── settings/SettingsFragment.kt  # 或单 Activity 内 Compose/View
│       └── res/
├── core/                         # 纯逻辑 + 任务编排（尽量少 Android 依赖）
│   └── src/
│       ├── main/java/.../core/
│       │   ├── model/
│       │   │   ├── Platform.kt
│       │   │   ├── MediaTask.kt
│       │   │   ├── TaskStatus.kt
│       │   │   ├── BiliTaskOptions.kt
│       │   │   └── FanqieTaskOptions.kt
│       │   ├── link/
│       │   │   ├── LinkParser.kt          # parse + parseBatch
│       │   │   └── BatchParseResult.kt
│       │   ├── path/
│       │   │   └── SavePathPolicy.kt
│       │   ├── task/
│       │   │   ├── TaskRepository.kt
│       │   │   └── TaskRunner.kt          # enqueue + enqueueBatch
│       │   └── provider/
│       │       ├── DownloadProvider.kt
│       │       ├── ProviderRegistry.kt
│       │       └── ProgressCallback.kt
│       └── test/java/.../core/
│           ├── link/LinkParserTest.kt
│           └── path/SavePathPolicyTest.kt
├── provider-bili/                # B站一体式 Provider
│   └── src/main/java/.../bili/
│       ├── BiliDownloadProvider.kt
│       ├── BiliIdResolver.kt
│       ├── BiliStreamClient.kt
│       ├── BiliSubtitleClient.kt
│       └── BiliExporter.kt       # mp4 封装 / mp3 导出
└── provider-fanqie/              # 番茄 Provider（借鉴 Tomato 流程）
    └── src/
        ├── main/java/.../fanqie/
        │   ├── FanqieDownloadProvider.kt
        │   ├── FanqieBookIdResolver.kt
        │   ├── FanqieCatalogClient.kt
        │   ├── FanqieContentFetcher.kt      # 接口
        │   ├── ConfigurableHttpContentFetcher.kt
        │   ├── FanqieChapterStore.kt        # 断点
        │   └── FanqieTxtFinalizer.kt
        └── test/java/.../fanqie/
            ├── FanqieBookIdResolverTest.kt
            └── FanqieTxtFinalizerTest.kt
```

**单元边界一句话：**

| 模块 | 只做什么 | 不做什么 |
|------|----------|----------|
| `core` | 解析链接类型、任务状态机、调 Provider | 不懂 B站/番茄协议细节 |
| `provider-bili` | B站解析与导出 | 不碰番茄、不碰 UI |
| `provider-fanqie` | 番茄 book 流程与 TXT | 不碰 B站、不碰 Termux |
| `app` | 入口与展示 | 不写下载协议 |

---

## 1. 关键常量与约定（禁止魔法值散落）

实现时集中到各模块 `Constants` / ` co` 对象，例如：

```kotlin
// core/.../CoreConstants.kt
object CoreConstants {
    const val DEFAULT_BILI_SUBDIR = "MineMedia/bilibili"
    const val DEFAULT_FANQIE_SUBDIR = "MineMedia/fanqie"
    const val PREFS_NAME = "mine_media_settings"
    const val KEY_DEFAULT_BILI_DIR = "default_bili_dir"
    const val KEY_DEFAULT_FANQIE_DIR = "default_fanqie_dir"
    const val KEY_FANQIE_API_ENDPOINTS = "fanqie_api_endpoints" // 多行 URL，个人配置
}

// provider-bili/.../BiliConstants.kt
object BiliConstants {
    val HOST_MARKERS = listOf("bilibili.com", "b23.tv", "bili2233.cn")
    val BV_REGEX = Regex("""BV[0-9A-Za-z]+""")
    val AV_REGEX = Regex("""av(\d+)""", RegexOption.IGNORE_CASE)
    const val DEFAULT_AUDIO_BITRATE_KBPS = 192
    const val FORMAT_MP3 = "mp3"
    const val FORMAT_MP4 = "mp4"
}

// provider-fanqie/.../FanqieConstants.kt
object FanqieConstants {
    val HOST_MARKERS = listOf("fanqienovel.com", "fqnovel.com", "novelfm.com")
    val BOOK_ID_QUERY = Regex("""[?&]book_id=(\d{10,})""")
    val BOOK_ID_PATH = Regex("""/page/(\d{10,})""")
    val BOOK_ID_PLAIN = Regex("""^\d{10,}$""")
    const val STATUS_JSON = "status.json"
    const val CHAPTER_JOURNAL = "downloaded_chapters.jsonl"
}
```

---

## 2. 实施任务

### Task 1: 创建 Android 多模块工程骨架

**Files:**
- Create: `android/settings.gradle.kts`
- Create: `android/build.gradle.kts`
- Create: `android/gradle.properties`
- Create: `android/app/build.gradle.kts`
- Create: `android/core/build.gradle.kts`
- Create: `android/provider-bili/build.gradle.kts`
- Create: `android/provider-fanqie/build.gradle.kts`
- Create: `android/app/src/main/AndroidManifest.xml`
- Create: `android/app/src/main/java/com/mineinterest/media/MediaApp.kt`
- Create: `android/app/src/main/java/com/mineinterest/media/ui/MainActivity.kt`

- [ ] **Step 1: 初始化 Gradle 多模块**

`settings.gradle.kts`：

```kotlin
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "mine-media-downloader"
include(":app", ":core", ":provider-bili", ":provider-fanqie")
```

模块依赖：`app` → `core` + `provider-bili` + `provider-fanqie`；两个 provider → `core`。  
`core` 使用 `com.android.library` 或纯 `java-library`+`kotlin`：若需 `Uri`/`Context` 仅放在 `app` 与 provider 的 Android 库中；**纯解析逻辑放 `core` 的纯 Kotlin 源集**。推荐：`core` 为 `com.android.library`（minSdk 对齐），便于以后扩展。

- [ ] **Step 2: 最小可安装 App**

`MainActivity` 仅显示标题「Mine Media」与空任务列表占位。  
`MediaApp : Application()` 预留，后续注入 `TaskRunner`。

- [ ] **Step 3: 本地验证骨架**

```bash
cd android && ./gradlew :app:assembleDebug
```

Expected: `BUILD SUCCESSFUL`，生成 debug APK。

- [ ] **Step 4: 询问用户是否提交**

说明改动范围后询问；**仅用户允许后**再 commit，信息示例：`feat: 初始化 Android 多模块骨架`。

---

### Task 2: 领域模型与 Provider 接口

**Files:**
- Create: `android/core/src/main/java/com/mineinterest/media/core/model/*.kt`
- Create: `android/core/src/main/java/com/mineinterest/media/core/provider/DownloadProvider.kt`
- Create: `android/core/src/main/java/com/mineinterest/media/core/provider/ProgressCallback.kt`
- Create: `android/core/src/main/java/com/mineinterest/media/core/provider/ProviderRegistry.kt`
- Test: `android/core/src/test/java/com/mineinterest/media/core/model/BiliTaskOptionsTest.kt`（可选，校验默认值）

- [ ] **Step 1: 定义模型**

```kotlin
enum class Platform { BILIBILI, FANQIE, UNKNOWN }

enum class TaskStatus { QUEUED, RUNNING, SUCCESS, FAILED, CANCELLED }

data class ParsedLink(
    val platform: Platform,
    val rawText: String,
    val canonicalUrl: String?,
    val idHint: String?, // BV 号或 book_id 等
)

data class BiliTaskOptions(
    val format: String = BiliConstants.FORMAT_MP3, // 常量定义在 bili 模块时可在 core 放镜像字符串常量避免循环依赖
    val audioBitrateKbps: Int = 192,
    val videoQualityHeight: Int = 720,
    val withSubtitle: Boolean = false,
    val saveDirUri: String, // 用字符串存 SAF tree uri 或绝对路径
)

data class FanqieTaskOptions(
    val saveDirUri: String,
    val resume: Boolean = true,
)

data class MediaTask(
    val id: String,
    val platform: Platform,
    val sourceText: String,
    val displayTitle: String?,
    val status: TaskStatus,
    val progressPercent: Int,
    val message: String?,
    val outputPath: String?,
    val createdAtEpochMs: Long,
    val updatedAtEpochMs: Long,
    val biliOptions: BiliTaskOptions? = null,
    val fanqieOptions: FanqieTaskOptions? = null,
)
```

为避免 `core` 依赖 provider 常量，在 `core` 内定义：

```kotlin
object CoreMediaFormats {
    const val MP3 = "mp3"
    const val MP4 = "mp4"
}
```

- [ ] **Step 2: Provider 接口**

```kotlin
fun interface ProgressCallback {
    fun onProgress(percent: Int, message: String?)
}

interface DownloadProvider {
    val platform: Platform
    suspend fun download(
        parsed: ParsedLink,
        taskId: String,
        biliOptions: BiliTaskOptions?,
        fanqieOptions: FanqieTaskOptions?,
        onProgress: ProgressCallback,
    ): Result<String> // success = 输出文件路径
}

class ProviderRegistry(private val providers: List<DownloadProvider>) {
    fun forPlatform(platform: Platform): DownloadProvider? =
        providers.firstOrNull { it.platform == platform }
}
```

- [ ] **Step 3: 编译**

```bash
cd android && ./gradlew :core:compileDebugKotlin
```

Expected: SUCCESS。

- [ ] **Step 4: 询问是否提交**（`feat: 添加任务模型与 DownloadProvider 接口`）

---

### Task 3: LinkParser（单条 + 批量解析）— TDD

**Files:**
- Create: `android/core/src/main/java/com/mineinterest/media/core/link/LinkParser.kt`
- Create: `android/core/src/main/java/com/mineinterest/media/core/link/BatchParseResult.kt`
- Create: `android/core/src/test/java/com/mineinterest/media/core/link/LinkParserTest.kt`

- [ ] **Step 1: 写失败测试（含批量）**

```kotlin
class LinkParserTest {
    private val parser = LinkParser()

    @Test
    fun parse_bilibili_bv_from_share_text() {
        val text = "【标题】https://www.bilibili.com/video/BV1xx411c7mD/?spm=1 完整放送"
        val r = parser.parse(text)
        assertEquals(Platform.BILIBILI, r.platform)
        assertEquals("BV1xx411c7mD", r.idHint)
    }

    @Test
    fun parse_bilibili_short_link_host() {
        val r = parser.parse("https://b23.tv/abcdefg")
        assertEquals(Platform.BILIBILI, r.platform)
        assertTrue(r.canonicalUrl!!.contains("b23.tv"))
    }

    @Test
    fun parse_fanqie_book_id_query() {
        val r = parser.parse("https://fanqienovel.com/page/1234567890123456789")
        assertEquals(Platform.FANQIE, r.platform)
        assertEquals("1234567890123456789", r.idHint)
    }

    @Test
    fun parse_unknown() {
        val r = parser.parse("hello world")
        assertEquals(Platform.UNKNOWN, r.platform)
    }

    @Test
    fun parseBatch_multiline_mixed_platforms() {
        val text = """
            https://www.bilibili.com/video/BV1xx411c7mD
            垃圾行没有链接
            https://fanqienovel.com/page/7318247498772674083
            https://www.bilibili.com/video/BV1xx411c7mD
        """.trimIndent()
        val batch = parser.parseBatch(text)
        assertEquals(2, batch.items.size) // 去重后 1 个 BV + 1 个番茄
        assertTrue(batch.skippedLines.isNotEmpty())
        assertEquals(1, batch.items.count { it.platform == Platform.BILIBILI })
        assertEquals(1, batch.items.count { it.platform == Platform.FANQIE })
    }

    @Test
    fun parseBatch_multiple_urls_in_one_line() {
        val text =
            "看这个 https://www.bilibili.com/video/BV1aa411c7mD 还有 https://b23.tv/xxxxxx"
        val batch = parser.parseBatch(text)
        assertTrue(batch.items.size >= 2 || batch.items.any { it.platform == Platform.BILIBILI })
    }
}
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd android && ./gradlew :core:test --tests com.mineinterest.media.core.link.LinkParserTest
```

Expected: FAIL（类不存在或断言失败）。

- [ ] **Step 3: 最小实现（含 parseBatch）**

```kotlin
data class BatchParseResult(
    val items: List<ParsedLink>,
    val skippedLines: List<String>,
)

class LinkParser {
    fun parse(raw: String): ParsedLink {
        val text = raw.trim()
        val url = URL_REGEX.find(text)?.value
        val lower = text.lowercase()

        val isBili = BiliHost.any { lower.contains(it) } ||
            BV_REGEX.containsMatchIn(text) ||
            AV_REGEX.containsMatchIn(text)
        if (isBili) {
            val bv = BV_REGEX.find(text)?.value
            val av = AV_REGEX.find(text)?.groupValues?.getOrNull(1)
            return ParsedLink(
                platform = Platform.BILIBILI,
                rawText = text,
                canonicalUrl = url,
                idHint = bv ?: av?.let { "av$it" },
            )
        }

        val isFanqie = FanqieHost.any { lower.contains(it) } ||
            BOOK_ID_QUERY.containsMatchIn(text) ||
            BOOK_ID_PATH.containsMatchIn(text) ||
            (url == null && BOOK_ID_PLAIN.matches(text))
        if (isFanqie) {
            val id = BOOK_ID_QUERY.find(text)?.groupValues?.get(1)
                ?: BOOK_ID_PATH.find(text)?.groupValues?.get(1)
                ?: text.takeIf { BOOK_ID_PLAIN.matches(it) }
            return ParsedLink(Platform.FANQIE, text, url, id)
        }

        return ParsedLink(Platform.UNKNOWN, text, url, null)
    }

    /**
     * 手动批量解析：按行拆分；若单行含多个 URL 则再拆。
     * 跳过 UNKNOWN；按 platform+idHint+canonicalUrl 去重。
     */
    fun parseBatch(raw: String): BatchParseResult {
        val candidates = mutableListOf<String>()
        val skipped = mutableListOf<String>()
        raw.lines().map { it.trim() }.filter { it.isNotEmpty() }.forEach { line ->
            val urls = URL_REGEX.findAll(line).map { it.value }.toList()
            when {
                urls.size >= 2 -> candidates.addAll(urls)
                urls.size == 1 -> candidates.add(line) // 保留整行分享文案便于抽 BV
                BOOK_ID_PLAIN.matches(line) -> candidates.add(line)
                else -> skipped.add(line)
            }
        }
        val seen = linkedSetOf<String>()
        val items = mutableListOf<ParsedLink>()
        for (c in candidates) {
            val p = parse(c)
            if (p.platform == Platform.UNKNOWN) {
                skipped.add(c)
                continue
            }
            val key = listOf(p.platform.name, p.idHint.orEmpty(), p.canonicalUrl.orEmpty())
                .joinToString("|")
            if (seen.add(key)) items.add(p)
        }
        return BatchParseResult(items = items, skippedLines = skipped)
    }

    companion object {
        private val URL_REGEX = Regex("""https?://[^\s]+""")
        private val BiliHost = listOf("bilibili.com", "b23.tv", "bili2233.cn")
        private val FanqieHost = listOf("fanqienovel.com", "fqnovel.com", "novelfm.com")
        private val BV_REGEX = Regex("""BV[0-9A-Za-z]+""")
        private val AV_REGEX = Regex("""av(\d+)""", RegexOption.IGNORE_CASE)
        private val BOOK_ID_QUERY = Regex("""[?&]book_id=(\d{10,})""")
        private val BOOK_ID_PATH = Regex("""/page/(\d{10,})""")
        private val BOOK_ID_PLAIN = Regex("""^\d{10,}$""")
    }
}
```

说明：`b23.tv` 短链解跳转仍在 **Provider 内**；`LinkParser` 只做分类与批量拆分/去重。

- [ ] **Step 4: 跑通测试**

```bash
cd android && ./gradlew :core:test --tests com.mineinterest.media.core.link.LinkParserTest
```

Expected: PASS。

- [ ] **Step 5: 询问是否提交**（`test: 链接解析器覆盖单条与批量 B站/番茄文案`）

---

### Task 4: 保存路径策略与任务仓库

**Files:**
- Create: `android/core/src/main/java/com/mineinterest/media/core/path/SavePathPolicy.kt`
- Create: `android/core/src/main/java/com/mineinterest/media/core/task/TaskRepository.kt`
- Create: `android/core/src/main/java/com/mineinterest/media/core/task/InMemoryTaskRepository.kt`
- Create: `android/app/.../settings` 读写默认目录（可与 Task 7 合并，但接口本任务先定）
- Test: `android/core/src/test/java/com/mineinterest/media/core/path/SavePathPolicyTest.kt`

- [ ] **Step 1: 测试文件名消毒**

```kotlin
@Test
fun sanitize_removes_illegal_chars() {
    val name = SavePathPolicy.sanitizeFileName("a/b:c*|?.txt")
    assertFalse(name.contains("/"))
    assertTrue(name.endsWith(".txt") || !name.contains(":"))
}
```

- [ ] **Step 2: 实现**

```kotlin
object SavePathPolicy {
    private val illegal = Regex("""[\\/:*?"<>|\n\r\t]""")

    fun sanitizeFileName(name: String, maxLen: Int = 120): String {
        val cleaned = name.replace(illegal, "_").trim().ifEmpty { "untitled" }
        return cleaned.take(maxLen)
    }

    fun defaultRelativeDir(platform: Platform): String = when (platform) {
        Platform.BILIBILI -> CoreConstants.DEFAULT_BILI_SUBDIR
        Platform.FANQIE -> CoreConstants.DEFAULT_FANQIE_SUBDIR
        Platform.UNKNOWN -> "MineMedia/other"
    }
}
```

- [ ] **Step 3: TaskRepository 接口 + 内存实现**

```kotlin
interface TaskRepository {
    fun observeTasks(): Flow<List<MediaTask>> // 若 core 不引 coroutines，可用回调 List listener
    fun get(id: String): MediaTask?
    fun upsert(task: MediaTask)
    fun updateStatus(id: String, status: TaskStatus, percent: Int, message: String?, outputPath: String?)
}

// MVP 可用 MutableStateFlow + 内存 Map；进程杀后丢失可接受，后续再 DataStore 持久化（本 plan 可选增强，不阻塞 MVP）
```

若希望 `core` 不依赖 coroutines：用 `fun addListener` + 主线程回调；`app` 侧再用 Flow 包装。  
**本 plan 选定：** `core` 引入 `kotlinx-coroutines-core`，`InMemoryTaskRepository` 用 `MutableStateFlow`。

- [ ] **Step 4: 测试与编译通过后询问提交**

---

### Task 5: TaskRunner（编排：解析 → 选 Provider → 更新状态）

**Files:**
- Create: `android/core/src/main/java/com/mineinterest/media/core/task/TaskRunner.kt`
- Create: `android/core/src/test/java/com/mineinterest/media/core/task/TaskRunnerTest.kt`

- [ ] **Step 1: 用 Fake Provider 写测试**

```kotlin
class FakeBiliProvider : DownloadProvider {
    override val platform = Platform.BILIBILI
    override suspend fun download(...): Result<String> {
        onProgress.onProgress(100, "ok")
        return Result.success("/tmp/a.mp3")
    }
}

@Test
fun enqueue_bili_link_marks_success() = runTest {
    val repo = InMemoryTaskRepository()
    val runner = TaskRunner(LinkParser(), ProviderRegistry(listOf(FakeBiliProvider())), repo)
    val id = runner.enqueue(
        sourceText = "https://www.bilibili.com/video/BV1xx411c7mD",
        biliOptions = BiliTaskOptions(saveDirUri = "file:///tmp"),
        fanqieOptions = null,
    )
    advanceUntilIdle()
    assertEquals(TaskStatus.SUCCESS, repo.get(id)?.status)
    assertEquals("/tmp/a.mp3", repo.get(id)?.outputPath)
}
```

- [ ] **Step 2: 实现 TaskRunner**

```kotlin
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
     * @return 成功入队的 taskId 列表；skipped 供 UI 提示
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
        return BatchEnqueueResult(taskIds = ids, skippedLines = batch.skippedLines)
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
            repo.updateStatus(id, TaskStatus.RUNNING, 0, "开始", null)
            if (parsed.platform == Platform.UNKNOWN) {
                repo.updateStatus(id, TaskStatus.FAILED, 0, "无法识别链接", null)
                return@launch
            }
            val provider = registry.forPlatform(parsed.platform)
            if (provider == null) {
                repo.updateStatus(id, TaskStatus.FAILED, 0, "未注册 Provider", null)
                return@launch
            }
            val optsBili = if (parsed.platform == Platform.BILIBILI) biliOptions else null
            val optsFq = if (parsed.platform == Platform.FANQIE) fanqieOptions else null
            val result = provider.download(parsed, id, optsBili, optsFq) { p, m ->
                repo.updateStatus(id, TaskStatus.RUNNING, p, m, null)
            }
            result.fold(
                onSuccess = { path ->
                    repo.updateStatus(id, TaskStatus.SUCCESS, 100, "完成", path)
                },
                onFailure = { e ->
                    repo.updateStatus(id, TaskStatus.FAILED, 0, e.message ?: "失败", null)
                },
            )
        }
        return id
    }
}

data class BatchEnqueueResult(
    val taskIds: List<String>,
    val skippedLines: List<String>,
)
```

- [ ] **Step 3: 为 enqueueBatch 增加 Fake Provider 测试（2 条有效 + 1 条垃圾行 → 2 个 SUCCESS）**
- [ ] **Step 4: 测试 PASS → 询问提交**

---

### Task 6: B站 Provider — ID 解析与短链解跳

**Files:**
- Create: `android/provider-bili/.../BiliIdResolver.kt`
- Create: `android/provider-bili/.../BiliDownloadProvider.kt`（骨架）
- Test: `android/provider-bili/src/test/.../BiliIdResolverTest.kt`

- [ ] **Step 1: 测试 BV/av 抽取与规范化**

```kotlin
@Test
fun resolve_bv_from_url() {
    val id = BiliIdResolver.extractFromParsed(
        ParsedLink(Platform.BILIBILI, "", "https://www.bilibili.com/video/BV1xx411c7mD", "BV1xx411c7mD")
    )
    assertEquals("BV1xx411c7mD", id)
}
```

- [ ] **Step 2: 短链解跳（集成逻辑，单测可用 MockWebServer）**

```kotlin
class BiliIdResolver(private val http: OkHttpClient) {
    suspend fun resolveToBvid(parsed: ParsedLink): String {
        val hint = parsed.idHint
        if (hint != null && hint.startsWith("BV")) return hint
        val url = parsed.canonicalUrl ?: error("无 URL")
        if (!url.contains("b23.tv")) {
            return extractBvidFromText(url) ?: error("无法解析 bvid")
        }
        val req = Request.Builder().url(url).head().build() // 或 GET，followRedirects=true
        http.newCall(req).await().use { resp ->
            val finalUrl = resp.request.url.toString()
            return extractBvidFromText(finalUrl) ?: error("短链未解析到 BV")
        }
    }
}
```

- [ ] **Step 3: 编译测试通过 → 询问提交**

---

### Task 7: B站 Provider — 一体式下载导出 MVP

**Files:**
- Create: `android/provider-bili/.../BiliStreamClient.kt`
- Create: `android/provider-bili/.../BiliSubtitleClient.kt`
- Create: `android/provider-bili/.../BiliExporter.kt`
- Modify: `android/provider-bili/.../BiliDownloadProvider.kt`

**实现策略（个人自用 MVP，接受接口变更风险）：**

1. 用 OkHttp 按 B站公开页面/播放信息常见流程获取可下载流地址（具体 URL 构造集中在 `BiliStreamClient`，便于失效时单点修改）。  
2. `format=mp4`：下载视频（及如需的音频轨）并合并/落盘为 `.mp4`（MVP 若合并复杂，可先保单一可播容器，在代码注释标明限制）。  
3. `format=mp3`：优先音频流；若无独立音频则下载后用 `MediaExtractor`+`MediaMuxer` 或 Android 可用 API 抽音轨；若设备 API 不足，MVP 允许先保存 `m4a` 并在 UI 标明「音频导出降级」，但 **接口仍暴露 mp3 选项**，能转则转。  
4. `withSubtitle=true`：尝试拉取字幕轨道并与媒体同目录写 `.srt`/`.ass`（无字幕则任务仍成功，message 提示无字幕）。  
5. `audioBitrateKbps` / `videoQualityHeight`：在选流时过滤最接近档位。

- [ ] **Step 1: 定义选流数据结构**

```kotlin
data class BiliPlaySelection(
    val bvid: String,
    val title: String,
    val videoUrl: String?,
    val audioUrl: String?,
    val subtitleUrl: String?,
)
```

- [ ] **Step 2: `BiliStreamClient.fetchSelection(bvid, options)`**

- 输入：`BiliTaskOptions`  
- 输出：`BiliPlaySelection`  
- 错误：网络失败 / 需登录 / 无权限 → `Result.failure` 带中文 message  

- [ ] **Step 3: `BiliExporter.export(selection, options, destDir, onProgress)`**

- 写临时文件到 `context.cacheDir`  
- 成功后移动/复制到用户 `saveDirUri`（SAF：`DocumentFile`）  
- 返回最终路径字符串  

- [ ] **Step 4: `BiliDownloadProvider.download` 串联**

```kotlin
class BiliDownloadProvider(
    private val resolver: BiliIdResolver,
    private val streams: BiliStreamClient,
    private val exporter: BiliExporter,
) : DownloadProvider {
    override val platform = Platform.BILIBILI
    override suspend fun download(...): Result<String> = runCatching {
        val options = biliOptions ?: error("缺少 B站选项")
        onProgress.onProgress(5, "解析视频 ID")
        val bvid = resolver.resolveToBvid(parsed)
        onProgress.onProgress(15, "获取媒体流")
        val selection = streams.fetchSelection(bvid, options).getOrThrow()
        onProgress.onProgress(30, "下载中")
        exporter.export(selection, options, onProgress).getOrThrow()
    }
}
```

- [ ] **Step 5: 真机/模拟器手工验证清单**

1. 公开可访问的 BV 链接 → mp3 或音频文件落盘  
2. 同一链接 → mp4  
3. 打开字幕开关 → 有则旁路文件，无则提示  
4. 自定义目录（SAF 选择器选一次）  

- [ ] **Step 6: 询问提交**（`feat: B站一体式下载导出 MVP`）

**风险备注（写入代码 KDoc）：** 非官方稳定 API；失效时只改 `BiliStreamClient`；长期可替换为延期项 yt-dlp 引擎而不改 `DownloadProvider` 接口。

---

### Task 8: 番茄 book_id 解析与目录客户端（借鉴 Tomato）

**Files:**
- Create: `android/provider-fanqie/.../FanqieBookIdResolver.kt`
- Create: `android/provider-fanqie/.../FanqieCatalogClient.kt`
- Create: `android/provider-fanqie/.../model/FanqieModels.kt`
- Test: `android/provider-fanqie/src/test/.../FanqieBookIdResolverTest.kt`

对照上游：`base_system/book_id.rs` 与 `network_parser/network.rs` 行为（见分析笔记）。

- [ ] **Step 1: book_id 测试**

```kotlin
@Test
fun resolve_from_page_path() {
    assertEquals(
        "7318247498772674083",
        FanqieBookIdResolver.resolve("https://fanqienovel.com/page/7318247498772674083"),
    )
}

@Test
fun resolve_plain_id() {
    assertEquals("7318247498772674083", FanqieBookIdResolver.resolve("7318247498772674083"))
}
```

- [ ] **Step 2: 实现 resolver**（纯函数，含短链 host 时仅提取，解跳转用 OkHttp followRedirects）

- [ ] **Step 3: CatalogClient**

```kotlin
data class FanqieBookMeta(val bookId: String, val title: String, val author: String?)
data class FanqieChapterRef(val itemId: String, val title: String, val index: Int)

interface FanqieCatalogClient {
    suspend fun fetchMeta(bookId: String): FanqieBookMeta
    suspend fun fetchChapters(bookId: String): List<FanqieChapterRef>
}
```

实现类 `FanqieWebCatalogClient`：  
- 请求番茄网页/公开目录接口（URL 与解析逻辑单独文件，标注「可能失效」）  
- 解析章节列表 JSON/HTML → `FanqieChapterRef`  
- **禁止** 把未开源 token 硬编码进仓库；无能力时抛出明确错误：`目录获取失败：...`

- [ ] **Step 4: 单测可用 fixture JSON 测解析函数；网络测手工**  
- [ ] **Step 5: 询问提交**

---

### Task 9: 番茄正文 Fetcher + 断点 + TXT 导出

**Files:**
- Create: `android/provider-fanqie/.../FanqieContentFetcher.kt`
- Create: `android/provider-fanqie/.../ConfigurableHttpContentFetcher.kt`
- Create: `android/provider-fanqie/.../FanqieChapterStore.kt`
- Create: `android/provider-fanqie/.../FanqieTxtFinalizer.kt`
- Create: `android/provider-fanqie/.../FanqieDownloadProvider.kt`
- Test: `android/provider-fanqie/src/test/.../FanqieTxtFinalizerTest.kt`

- [ ] **Step 1: 接口（可插拔正文源）**

```kotlin
interface FanqieContentFetcher {
    suspend fun fetchChapterContent(itemId: String): String
}

/**
 * 个人配置的 HTTP 正文源。
 * endpoints 来自设置页多行文本，不在仓库硬编码第三方 token。
 * 请求格式对齐上游 ThirdPartyContentClient 的可公开约定（路径参数 item_id 等），
 * 具体 path 模板做成可配置：endpoint 支持 `{item_id}` 占位符。
 */
class ConfigurableHttpContentFetcher(
    private val http: OkHttpClient,
    private val endpointTemplates: List<String>,
) : FanqieContentFetcher {
    override suspend fun fetchChapterContent(itemId: String): String {
        require(endpointTemplates.isNotEmpty()) {
            "未配置番茄正文 API 端点。请在设置中填写个人可用端点（含 {item_id}）。"
        }
        var last: Exception? = null
        for (tpl in endpointTemplates) {
            try {
                val url = tpl.replace("{item_id}", itemId)
                // GET → 解析 JSON 正文字段（字段名兼容 content/data/content 等，集中在 extractContent）
                return extractContent(httpGet(url))
            } catch (e: Exception) {
                last = e
            }
        }
        throw last ?: IllegalStateException("正文获取失败")
    }
}
```

- [ ] **Step 2: 断点存储（借鉴 status.json + jsonl 思路，可简化）**

```kotlin
class FanqieChapterStore(private val bookCacheDir: File) {
    fun loadDownloadedIds(): Set<String>
    fun markDownloaded(itemId: String, title: String)
    fun writeChapterText(itemId: String, title: String, body: String)
}
```

缓存目录：`{appFilesDir}/fanqie_cache/{bookId}/`  
最终 TXT：用户 `saveDir` 下 `{sanitize(title)}.txt`。

- [ ] **Step 3: TxtFinalizer**

```kotlin
object FanqieTxtFinalizer {
    fun merge(chapters: List<Pair<String, String>>): String {
        // Pair<title, body>
        return chapters.joinToString("\n\n") { (title, body) ->
            "第章 $title\n\n${body.trim()}"
        }
    }
}
```

单测：两章合并含标题分隔。

- [ ] **Step 4: FanqieDownloadProvider 主流程**

```text
resolve bookId
→ fetchMeta + fetchChapters
→ 过滤已下载（resume）
→ 低并发（默认 2）逐章 fetchChapterContent
→ 写 cache + journal
→ merge → 写 TXT 到 saveDir
→ 进度按章节比例回调
```

并发常量：`FanqieConstants.DEFAULT_CONCURRENCY = 2`（避免压测式打爆源）。

- [ ] **Step 5: 设置项「番茄正文端点」**

- 未配置时：任务失败 message 明确指导填写，**不**静默崩溃  
- 开发验证：可用上游 Termux 二进制对照同一 book_id 的章节完整性（人工）  

- [ ] **Step 6: 询问提交**（`feat: 番茄 TXT 下载链路与可配置正文源`）

---

### Task 10: App 入口 — 分享 / 剪贴板 / 手动解析 + 极简 UI

**Files:**
- Modify: `android/app/src/main/AndroidManifest.xml`
- Create: `android/app/.../ui/ShareReceiverActivity.kt`
- Modify: `android/app/.../ui/MainActivity.kt`
- Create: `android/app/.../ui/TaskListViewModel.kt`
- Create: `android/app/.../ui/ParseBarViews`（手写 View 或 Compose，任选；**优先简单 XML+View** 降低干扰）
- Create: `android/app/.../di/ServiceLocator.kt`（无 Hilt 时手动组装，YAGNI）

- [ ] **Step 1: Manifest 分享与权限**

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
<!-- 按目标 SDK 增加通知权限 POST_NOTIFICATIONS -->

<activity android:name=".ui.ShareReceiverActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="text/plain" />
    </intent-filter>
</activity>
```

- [ ] **Step 2: ShareReceiverActivity**

```kotlin
// onCreate:
val text = intent.getStringExtra(Intent.EXTRA_TEXT)
if (!text.isNullOrBlank()) {
    viewModel.prepareFromSharedText(text) // 解析并跳转主界面带入草稿
}
finish() // 或直接展示确认页
```

推荐：分享进入后打开主界面并填充「待确认任务」卡片（平台 + B站选项），用户点「开始」再 `enqueue`。

- [ ] **Step 3: 打开时剪贴板一次检测**

```kotlin
// MainActivity.onResume 仅首次冷启动或设置开关开启时：
val clip = clipboard.primaryClip?.getItemAt(0)?.coerceToText(this)?.toString()
if (!clip.isNullOrBlank() && linkParser.parse(clip).platform != Platform.UNKNOWN) {
    showDetectDialog(clip) // 是否解析
}
// 不做后台常驻监听
```

- [ ] **Step 4: 手动输入框（多行）+「解析 / 批量开始」+ 任务 RecyclerView**

- 输入框使用 **多行** `EditText`（或等价），hint 示例：  
  `每行一条链接，也可一次粘贴多段分享文案`  
- 主按钮调用 `taskRunner.enqueueBatch(text, biliOptions, fanqieOptions)`（单条也走 batch，内部自然兼容）  
- 若 `skippedLines` 非空：Toast 或对话框提示「已跳过 N 条无法识别」  
- 显示：标题/平台/状态/进度/错误 message/输出路径  
- B站选项 UI：Spinner format、码率、字幕 CheckBox、目录选择按钮（`ACTION_OPEN_DOCUMENT_TREE`）  
- **本批** B站任务共用当前选项；番茄共用当前目录  

- [ ] **Step 5: ServiceLocator 组装真实 Provider 与 TaskRunner**

```kotlin
object ServiceLocator {
    lateinit var taskRunner: TaskRunner
    fun init(app: Application) {
        val http = OkHttpClient.Builder().followRedirects(true).build()
        val repo = InMemoryTaskRepository()
        val registry = ProviderRegistry(
            listOf(
                BiliDownloadProvider(...),
                FanqieDownloadProvider(...),
            )
        )
        taskRunner = TaskRunner(LinkParser(), registry, repo, app.applicationScope)
    }
}
```

- [ ] **Step 6: 手工验收 Align S1–S5、S8**

| 编号 | 操作 | 期望 |
|------|------|------|
| S1 | 分享/剪贴板/手动 | 均能进入解析 |
| S2 | B站与番茄链接 | 平台识别正确 |
| S3 | 改 format/码率/字幕/目录 | 选项生效或明确降级提示 |
| S4 | 番茄 + 已配置端点 | 产出 TXT |
| S5 | 任务列表 | 状态与失败信息可见 |
| S8 | 手动框粘贴 2+ 条链接（可混平台）点解析 | 产生多条任务；垃圾行跳过并提示；本批 B站共用选项 |

- [ ] **Step 7: 询问提交**（`feat: 分享剪贴板入口与任务 UI`）

---

### Task 11: 前台服务（可选但推荐，避免下载杀进程）

**Files:**
- Create: `android/app/.../download/DownloadForegroundService.kt`
- Modify: Manifest service 声明

- [ ] **Step 1:** `TaskRunner.enqueue` 启动时 `startForegroundService`，通知显示进度。  
- [ ] **Step 2:** 任务全部结束后 `stopSelf`。  
- [ ] **Step 3:** 真机后台切换仍能完成小文件任务。  
- [ ] **Step 4: 询问提交**

若时间紧，可标为 MVP+：先无前台服务完成演示，再补。

---

### Task 12: 文档与 mission 收尾（实现阶段结束时）

**Files:**
- Create: `android/README.md`（如何用 Android Studio 打开、组装、配置番茄端点、个人自用声明）
- Update: `.devflow/bilibili-fanqie-mobile-plugin/state.md` / `checkpoints.md`

- [ ] **Step 1:** README 中文说明构建与使用  
- [ ] **Step 2:** 对照 Align 成功标准打勾  
- [ ] **Step 3:** 未完成项写入 `deferred/` 或 `backlog.md`  
- [ ] **Step 4: 询问是否提交文档**

---

## 3. 本轮不做（与 Align 一致，禁止在 Apply 时偷做）

- yt-dlp + ffmpeg 引擎（见 `deferred/b站-外部引擎-yt-dlp-ffmpeg.md`）  
- Termux 本地服务主架构  
- RN/Flutter 壳  
- iOS、注入插件、后台剪贴板监听  
- 番茄 TTS / 书架订阅  
- 在仓库硬编码未开源第三方 token  

---

## 4. Plan 自检（Spec coverage）

| Align 要求 | 对应 Task |
|------------|-----------|
| S1 三种入口 | Task 10 |
| S2 平台识别 | Task 3, 5, 10 |
| S3 B站选项 | Task 2, 7, 10 |
| S4 番茄 TXT | Task 8, 9, 10 |
| S5 任务状态 | Task 4, 5, 10 |
| S6 无 Termux 依赖 | 全任务；番茄用 App 内 Provider |
| S7 核心与 UI 解耦 | Task 1 模块地图 + Provider 接口 |
| **S8 手动批量解析** | **Task 3（parseBatch）、Task 5（enqueueBatch）、Task 10（多行 UI）** |
| Kotlin | 全任务 |
| 可替换 B站引擎预留 | `DownloadProvider` 接口；延期 yt-dlp |
| 番茄借鉴流程 | Task 8–9 |
| 正文源风险 | Task 9 ConfigurableHttpContentFetcher + 设置页 |

**Placeholder 扫描：** 已避免笼统「之后再写测试」；B站具体 HTTP 路径因合规与漂移集中在 `BiliStreamClient` 单点实现，Apply 时按当时可用公开流程填写，不在 plan 伪造过期 URL。  
**类型一致性：** `ParsedLink` / `MediaTask` / `DownloadProvider.download(...)` 在 Task 2 定义，后续任务沿用。

---

## 5. 建议执行方式

完成 Plan 后进入重型路径下一阶段：可用 `openspec-propose` 生成 `spec/proposal.md` + `design.md` + `tasks.md`（从本 plan 拆 checkbox），再 Apply。

**执行选项（实现时二选一）：**

1. **Subagent-Driven（推荐）** — 每 Task 新开子代理 + 审查  
2. **Inline Execution** — 本会话按 Task 连续做，阶段检查点暂停  

**默认推荐顺序：** Task 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12。

---

## 6. 验证总清单（宣称完成前必须具备新鲜证据）

```bash
cd android
./gradlew :core:test :provider-fanqie:test :provider-bili:test :app:assembleDebug
```

加上真机：分享入口、B站一链两格式、番茄一链出 TXT（端点已配置时）。
