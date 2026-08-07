# B站 + 番茄小说 手机工具 — Align（对齐）结论

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| 创建时间（Created At） | 2026-08-07 16:39:47 CST |
| 更新时间（Updated At） | 2026-08-07 16:58:59 CST |
| 作者（Author） | Grok |
| 目的（Purpose） | 固化本 mission 的需求对齐与技术方向，作为后续 Plan / Spec 的输入 |
| 关联仓库或项目（Related Repository / Project） | mine-interest-bilibili-fanqie |
| 关联 mission（Related Mission） | bilibili-fanqie-mobile-plugin |
| 当前状态（Status） | 已确认（Confirmed）— 用户 2026-08-07 确认可写 Plan |
| 文档边界（Scope / Boundary） | Align 真相源片段；**不是**实施 plan；确认后已进入 Plan 文档 |
| 开发分支（Branch） | `rin-bilibili-fanqie-mobile/dev` |
| 路径类型（Route） | 重型路径（Heavy Path） |

### 关联输入

- 原始需求索引：`.devflow/bilibili-fanqie-mobile-plugin/origin.md`
- 决策日志：`.devflow/bilibili-fanqie-mobile-plugin/decision-log.md`
- B站调研：`zzz-docs/开源B站视频下载项目调研.md`
- 番茄上游分析：`.devflow/bilibili-fanqie-mobile-plugin/references/Tomato-Novel-Downloader-分析笔记.md`
- 番茄上游浅克隆：`.devflow/bilibili-fanqie-mobile-plugin/references/Tomato-Novel-Downloader/`

---

## 1. 问题与目标

### 1.1 要解决什么

在 **Android 手机** 上，用 **一个个人工具 App**：

1. **B站（Bilibili）**：拿到视频分享链接后，按选项下载并导出，保存到指定文件夹。  
2. **番茄小说（Fanqie）**：拿到小说分享链接后，下载为 **TXT**，保存到指定位置。

### 1.2 成功标准（Align 级）

| 编号 | 标准 |
|------|------|
| S1 | 用户可通过 **系统分享 / 打开时剪贴板 / 手动粘贴** 任一方式提交链接 |
| S2 | 能识别链接类型（B站 vs 番茄），进入对应任务流 |
| S3 | B站任务支持：`mp3` / `mp4`、码率或清晰度、是否字幕、自定义保存目录 |
| S4 | 番茄任务支持：解析 book_id/链接 → 下载 → 输出 TXT 到自定义目录 |
| S5 | 有任务状态（排队/进行中/成功/失败）与基础错误提示 |
| S6 | **不依赖** 用户日常安装/常开 Termux 本地服务 |
| S7 | 下载核心与 UI 解耦，核心逻辑可独立演进 |
| S8 | **手动入口支持批量解析（Batch Parse）**：一次粘贴多条链接/分享文案，解析出多条可识别项并分别入队 |

### 1.3 非目标（本轮明确不做）

见第 6 节延期项；摘要：

- iOS、系统注入插件、后台常驻剪贴板监听  
- B站 `yt-dlp + ffmpeg` 外部引擎（已记 deferred）  
- 以 Termux + Tomato 本地 Web 服务作为产品主架构  
- 番茄 TTS、复杂书架、**整站/收藏夹级**批量爬取（与「手动粘贴多条链接」不同）  
- 公开分发/商业化盗版能力  

---

## 2. 用户主路径

```text
在 B站/番茄 App 中：分享 → 选本应用
        或：复制链接 → 打开本应用（自动检测剪贴板）
        或：打开本应用 → 手动粘贴（可多条）→ 批量解析
                ↓
        识别平台 + 展示可选项（B站格式等；批量时 B站项共用当前选项）
                ↓
        为每条可识别链接创建任务 → 下载/转换 → 写入保存目录
                ↓
        任务列表显示结果；失败可重试或查看原因
```

### 2.1 手动批量解析（Batch Parse）约定

