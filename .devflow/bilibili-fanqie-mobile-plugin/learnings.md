# Learnings（经验）

## Metadata（元数据）

- 创建时间（Created At）：2026-08-07 17:45:25 CST
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
