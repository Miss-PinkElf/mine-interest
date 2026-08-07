# Tomato-Novel-Downloader 代码分析笔记

## Metadata（元数据）

| 字段 | 值 |
|------|----|
| 创建时间（Created At） | 2026-08-07 12:00 |
| 作者（Author） | Grok Build 只读分析 Agent |
| 目的（Purpose） | 梳理开源项目 Tomato-Novel-Downloader 的模块、主链路与可借鉴点，供 mission `bilibili-fanqie-mobile-plugin` 后续 Align / Plan 使用 |
| 关联仓库 / 项目（Related Repository / Project） | `references/Tomato-Novel-Downloader`（浅克隆分析副本） |
| 关联 mission（Related Mission） | `bilibili-fanqie-mobile-plugin` |
| 当前状态（Status） | 候选项（Candidate）/ 分析笔记（Analysis Note） |
| 文档边界（Scope / Boundary） | **非实现规格**；不代表已批准方案；不触发产品代码实现；仅作思路借鉴 |
| 关联路径 | `.devflow/bilibili-fanqie-mobile-plugin/references/Tomato-Novel-Downloader/` |
| 分析对象版本 | `Cargo.toml` 中 `version = "2.4.13"` |

### 已定决策（不推翻）

- 产品形态：Android 单 App。
- 番茄小说：App 内自研最小 TXT 下载；**借鉴**本项目思路，**不**把 Termux / 本地服务当主架构。
- 本轮只分析，不改产品代码，不提交 git。

---

## 1. 目录结构与模块职责

项目为 **Rust** 单体二进制（TUI / WebUI / 老 CLI），入口 `src/main.rs`。

```
src/
├── main.rs                 # CLI 参数、日志、配置加载、模式分发（TUI/WebUI/update）
├── prewarm_state.rs        # official-api 启动时 IID 预热状态
├── base_system/            # 基础设施
│   ├── book_id.rs          # 链接/分享文案 → book_id
│   ├── book_paths.rs       # 缓存目录命名（稳定 book_id）
│   ├── config.rs           # config.yml 读写与字段注释
│   ├── context.rs          # Config 结构、默认值、保存路径、状态目录
│   ├── cooldown_retry.rs   # 官方 API Cooldown 退避（依赖 official-api）
│   ├── download_history.rs # 下载历史
│   ├── json_extract.rs     # JSON 字段宽松提取
│   └── ...                 # 日志、自更新、文件清理等
├── network_parser/         # 网页解析网络层
│   └── network.rs          # FanqieWebNetwork：书页 HTML + 目录 API
├── third_party/            # 第三方正文客户端（开源部分）
│   ├── content_client.rs   # ThirdPartyContentClient（batch_full 风格）
│   └── media_fetch.rs      # 媒体拉取
├── download/               # 下载编排
│   ├── models.rs           # BookMeta / ChapterRef / DownloadPlan / DownloadMode 等
│   ├── plan.rs             # prepare_download_plan（目录+元数据）
│   ├── downloader.rs       # 主流程：章节拉取、断点、finalize 入口
│   ├── third_party.rs      # 地址池、探测、分组重试
│   ├── progress.rs         # 进度快照
│   └── segment_pool.rs     # 段评并发池（official-api）
├── book_parser/            # 解析与导出
│   ├── book_manager.rs     # 状态机 + status.json / jsonl 断点
│   ├── parser.rs           # ContentParser：API JSON → 正文
│   ├── finalize_utils.rs   # run_finalize → txt/epub/pdf
│   ├── finalize_epub.rs / finalize_pdf.rs / epub_generator.rs
│   └── audio_generator.rs  # Edge TTS 有声（feature 可选）
└── ui/                     # 交互壳（产品不必照搬）
    ├── tui/                # ratatui 终端 UI
    ├── web/                # axum Web UI（--server）
    └── noui/               # 老 CLI / 非交互 update
```

### 模块职责一览