| 项 | 约定 |
|----|------|
| 触发入口 | **手动输入框**（主路径）；剪贴板若含多段文本，打开检测时可按同样规则拆分（可选增强，不阻塞 MVP） |
| 输入形态 | 多行文本：一行一条；或同一大段中含多个 `http(s)://` URL；亦可混有书名/口令文案 |
| 解析结果 | 拆出 0..N 条 `ParsedLink`；过滤 `UNKNOWN`；对有效项分别入队 |
| 失败策略 | 单条无法识别 → 记一条失败提示或列表旁注「第 k 行无法识别」，**不阻断**其它有效条 |
| 去重 | 同一规范化 id/url 在本批次内默认去重（避免重复入队） |
| B站选项 | 批量提交时，本批 B站任务共用当前 UI 上的 format/码率/字幕/目录 |
| 番茄选项 | 本批番茄任务共用当前保存目录等选项 |
| 非目标 | 不做「整站收藏夹一键扒光」；批量仅限用户粘贴的多条链接/文案 |

---

## 3. 产品与技术决策（已确认）

| ID | 主题 | 决策 |
|----|------|------|
| D001 | 路径 | 重型：Align → Plan → proposal/design/tasks → Apply |
| D005/D012 | 形态 | **Android 单 App**，非注入插件 |
| D010 | 入口 | 分享 + 打开检测剪贴板 + 手动解析；不做后台常驻监听 |
| D015 | 手动批量 | 手动入口支持 **批量解析** 多条链接并分别入队（见 2.1） |
| D011 | B站 | **一体式 A**；选项可配；Provider 可替换接口预留 |
| D011 延期 | B站引擎 | `yt-dlp + ffmpeg` 见 deferred |
| D012 | 番茄 | **App 内自研 TXT**；借鉴 Tomato-Novel-Downloader **思路与流程** |
| D012 | Tomato 二进制 | arm64 包 / Termux 仅开发验证，非主架构 |
| D013 | 技术栈 | **Kotlin 原生**；UI 次要，**下载核心优先** |
| D008 | 分支 | `rin-bilibili-fanqie-mobile/dev`，不在 main 开发 |

### 3.1 架构草图

```text
┌────────────────────────────────────────────┐
│  UI 层（Kotlin，极简即可）                    │
│  分享接收 / 剪贴板 / 粘贴(支持批量) / 任务列表   │
└─────────────────┬──────────────────────────┘
                  │ 仅调接口
┌─────────────────▼──────────────────────────┐
│  领域层（Domain）                             │
│  LinkParser（含 parseBatch）/ TaskQueue / …  │
└─────────────────┬──────────────────────────┘
        ┌─────────┴─────────┐
        ▼                   ▼
┌───────────────┐   ┌───────────────────┐
│ BiliProvider  │   │ FanqieProvider    │
│ 一体式下载导出 │   │ 自研 TXT（借鉴流程）│
│ mp3/mp4/字幕  │   │ book_id→章节→TXT  │
└───────────────┘   └───────────────────┘
```

**模块化约束（为将来可选 RN 壳）：**

- 下载/解析/存盘 **不得** 写死在 Activity UI 里  
- 对外接口形态稳定：`parseLink` / `parseBatch` / `createTask` / `enqueueBatch` / `observeProgress` / `cancel`  

### 3.2 B站任务参数（扩展点）

```text
BiliTaskOptions
- format: mp3 | mp4
- quality: 音频码率 或 视频清晰度档位（实现期再定枚举名）
- withSubtitle: Boolean
- saveDir: Uri/路径
- filenamePattern: 可选（默认 标题-id）
```

默认建议：`mp3` + 中等码率 + 字幕关 + 全局默认目录。

### 3.3 番茄借鉴范围（来自上游分析）

**借鉴：**

- 主链路：`resolve book_id → 书信息+目录 → 分章正文 → 断点 → finalize TXT`  
- 链接/分享文案解析规则  
- 断点与按 book_id 缓存的思路  
- 下载与导出分层  

**不照搬：**

