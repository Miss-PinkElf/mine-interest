# B站 + 番茄小说 手机插件 State（状态）

## Metadata（元数据）

- 更新时间（Updated At）：2026-08-07 18:22:06 CST
- 作者（Author）：Grok
- 关联 mission：bilibili-fanqie-mobile-plugin
- 当前状态（Status）：主线 B站可用性；番茄增强已延期落盘
- 文档边界：短当前态快照。

## 当前目标

Kotlin Android 单 App：优先打通 **B站** 一体式下载；番茄维持链接/短链 + 自配端点。

## 当前阶段

- Apply 源码已有；B站 403 缓解已提交本地（`ba63d16`，可能未 push）
- 番茄 Official-API / 搜书名 / 零配置：**延期**（见 deferred 单条）
- 完整 Close：禁止

## 下一步

1. **B站**：装新 APK 复测；看失败是「获取媒体流」还是「CDN 403」；继续修一体式或评估 Cookie/yt-dlp 延期
2. 番茄：不扩 Official-API；仅 bug/短链类
3. 推送 APK/代码按用户要求

## 延期入口

- `deferred/番茄-Official-API与搜书名零配置正文.md`
- `deferred/b站-外部引擎-yt-dlp-ffmpeg.md`
- `deferred/mvp-与延期范围总表.md`
