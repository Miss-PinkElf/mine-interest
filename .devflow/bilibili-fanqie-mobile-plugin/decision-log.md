# B站 + 番茄小说 手机插件 Decision Log（决策日志）

## Metadata（元数据）

- 创建时间（Created At）：2026-08-07 15:43:57 CST
- 作者（Author）：Grok
- 目的（Purpose）：记录影响后续方向的关键决策。
- 关联仓库或项目（Related Repository / Project）：mine-interest-bilibili-fanqie
- 关联 mission（Related Mission）：bilibili-fanqie-mobile-plugin
- 当前状态（Status）：实施中（In Progress）
- 文档边界（Scope / Boundary）：决策记录，不是实现规格。

## 决策列表

### D001 - 走重型路径并新建 mission

- 时间：2026-08-07 15:43:57 CST
- 决策：新建 mission `bilibili-fanqie-mobile-plugin`，采用重型路径（Heavy Path）。
- 原因：需求存在平台/形态歧义，含两个子系统，需要 Align → Plan → Spec 再实现。
- 影响：不得跳过 Align 直接写代码；plan 落盘到 `.devflow/bilibili-fanqie-mobile-plugin/plans/`。

### D002 - 版权与合规边界（待确认）

- 时间：2026-08-07 15:43:57 CST
- 决策：暂定仅面向个人自用/学习场景做技术方案讨论，不默认做公开分发的绕过 DRM 商业产品。
- 原因：B站与番茄小说内容通常受版权与平台协议约束。
- 影响：后续设计会强调“个人设备、本地保存、不提供公开盗版分发能力”；具体合规口径需用户确认。

### D003 - 入口形态倾向：链接解析（Align 进行中）

- 时间：2026-08-07
- 决策：交互以「分享链接」为核心入口，支持剪贴板解析 / 自动解析 / 手动点击解析（具体默认策略待用户确认）。
- 原因：用户明确提出该交互方式，比 App 内注入更现实、可维护。
- 影响：产品形态收敛为「链接处理 App/工具」，不优先做 Xposed/无障碍注入。

### D004 - 番茄下载参考项目（Align 进行中）

- 时间：2026-08-07
- 决策：番茄小说下载能力优先参考 `zhongbai2333/Tomato-Novel-Downloader`（MIT），集成方式待用户确认。
- 原因：用户指定该仓库为番茄侧参考实现。
- 关键事实：
  - Rust 实现；支持 TUI / Web UI / 受限 CLI。
  - 手机侧官方路径主要是 **Android + Termux**，推荐 `--server` Web UI。
  - Release 有 Android arm64 产物。
  - 部分第三方正文 API（地址/token）**未开源**。
  - 支持从分享信息提取 Book ID；输出含 TXT/EPUB 等。
- 影响：番茄链路不宜从零造下载器；优先评估「复用二进制 / 本地 Web 服务 / 仅借鉴思路」三种集成。

### D005 - 手机形态：Android 统一工具 App（已确认）

- 时间：2026-08-07
- 决策：做成 **Android 个人工具 App**，而不是系统注入插件。
- 原因：用户确认采纳推荐形态。
- 能力分层：
  - 壳：分享接收 / 剪贴板解析 / 手动粘贴 / 任务列表 / 保存目录
  - B站：可配置下载（格式/码率/字幕/路径）
  - 番茄：复用 Tomato-Novel-Downloader，输出 TXT
- 影响：后续 Align/Plan 按「单 App 双链路」推进；iOS、注入插件、后台剪贴板监听默认延期。

### D006 - B站扩展能力（已确认需求）

- 时间：2026-08-07
- 决策：B站任务支持可选项：输出格式（mp3/mp4）、码率、是否携带字幕、自定义保存位置。
- 原因：用户明确要求扩展性，避免只做死写死的 MP3 单路径。
- 影响：B站模块需做成「任务参数模型 + 下载器 + 转码/封装」，而不是硬编码单一导出。

### D007 - 番茄复用与上游同步策略（提案，待最终确认）

- 时间：2026-08-07
- 决策（提案）：番茄下载**不 Fork 魔改业务核心**；采用「外部引擎」模式，支持一键更新上游。
- 推荐组合：
  1. **开发仓库**：`git submodule`（或 subtree）跟踪上游源码/发行策略文档。
  2. **运行时**：优先消费上游 **GitHub Releases 二进制**（Android arm64），App/脚本提供「检查更新 / 一键替换引擎」。
  3. **适配层**：只维护薄封装（链接解析、任务参数、保存路径、进度展示），避免把上游代码 copy 进业务树。
- 原因：用户要求上游更新时可一键同步；上游部分第三方 API 未完全开源，拷贝改造风险高。
- 影响：我们的代码与上游解耦；更新上游 ≈ 拉 submodule + 拉新 release，而不是手工合并大量 diff。

### D008 - 开发分支策略（已确认）

- 时间：2026-08-07
- 决策：不在 `main` 上开发；本 mission 使用分支 `rin-bilibili-fanqie-mobile/dev`。
- 原因：用户明确要求新建 `rin-{主题}/dev` 分支走重型开发。
- 影响：后续代码、Align/Plan/Spec 相关提交均在该分支进行；合并回 `main` 需另议。

### D009 - 路径确认：重型路径（已确认）

- 时间：2026-08-07
- 决策：明确走重型路径：`Align -> Plan -> proposal/design/tasks -> Apply -> Review/Verify -> Close`。
- 原因：用户确认走重型路径；需求含双链路与扩展配置，适合正式 spec 管理。
- 影响：无落盘 plan 不进入 propose/apply；无 tasks 不写业务代码。