- TUI / WebUI / Termux 分发形态  
- 未开源 Official-API / 第三方 token 池整包搬运  
- 把「本地 HTTP 服务」当产品依赖  

**已知硬风险（必须进 Plan）：**

- 开源树 **无完整开箱正文源**；MVP 需单独选定正文获取策略与失败降级  
- 接口漂移与合规（个人自用边界）  

参考：`references/Tomato-Novel-Downloader-分析笔记.md`

---

## 4. 推荐实现顺序（Align 级）

1. **工程骨架**：Kotlin 单模块/多模块起步 + 领域接口  
2. **入口三件套**：分享 / 剪贴板一次检测 / 手动解析 + 链接分类  
3. **任务与目录**：队列、状态、默认路径与任务级覆盖  
4. **B站 Provider MVP**：至少跑通 mp3 或 mp4 其一，再补全选项  
5. **番茄 Provider MVP**：book_id → TXT（正文策略在 Plan 中明确）  
6. **手动批量解析**：`parseBatch` + 多任务入队 + UI 多行粘贴  
7. **打磨**：错误提示、重试、基础设置页  

---

## 5. 合规与使用边界

- 默认定位：**个人设备、本地自用** 效率工具  
- 不设计为公开传播破解能力、批量盗版分发  
- B站/番茄内容版权与平台协议由使用者自行遵守  
- 工程上接受：非官方接口可能失效，需可维护与可替换（B站已预留引擎延期）  

---

## 6. 本轮不做 / 后续阶段（延期项 Deferred Scope）

| 项 | 暂不做原因 | 后续触发 |
|----|------------|----------|
| B站外部引擎 yt-dlp+ffmpeg | 先验证一体式闭环 | 一体式维护成本过高或需统一引擎架构；见 `deferred/b站-外部引擎-yt-dlp-ffmpeg.md` |
| Termux + Tomato 本地服务主架构 | 与单 App 目标冲突 | 仅个人验证或自研正文长期不可行时再评估 |
| iOS | 范围与权限成本 | 明确跨端需求时 |
| 后台常驻剪贴板 | 隐私/系统限制/误触发 | 无强需求不启动 |
| 系统注入插件 | 兼容与维护地狱 | 不计划 |
| 番茄 TTS / 书架订阅 / 整站级爬取 | 非 MVP；**不含**已确认的「手动多链接批量解析」 | 核心 TXT 稳定后 |
| 一键同步 Tomato 上游全部能力 | 已选 App 内自研 | 若改回外部引擎路线再恢复 |
| RN / Flutter 壳 | UI 非重点；先 Kotlin 核心 | 若未来要 React UI，可换壳调用同一下载核心 |

---

## 7. 开放问题（留给 Plan，不阻塞 Align 方向）

1. B站一体式具体依赖哪些库/协议实现路径（自研解析 vs 有限复用思路）  
2. 番茄正文 MVP 的具体数据源策略与合规实现边界  
3. 最低 Android SDK、存储权限（SAF vs 传统路径）选型  
4. 是否需要登录态（大会员清晰度、番茄完整章节）——默认 MVP 先不做复杂账号体系，Plan 再定  

---

## 8. Align 自检

| 检查项 | 结果 |
|--------|------|
| 占位符 / TBD 是否阻塞方向 | 开放问题已隔离到 Plan，不推翻形态 |
| 内部一致性 | 单 App / Kotlin / 双 Provider / 入口三件套一致 |
| 范围是否可进一个 Plan | 是；实现可分阶段 tasks |
| 歧义是否消除 | 「插件」= App；番茄≠Termux 主架构；B站≠本轮 yt-dlp；「批量」= 手动多链接解析，≠ 整站爬取 |

---

## 9. 用户确认闸门

请确认本 Align 是否可以作为后续 **Plan** 的输入：

- [ ] 同意全文  
- [ ] 同意，但需修改：________  

确认后进入：`superpowers-writing-plans`，plan 落盘于  
`.devflow/bilibili-fanqie-mobile-plugin/plans/`。
