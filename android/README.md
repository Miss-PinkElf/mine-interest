# Mine Media — B站 + 番茄小说 Android 工具

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| 目的（Purpose） | 说明如何构建、配置与使用本 App |
| 关联 mission | `bilibili-fanqie-mobile-plugin` |
| 状态（Status） | MVP 实现中 |
| 边界 | 个人设备本地自用；非商店上架产品 |

## 是什么

Kotlin 单 App，链接驱动：

1. **B站**：分享 / 剪贴板 / 手动（可批量）→ 导出 mp3 选项（实为 m4a 降级）或 mp4、可选字幕、自定义目录  
2. **番茄**：同上入口 → 目录 + 可配置正文端点 → 合并 TXT  

不依赖 Termux 常驻服务。

## 环境要求

- JDK 17  
- Android SDK（`compileSdk` 34+，建议安装 platform 与 build-tools）  
- 真机调试推荐  

## 打开工程

1. Android Studio 打开本目录 `android/`（不是仓库根）。  
2. 或命令行：

```bash
cp local.properties.example local.properties
# 编辑 sdk.dir=/Users/你/Library/Android/sdk

./gradlew :core:test :provider-bili:test :provider-fanqie:test :app:assembleDebug
```

Debug APK 一般在：

`app/build/outputs/apk/debug/app-debug.apk`

## 使用说明

1. 安装 APK 后打开 **Mine Media**。  
2. **B站选项**：格式 mp3/mp4、码率、视频高度、字幕；点「B站目录」选保存位置（SAF）。  
3. **番茄**：在「正文 API 端点」填写个人可用模板，**必须包含** `{item_id}`，例如：  
   `https://your-endpoint.example/content?item_id={item_id}`  
   未配置时番茄任务会失败并提示去设置填写。  
4. **手动批量**：多行粘贴链接 →「解析并开始」。无法识别的行会 Toast 跳过数量。  
5. **分享**：在 B站/番茄 App 分享到 Mine Media。  
6. **剪贴板**：打开 App 时若开关开启，检测一次是否像有效链接并询问。  

## 模块结构

| 模块 | 职责 |
|------|------|
| `app` | UI、分享入口、前台服务、SAF 写盘 |
| `core` | LinkParser / TaskRunner / 模型 |
| `provider-bili` | 一体式 B站下载（流地址集中在 `BiliStreamClient`） |
| `provider-fanqie` | 番茄目录 + 可配置正文 + TXT |

## 合规

个人本地自用。请遵守 B站 / 番茄平台协议与版权法；勿用于公开盗版分发。仓库内**不**硬编码闭源 token。

## 已知限制（MVP）

- B站接口非官方，可能漂移；音频 mp3 常降级为 m4a；DASH 音视频旁路保存，未必完美合并。  
- 番茄正文依赖你配置的端点；目录接口可能变更。  
- 任务列表默认内存态，杀进程可能丢失队列。  
- 前台服务用于降低下载被杀概率。  
