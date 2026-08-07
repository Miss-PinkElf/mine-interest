# Handoff：Apply 源码完成，待 Verify

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| 创建时间（Created At） | 2026-08-07 17:45:25 CST |
| 作者（Author） | Grok |
| 目的（Purpose） | 上下文过长新开对话；记录 Apply 结果与 Verify 阻塞 |
| 关联 mission | bilibili-fanqie-mobile-plugin |
| handoff 编号 | 2026-08-07-002 |
| 是否 superseded 上一份 | 是（001 被本份取代为最新恢复入口） |
| 当前状态（Status） | 交接用（Handoff） |
| 文档边界 | 会话交接；**不**表示已交付；**不**替代 state/plan/spec |
| 开发分支 | `rin-bilibili-fanqie-mobile/dev` |
| 路径类型 | 重型路径（Heavy Path） |

---

## 当前目标

交付可 sideload 的 **Kotlin Android 个人工具 App**：

1. B站：分享/剪贴板/手动批量 → mp3(m4a 降级)/mp4/字幕/目录  
2. 番茄：同上 → 可配置正文端点 → TXT  
3. 不依赖 Termux 主架构  

## 当前阶段

| 阶段 | 状态 |
|------|------|
| Align / Plan | 完成 |
| Propose（spec 三件套） | 完成 |
| Apply（12 Task 源码） | **完成** |
| Verify（gradle + 真机） | **未完成**（SDK Platform 未齐） |
| 完整 Close | **禁止**，待验收后用户允许 |

## 本轮完成内容

- [x] 路径 A：`spec/proposal.md` + `design.md` + `tasks.md`  
- [x] `android/` 多模块：app / core / provider-bili / provider-fanqie  
- [x] LinkParser 批量、TaskRunner、内存任务仓库  
- [x] B站一体式：IdResolver / StreamClient / Exporter / DownloadProvider  
- [x] 番茄：BookId / WebCatalog / ContentFetcher / ChapterStore / TxtFinalizer / Provider  
- [x] UI：MainActivity 批量与选项、ShareReceiver、剪贴板一次、SAF 目录  
- [x] 前台服务 `DownloadForegroundService`  
- [x] `android/README.md`、deferred MVP/延期表更新、learnings  
- [ ] assembleDebug / 单测通过  
- [ ] 真机 S1–S8 验收  
- [ ] 完整 mission Close  

## 对话核对结论

### 已锁定（勿重新辩论）

- 单 App、Kotlin、入口三件套 + 手动批量  
- B站一体式；yt-dlp+ffmpeg **延期**  
- 番茄 App 内自研 + 可配置端点；不硬编码 token  
- 分支 `rin-bilibili-fanqie-mobile/dev`  
- 个人自用合规  

### 第一版 vs 延期

见 `deferred/mvp-与延期范围总表.md`（已含实现状态与触发条件）。

### 未讨论完阻塞

无。开放问题均为实现期/验收期：SDK 装齐、接口是否可用、端点配置。

## 关键决策速查

| ID | 决策 |
|----|------|
| D001 | 重型路径 |
| D008 | 分支 rin-bilibili-fanqie-mobile/dev |
| D010 | 入口三件套 |
| D011 | B站一体式；引擎延期 |
| D012 | 番茄 App 内自研 |
| D013 | Kotlin |
| D015 | 手动批量 |
| D016 | 先 Propose 再 Apply 并授权写代码 |

## 关键路径

| 路径 | 作用 |
|------|------|
| `android/` | 产品代码 |
| `android/README.md` | 构建与使用 |
| `spec/*` | proposal/design/tasks |
| `plans/*` | Align + Plan |
| `deferred/mvp-与延期范围总表.md` | MVP/延期 |
| `zzz-docs/Mac-Android-Kotlin-开发环境安装指南.md` | 环境 |
| `zzz-docs/开源B站视频下载项目调研.md` | B站调研 |

## 风险 / 阻塞

| 项 | 说明 |
|----|------|
| SDK | 需 Platform 36 + build-tools 36；`local.properties` 已示例/本机忽略提交 |
| B站 API | 非官方，可能失败；改 `BiliStreamClient` |
| 番茄 | 未配端点必失败；目录 API 可能变 |
| 验证 | 无新鲜 BUILD SUCCESSFUL / 真机证据，不得宣称交付 |

## 立即下一步

1. 读 `state.md` + `checkpoints.md` + **本 handoff**  
2. SDK Manager 安装 Android SDK Platform 36  
3. `cd android && ./gradlew :core:test :provider-bili:test :provider-fanqie:test :app:assembleDebug`  
4. 真机 APK 验收；失败则 systematic debugging  
5. **勿**完整 Close，除非用户允许；commit 按用户要求  

## 恢复指引

1. 热路径：state → checkpoints  
2. 本 handoff  
3. `android/README.md` + `spec/tasks.md`  
4. 范围：`deferred/mvp-与延期范围总表.md`  

## 可从活跃上下文移除

- Align 早期形态辩论过程  
- Tomato 源码全文  
- Gradle 下载超时逐步排障过程（结论在 learnings）  
