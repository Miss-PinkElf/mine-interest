# Proposal — B站 + 番茄小说 Android 个人工具 App

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| 创建时间（Created At） | 2026-08-07 17:10:28 CST |
| 作者（Author） | Grok |
| 目的（Purpose） | 将已确认 Align/Plan 正式落成 proposal，作为 Apply 门禁输入之一 |
| 关联仓库或项目（Related Repository / Project） | mine-interest-bilibili-fanqie |
| 关联 mission（Related Mission） | bilibili-fanqie-mobile-plugin |
| 当前状态（Status） | 已批准进入 Apply（用户授权：先 propose 再写代码） |
| 文档边界（Scope / Boundary） | 正式 lifecycle artifact；与 plan 一致；**不是**实现代码 |
| 关联 Align | `.devflow/bilibili-fanqie-mobile-plugin/plans/2026-08-07-bilibili-fanqie-mobile-align.md` |
| 关联 Plan | `.devflow/bilibili-fanqie-mobile-plugin/plans/2026-08-07-bilibili-fanqie-mobile-plan.md` |
| 开发分支（Branch） | `rin-bilibili-fanqie-mobile/dev` |

---

## 背景

用户需要在 **Android 手机** 上，用 **一个个人自用工具 App** 完成两类下载：

1. **B站（Bilibili）**：从分享/链接拿到视频，按选项导出 **mp3 / mp4**（码率或清晰度、字幕、自定义目录）。
2. **番茄小说（Fanqie）**：从分享/链接拿到小说，下载为 **TXT** 到自定义目录。

已排除的主路径：系统注入插件、Termux 常驻本地 Web 服务、iOS 首发。Align 与详细 Plan（12 Task）已落盘；本 proposal 固化「为什么做 / 做什么 / 不做什么」。

---

## 目标

交付可 sideload 的 **Kotlin Android 单 App**，成功标准对齐 Align S1–S8：

| 编号 | 标准 |
|------|------|
| S1 | 系统分享 / 打开时剪贴板一次检测 / 手动粘贴 三种入口 |
| S2 | 识别 B站 vs 番茄，进入对应任务流 |
| S3 | B站：mp3/mp4、码率或清晰度、字幕开关、自定义保存目录 |
| S4 | 番茄：book_id/链接 → 下载 → TXT 到自定义目录 |
| S5 | 任务状态（排队/进行中/成功/失败）与错误提示 |
| S6 | **不依赖** 用户日常 Termux 本地服务 |
| S7 | 下载核心与 UI 解耦，Provider 可替换 |
| S8 | 手动入口 **批量解析**：多条链接分别入队，单条失败不阻断其它条 |

验收偏好：`assembleDebug` 出 APK → **真机手工测**（模拟器可选）。

---

## 范围

### 产品形态

- Android **单 App**（非 Xposed/系统注入）
- 链接驱动：分享 + 冷启动/打开时读剪贴板一次 + 手动（多行批量）
- UI 极简；**下载核心优先**

### 技术范围

- Kotlin + Android Gradle 多模块：`app` / `core` / `provider-bili` / `provider-fanqie`
- 代码根目录：`android/`
- B站：**一体式** 实现（`BiliStreamClient` 单点承载接口漂移）
- 番茄：App 内自研 TXT；流程借鉴 Tomato-Novel-Downloader；**可配置** `ContentFetcher` 端点
- 任务编排：`LinkParser`（含 `parseBatch`）、`TaskRepository`、`TaskRunner`（含 `enqueueBatch`）

### 合规边界

- 个人设备本地自用；不做公开盗版分发能力
- **禁止** 在仓库硬编码未开源第三方 token

---

## 非目标

见 `deferred/mvp-与延期范围总表.md`，摘要：

- B站 `yt-dlp + ffmpeg` 外部引擎（延期单条已记）
- Termux / 本地 Web 服务作为主架构
- iOS、后台常驻剪贴板监听、系统注入
- RN/Flutter 首发壳
- 番茄 TTS、书架订阅、整站/收藏夹级爬取
- 「一键同步 Tomato 上游全部能力」
- 完整 mission Close 在 Apply 前宣称完成；未经允许的 git commit

---

## 边界场景

| 场景 | 期望行为 |
|------|----------|
| 单条无法识别 | 记跳过/失败提示，**不阻断**同批其它有效条 |
| 本批重复链接 | 按 platform+idHint+canonicalUrl 去重 |
| 批量 B站选项 | 本批共用当前 UI 的 format/码率/字幕/目录 |
| B站无字幕 | 任务仍可成功，message 提示无字幕 |
| B站 mp3 设备能力不足 | 允许降级 m4a，UI 标明 |
| 番茄未配置正文端点 | 任务失败，message 明确指导去设置填写 |
| 短链 b23.tv | LinkParser 只分类；解跳转在 Bili Provider |
| 杀进程 | MVP 内存任务可丢失（可接受） |
| 接口漂移 | 只改对应 Client，不改 `DownloadProvider` 接口形状 |

---

## 开放问题（实现期处理，不阻塞 Apply）

1. B站具体 HTTP 路径随平台变化 → 集中在 `BiliStreamClient`
2. 番茄正文端点模板格式（`{item_id}` 等）→ 设置页配置
3. minSdk / SAF 细节 → 搭工程时定（建议 minSdk 26+）
4. 复杂账号登录拿更高清 → MVP 默认不做
5. 前台服务（Task 11）→ 可选增强，时间紧可后补

---

## 进入 Apply 条件

- [x] Align 已确认
- [x] Plan 已落盘
- [x] 本 proposal + design + tasks 已写出且与 plan 一致
- [x] 用户选择路径 A 并授权写代码（本会话）

**下一步：** 按 `spec/tasks.md` 与 Plan Task 1→12 顺序实施；默认 **不 commit** 除非用户允许。
