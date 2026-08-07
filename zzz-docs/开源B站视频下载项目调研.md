# 开源 B 站（Bilibili）视频下载项目调研

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| 创建时间（Created At） | 2026-08-07 15:53 |
| 更新时间（Updated At） | 2026-08-07 15:53 |
| 作者（Author） | Grok（调研整理） |
| 目的（Purpose） | 汇总当前可公开检索到的、用于下载 B 站视频的开源项目，便于选型与技术调研；不构成实现方案或已批准计划。 |
| 关联仓库或项目（Related Repository / Project） | `mine-interest` worktree：`mine-interest-bilibili-fanqie` |
| 关联 mission（Related Mission） | 无（独立调研文档；与 `.devflow/bilibili-fanqie-mobile-plugin/` 可能存在后续关联，但本文不绑定 mission） |
| 当前状态（Status） | 候选项（Candidate） |
| 文档边界（Scope / Boundary） | 技术调研备忘，**非**真相源（source of truth），**非**已批准方案（Plan），**不**触发实现（Apply）。链接与 star 数以撰写时公开信息为准，可能随时间变化。 |
| 相对路径 | `zzz-docs/开源B站视频下载项目调研.md` |

---

## 1. 调研结论摘要

- 生态上，B 站视频下载能力大致分两类：
  1. **通用多站点下载器**（如 `yt-dlp`）：命令行友好、维护活跃、适合脚本与集成。
  2. **B 站专用 GUI / 客户端**：交互更友好，功能更贴近收藏夹、稍后再看、弹幕字幕、媒体库刮削等。
- **优先推荐了解**：`yt-dlp`（CLI）、`Bili23-Downloader`（GUI，仍较活跃）。
- **慎用 / 已停更**：`BBDown`（已 archived）、`DownKyi`（律师函后永久关停）。
- 合规风险高：涉及登录态绕过、会员/番剧/课程完整高清、非公开接口适配的工具，近年压力明显增大。

---

## 2. 通用下载器（Multi-site）

### 2.1 yt-dlp

| 项 | 说明 |
|----|------|
| 仓库 | https://github.com/yt-dlp/yt-dlp |
| 形态 | 命令行（CLI） |
| 语言生态 | Python 为主；提供预编译二进制 |
| 特点 | 支持数千站点（含 Bilibili）；维护极活跃；格式选择、批量、播放列表、字幕等能力完整 |
| 适用场景 | 脚本自动化、跨平台批处理、开发者集成 |
| 状态（撰写时） | 活跃维护 |

**基本用法示例：**

```bash
# 安装（示例）
pip install yt-dlp
# 或 macOS
# brew install yt-dlp

# 下载单个视频
yt-dlp "https://www.bilibili.com/video/BVxxxxxx"

# 限制最高清晰度示例（需结合实际 format 列表）
yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]" "URL"
```

### 2.2 lux（原 annie）

| 项 | 说明 |
|----|------|
| 仓库 | https://github.com/iawia002/lux |
| 形态 | 命令行（CLI） |
| 语言 | Go |
| 特点 | 多站点、相对轻量；历史上以 annie 名称传播较广 |
| 适用场景 | 需要 Go 生态或单一二进制分发的场景 |
| 状态（撰写时） | 需以仓库近期提交为准再评估 |

---

## 3. B 站专用（GUI / 桌面）

### 3.1 Bili23-Downloader（优先关注）

| 项 | 说明 |
|----|------|
| 仓库 | https://github.com/ScottSloan/Bili23-Downloader |
| 形态 | 跨平台 GUI |
| 协议 | GPL-3.0 |
| 亮点 | 多线程加速、音视频分离、弹幕与元数据、自定义命名与分类；社区关注度较高（撰写时约 6k+ stars） |
| 适用场景 | 个人本地下载、桌面端日常使用 |
| 状态（撰写时） | 仍在更新（相对活跃） |

### 3.2 BilibiliDown

| 项 | 说明 |
|----|------|
| 仓库 | https://github.com/nICEnnnnnnnLee/BilibiliDown |
| 形态 | GUI，多平台 |
| 亮点 | 稍后再看、收藏夹、UP 主视频批量下载 |
| 适用场景 | 需要批量从「稍后再看 / 收藏夹」拉内容 |
| 状态（撰写时） | 需以仓库近期提交为准再评估 |

### 3.3 bilibili-video-downloader（媒体库向）

| 项 | 说明 |
|----|------|
| 仓库 | https://github.com/lanyeeee/bilibili-video-downloader |
| 形态 | GUI 桌面应用 |
| 亮点 | nfo 刮削、广告标记、字幕/弹幕下载；面向 Emby 等媒体库整理 |
| 适用场景 | 本地媒体库归档（Emby / Jellyfin 等） |
| 状态（撰写时） | 需以仓库近期提交为准再评估 |

### 3.4 BilibiliVideoDownload

| 项 | 说明 |
|----|------|
| 仓库 | https://github.com/BilibiliVideoDownload/BilibiliVideoDownload |
| 形态 | 跨平台桌面（TypeScript / Electron 一类） |
| 亮点 | Windows / macOS / Linux 桌面下载 |
| 适用场景 | 需要图形界面的跨平台客户端 |
| 状态（撰写时） | 需以仓库近期提交为准再评估 |

