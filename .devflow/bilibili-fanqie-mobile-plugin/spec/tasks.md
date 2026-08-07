# Tasks — B站 + 番茄小说 Android 工具

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| 创建时间（Created At） | 2026-08-07 17:10:28 CST |
| 更新时间（Updated At） | 2026-08-07 18:10:00 CST |
| 作者（Author） | Grok |
| 目的（Purpose） | 可勾选实施任务清单；与 plan 12 Task 对齐 |
| 关联 mission（Related Mission） | bilibili-fanqie-mobile-plugin |
| 当前状态（Status） | Apply 源码已齐；构建验证待完整 SDK platform |
| 文档边界（Scope / Boundary） | tasks artifact |
| 开发分支（Branch） | `rin-bilibili-fanqie-mobile/dev` |

> 未经用户允许 **不得** `git commit`。

---

## 任务清单

### Task 1: Android 多模块工程骨架

- [x] 1.1 创建 `android/` Gradle 多模块
- [x] 1.2 最小可安装 App（MainActivity + UI）
- [ ] 1.3 本地验证 assembleDebug（**待 platform/build-tools 与 AGP 对齐完成**）
- [ ] 1.4 询问是否提交

### Task 2: 领域模型与 Provider 接口

- [x] 2.1–2.3 模型 / 接口 / 常量
- [ ] 2.4 编译验证（待 SDK）

### Task 3: LinkParser（单条 + 批量）

- [x] 3.1–3.2 测试 + 实现
- [ ] 3.3 测试执行（待 SDK）

### Task 4: 保存路径策略与任务仓库

- [x] 4.1–4.2 SavePathPolicy + InMemoryTaskRepository
- [ ] 4.3 测试执行（待 SDK）

### Task 5: TaskRunner 编排

- [x] 5.1–5.3 enqueue / enqueueBatch + 测试源码

### Task 6: B站 — ID 解析与短链解跳

- [x] 6.1 BiliIdResolver + 单测
- [x] 6.2 短链 resolveToBvid
- [x] 6.3 BiliDownloadProvider

### Task 7: B站 — 一体式下载导出 MVP

- [x] 7.1 BiliStreamClient
- [x] 7.2 BiliExporter + 字幕
- [x] 7.3 BiliDownloadProvider 串联
- [ ] 7.4 真机手工验收（用户环境）

### Task 8: 番茄 — book_id 与目录

- [x] 8.1 FanqieBookIdResolver + 单测
- [x] 8.2 FanqieWebCatalogClient
- [x] 8.3 fixture 解析测试

### Task 9: 番茄 — 正文 + 断点 + TXT

- [x] 9.1 ContentFetcher + ConfigurableHttpContentFetcher
- [x] 9.2 ChapterStore + TxtFinalizer
- [x] 9.3 FanqieDownloadProvider
- [x] 9.4 未配置端点中文错误

### Task 10: App 入口与极简 UI

- [x] 10.1 Manifest 分享与权限
- [x] 10.2 ShareReceiverActivity
- [x] 10.3 剪贴板一次检测
- [x] 10.4 多行手动 + 选项 + 任务列表
- [x] 10.5 ServiceLocator
- [ ] 10.6 真机手工验收 S1–S5、S8

### Task 11: 前台服务

- [x] 11.1 DownloadForegroundService + Manifest
- [x] 11.2 任务结束后 stopSelf
- [ ] 11.3 真机后台验证

### Task 12: 文档与阶段记录

- [x] 12.1 android/README.md
- [x] 12.2 Align 标准对照见 README / state
- [x] 12.3 state / checkpoint 更新
- [ ] 12.4 完整 Close（仅用户允许后）

---

## 验证

```bash
cd android
# local.properties 中 sdk.dir 已指向本机 SDK
# 需安装 Android SDK Platform（建议 36）与匹配 build-tools
./gradlew :core:test :provider-bili:test :provider-fanqie:test :app:assembleDebug
```

当前机器曾报错：`Failed to find Build Tools revision 34.0.0` / platform 未装全；工程已改为 `compileSdk=36` + `buildToolsVersion=36.0.0`（与本机已有 build-tools 对齐）。

### 禁止偷做

- yt-dlp+ffmpeg、Termux 主架构、RN 壳、硬编码 token、未授权 commit、Apply 前完整 Close
