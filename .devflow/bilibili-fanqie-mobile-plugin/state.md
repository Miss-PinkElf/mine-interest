# B站 + 番茄小说 手机插件 State（状态）

## Metadata（元数据）

- 更新时间（Updated At）：2026-08-07 18:28:48 CST
- 作者（Author）：Grok
- 关联 mission：bilibili-fanqie-mobile-plugin
- 当前状态（Status）：B站主路径已通；音频音量 bug 待修；会话交接
- 文档边界：短当前态快照。

## 当前目标

Kotlin Android 单 App：B站可配置导出 + 番茄 TXT（自配端点）；个人自用。

## 当前阶段

- Align / Plan / Propose / Apply：完成
- **B站 Verify（用户）**：下载成功；切换保存目录成功
- **已知 bug**：导出音频 **音量偏小**（BUG-001，下次修）
- 番茄：短链已修；Official-API/搜书名/零配置 **延期**
- 完整 mission Close：**不做**（仍有 bug + 番茄端点依赖）

## 下一步（新会话）

### 2026-10-11 探索（Explore）更新

- 新需求：`zzz-prompt-debug/下载番茄b站/prompt-1.md`；查找番茄小说批量下载详细方法。
- 两参考项目已克隆；调研见 `references/番茄小说批量下载方法调研-2026-10-11.md`。
- 最新目标：复用公开方法到自己的软件或命令行工具（CLI）；新增七份公开项目克隆。
- 最新证据：`references/两个指定项目下载源码追踪-2026-10-11.md`；POf-L 历史版有 Python 下载器和批量 CLI，Tomato 当前下载编排公开，正文服务或底层依赖待验证。
- 新增证据：`references/yinian与Gavin下载源码对比-2026-10-11.md`；两新增仓库核心公开，但均依赖第三方正文且有具体实现问题，未运行验证。
- 后续：先确认接受自配正文服务还是要求独立正文获取，再对齐 CLI 路线与计划；旧节点实测、业务实施和全本批量验证延期，触发条件见 D022。

### 原有后续事项

1. 修 BUG-001 音量偏小（先复现、定位主文件/旁路轨/增益）
2. 按需补测 mp3/mp4/字幕
3. 番茄维持现状，不扩 Official-API

## 延期 / Bug 入口

- `bug-log.md` → BUG-001
- `deferred/番茄-Official-API与搜书名零配置正文.md`
- `deferred/b站-外部引擎-yt-dlp-ffmpeg.md`
- `deferred/mvp-与延期范围总表.md`

## 最新 handoff

`handoffs/2026-08-07-003-bili-ok-audio-volume-bug.md`
