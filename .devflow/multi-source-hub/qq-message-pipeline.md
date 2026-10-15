# Metadata（元数据）

- 创建时间（Created At）：2026-10-15 22:35:00 +08:00。
- 更新时间（Updated At）：2026-10-15 22:35:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：把 QQ 群消息从「进群消息」到「进私有仓库」的当前链路讲清楚，供排查与后续改动定位。
- 关联仓库（Related Repository / Project）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联既有文档（Related Docs）：`.devflow/multi-source-hub/qq-bilibili-capability-boundary.md`、`.devflow/multi-source-hub/plans/2026-09-21-多源信息中心-成条与原始资料落盘-align.md`、`.devflow/multi-source-hub/plans/2026-09-22-QQ日收集与异步媒体实施-plan.md`、`.devflow/multi-source-hub/plans/2026-09-23-QQ标题分层目录迁移-plan.md`。
- 当前状态（Status）：说明（Reference）。
- 文档边界（Scope / Boundary）：**说明文档，不是真相源。** 真相源是代码与 `state.md`。不批准新功能，不触发实现。文中的代码位置以 `backend/src/sourcehub/` 与两个插件副本为准；三份副本内容必须字节级一致（由 `tests/test_sourcehub_vendoring.py` 守卫）。

# QQ 群消息采集链路说明

本文只讲 QQ。B 站是另一条独立的采集源，见 `qq-bilibili-capability-boundary.md`。

两者的分工：`qq-bilibili-capability-boundary.md` 讲**能拿到什么**（2026-09-21 视角，早于日账本与按天归档）；本文讲**拿到之后怎么流转**（当前链路）。

---

## 一、一条消息的完整旅程

```text
QQ 群消息
  │
  ├─[群白名单过滤]
  ├─[写原始快照]           data/sourcehub-inspector/snapshots/
  ├─[展开合并转发]         data/sourcehub-inspector/forwards/
  │
  └─ 成条引擎（GroupingEngine）
        ├─ 会话中 / 会话标记 / 合并转发 → 立刻 vault.upsert
        └─ 普通消息（single）        → 日账本 + 日文档「实时消息」区
                                          ↓
                              [@机器人 整理 或 每天 0 点]
                                          ↓
                                   vault.upsert（成条为 daily Item）
                                          ↓
  ┌───────────────────────────────────────┴────────────────────────────┐
  │ items/qq/<日期>/<message|forward|session>/<标题-ID>/                │
  │     ├─ envelope.json   结构真相源                                  │
  │     └─ content.md      人读原文                                    │
  │ catalog.sqlite3        身份索引（item_id → 路径）                   │
  │ 本地 git commit        只提交，不 push                             │
  │ 媒体 → media/<sha256>.<ext>                                        │
  └────────────────────────────────────────────────────────────────────┘
                                          ↓
                          发布器每 30 秒推送到私有远端仓库
```

---

## 二、插件配置项逐项含义

配置声明在 `integrations/astrbot/astrbot_plugin_sourcehub_inspector/_conf_schema.json`，键名常量在 `integrations/astrbot/astrbot_plugin_sourcehub_inspector/constants.py`，读取在 `main.py`。

### 采集范围与开关

| 配置项 | 读取位置 | 含义 |
| --- | --- | --- |
| `enabled_group_ids` | `main.py:186` `_is_group_enabled` | 群白名单。**留空 = 所有群都收集**；填了纯数字群号就只收列出的群 |
| `collect_enabled` | `main.py:103` | 总开关。关掉后只写快照，不进成条与落盘 |
| `vault_dir` | `main.py:104` | 资料目录（Vault）根。默认 `data/sourcehub`（相对 AstrBot 工作目录），可填绝对路径 |

### 成条规则

| 配置项 | 读取位置 | 含义 |
| --- | --- | --- |
| `session_start` / `session_end` | `collect.py:29` `build_pack` | 会话标记，**整句精确匹配**。默认 `，，，` / `。。。`（`backend/src/sourcehub/constants.py:14-15`） |
| `organize_command` | `main.py:121` | 手动整理命令词，默认「整理」（`constants.py:49`） |
| `timezone` | `main.py:119` | 日账本按哪个时区切天，默认 `Asia/Shanghai`（`constants.py:48`）。**不跟随机器本地时区** |

