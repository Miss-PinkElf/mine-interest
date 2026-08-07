# Handoff：Align/Plan 完成，待 Apply

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| 创建时间（Created At） | 2026-08-07 17:03:22 CST |
| 作者（Author） | Grok |
| 目的（Purpose） | 上下文过长，新开对话继续；完整 mission Close 延后到 Apply 后且用户允许 |
| 关联 mission（Related Mission） | bilibili-fanqie-mobile-plugin |
| handoff 编号 | 2026-08-07-001 |
| 是否 superseded | 否 |
| 当前状态（Status） | 交接用（Handoff） |
| 文档边界（Scope / Boundary） | 会话交接真相源片段；**不**替代 state/plan；**不**表示产品已交付 |
| 开发分支（Branch） | `rin-bilibili-fanqie-mobile/dev` |
| 路径类型 | 重型路径（Heavy Path） |

---

## 基础信息

- **mission**：`bilibili-fanqie-mobile-plugin`
- **当前阶段**：Align 已确认 + Plan 已落盘（含批量解析增量）→ **尚未 Apply / 无产品代码**
- **完整收尾（Close）**：用户要求 **Apply 之后且明确允许** 才做；本次只做轻量 handoff
- **Git**：用户要求 **不执行提交**；工作区有未提交的 `.devflow/`、`zzz-docs/` 等文档改动

---

## 当前目标

交付 **Android 个人工具 App（Kotlin）**：

1. **B站**：分享/剪贴板/手动（可批量）→ 可配置导出 mp3/mp4（码率/字幕/目录）→ 存盘  
2. **番茄**：同上入口 → 自研 TXT 下载（流程借鉴 Tomato-Novel-Downloader）→ 存盘  
3. **不依赖** 用户日常 Termux 本地服务  

验收偏好：**打 APK → 真机手动测**（可不装模拟器）。

---

## 当前进度

| 阶段 | 状态 |
|------|------|
| Classify / Mission Init | 完成 |
| Align | 完成并用户确认；后补 **S8 手动批量解析** |
| Plan | 完成详细实施计划（12 Task + 批量增量） |
| openspec-propose（proposal/design/tasks） | **未做**（可选；用户可要求跳过直接按 Plan Apply） |
| Apply（android/ 代码） | **未开始** |
| Verify / Close | **禁止提前**；Apply 后等用户允许再完整收尾 |

---

## 本轮完成内容

- [x] 新建 mission 与重型路径记录  
- [x] 澄清形态：Android 单 App、链接驱动（分享+剪贴板一次+手动）  
- [x] B站：一体式 A；yt-dlp+ffmpeg **延期**  
- [x] 番茄：App 内自研；浅克隆上游 + subagent 分析笔记  
- [x] 技术栈：**Kotlin**（UI 次要，下载核心优先；可模块化以便未来 RN 壳）  
- [x] 分支：`rin-bilibili-fanqie-mobile/dev`（勿在 main 开发）  
- [x] Align + Plan 落盘；补 **手动批量解析**  
- [x] 环境文档：`zzz-docs/Mac-Android-Kotlin-开发环境安装指南.md`（真机 APK 工作流、CLT≠完整 Xcode、模拟器可选）  
- [x] deferred 索引：MVP/延期总表 + B站引擎延期单条  
- [ ] **未做**：任何 `android/` 工程代码、commit、openspec、完整 Close  

---

## 对话核对结论（再审）

### 已锁定且文档一致

1. 产品 = 单 App，不是 Xposed/系统注入  
2. 入口 = 分享 + 打开读剪贴板 + 手动；**不做**后台常驻监听  
3. 手动 **批量解析** = 多链接分别入队，≠ 整站爬取  
4. B站本轮一体式；可替换 Provider；yt-dlp 延期  
5. 番茄借鉴思路/流程，**不**以 Termux HTTP 服务为主架构  
6. Tomato Android_arm64 = Termux 可执行文件，**不是** APK；仅开发对照  
7. 正文源开源树不完整 → 可配置 ContentFetcher，禁硬编码闭源 token  
8. 个人自用合规边界（D002）  
9. 真机 APK 手工测；完整 Xcode 非必须；SDK 必须能打 APK  

### 第一版 vs 延期

详见：`deferred/mvp-与延期范围总表.md`  

### 开放问题（留给 Apply/Plan 实现期，不阻塞开干）