| 模块 | 职责 | 关键符号 |
|------|------|----------|
| `base_system::book_id` | 输入规范化 | `parse_book_id`, `resolve_book_id`, `is_short_link` |
| `base_system::context` | 配置与路径 | `Config`, `default_save_dir`, `status_folder_path` |
| `network_parser::network` | Web 书信息 + 目录 | `FanqieWebNetwork::get_book_info`, `fetch_chapter_list` |
| `download::plan` | 下载计划 | `prepare_download_plan`, `prepare_download_plan_web` |
| `download::downloader` | 调度执行 | `download_with_plan_flow`, `download_chapters_into_manager` |
| `download::third_party` | 第三方正文 | `fetch_group_third_party`, `validate_endpoints` |
| `third_party::content_client` | HTTP 正文客户端 | `ThirdPartyContentClient::get_contents_unthrottled` |
| `book_parser::book_manager` | 缓存与断点 | `save_chapter`, `append_downloaded_chapter`, `load_existing_status` |
| `book_parser::parser` | 内容清洗 | `ContentParser::extract_api_content`, `clean_plain` |
| `book_parser::finalize_utils` | 最终文件 | `run_finalize`, `finalize_txt`, `prepare_output_path` |
| `ui::*` | 人机界面 | TUI / Web 任务创建 / CLI update |

### Feature 与不可见依赖

| Feature | 含义 |
|---------|------|
| `official-api`（默认） | 依赖路径 crate `tomato-novel-official-api`（`../Tomato-Novel-Official-API`） |
| `no-official-api` | 目录/书信息走 Web；正文强制第三方 |
| `tts` / `tts-native` | 有声书 |
| `clipboard` / `docker` | 剪贴板 / Docker 禁自更新 |

**本浅克隆仓库内不可见：**

1. **`Tomato-Novel-Official-API` crate**（`Cargo.toml` path 依赖，当前 references 下无该目录）——搜索、官方目录客户端 `DirectoryClient`、`FanqieClient` 批量正文、段评、IID 预热 `prewarm_iid` 的实现均在此。
2. **官方网络核心动态库** `Tomato-Novel-Network-Core`（错误提示需 `FANQIE_NETWORK_CORE_DLL`）——**仓库内不可见**。
3. **第三方 API 真实地址池与 token**——README 明确「部分第三方接口相关代码并不开源，包括地址和 token」；开源侧只见 `api_endpoints: Vec<String>` 配置槽与 `ThirdPartyContentClient` 的 URL 拼装约定。

---

## 2. 主链路还原：分享链接 / book_id → TXT/EPUB

### 2.1 总览（数据流）

```
用户输入（纯数字 / URL / 分享文案 / 短链）
    ↓  resolve_book_id / parse_book_id
book_id: String
    ↓  prepare_download_plan(config, book_id, meta_hint)
DownloadPlan { book_id, meta: BookMeta, chapters: Vec<ChapterRef>, _raw }
    ↓  init_manager_from_plan + load_existing_status
BookManager（内存 downloaded + 磁盘 status.json / downloaded_chapters.jsonl）
    ↓  pending_resume / pending_failed + DownloadMode
待下章节列表
    ↓  download_chapters_into_manager
    │     ├─ official-api + use_official_api → ChapterDownloader + FanqieClient
    │     └─ 否则 / no-official-api → download_third_party_flow
    ↓  每章 ContentParser::extract_api_content → save_chapter + append_downloaded_chapter
    ↓  finalize_from_manager → run_finalize
输出 {书名}.txt / .epub / .pdf 或散装目录
```

### 2.2 入口（UI → 编排）

| 入口 | 文件 | 调用链 |
|------|------|--------|
| Web 创建任务 | `ui/web/routes/jobs.rs` → `create_job` | `resolve_book_id` → `prepare_download_plan` → `download_with_plan_flow`（默认 `DownloadMode::Resume`，失败章自动重试一次） |
| TUI 预览/下载 | `ui/tui/preview.rs`, `ui/tui/download.rs` | 同上 |
| 老 CLI | `ui/noui/download.rs` | `download_book_with_options`；**新建下载已禁用**；`--update` 仅本地已有记录 |

Web 创建任务请求体：

```rust
// CreateJobReq
book_id: String,           // 可为链接/短链，后端 resolve
range_start / range_end: Option<usize>,  // 1-based 章节区间
```

### 2.3 步骤拆解

#### Step A：解析 book_id

- 符号：`base_system::book_id::parse_book_id` / `resolve_book_id`
- 见第 4 节。