规则默认值写在代码里（`backend/src/sourcehub/rules.py` 的 `RulePack`），插件配置只做覆盖。这是 2026-09-21 对齐稿第 3 节定下的分工：群号与开关留在插件配置，规则默认值跟着代码走。

### 媒体

| 配置项 | 读取位置 | 含义 |
| --- | --- | --- |
| `media_max_bytes` | `main.py:126` | 单文件上限，默认 100 MiB（`constants.py:17`）。超限记缺口 `media_too_large`，条目仍保存 |

### 推送与告警（与采集本身无关，属运行保障）

| 配置项 | 读取位置 | 含义 |
| --- | --- | --- |
| `publish_enabled` | `main.py:106` | 是否启用资料自动推送 |
| `alert_enabled` / `alert_remote` | `main.py:111-114` | GitHub 私有告警仓库，与资料仓库分开 |
| `qq_status_enabled` / `qq_platform_id` / `qq_account_id` / `qq_disconnect_grace_seconds` | `main.py:145,160-162` | QQ 掉线监测与告警去重 |

---

## 三、采集（Capture）

入口是 `main.py:193` 的 `inspect_message`，挂在整个平台的**所有消息事件**上（`@filter.event_message_type(ALL)`）。每条群消息依次做三件事：

### 1. 白名单过滤

`main.py:194-199`。不在 `enabled_group_ids` 里的群直接 `return`，连快照都不写。

### 2. 写原始快照

`main.py:201-213`。把整个事件对象递归安全化后落到 `data/sourcehub-inspector/snapshots/<接收时间戳>_<事件ID>.json`。

日志表现：`[SourceHub Inspector] 已保存消息快照：渊下宫分宫(836229427) -> ...`

**这一层是诊断用档案，不是资料真相源。** 消息正文的真相源是成条后的 `envelope.json`。

### 3. 展开合并转发

`main.py:257` `_expand_forwards` → `main.py:281` `_expand_one_forward`。

- 只对消息里含合并转发段（`Forward` 组件）的消息生效。
- 通过 OneBot v11 的 `get_forward_msg` 取内层；**嵌套转发优先使用内联 `content`**，缺失才按 id 二次请求（按 id 再取可能 `retcode 1200`）。
- 递归深度硬上限 5 层（`integrations/.../constants.py` 的 `MAX_FORWARD_DEPTH`），超限写 `_sourcehub_truncated`。
- 结果落 `data/sourcehub-inspector/forwards/`，同时输出一份可读 `.txt`。

日志表现：`已展开转发消息：… 层数=2 内层条数=48 段类型={'forward': 1, 'image': 17, ...}`

### 4. 进入成条

`main.py:216-230` 调 `collect.py:62` 的 `collect_event`。异常被 `except Exception` 兜住并记 `成条入库失败`，**不会中断事件循环**。

---

## 四、成条（Grouping）

`backend/src/sourcehub/grouping.py` 的 `GroupingEngine.ingest`（`:134`）是分流器。

### 4.1 转成 IncomingMessage

先由 `backend/src/sourcehub/qq_ingest.py` 的 `parse_onebot_message` 把 OneBot 载荷转成 `IncomingMessage`：

- 文本段 → `text` 节点；图片段 → `image` 节点；文件段 → `file` 节点；转发段 → `forward` 节点（递归子节点）；其余 → `unknown` 节点（**原样保留，不丢**）。
- `event_id` 取 `message_id`；**取不到则记缺口 `event_id_missing`**（不确定身份的消息不静默放过）。

### 4.2 四条分流

判断顺序不可调换：

