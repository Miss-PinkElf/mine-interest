# 延期项：番茄 Official-API / 搜书名 / 零配置正文

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| 创建时间（Created At） | 2026-08-07 18:30:00 CST |
| 作者（Author） | Grok |
| 目的（Purpose） | 结构化记录「Tomato 完整版式体验（搜书名、零配置正文）」为何本轮不做、与闭源 Official-API 的边界，以及后续触发条件 |
| 关联仓库或项目（Related Repository / Project） | mine-interest-bilibili-fanqie |
| 关联 mission（Related Mission） | bilibili-fanqie-mobile-plugin |
| 当前状态（Status） | 延期（Deferred）— **非永久放弃** |
| 文档边界（Scope / Boundary） | 延期项真相源；**不**触发本轮实现；**不**把未开源 token/Official-API 写进产品代码 |
| 关联 Align / Plan | `plans/2026-08-07-bilibili-fanqie-mobile-align.md`、`plans/2026-08-07-bilibili-fanqie-mobile-plan.md` Task 8–9 |
| 关联分析 | `references/Tomato-Novel-Downloader-分析笔记.md` |
| 关联上游 | `references/Tomato-Novel-Downloader/`（开源壳）；闭源 crate `tomato-novel-official-api` **不在本仓库** |
| 优先级说明 | 用户确认：**先推进 B站**；本项番茄增强整体延后 |

---

## 1. 暂不做的对象或能力

以下能力 **本轮 / 当前阶段均不做**，单独作为延期包管理：

| ID | 能力 | 用户侧表现 |
|----|------|------------|
| FQ-D01 | **Official-API 模式正文** | 不配置第三方端点也能批量拉章节正文 |
| FQ-D02 | **按书名搜索** | 输入小说名字 → 选书 → 下载（Tomato TUI/Web 体验） |
| FQ-D03 | **内置第三方地址池 / token** | App 预置可用正文 API，开箱即用 |
| FQ-D04 | **嵌套 Tomato 二进制 / Termux 本地 Web 作正文源主路径** | 调 127.0.0.1 或 arm64 可执行文件当产品主架构 |
| FQ-D05 | **一键对齐 Tomato 上游全部能力**（TTS/书架/段评等） | 与 D012 一致，不作为目标 |

**本轮番茄仍保留（已实现或进行中）：**

- 分享链接 / 短链（含 `changdunovel.com/t/...`）→ `book_id`
- 网页/公开目录接口拉章节列表
- **用户自填** `ContentFetcher` 端点（`{item_id}`）→ TXT
- 断点缓存、合并导出

---

## 2. 背景：为什么用户会觉得「Tomato 不用配端点」

### 2.1 Tomato 的两种构建

| 模式 | Feature | 搜索 | 正文默认来源 |
|------|---------|------|----------------|
| **默认完整版（Releases 常见）** | `official-api` | 有（闭源） | **Official-API 闭源客户端**；亦可兼容第三方 |
| **无官方 API 版** | `no-official-api` | **无** | **强制** `api_endpoints` 第三方池 |

用户个人使用 Tomato 发行包时，多半是 **默认 `official-api`**：搜书名 / 贴链接后直接下，界面上**不必**手填端点。

### 2.2 Official-API **不是**番茄开放平台官方 API

| 误解 | 澄清 |
|------|------|
| 「Official-API = 番茄公司开放平台」 | **否**。是 Tomato 项目 feature/crate **命名**，封装对接番茄体系的 **闭源实现** |
| 「开源仓库里有完整正文实现」 | **否**。`tomato-novel-official-api` 为 path 依赖，**浅克隆中不可见**；另有 Network-Core 等闭源组件 |
| 「第三方地址池可直接抄进我们 App」 | **否**。README 写明地址与 token **不开源** |
| 「个人用 Tomato 软件 = 可嵌入我们产品」 | **否**。个人跑二进制 ≠ 获得闭源再分发/嵌入授权 |

### 2.3 与本 App 架构的差异

```text
Tomato 完整版：闭源 Official-API（搜索+正文）± 内置第三方池
本 App MVP：  开源可写部分（链接/目录）+ 用户自备正文 HTTP
```

---

## 3. 本轮暂不做的原因