#### Step B：准备下载计划（目录 + 元数据）

- 符号：`download::plan::prepare_download_plan`

**official-api 路径：**

1. 并行尝试 `prepare_download_plan_web` 作为回退/补全。
2. `DirectoryClient::fetch_directory_with_cover(book_id, api_url, None)` 拉官方目录。
3. 失败或目录为空 → 用 web_plan；再失败则报错。
4. 元数据：`DirectoryMeta` → `BookMeta`，与 `meta_hint`、搜索元数据、web 元数据 `merge_meta` / `merge_meta_prefer_hint_name`。
5. 封面优先 web 页抓取（`download_web_cover`）。
6. 输出 `DownloadPlan`。

**no-official-api / web 回退路径：**

1. `FanqieWebNetwork::fetch_chapter_list(book_id)` → 章节 JSON 数组。
2. `parse_chapter_ref_from_value` 提取 `item_id`/`chapter_id`/… 与 title。
3. `FanqieWebNetwork::get_book_info(book_id)` → 书名/作者/简介/封面/完结等。
4. 组装 `DownloadPlan`。

#### Step C：初始化状态与断点

- `init_manager_from_plan` → `BookManager::new`
- `BookManager::load_existing_status` 读：
  - `{save_dir}/{book_id}/status.json`（主状态）
  - 或 legacy `chapter_status_{book_id}.json`
  - 并 `merge_resume_journal` 合并 `downloaded_chapters.jsonl`（更实时）

#### Step D：选择模式与待下章节

- `DownloadMode`：`Resume` | `Full` | `FailedOnly` | `RangeIgnoreHistory`
- `pending_resume`：无成功内容（`Some((_, Some(_)))`）的章
- `pending_failed`：标记失败（`Some((_, None))`）的章
- `apply_range`：章节区间裁剪

#### Step E：拉正文

- 动态分组：`build_dynamic_chapter_groups`，每组 **15～25** 章（`MIN_DYNAMIC_GROUP_SIZE` / `MAX_DYNAMIC_GROUP_SIZE`）
- 官方：`ChapterDownloader::download_book` + `fetch_with_cooldown_retry` / best-effort + deferred 重试
- 第三方：`download_third_party_flow` → `validate_endpoints` → 线程池 `max_workers` → `fetch_group_third_party`
- 解析：`ContentParser::extract_api_content` → 缓存统一 XHTML 风格 → `save_chapter` + `append_downloaded_chapter`
- 失败：`save_error_chapter`（title + content=None）
- 每组后 `save_download_status` 写 `status.json`

#### Step F：收尾导出

- `finalize_from_manager` → `finalize_utils::run_finalize`
- 按 `novel_format`：`finalize_txt` / `finalize_epub` / `finalize_pdf`
- TXT 时缓存 XHTML 再 `ContentParser::clean_plain` 转纯文本（段落缩进全角空格）
- 可选：有声书 `generate_audiobook`、`auto_clear_dump` 清缓存

### 2.4 核心数据结构

```text
ChapterRef { id, title }
BookMeta { book_name, author, description, tags, cover_url, finished, chapter_count, ... }
DownloadPlan { book_id, meta, chapters, _raw }
DownloadedMap = HashMap<chapter_id, (title, Option<content>)>
  - Some(content) = 成功
  - None = 失败占位
ProgressSnapshot { group_done, group_total, saved_chapters, chapter_total, save_phase, ... }
```

---

## 3. 网络层分工

| 能力 | official-api 构建 | no-official-api 构建 | 代码位置 |
|------|-------------------|----------------------|----------|
| 搜索 | `SearchClient`（crate 内，**实现不可见**） | 不可用 | feature 门控 |
| 目录 / 书信息 | 优先 `DirectoryClient`；失败回退 Web | **仅** `FanqieWebNetwork` | `download/plan.rs` |
| 正文 | `use_official_api=true` → `FanqieClient`；`false` → 第三方地址池 | **强制**第三方 | `download/downloader.rs` |
| 段评 | `SegmentCommentPool` + official | 强制关闭 | feature 门控 |
| Web 书页 | `https://fanqienovel.com/page/{book_id}` HTML | 同左 | `network_parser/network.rs` |
| Web 目录 | `https://fanqienovel.com/api/reader/directory/detail?bookId=` | 同左 | 同上 |
| 第三方正文 | `api_endpoints` + `ThirdPartyContentClient` | 同左（必填） | `third_party/content_client.rs` |