### D010 - 链接入口组合（已确认）

- 时间：2026-08-07
- 决策：入口 = **系统分享到本应用** + **打开 App 时检测一次剪贴板** + **手动解析兜底**。
- 原因：用户确认 B，并要求分享选择本应用后自动解析；三者互补。
- 不做：后台常驻监听剪贴板。
- 影响：App 需支持 Android Share Intent、剪贴板一次性读取、粘贴/按钮解析。

### D011 - B站下载：一体式 A（已确认）；引擎化延期

- 时间：2026-08-07
- 决策：
  - 本轮 B站 = **方案 A 一体式 MVP**（App 内完成解析/下载/转码或封装/存盘）。
  - 扩展选项：`mp3|mp4`、码率/清晰度、是否字幕、自定义保存位置。
  - 架构上预留可替换 Provider 接口。
  - **延期**：外部引擎 `yt-dlp + ffmpeg` 作为可替换实现（见 `deferred/b站-外部引擎-yt-dlp-ffmpeg.md`）。
- 参考输入：`zzz-docs/开源B站视频下载项目调研.md`
  - 通用 CLI 首选关注：`yt-dlp`
  - 慎用/停更参考：BBDown（archived）、DownKyi（关停）
  - 合规与接口漂移风险写入后续 design 约束
- 原因：用户明确「暂时 A」；可替换做成 yt-dlp+ffmpeg 但先放延期。
- 影响：Plan/Spec 按一体式实现；不得把 yt-dlp 集成写进本轮必做 tasks。

### D012 - 总体方案与番茄路线（已确认）

- 时间：2026-08-07
- 决策：
  - **最终形态**：Android 单 App（不依赖用户日常使用 Termux 本地服务）。
  - **入口**：分享 + 打开检测剪贴板 + 手动解析。
  - **B站**：一体式 A；yt-dlp+ffmpeg 延期。
  - **番茄**：App 内自研最小 TXT 下载；**借鉴** `zhongbai2333/Tomato-Novel-Downloader` 的流程与实现思路。
  - **Tomato Android_arm64 二进制 / Termux / 本地 Web 服务**：仅开发期对照验证或个人备用，**不作为**产品主架构。
  - **分析方式**：允许浅克隆上游仓库做结构分析；可用 subagent 探测；**业务实现仍遵守 Align → Plan → Spec 门禁**，禁止跳过 plan 直接写产品代码。
- 原因：用户确认推荐方案，并授权借鉴开源项目与拉仓分析。
- 影响：Align 阶段可产出上游分析笔记；Apply 前必须有 plan 与 tasks。

### D013 - App 壳技术：Kotlin（已确认）

- 时间：2026-08-07
- 决策：使用 **Kotlin 原生 Android** 开发；UI 降优先级，**下载核心逻辑优先**。
- 原因：用户明确 UI 不重要、核心是下载；熟悉 React 但接受 Kotlin；后续若换 RN 可通过模块化保留下载核心。
- 架构约束：下载/解析/存盘与 UI 解耦，便于将来可选 RN 壳调用同一套原生核心。
- 不做：本轮不选 Flutter / RN 作为壳。

### D014 - Align 确认并进入 Plan（已确认）

- 时间：2026-08-07
- 决策：用户确认 Align，正式撰写并落盘 Implementation Plan。
- 产物：`plans/2026-08-07-bilibili-fanqie-mobile-plan.md`
- 影响：工程根目录规划为 `android/` 多模块；番茄正文走可配置 `ContentFetcher`，不硬编码闭源 token。

### D015 - 手动批量解析（已确认）

- 时间：2026-08-07
- 决策：手动入口支持 **批量解析（Batch Parse）** 多条链接/分享文案，分别入队。
- 约定：多行或同行多 URL；去重；单条失败/无法识别不阻断其它条；本批 B站/番茄分别共用当前选项。
- 非目标：整站/收藏夹级爬取。
- 影响：Align 增加 S8；Plan 的 LinkParser/TaskRunner/UI 增加 `parseBatch` / `enqueueBatch`。

### D016 - 路径 A：先 Propose 再 Apply，并授权写代码

- 时间：2026-08-07 17:10:28 CST
- 决策：用户选择 openspec-propose 生成 spec 三件套后直接进入 Apply；环境安装中允许先写代码。
- 影响：`spec/` 为 lifecycle artifact；实现按 tasks/plan 推进；默认不 commit。

### D017 - Apply 源码完成后会话交接，Verify 延后

- 时间：2026-08-07 17:45:25 CST
- 决策：全 Task 源码落地后做 handoff；完整 Close 与宣称交付以 gradle+真机验证为准。
- 影响：新会话优先 Verify；延期表已标注实现状态。

### D018 - 番茄 Official-API/搜书名/零配置正文单独延期，主线优先 B站

- 时间：2026-08-07 18:22:06 CST
- 决策：不接入 Tomato 闭源 Official-API；搜书名与零配置正文整包延期；用户确认先推进 B站。
- 记录：`deferred/番茄-Official-API与搜书名零配置正文.md`；总表已同步。
- 影响：番茄维持链接+目录+自配端点；禁止把闭源 token/Official-API 写进仓库。

### D019 - 会话交接：B站主路径验收通过，音量 bug 下次修

- 时间：2026-08-07 18:28:48 CST
- 决策：不完整 Close；BUG-001 记入 bug-log；handoff 003。