1. B站 `BiliStreamClient` 具体请求路径随平台变化，集中单点实现  
2. 番茄正文端点由用户配置；未配置时明确失败  
3. minSdk / SAF 目录细节在搭工程时定  
4. 是否做账号登录拿更高清 —— MVP 默认不做复杂账号体系  
5. 重型路径是否先 `openspec-propose`：用户可跳过，直接按 Plan Task 1 起 Apply  

### 未发现的「未讨论完的分叉」

入口、形态、B站 A、番茄自研、Kotlin、批量解析、真机验收 —— 均已拍板，无待定二选一阻塞项。

---

## 关键决策速查

| ID | 决策 |
|----|------|
| D001 | 重型路径 |
| D008 | 分支 `rin-bilibili-fanqie-mobile/dev` |
| D010 | 入口三件套 |
| D011 | B站一体式；引擎延期 |
| D012 | 番茄 App 内自研 + 借鉴 Tomato |
| D013 | Kotlin |
| D014 | Align 确认 → Plan |
| D015 | 手动批量解析 |

完整原因见 `decision-log.md`。

---

## 关键文件 / 产物

| 路径 | 作用 |
|------|------|
| `plans/2026-08-07-bilibili-fanqie-mobile-align.md` | Align 真相源 |
| `plans/2026-08-07-bilibili-fanqie-mobile-plan.md` | **详细实施 Plan（12 Task）** |
| `decision-log.md` | 决策 |
| `origin.md` | 原始需求索引 |
| `deferred/mvp-与延期范围总表.md` | MVP/延期一览 |
| `deferred/b站-外部引擎-yt-dlp-ffmpeg.md` | B站引擎延期 |
| `references/Tomato-Novel-Downloader/` | 上游浅克隆 |
| `references/Tomato-Novel-Downloader-分析笔记.md` | 番茄可借鉴点 |
| `zzz-docs/Mac-Android-Kotlin-开发环境安装指南.md` | Mac 环境 + 真机 APK |
| `zzz-docs/开源B站视频下载项目调研.md` | B站开源调研 |
| `NEXT-SESSION-PROMPT-bilibili-fanqie-mobile-plugin.md` | 下次开场提示词 |

**尚不存在：** `android/` 工程、`spec/proposal|design|tasks`。

---

## 风险 / 阻塞

| 风险 | 说明 |
|------|------|
| B站接口漂移 | 一体式可能失效；接口预留换引擎 |
| 番茄正文源 | 无开箱闭源能力；依赖用户配置端点或后续策略 |
| 合规 | 个人自用；勿做成公开盗版分发 |
| 环境 | 用户可能还在装 JDK/SDK；无 SDK 无法出 APK |
| 完整收尾 | **勿**在 Apply 前宣称 Close；**勿**擅自 commit |

---

## 立即下一步（新会话按序）

1. 读 `state.md` + `checkpoints.md` + **本 handoff**（或 NEXT-SESSION-PROMPT）  
2. 确认分支：`rin-bilibili-fanqie-mobile/dev`  
3. （可选）用户环境：JDK17 + Android SDK；`zzz-docs` 安装指南  
4. 二选一推进：  
   - **A.** `openspec-propose` 从 Plan 生成 `spec/` 三件套再 Apply  
   - **B.** 用户要求快速时：**直接按 Plan Task 1** 创建 `android/` 多模块骨架  
5. 严格按 Plan 任务推进；批量解析落在 Task 3/5/10  
6. **禁止**：无用户允许的 git commit；Apply 完成前的完整 mission Close  

---

## 恢复指引

1. 热路径：`state.md` → `checkpoints.md`  
2. 本 handoff 全文  
3. 实施前必读：`plans/2026-08-07-bilibili-fanqie-mobile-plan.md`  
4. 范围边界：`deferred/mvp-与延期范围总表.md`  
5. 番茄细节：`references/Tomato-Novel-Downloader-分析笔记.md`  
6. 从 Plan **Task 1** 或用户指定的步骤开始  

## 可从活跃上下文移除的内容

- 早期「插件形态 / Termux 是否全局环境」长讨论过程（结论已写入 Align/决策）  
- Tomato README 全文、安装指南逐条解释过程  
- 与 `organize-zzz-cmd` 无关历史  

---

## 用户特别指令（本 handoff 绑定）

1. 新开对话继续；无待讨论阻塞项  
2. 第一版 / 延期已记文档  
3. 轻量收尾：详细 handoff + NEXT-SESSION-PROMPT 即可  
4. **Apply 之后，用户允许才能完整收尾**  
5. **不用提交操作（no commit）**  