### 3.1 网页解析（`FanqieWebNetwork`）

- **书信息**：GET 书页 HTML → `ContentParser::parse_book_info`（本文件内私有实现）
  - 优先 `__NEXT_DATA__` script JSON
  - 其次 `window.__INITIAL_STATE__`
  - 再正则字段与 `info-label-grey/yellow` 完结标签
  - 封面还可从 `ld+json` / `book-cover-img` 等取
- **目录**：GET `.../api/reader/directory/detail?bookId=`
  - 请求间隔节流 ≥ 800ms
  - 403 时预热书页再退避重试
  - 指数退避 + 本地 dir_cache 回退（`temp/.../dir_cache/{book_id}.json`）
  - 解析多形态：`chapterList` / `chapterListWithVolume` 展平 / 递归找「像章节」的数组

### 3.2 官方 API（可见边界）

- 调用点：`DirectoryClient`, `FanqieClient`, `prewarm_iid`, `fetch_with_cooldown_retry`
- Cooldown 错误：1.1s 起倍增，上限 8s，最多 6 次
- 批量正文失败章节进入 deferred 队列，可单章回退（阈值常量 `DEFERRED_RETRY_SINGLE_FALLBACK_THRESHOLD = 3`）
- **具体协议、签名、加密：仓库内不可见**

### 3.3 第三方正文（开源约定）

`ThirdPartyContentClient` 拼装：

```
{endpoint}/reading/reader/batch_full/v?item_ids=...&aid=1967&epub=0|1&...
```

- 期望返回 JSON：`data` 或顶层 object，key=chapter_id，value 含 `content`/`title`
- 与 Official 解密后结构「尽量兼容」
- `download::third_party::resolve_api_urls` 还可从 base 推导 directory / registerkey / batch_full（官方路径下 `use_official_api=false` 时用）
- **默认 endpoint 列表不在开源仓库中提供**；用户需自行配置 `api_endpoints`

---

## 4. 链接 / ID 解析

文件：`src/base_system/book_id.rs`

### `parse_book_id(input)`

1. trim；空 → None
2. 全为 ASCII 数字 → 直接作为 book_id
3. 从文本中抽出第一个 `https?://\S+`
4. 查询参数：`(?i)(book_id|bookId)=([0-9]+)`
5. 路径：`/page/(\d+)`（对应 fanqienovel 书页）
6. 否则 None

测试用例示例：

- 纯数字 `7423591956359416856`
- 分享页：`https://changdunovel.com/ug/pages/book-share?...&book_id=7423...`

### `resolve_book_id(input)`

1. 先 `parse_book_id`
2. 若失败且是**允许域名**上的短链 `/t/{token}`：
   - 允许主机：`changdunovel.com`, `fanqienovel.com`, `fqnovel.com`（含 www）
   - 发 GET 跟随跳转，对 `response.url()` 再 `parse_book_id`
   - 超时 10s；**仅白名单 host**，防 SSRF
3. 未知 host 的 `/t/...` 不跟随

### 产品借鉴提示

- 分享文案常夹杂「复制打开番茄小说」等文字 → 先抽 URL 再抽 `book_id` 的策略很实用。
- 短链解析需要一次网络跳转；Android 上可用 OkHttp 且禁止任意 host 重定向。

---

## 5. 输出格式与保存路径

### 5.1 配置文件

- 文件名：`config.yml`（`Config::FILE_NAME`）
- 加载：`base_system::config::load_or_create_with_base`
- 数据目录：CLI `--data-dir` 可改配置/日志位置（Docker 友好）

### 5.2 与输出相关的配置项（`Config`）

