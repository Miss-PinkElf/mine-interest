# 下次会话提示词 — bilibili-fanqie-mobile-plugin

> 复制本文件全文到新对话即可恢复。

---

## 你是谁 / 流程

- mission：`bilibili-fanqie-mobile-plugin`（devflow）  
- 分支：`rin-bilibili-fanqie-mobile/dev`  
- 简体中文；术语中英双语  
- **完整 Close 勿擅自做**  

---

## 先读（热路径）

1. `.devflow/bilibili-fanqie-mobile-plugin/state.md`  
2. `.devflow/bilibili-fanqie-mobile-plugin/checkpoints.md`  
3. `handoffs/2026-08-07-003-bili-ok-audio-volume-bug.md`  
4. **`bug-log.md` → BUG-001（音量偏小，本次优先）**  
5. 范围：`deferred/mvp-与延期范围总表.md`  

---

## 一句话进度

**B站已能成功下载，切换目录正常；导出声音偏小（BUG-001）下次优先修。番茄 Official-API/搜书名/零配置已延期。**

---

## 下次优先任务

1. **修复 BUG-001：B站导出音频音量偏小**  
   - 现象：下载成功，听感音量小  
   - 初判：m4a 源轨/未 loudnorm；或听了旁路/仅视频轨  
   - 代码：`BiliExporter` / `BiliStreamClient`  
   - 详见 `bug-log.md`  
2. 复测 mp3 选项（实为 m4a）与 mp4  
3. 需要时打 APK / push（问用户）  

## 不要做

- 番茄 Official-API、搜书名、内置 token（见 `deferred/番茄-Official-API与搜书名零配置正文.md`）  
- yt-dlp 引擎（除非用户改口）  
- main 开发；未授权 Close  

## 已锁定

- 单 App Kotlin；入口三件套 + 批量  
- B站一体式；番茄自配端点  
- 个人自用  

## 一键开场

```text
继续 mission bilibili-fanqie-mobile-plugin。
先读 state、checkpoints、handoff 003、bug-log BUG-001。
分支 rin-bilibili-fanqie-mobile/dev。
优先修复 B站导出音频音量偏小；不要做番茄 Official-API 延期包。
```