| 顺序 | 条件 | 行为 | 成条类型 |
| --- | --- | --- | --- |
| ① | 该群**已有开着的会话** | 本条塞进会话成员；若是 `session_start` 则先把上一个按「缺结束」收口再开新会话；若是 `session_end` 则关会话并产出条目 | `session_markers` |
| ② | 整句 == `session_start` | 开一个会话，**本条不单独成条** | — |
| ③ | 整句 == `session_end` | 丢弃（没有开着的会话时它不算边界） | — |
| ④ | 其它 | 带转发 → `qq:forward:<ID>`；否则 → `qq:message:<ID>` | `merged_forward` / `single` |

补充：

- **会话标记按整个群共用一份**，不按发送者拆（`grouping.py:103` `self._sessions` 以群号为键）。
- **空闲超时**：`flush_idle`（`:154`）在每次 ingest 时检查，超过 30 分钟（`constants.py:16` `DEFAULT_SESSION_IDLE_SECONDS`）没新消息就强制收口，记缺口 `session_end_missing`。
- 转发内部的 `，，，` / `。。。` **不触发外层成条**，只当转发正文。
- 未关闭的会话缓冲落 `spool/qq_sessions.json`，插件重载后按原 `item_id` 接着收（`collect.py:132` `load_engine`）。

### 4.3 捕获封套（Capture Envelope）

成条的产出是 `Envelope`（`backend/src/sourcehub/envelope.py`）。关键字段：

| 字段 | 作用 |
| --- | --- |
| `item_id` | 资料身份，如 `qq:message:1441885612`、`qq:forward:1288246808`、`qq:session:<首条ID>`、`qq:daily:<群>:<日期>:<首条ID>` |
| `event_id` | 触发本次写入的平台事件 ID |
| `content` | 有序节点树：`text` / `image` / `file` / `quote` / `forward` / `unknown` |
| `gaps` | 缺口列表（`session_end_missing`、`media_failed`、`forward_unexpanded` 等） |
| `grouping` | 成条类型与成员事件 ID |
| `source_time` / `received_at` | 来源发送时间（可空）/ 接收时间（必有） |

---

## 五、落盘分流（关键分叉点）

`collect.py:81-89` 是整个链路唯一的分叉点：

```python
for envelope in envelopes:
    if daily_ledger is not None and envelope.grouping.get("type") == GROUPING_SINGLE:
        daily_ledger.append(incoming, now)          # 进日账本
        vault.append_daily_message(envelope)        # 写日文档「实时消息」区
        continue                                     # ← 不 upsert，不建 Item
    vault.upsert(envelope)                           # 立刻建 Item
    _enqueue_media(envelope.item_id, vault, max_bytes)
```

**这就是「为什么某天 `items/qq/<日期>/` 下没有子目录」的答案**：当天只有普通消息时，它们还躺在日账本里等着被整理，尚未成为独立 Item。

### 日账本（Daily Ledger）

`backend/src/sourcehub/daily.py`，落 `spool/qq_daily/<群>/<日期>.json`，含两部分：

- `messages`：当天收到的普通消息（完整原文，含 `nodes` 与 `raw`）。
- `finalized_event_ids`：**游标**，已整理的 `event_id`。

游标的作用是保证「插件重载」「手动整理 + 午夜整理都跑一次」都不会重复成条（`daily.py:35` `pending` 会过滤掉已游标化的消息）。

### 日文档的「实时消息」区

`backend/src/sourcehub/vault.py:112` `append_daily_message`。

设计意图（2026-09-22 既定）：普通消息不会立刻变成 Item，但用户不希望等到半夜才能看到内容，所以先把每条消息摘要进当天的 `content.md`，**先能读、后成条**。

两个要点：

1. **它是摘要区，不是真相源。** 完整原文在日账本与成条后的 Item 里。
2. **`_write_daily_index` 会原样保留它**（`vault.py:157-186`）。成条后重写日文档时，会在「实时消息」上方插入 Item 链接行，摘要块不动。所以日文档最终同时承担「索引」与「即时可读」两个职责——这是设计，不是冗余。