| 配置键 | 默认（代码） | 含义 |
|--------|--------------|------|
| `save_path` | `""` → 当前工作目录 | 保存根目录 |
| `novel_format` | `"epub"` | `txt` / `epub` / `pdf` |
| `bulk_files` | `false` | TXT 散装（每章一文件） |
| `ask_format_after_download` | `false` | 下载后询问格式 |
| `allow_overwrite_files` | `true` | 是否允许覆盖已存在输出 |
| `auto_clear_dump` | `true` | 完结+全书+全成功后清缓存 |
| `preferred_book_name_field` | `book_name` | 书名字段偏好 |
| `use_official_api` | `true` | 官方/第三方正文 |
| `api_endpoints` | `[]` | 第三方地址池 |
| `max_workers` | `1` | 并发线程数 |
| `request_timeout` | `15` 秒 | 超时 |
| `max_retries` | `3` | 重试次数 |
| `min_wait_time` / `max_wait_time` | 1000 / 1200 ms | 退避窗口 |

### 5.3 路径约定

| 类型 | 规则 | 符号 |
|------|------|------|
| 缓存/状态目录 | `{save_dir}/{book_id}/`（**只用 ID，不用书名**） | `book_paths::book_folder_path`, `Config::canonical_status_folder_path` |
| 状态文件 | `status.json` | `BookManager::save_download_status` |
| 断点日志 | `downloaded_chapters.jsonl` | `RESUME_JOURNAL_FILE` |
| 封面 | `cover.jpg` 等（稳定 stem） | `book_paths::COVER_FILE_STEM` |
| 最终 TXT | `{save_dir}/{safe_book_name}.txt` | `prepare_output_path` |
| 散装 TXT | `{save_dir}/{safe_book_name}/0001_标题.txt` + `0000_书籍信息.txt` | `finalize_txt` + `bulk_files` |
| EPUB/PDF | `{save_dir}/{safe_book_name}.epub|.pdf` | 同上 |
| 有声 | `{书名}_audio/0001-章节.mp3` | README / audio_generator |

`safe_fs_name`：清洗非法文件名字符，截断长度 120。

**设计亮点：** 缓存目录只认 `book_id`，避免改名导致多目录；最终导出文件仍用书名。旧版 `{book_id}_{book_name}` 会迁移合并到稳定目录。

### 5.4 TXT 内容形态

单文件头部示例字段：书名、作者、`book_id=`、状态、评分、字数、章节数、分类、标签、简介，分隔线后按章：

```
章节标题

　　正文段落...
```

失败章内容为 `[本章下载失败]`（finalize 阶段占位）。

---

## 6. 断点续传、并发、错误重试

### 6.1 断点续传

| 机制 | 说明 |
|------|------|
| 内存 map | `BookManager.downloaded: chapter_id → (title, Option<content>)` |
| 全量快照 | `status.json` 含元数据 + downloaded（体积大但可恢复） |
| 追加日志 | 每成功一章 `append_downloaded_chapter` 写 JSONL；崩溃时比 status 更「实时」 |
| 加载顺序 | status.json → merge jsonl（jsonl 可补 status 未 flush 的章） |
| 续传判定 | `pending_resume`：缺成功内容即待下；失败章可 `FailedOnly` 或 `RetryFailed` 再下 |
| Full 模式 | `manager.downloaded.clear()` 后重下 |

### 6.2 并发

| 点 | 默认/规则 |
|----|-----------|
| `max_workers` | 默认 **1**（README 明确劝阻盲目加线程，防压垮 API） |
| 章节分组 | 15～25 章一组，组为任务单元 |
| 实现 | `crossbeam_channel` 任务队列 + 多线程 worker |
| 段评 | 独立 `segment_comments_workers`（默认 32），与正文可并行 |
| Web 任务 | **全局仅 1 个活跃下载任务**（防滥用） |
| TTS | `audiobook_concurrency` 默认 24 |

### 6.3 错误重试

| 场景 | 策略 |
|------|------|
| Web 目录 | max_retries + 指数退避（上限约 3s）+ 403 预热 + 本地缓存 |
| 官方正文 Cooldown | `fetch_with_cooldown_retry` 最多 6 次，1.1s→8s |
| 官方组失败 | 整组 deferred，后续批/单章重试 |
| 第三方 | 轮询 endpoint；无有效内容则剔除该 endpoint；`sleep_backoff` 指数（受 min/max_wait_time 约束） |
| 失败章二次机会 | `RetryFailed::Decide`（Web 默认自动再试一轮；CLI 可交互） |
| 取消 | `AtomicBool` cancel flag，worker 与主循环检查 |

