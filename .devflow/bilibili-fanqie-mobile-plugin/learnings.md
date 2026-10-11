# Learnings（经验）

## Metadata（元数据）

- 创建时间（Created At）：2026-08-07 17:45:25 CST
- 更新时间（Updated At）：2026-10-11 12:03:00 +08:00。
- 作者（Author）：原记录 Grok；本轮维护 Codex。
- 目的（Purpose）：沉淀实现及源码调查经验。
- 关联仓库或项目（Related Repository / Project）：mine-interest-bilibili。
- 当前状态（Status）：持续维护。
- 关联 mission：bilibili-fanqie-mobile-plugin
- 文档边界：踩坑与可复用经验；非规格。

## 条目

### L001 - Mac 上有 SDK 目录不等于能 assemble

- 现象：`local.properties` 指向 `~/Library/Android/sdk` 仍失败。  
- 原因：Platform 包未下完（仅有 `.installer`）、或 build-tools 版本与 AGP/compileSdk 不匹配（曾缺 34.0.0，本机有 36.0.0）。  
- 处理：`compileSdk=36` + `buildToolsVersion=36.0.0`；用户需在 SDK Manager 装齐 **Platform 36**。  
- 验证：存在 `platforms/android-*/android.jar` 后再 `./gradlew :app:assembleDebug`。

### L002 - Gradle 官方分发与 Google Maven 可能超时

- 现象：wrapper 下 Gradle、解析 AGP 超时。  
- 处理：`settings.gradle.kts` 增加阿里云 google/public/gradle-plugin 镜像；`networkTimeout` 加大；必要时本地 `file://` 指向已下好的 gradle zip（勿提交本机路径）。

### L003 - B站/番茄接口不要散落

- B站流地址集中 `BiliStreamClient`；番茄目录集中 `FanqieWebCatalogClient`；正文端点用户配置，禁止硬编码闭源 token。

### L004 - B站一体式用户验收通过；音量问题单独记 bug

- 用户确认：下载成功、切换目录成功。
- 音量偏小记 BUG-001，勿与 403 混为一谈。
- 当时番茄增强依赖外部 Official-API，已结构化延期，优先 B站；2026-10-11 新探索发现其他公开路线，不能沿用为所有零配置实现的定论。

### L005 - 当前浅克隆不能代表所有公开历史

- 现象：初次仅看 POf-L 当前版本，遗漏公开 Python 下载器及 CLI。
- 原因：当前核心迁移私有，浅克隆未包含移除前版本。
- 处理：补齐历史，固定 `5a8f875`，分别写当前 / 历史事实；不切换或覆盖参考目录当前 HEAD。

### L006 - 下载编排、正文来源、运行成功分别核验

- 现象：缺正文依赖被过度概括成没有公开思路；页面 HTTP 200 容易被误认成全文成功。
- 原因：混淆模块边界和证据层级。
- 处理：追踪目录 → 请求 → 解析 → 缓存 → 导出；分别核验服务或外部 crate。README 功能声明、作者回复、源码和实际运行使用不同标签；未运行不声称成功。

### L007 - 首版未讨论不等于明确延期

- 现象：新会话可能把候选路线及未讨论登录 / 搜索范围当作已批准。
- 原因：将本轮纯探索与原 App 规格混用。
- 处理：独立落盘首版议题、原延期与后续触发；方向确认后才写计划。公开思路能参考不等于已取得所有代码复制授权。