摘要行的投影由 `vault.py:22` `format_daily_message_entry` 负责：首行跟在 `` - `event_id` `` 之后，其余行按 2 空格缩进续写（`DAILY_MESSAGE_CONTINUATION_INDENT`），空白行保持为空行。正文取自 `backend/src/sourcehub/markdown.py:33` `render_message_body_md`（只取正文，不含封套头部元信息）。

> 历史坑：2026-10-15 之前这里用 `render_content_md(envelope).splitlines()[-1]` 取摘要，多行消息只剩最后一行。详见 `bug-log.md` 的「2026-10-15：QQ 日文档摘要多行截断」。

---

## 六、入库（Vault.upsert）

`vault.py:68` `upsert` 对一条 Item 做五件事：

### 1. 决定存储路径

`backend/src/sourcehub/paths.py:24` `item_storage_path`：

```text
items/qq/<采集日>/<类型目录>/<标题>-<稳定ID>/
```

- **采集日**：由 `received_at` 换算到 `Asia/Shanghai` 的日期（`paths.py:37` `capture_day`）。日期在 Item 建立时定格，**之后不会随重新整理而改变**。
- **类型目录**：由 `item_id` 的第二段决定（`paths.py:18` `QQ_PATH_KIND`）：

  | `item_id` 第二段 | 目录 |
  | --- | --- |
  | `message` | `message/` |
  | `daily` | `message/`（同日收集成条后也归到 message） |
  | `forward` | `forward/` |
  | `session` | `session/` |

- **标题**：`paths.py:59` `_qq_title` 取正文首个非会话标记节点的**首行**；无文本时退化为附件名 / 「图片」/ 类型名（如「消息」「转发」「会话」）。

### 2. 写两个文件

- `envelope.json`：结构真相源。
- `content.md`：由封套生成的人读原文（`backend/src/sourcehub/markdown.py:27` `render_content_md`）。条目有更新就整篇重生成，与 JSON 保持一致。**手工改 `content.md` 不算改真相源。**

### 3. 更新身份索引

`catalog.sqlite3`（`vault.py:141` `_index`）：`item_id → 平台 / object_key / 路径`。去重、查找、迁移都靠它。

### 4. 重写日索引

`vault.py:157` `_write_daily_index`：重写 `items/qq/<日期>/content.md` 的 Item 链接列表（按 `updated_at` 排序），并保留「实时消息」块。

### 5. 本地 Git 提交

`backend/src/sourcehub/gitstore.py`：`git add` Item 目录 + `.gitignore`，提交信息 `sourcehub: <item_id>`。

**只提交，不 push**；`private/`、`spool/`、`*.sqlite3` 由 `.gitignore` 挡在外面。

> 已知边界：`commit_item` 只 add **Item 目录**，日索引 `content.md` 的改动不进提交。所以 `git status` 里会长期看到日索引是 modified。

---

## 七、媒体（异步下载队列）

图片/文件**不在事件处理路径上下载**（早期同步下载曾把事件循环卡死）。

- `collect.py:102` `_enqueue_media`：先持久入队到 `spool/media_jobs.json`，再拉起 worker。**先落盘再下载**，进程重启可恢复。
- `collect.py:115` `_drain_media_jobs`：worker 通过 `asyncio.to_thread` 调 `backend/src/sourcehub/media.py` 的 `persist_media_nodes`，并发上限 2（`collect.py:23` `MAX_CONCURRENT_MEDIA_DOWNLOADS`）。
- 下载后按**内容魔数**判断扩展名、按 SHA-256 命名存 `media/<hash>.<ext>`，**按内容哈希去重**，多条 Item 可指向同一文件。
- 失败记缺口 `media_failed`，超上限记 `media_too_large`；条目仍保存为「部分（Partial）」状态，可重试。

时效性提醒：QQ 图片 URL 带 `rkey` 鉴权且会过期，所以「收到就下」是必要的。

---

## 八、整理（成条为 Item）

两条触发路径，**共用同一个入口** `collect.py:92` `finalize_daily_collection`：

| 触发 | 位置 | 说明 |
| --- | --- | --- |
| 手动 | `main.py:233` `organize_today` | 群里 @机器人 发「整理」（命令词可配） |
| 定时 | `main.py:245` `_finalize_previous_days` | 每天 0 点扫昨日账本，对每个群目录各调一次 |