### 6.4 进度

- `ProgressSnapshot` 上报 group/chapter/段评/有声阶段
- Web：`jobs.set_progress`；TUI：回调；CLI：indicatif 进度条（单 worker 时）

---

## 7. 对我们 App 可借鉴点 vs 不要照搬点

### 7.1 可借鉴（流程 / 数据 / 配置）

1. **主链路分层清晰**  
   `parse id → plan(目录+元数据) → 状态管理 → 拉正文 → finalize(TXT)`  
   与 UI 壳解耦：`download_with_plan_flow` 可直接对应 Android 用例层。

2. **book_id 解析规则**  
   纯数字 / `book_id=` / `/page/{id}` / 白名单短链跳转；适合分享粘贴场景。

3. **稳定缓存键用 book_id**  
   状态目录、续传文件不绑书名，避免改名分裂。

4. **双写断点**  
   内存 + 周期 `status.json` + 每章 append JSONL（或 Room/SQLite 等价物）。

5. **章节引用模型**  
   `ChapterRef { id, title }` 足够轻；`DownloadedMap` 成功/失败三分态清晰。

6. **分组批量拉取**  
   15～25 一节一组，降低 RTT；默认并发 1，可配置，避免默认打爆。

7. **正文与导出分离**  
   缓存保留较「富」格式（XHTML），导出 TXT 时再 `clean_plain`——便于以后加 EPUB 而不重下。

8. **Web 目录/书信息作为可实现路径**  
   公开页面 + directory API + HTML 内嵌 JSON 解析策略（`__NEXT_DATA__` 优先）比闭源 official crate 更可在 App 内复现。

9. **配置项白名单**  
   `save_path`、`max_retries`、`request_timeout`、`max_workers`、输出格式——MVP 只需其中一小撮。

10. **失败占位不丢目录顺序**  
    失败章仍进 finalize 顺序，占位文案，便于用户知道缺哪章。

### 7.2 不要照搬

| 项 | 原因 |
|----|------|
| TUI / WebUI / Docker 整壳 | 产品是 Android 单 App，不是本地下载器 |
| Termux 部署路径 | 已决策不做主架构 |
| `tomato-novel-official-api` + Network-Core 动态库 | 闭源/不可见，无法合规移植进 App |
| 默认依赖「神秘第三方地址池」 | 地址/token 不开源，且有合规与稳定性风险 |
| EPUB/PDF/段评/有声/媒体转码全家桶 | 超出「最小 TXT」MVP |
| 高默认并发、段评 32 线程等 | 移动端电量/风控不友好 |
| CLI 防滥用策略本身 | 可学思想，但 App 内交互不同 |
| 自更新 / hotfix / GitHub Release 检查 | 与应用商店更新模型冲突 |

---

## 8. MVP 最小移植清单（链接 → TXT）

若 App 只做 **「粘贴链接/ID → 下载为 TXT」**，最少需要理解/复现的能力：

### 必做能力

| # | 能力 | 参考符号 / 行为 |
|---|------|-----------------|
| 1 | **ID 解析** | `parse_book_id` +（可选）`resolve_book_id` 短链 |
| 2 | **拉书信息** | `GET fanqienovel.com/page/{id}` + 解析 `__NEXT_DATA__` / 兜底字段 |
| 3 | **拉章节目录** | `GET .../api/reader/directory/detail?bookId=` + 解析 `chapterList` / `chapterListWithVolume` |
| 4 | **章节模型** | `id` + `title` 列表，保持顺序 |
| 5 | **正文获取** | **需自建合法/可用数据源策略**（见风险）；本仓库无完整可用的默认正文源实现 |
| 6 | **正文清洗** | HTML/XHTML → 纯文本段落（可参考 `clean_plain`） |
| 7 | **落盘 TXT** | 书名头信息 + 按章拼接；`safe_fs_name` |
| 8 | **基础重试** | 超时、有限次重试、退避；失败章记录 |
| 9 | **最小断点** | 按 chapter_id 记录已成功内容，杀进程可续 |

### 建议一并做的「小增强」（仍属 MVP 周边）

