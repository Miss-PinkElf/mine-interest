# Design — B站 + 番茄小说 Android 工具

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| 创建时间（Created At） | 2026-08-07 17:10:28 CST |
| 作者（Author） | Grok |
| 目的（Purpose） | 固化模块边界、接口与数据流，指导 Apply 实现 |
| 关联 mission（Related Mission） | bilibili-fanqie-mobile-plugin |
| 当前状态（Status） | 已批准进入 Apply |
| 文档边界（Scope / Boundary） | design artifact；与 plan 模块地图一致；**不**替代 plan 中的逐步 checkbox |
| 关联 Plan | `.devflow/bilibili-fanqie-mobile-plugin/plans/2026-08-07-bilibili-fanqie-mobile-plan.md` |
| 开发分支（Branch） | `rin-bilibili-fanqie-mobile/dev` |

---

## 总体思路

单 App、多模块、**链接驱动**：

1. UI 只负责入口与展示（分享 / 剪贴板一次 / 多行手动）。
2. `core` 负责解析、任务状态机、调用 Provider。
3. `provider-bili` / `provider-fanqie` 各自实现下载与导出；通过 `DownloadProvider` 接口挂接。
4. B站本轮一体式实现，接口预留日后替换为 yt-dlp 引擎而不改编排层。
5. 番茄借鉴 Tomato 主链路（book_id → 目录 → 分章 → 断点 → TXT），正文源 **可配置**，不硬编码闭源 token。

技术栈：Kotlin、AGP 8.x、OkHttp、Kotlinx Coroutines、JUnit 单测；UI 优先简单 XML+View。

---

## 结构与边界

```text
android/
├── app/                 # UI + Application + 分享入口 +（可选）前台服务
├── core/                # 模型、LinkParser、TaskRepository、TaskRunner、Provider 接口
├── provider-bili/       # B站一体式下载导出
└── provider-fanqie/     # 番茄 TXT + 可配置 ContentFetcher
```

| 模块 | 只做什么 | 不做什么 |
|------|----------|----------|
| `core` | 链接分类与批量、任务编排、进度状态 | 不懂 B站/番茄协议细节 |
| `provider-bili` | BV/短链、选流、导出 mp3/mp4/字幕 | 不碰番茄、不碰 UI |
| `provider-fanqie` | book 流程、断点、TXT、可配置正文 | 不碰 B站、不碰 Termux 主架构 |
| `app` | 入口、选项 UI、任务列表、DI 组装 | 不写下载协议 |

依赖：`app` → `core` + 两个 provider；两个 provider → `core`。

包名建议：`com.mineinterest.media`（及 `.core` / `.bili` / `.fanqie`）。

---

## 数据流与接口

### 主路径

```text
分享 / 剪贴板 / 手动多行
        ↓
LinkParser.parse / parseBatch  →  ParsedLink[]（去重，跳过 UNKNOWN）
        ↓
TaskRunner.enqueue / enqueueBatch
        ↓
TaskRepository（QUEUED → RUNNING → SUCCESS|FAILED）
        ↓
ProviderRegistry.forPlatform → DownloadProvider.download
        ↓
落盘路径字符串 → UI 展示
```

### 关键类型（core）

- `Platform`：`BILIBILI` / `FANQIE` / `UNKNOWN`
- `TaskStatus`：`QUEUED` / `RUNNING` / `SUCCESS` / `FAILED` / `CANCELLED`
- `ParsedLink`：platform、rawText、canonicalUrl、idHint
- `BatchParseResult`：items + skippedLines
- `BiliTaskOptions` / `FanqieTaskOptions`
- `MediaTask`：展示与状态字段 + 可选平台选项
- `BatchEnqueueResult`：taskIds + skippedLines

### 关键接口

```kotlin
interface DownloadProvider {
    val platform: Platform
    suspend fun download(
        parsed: ParsedLink,
        taskId: String,
        biliOptions: BiliTaskOptions?,
        fanqieOptions: FanqieTaskOptions?,
        onProgress: ProgressCallback,
    ): Result<String> // 成功 = 输出路径
}

fun interface ProgressCallback {
    fun onProgress(percent: Int, message: String?)
}

interface FanqieContentFetcher {
    suspend fun fetchChapterContent(itemId: String): String
}
```

### 批量约定

- 按行拆；单行多 URL 再拆
- 有效项分别入队；skipped 供 UI 提示
- 本批 B站共用当前 `BiliTaskOptions`；番茄共用当前 `FanqieTaskOptions`

### 常量

业务常量集中到 `CoreConstants` / `BiliConstants` / `FanqieConstants` / `CoreMediaFormats`，禁止魔法字符串散落。

---

## 复用点

| 来源 | 复用方式 |
|------|----------|
| Tomato-Novel-Downloader | **流程与解析思路**（book_id、目录、断点 journal、finalize）；非二进制嵌入 |
| 开源 B站下载调研 | 选流/导出策略参考；实现集中在 `BiliStreamClient` |
| OkHttp | 短链解跳、网页/API 请求 |
| Android SAF | 用户自定义保存目录（`DocumentFile` / tree URI 字符串） |
| 未来 yt-dlp 引擎 | 新 `DownloadProvider` 实现替换 bili 模块内部，接口不变 |

---

## 风险与权衡

| 风险 | 权衡 / 缓解 |
|------|-------------|
| B站非官方接口漂移 | 单点 `BiliStreamClient`；Provider 可替换；延期 yt-dlp |
| 番茄开源正文源不完整 | 可配置 HTTP 端点；未配置明确失败 |
| 合规 | 个人自用声明；禁止硬编码闭源 token |
| 进程被杀 | MVP 内存仓库可接受；Task 11 前台服务可选增强 |
| mp3 转码能力 | 允许降级 m4a 并 UI 标明 |
| 环境未就绪 | 可先写代码与单测；APK 真机验收等用户 SDK |

---

## 验证策略

```bash
cd android
./gradlew :core:test :provider-fanqie:test :provider-bili:test :app:assembleDebug
```

真机：分享入口、B站一链两格式、番茄一链出 TXT（端点已配置时）、手动批量 2+ 条。

---

## 实施顺序

与 Plan / tasks.md 一致：Task 1 骨架 → 2 模型接口 → 3 LinkParser → 4 仓库路径 → 5 TaskRunner → 6–7 B站 → 8–9 番茄 → 10 UI 入口 → 11 前台服务（可选）→ 12 文档。