流程：

```python
envelope = ledger.finalize(conversation_id, day)   # grouping.daily_envelope 把当天待整理消息合成一条
vault.upsert(envelope)                              # 产出 qq:daily:<群>:<日期>:<首条ID>
ledger.mark_finalized(conversation_id, day, envelope.grouping["member_event_ids"])  # 游标推进
```

`grouping.py:253` `daily_envelope` 把多条消息的节点**按顺序铺平**成一条 Item 的 `content`，所以日 Item 的 `content.md` 里能看到当天所有消息的完整原文（含多行）。

**游标后推进**：先 `upsert` 成功再 `mark_finalized`，失败时不推进，下次会重试。

---

## 九、推送与告警

与采集链路解耦，各自独立循环：

| 循环 | 位置 | 周期 | 作用 |
| --- | --- | --- | --- |
| 发布 | `main.py:170` `_publish_loop` → `publish.py:215` `sync_once` | 30 秒（`publish.py:25`） | 把独立的 `-publish` 目录投影并推送到私有远端（默认 `git@github.com:Miss-PinkElf/data-hub.git`） |
| 告警 | `main.py:148` `_alert_loop` | 30 秒 | 把待推送告警事件推送到**另一个**专用私有仓库 |
| QQ 状态 | `main.py:159` `_qq_status_loop` | 30 秒 | 探测 QQ 在线状态，连续异常超过宽限期（默认 300 秒）才确认断线并产生告警 |

发布前会做**隐私校验**（`publish.py:165` `verify_remote_access`），并清洗外链查询参数与已知凭据（`publish.py:51` `sanitize_markdown`）。

日志里反复出现的 `资料待推送：remote_private_unverified` 就是隐私校验没过。这是已记录的延期项，见 `state.md` 与 `bug-log.md`。

---

## 十、目录职责速查

`data/` 根目录：`~/.astrbot/data/`。

| 路径 | 是什么 | 是否真相源 |
| --- | --- | --- |
| `sourcehub/items/` | 资料条目（`envelope.json` + `content.md`） | **是** |
| `sourcehub/media/` | 媒体字节，按内容哈希去重 | 是（媒体本体） |
| `sourcehub/catalog.sqlite3` | 身份索引 | 否（可重建） |
| `sourcehub/spool/qq_sessions.json` | 未关闭的会话缓冲 | 否（恢复用） |
| `sourcehub/spool/qq_daily/<群>/<日期>.json` | 日账本：待整理消息 + 整理游标 | **是**（成条前） |
| `sourcehub/spool/media_jobs.json` | 媒体任务队列 | 否（恢复用） |
| `sourcehub/private/` | 平台原包等敏感内容 | 不进 Git、不进远端 |
| `sourcehub-inspector/snapshots/` | 原始事件快照 | 否（诊断档案） |
| `sourcehub-inspector/forwards/` | 展开后的转发内层树 | 否（诊断档案） |
| `sourcehub-publish/` | 投影后的发布副本 | 否（由 items 生成） |

---

## 十一、常见症状与定位入口

| 症状 | 先看哪里 |
| --- | --- |
| 某条消息没进资料库 | `backend.log` 搜该群号 → 是否被白名单过滤；再搜 `成条入库失败` |
| 某天没有 `items/qq/<日期>/<类型>/` 目录 | 该天只有普通消息、还没整理。对账本：`spool/qq_daily/<群>/<日期>.json`；整理后即出现 |
| 日文档「实时消息」区内容不对 | 摘要投影在 `vault.py:112`；正文取自 `markdown.py:33` |
| 转发内层缺内容 | `get_forward_msg` 返空是平台侧问题（已确认 NapCat 对个别 id 返回空列表），不是插件问题 |
| 图片没落地 | 看 `media_jobs.json` 的失败状态与 `envelope.json` 的 `gaps` |
| 远端没更新 | `资料待推送：remote_private_unverified` 是隐私校验没过，不是推送坏了 |