- 并发默认 1，分组大小可配置但默认保守
- 目录请求节流（如 ≥800ms）与 403 时打开书页预热
- 用户可见进度：已下章数 / 总章数

### MVP 明确不做

- EPUB/PDF/TTS/段评/搜索
- Official-API crate / 动态库
- WebUI 任务系统
- 散装多文件（除非产品需要）

### 关键缺口（对齐时必须正视）

> **正文（content）路径在本开源树中没有「开箱即用」的官方明文实现。**  
> Web 层只可靠地提供 **元数据 + 目录**；正文依赖：  
> (a) 闭源 Official-API + Network-Core，或  
> (b) 用户配置的第三方 `api_endpoints`。  
> 产品若「自研最小 TXT 下载」，Align 阶段必须单独定义：**正文数据来源、合规边界、失效降级**。

---

## 9. 风险清单

### 9.1 闭源 / 不可见组件

- `Tomato-Novel-Official-API`：路径依赖，浅克隆中不存在实现源码。
- `Tomato-Novel-Network-Core`：动态库，协议/签名不可审计。
- 第三方 API 地址与 token：作者声明不开源。
- **结论：** 不能把「能跑 Release 二进制」等同于「可合法嵌入我们 App 的可维护源码」。

### 9.2 接口失效

- README 已警示 API 随时失效、高峰限流、「不要 VPN/代理」、不建议 >1500 章等。
- Web HTML 结构（`__NEXT_DATA__` class 名）变更会导致书信息解析失败。
- directory API 403/风控。
- 第三方地址池单点失效 → 需探测剔除（`validate_endpoints` 思路可借鉴）。

### 9.3 合规与产品风险

- 项目免责声明：仅学习研究；禁止转载传播下载内容；侵权责任自负。
- 番茄小说内容受著作权与平台 ToS 约束；App 内下载功能需法务/产品边界（个人阅读？是否默认开启？是否仅用户自有内容？）。
- 逆向官方 API / 使用不明第三方中转可能涉及 ToS、数据安全、用户隐私（IID/设备指纹等，official 路径侧有 IID 预热）。
- 高并发爬取可能触发封禁，并影响其他用户。
- Android 上明文存全文：存储权限、备份泄露、应用商店审核政策。

### 9.4 工程风险

- Rust 工具链与 Android Kotlin/Java 栈不同——只借鉴算法与流程，不建议整仓嵌入。
- 默认 `novel_format=epub` 与我们的 TXT 目标不一致，移植时别照抄默认值。
- `status.json` 内嵌全文会导致状态文件巨大；移动端更宜 SQLite/分文件。

---

## 10. 关键文件速查表

| 主题 | 相对路径 | 关键符号 |
|------|----------|----------|
| ID 解析 | `src/base_system/book_id.rs` | `parse_book_id`, `resolve_book_id` |
| 配置 | `src/base_system/context.rs` | `Config`, defaults, `default_save_dir` |
| 路径 | `src/base_system/book_paths.rs` | `book_folder_path` |
| Web 网络 | `src/network_parser/network.rs` | `FanqieWebNetwork` |
| 计划 | `src/download/plan.rs` | `prepare_download_plan` |
| 下载编排 | `src/download/downloader.rs` | `download_with_plan_flow`, `build_dynamic_chapter_groups` |
| 第三方正文 | `src/download/third_party.rs`, `src/third_party/content_client.rs` | `fetch_group_third_party` |
| 状态/断点 | `src/book_parser/book_manager.rs` | `load_existing_status`, `append_downloaded_chapter` |
| 解析 | `src/book_parser/parser.rs` | `ContentParser` |
| 导出 | `src/book_parser/finalize_utils.rs` | `run_finalize`, `finalize_txt` |
| Web 任务 | `src/ui/web/routes/jobs.rs` | `create_job` |
| 说明 | `README.md` | 双构建模式、免责、Termux/WebUI |

---

## 11. 给后续 Align / Plan 的一句话建议

**借鉴「解析 → 目录计划 → 带断点的分章拉取 → TXT 导出」的状态机与路径/解析细节；正文数据源与合规策略必须在 Align 单独拍板，不能默认依赖本仓库的 official/第三方闭源部分；架构上坚持 Android 进程内最小实现，不引入 Termux/本地 WebUI 壳。**
