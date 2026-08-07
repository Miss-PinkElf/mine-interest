# 下次会话提示词 — bilibili-fanqie-mobile-plugin

> 复制本文件全文到新对话即可恢复。勿在 Apply 验证完成且用户允许前做完整 Close。

---

## 你是谁 / 用什么流程

- 仓库 worktree：`mine-interest-bilibili-fanqie`  
- 协作：简体中文；术语中英双语；相对路径  
- mission：`bilibili-fanqie-mobile-plugin`（**devflow**）  
- 分支：**`rin-bilibili-fanqie-mobile/dev`**（禁止 main）  
- 硬门禁：有新鲜验证证据才能宣称完成；完整 Close 需用户允许  

---

## 先读什么（恢复热路径）

1. `.devflow/bilibili-fanqie-mobile-plugin/state.md`  
2. `.devflow/bilibili-fanqie-mobile-plugin/checkpoints.md`  
3. `.devflow/bilibili-fanqie-mobile-plugin/handoffs/2026-08-07-002-apply-code-ready-verify-pending.md`  
4. 范围：`deferred/mvp-与延期范围总表.md`  
5. 构建：`android/README.md`  

深度需要再读：`spec/tasks.md`、`plans/*`、`learnings.md`  

---

## 当前进度（一句话）

**Apply 全 Task 源码已写完；SDK Platform 未齐导致未通过 gradle 验证；下一步装 Platform 36 → 测试+assemble → 真机验收。**

---

## 已锁定方案（勿重新辩论）

| 项 | 结论 |
|----|------|
| 形态 | Android 单 App，链接驱动 |
| 入口 | 分享 + 打开剪贴板一次 + 手动批量 |
| B站 | 一体式；yt-dlp+ffmpeg **延期**；mp3 可降级 m4a |
| 番茄 | App 内 TXT；可配置正文端点；禁硬编码 token |
| 技术 | Kotlin；core 与 UI 解耦 |
| 验收 | APK 真机手工测 |

---

## 未完成任务

1. 安装 Android SDK **Platform 36**（`compileSdk=36`，build-tools 36.0.0）  
2. `cd android && ./gradlew :core:test :provider-bili:test :provider-fanqie:test :app:assembleDebug`  
3. 修编译/测试失败（若有）  
4. 真机：分享 / 剪贴板 / 批量 / B站 / 番茄（端点已配）  
5. 用户允许后完整 Close  

---

## 延期（不要做进「顺手」）

见 `deferred/mvp-与延期范围总表.md`：yt-dlp+ffmpeg、Termux 主架构、iOS、后台剪贴板监听、RN 壳、番茄 TTS/整站爬取、硬编码 token、任务 DB 持久化等。

---

## 建议本对话优先做

1. 确认分支 `rin-bilibili-fanqie-mobile/dev`  
2. 确认 `platforms/*/android.jar` 存在  
3. 跑 gradle 验证并贴结果  
4. 出 APK 真机测  

---

## 禁止

- main 开发  
- 无用户允许的完整 Close  
- 把延期当 MVP 做  
- 硬编码闭源 token  
- 无验证证据宣称交付  

---

## 一键开场示例

```text
继续 mission bilibili-fanqie-mobile-plugin。
先读 state.md、checkpoints.md、handoffs/2026-08-07-002。
分支 rin-bilibili-fanqie-mobile/dev。
优先：装齐 Platform 36 后跑 gradle 测试与 assembleDebug，再真机验收。
不要完整 Close，除非我明确允许。
```