1. **合规与授权**  
   - 闭源 Official-API / 动态库 / 未开源 token **不能**合法干净地嵌进本仓库产品。  
   - Align 已禁止「仓库硬编码闭源 token」。

2. **架构决策已锁定（D012 等）**  
   - 番茄：App 内自研最小 TXT；**借鉴** Tomato 流程，**不以** Termux + 本地服务 / 嵌二进制为主架构。  
   - 正文可插拔 `ContentFetcher`，端点用户配置。

3. **可维护性**  
   - 逆向/私有协议易变、封控与协议风险高，不适合作为本 mission 当前主交付。

4. **优先级**  
   - 用户明确：**先弄 B站**（一体式 403、导出可用性）；番茄「番茄官方级体验」整体延期。

---

## 4. 后续进入的触发条件或推荐阶段

满足 **任一** 可重开讨论（仍须 Align，禁止静默塞进 MVP）：

| 触发 | 说明 |
|------|------|
| T1 | B站一体式下载 **稳定可用** 后，用户明确要求提升番茄「少配置」体验 |
| T2 | 用户自备 **长期可用** 的搜索+正文 HTTP 服务，只需 App 接客户端（仍不嵌闭源） |
| T3 | 合规策略变更：允许个人侧 **可选** 调用用户本机 Tomato/Termux（副路径，非商店分发） |
| T4 | 出现 **可授权、可文档化** 的正文/搜索方案（非未授权逆向） |
| T5 | 用户明确启动「番茄体验对齐」子阶段并接受延期包范围裁剪 |

**推荐阶段顺序（示意）：**

```text
当前 → 主线：B站一体式可用性（含 403 缓解 / 真机验）
     → 番茄 MVP 维持：链接+目录+自配端点
     → 触发 T1～T5 后 → 再开 Align 选路径（见第 5 节）
```

---

## 5. 后续可选路径（仅候选项，未批准）

> 以下均为 **候选项（Candidate）**，不代表已批准 Plan。

| 路径 | 做法摘要 | 优点 | 风险 / 成本 |
|------|----------|------|-------------|
| A. 维持自配端点 | 仅优化 UI 引导、端点校验与错误文案 | 合规清晰 | 体验不如 Tomato |
| B. 用户本机 Tomato 副路径 | 可选：检测本机/Termux HTTP，转发任务 | 复用用户已有完整版 | 非主架构；环境碎片；Align 曾排除主路径 |
| C. 用户自建网关 | 用户部署自己的搜索+正文服务，App 填 Base URL | 不碰闭源进仓 | 用户运维成本 |
| D. 自研逆向 Official 能力 | App 内实现类似协议 | 体验接近 | **高合规与失效风险；默认不推荐** |

**明确不选（本延期项约束）：**

- 将 `tomato-novel-official-api` 或未开源 token **拷贝进本仓库**  
- 把「Official-API」宣传成「番茄官方开放 API」误导用户  

---

## 6. 与本轮实现的关系（边界）

| 本轮做 | 本轮不做（本文件范围） |
|--------|------------------------|
| 短链 / book_id / 目录 / 可配置正文 / TXT | 搜书名、零配置正文、Official-API、内置地址池 |
| B站优先修复与验收 | 番茄体验对齐 Tomato 完整版 |

番茄相关 **bug 修复**（如短链识别）仍可做，**不等于**启动本延期包。

---

## 7. 验收标准（若未来进入实现）

进入实现前必须先有新 Align + Plan。届时建议验收：

1. 不引入未授权闭源代码与硬编码 token。  
2. 若选路径 B/C：文档写清「个人自用、可选依赖」。  
3. 搜索与正文失败有中文可操作错误。  
4. 与 B站 Provider 解耦，不拖垮主路径。  

---

## 8. 相关文档索引

- Tomato 分析：`references/Tomato-Novel-Downloader-分析笔记.md`  
- Tomato README：默认 `official-api` vs `no-official-api`  
- MVP 总表：`deferred/mvp-与延期范围总表.md`  
- B站引擎延期：`deferred/b站-外部引擎-yt-dlp-ffmpeg.md`（B站另一条线，互不替代）  

---

## 9. 变更记录

| 时间 | 说明 |
|------|------|
| 2026-08-07 | 初建；用户确认 Official-API/搜书名/零配置正文单独延期，**优先 B站** |