### 3.5 其他可检索项目（备忘）

| 项目 | 仓库 | 备注 |
|------|------|------|
| BiliDownloader | https://github.com/Harlan-H/BiliDownloader | Dart 实现，见 GitHub topic `bilibili-downloader` |
| bilibili-downloader-gui | https://github.com/j4rviscmd/bilibili-downloader-gui | 跨平台 GUI，无广告宣传 |
| bilibili_downloader | https://github.com/PyJun/bilibili_downloader | JS 相关，社区项目 |
| Bili.TV-Downloader | https://github.com/jjaruna/Bili.TV-Downloader | 面向 bilibili.tv 的 CLI 脚本 |

> 以上「其他」项仅作索引，未逐一深度核验质量与合规边界。

---

## 4. 已停更 / 高风险项目（历史参考）

### 4.1 BBDown

| 项 | 说明 |
|----|------|
| 仓库 | https://github.com/nilaoda/BBDown |
| 形态 | 命令行 |
| 状态 | **已 archived**（约 2026-05-14）；官方说明不再维护与支持 |
| 建议 | 新项目不要依赖；仅作历史方案参考 |

### 4.2 DownKyi（哔哩下载姬）

| 项 | 说明 |
|----|------|
| 仓库 | https://github.com/leiurayer/downkyi |
| 形态 | 桌面 GUI（曾极热门） |
| 状态 | **Deprecated / 永久关停** |
| 原因摘要 | 维护者称 2026-07 收到 B 站委托律师函，指控涉及非公开接口、认证与访问控制、付费内容保护与会员体系等逆向适配与传播 |
| 建议 | **不要用于新产品或二次分发**；仅作行业合规案例记录 |

---

## 5. 选型对照表

| 场景 | 更合适的方向 | 候选 |
|------|--------------|------|
| 命令行 / 脚本 / 自动化 | 通用 CLI | **yt-dlp** |
| 日常桌面 GUI | B 站专用 GUI | **Bili23-Downloader**、BilibiliDown |
| 收藏夹 / 稍后再看批量 | B 站专用批量能力 | BilibiliDown |
| 下完进 Emby / Jellyfin | 媒体库向 GUI | lanyeeee/bilibili-video-downloader |
| 跨站统一工具链 | 多站点 CLI | yt-dlp、lux |
| 长期产品集成 | 官方能力优先 | 官方 API / 开放平台（非破解下载器） |

---

## 6. 合规与工程风险

### 6.1 使用侧

1. 仅下载**有权保存**的内容（例如自己的投稿、权利方明确允许的内容）。
2. 会员专属、付费课程、番剧版权内容通常**不允许**随意下载与再分发。
3. 工具可能随时因接口变更失效。

### 6.2 产品集成侧

1. 第三方「破解型 / 逆向适配型」下载器法律与平台风险高，不适合作为产品核心能力。
2. 若业务需要 B 站相关能力，优先评估：
   - 官方开放平台 / 公开文档接口
   - 用户主动导出或授权链路
   - 仅处理用户自有内容的本地工具链
3. 若仅做研究或个人归档，也应控制传播范围，避免二次分发完整破解方案。

### 6.3 工程维护风险

| 风险 | 说明 |
|------|------|
| 接口漂移 | B 站前端与鉴权策略变更频繁，专用工具易失效 |
| 依赖停更 | 如 BBDown、DownKyi 已证明热门项目也可能突然终止 |
| 合规升级 | 律师函与平台维权可能波及同类工具 |
| 供应链 | 随意下载第三方预编译包有投毒风险，优先从官方 Release 校验 |

---

## 7. 若后续要落到本仓库的建议方向（非决策）

> 本节仅为后续讨论输入，**不是**已批准 Plan。

可能的用途分层：

1. **个人效率工具**：直接使用 `yt-dlp` 或 `Bili23-Downloader`，不进主产品代码。
2. **研究/对比**：在隔离环境复现解析流程，不提交可执行破解链路。
3. **产品能力**：只做「元数据、播放页、官方允许的开放能力」；下载完整视频流不作为默认能力。

若与 `bilibili-fanqie-mobile-plugin` 等 mission 相关，应在对应 `.devflow/<mission>/` 下重新做 Align / Plan，再决定是否引用本文结论。

---

## 8. 参考链接（撰写时）

- GitHub Topic：https://github.com/topics/bilibili-downloader
- yt-dlp：https://github.com/yt-dlp/yt-dlp
- Bili23-Downloader：https://github.com/ScottSloan/Bili23-Downloader
- BilibiliDown：https://github.com/nICEnnnnnnnLee/BilibiliDown
- bilibili-video-downloader：https://github.com/lanyeeee/bilibili-video-downloader
- BilibiliVideoDownload：https://github.com/BilibiliVideoDownload/BilibiliVideoDownload
- BBDown（已归档）：https://github.com/nilaoda/BBDown
- DownKyi（已关停）：https://github.com/leiurayer/downkyi
- lux：https://github.com/iawia002/lux

---

## 9. 修订记录

| 日期 | 变更 |
|------|------|
| 2026-08-07 | 初稿：完成公开项目检索与选型对照，落盘为候选调研文档 |
