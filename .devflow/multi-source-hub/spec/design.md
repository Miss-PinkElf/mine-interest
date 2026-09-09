# Metadata（元数据）

- 创建时间（Created At）：2026-09-09 15:19:34 +08:00
- 更新时间（Updated At）：2026-09-09 15:37:05 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：设计独立知识核心与 AstrBot 桥接的接口、存储、权限和恢复机制
- 关联仓库或项目（Related Repository / Project）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`。
- 关联需求草案（Related PRD）：`zzz-docs/多源信息中心PRD.md`。
- 关联对齐（Related Align）：`../plans/2026-09-09-多源信息中心-QQ收藏群首期整体对齐-align.md`。
- 关联计划（Related Plan）：`../plans/2026-09-09-多源信息中心-通用接入与QQ收藏闭环-plan.md`。
- 当前状态（Status）：暂停（Paused），规格待审（Spec Pending Review），未实施。
- 文档边界（Scope / Boundary）：明确待审技术设计与接口契约，属于当前任务规格真相源（Source of Truth）；用户授权本轮编写规格，不等于批准实施（Apply）。

# QQ 收藏群与独立知识核心设计（Design）

**暂停边界**：用户已确认产品方向，但本技术设计尚未审阅批准，当前明确不进入 Apply。这里的存储、权限部署、租约、开关恢复及媒体策略是工程建议；下一会话可继续简化和讨论，不因文档提交而自动执行。

## 1. 总体思路与复用

AstrBot 负责消息平台连接、现成适配器和工具执行循环。单个桥接插件负责统一封套、原始结构补充、持久投递缓存及任务执行衔接。核心负责资料、权限、索引、任务、Git 与二次页面；不依赖 AstrBot 会话数据库。

技术选型：Python 3.12、FastAPI、Pydantic v2、SQLite（标准 sqlite3）、HTTPX、Typer、Git 子进程接口、官方 Python MCP SDK。具体依赖在 T01 验证并锁定 `backend/uv.lock`；后端执行环境固定 `backend/.venv`。不引入消息总线、分布式数据库或通用插件市场。

平台扩展主要在 AstrBot 配置已有适配器。桥接通用字段使用统一消息对象，QQ 嵌套和来源补充在一个 normalizer 中处理；不创建独立平台 SDK 层。

## 2. 进程、文件与权限

运行实例由独立核心服务、AstrBot 与薄 MCP 客户端适配构成。核心单写进程串行提交文件/Git 修改；读请求只看已完成版本。首期不支持多实例同时直接写同一数据根。

推荐部署隔离：核心容器独占数据卷，AstrBot 容器只挂插件、自己的配置和投递缓存，不挂核心原文目录、Git 仓库或管理凭证。MCP 进程仅持智能体令牌，通过 API 读写；不暴露任意文件写和 shell 工具给本项目整理执行器。外部智能体也按此约束配置，拥有宿主完整权限的执行器不在应用可强制隔离范围内。

数据根由 `SOURCEHUB_DATA_DIR` 指定，默认采用部署数据卷，不放开发 Git 仓库。相对数据根布局：

| 路径 | 内容 | 历史/访问 |
| --- | --- | --- |
| `state/catalog.sqlite3` | 身份、投递、版本、任务、控制和操作日志 | 本地，核心独占；不进 Git |
| `vault/raw/<item_id>/body.json` | 当前原文、节点和稳定媒体引用，允许用户修订 | 本地知识 Git 跟踪 |
| `vault/raw/<item_id>/metadata.json` | 可公开给工具的来源描述、修订号、缺失项 | Git 跟踪 |
| `vault/wiki/pages/<page_id>.md` | 二次页面及来源版本引用 | Git 跟踪 |
| `vault/wiki/index.md` | 从已提交页面生成的导航索引 | Git 跟踪，可重建 |
| `vault/schema/` | 当前发布的资料/页面结构约定 | Git 跟踪 |
| `media/<sha256>` | 正文引用的原始附件字节 | 本地保存，不直接放普通 Git |
| `private/events/<receipt_id>.json` | 平台原始投递快照，可能含短期下载授权信息 | 核心本地受限，不给模型/远端 |
| `staging/<operation_id>/` | 准备中的写入内容、媒体临时文件 | 提交/恢复后清理 |

原始平台快照按收到的版本保留，不覆盖用户的可编辑原文。模型读接口返回稳定内容表示，屏蔽凭证和带签名下载地址，不伪称剔除凭证后的内容是字节级原包。来源不可用字段记 null 与 missing_fields。用户能修订 body 和可编辑描述，但稳定事件身份由来源索引保存，用户修订不会改变重放去重结果。

Git 历史与媒体共同构成本地可恢复资产；仅备份 Git 不是完整媒体备份。删除历史版本或垃圾回收媒体不是首期默认操作。

### 权限角色

| 角色 | 权限 |
| --- | --- |
| 收集者（collector） | 提交配置范围内的新事件及附件、读取本人投递状态，不能改既有原文或二次页面 |
| 智能体（agent） | 读原文内容表示、查页/搜索/历史、提交二次变更、指定来源收集和手动整理；不能编辑原文或管理凭证 |
| 执行桥接（worker） | 领取整理任务、心跳和回报；每次任务持临时运行令牌，模型工具使用受限 agent 能力 |
| 用户（owner） | 原文修订、二次修订、来源/运行开关配置、历史恢复；管理凭证不提供给 AstrBot/MCP |

使用独立随机令牌，服务侧按令牌映射角色和来源范围，不信任请求自报角色。用户管理端口只绑定本机 loopback；容器网络工作接口拒绝 owner 路由，防止误挂同一入口。不同角色 API 共享核心逻辑，鉴权在读业务对象前完成。部署模板凭证通过本机私密配置注入，不写进示例、日志或文档。

## 3. 契约与身份

### 捕获封套（CaptureEnvelope，版本 1）

| 字段 | 类型/含义 |
| --- | --- |
| schema_version | 固定字符串 1；未知版本 422 |
| source_instance_id | 服务登记的 AstrBot 平台实例和收藏来源，不直接信任客户端任意创建 |
| platform | 来源平台标识，例如 qq_official |
| conversation_id | 平台提供的群/会话标识 |
| event_id | 平台稳定消息标识；连接重发若事件包装 ID 不稳定，normalizer 必须选稳定消息 ID |
| sender_id | 收到投递时的发送者；与转发内部原作者分开 |
| source_time | 来源发送时间，可空；不以接收时间填充伪造 |
| received_at | 桥接收到时间，必须有时区；核心另生成 saved_at |
| source_locator | 原始消息定位对象，可带 source message/version；不可得时不编造 |
| content | 有序 ContentNode 列表，支持 text、image、file、quote、forward、unknown |
| attachments | 有序附件元数据，保存原始类型、文件名和 transport_ref |
| missing_fields | 未获取到的来源字段路径列表 |

ContentNode 含 type、text、children、attachment_refs、origin 与 extra。children 保留嵌套顺序；origin 可缺失。unknown 节点保留可序列化原始结构，显示未解析，不能默默丢弃。附件 transport_ref 仅用于受限下载/上传通道，对 agent 返回 blob_id、状态和媒体读取入口。

发布 Schema 由模型导出，合成样例和 schema round-trip 做契约测试；JSON 字段不是每个源新造一套。

### 去重层次

1. 唯一投递键：`(source_instance_id, conversation_id, event_id)`。同键同 payload 重试返回相同 item_id；同键不同 payload 返回 409 `source_event_conflict`，不覆盖。
2. 可验证的原始资料键：原始来源范围＋消息身份＋源版本，可从不同投递追溯同一内容时复用资料，但保存新的 receipt。
3. 无原始身份时，文本和媒体指纹仅提示疑似重复；不能仅因内容一样而删掉另一来源。
4. 附件字节哈希可跨条目物理复用，条目出处仍分开保存。
5. 时间只是范围/诊断字段，不是唯一键。源更新如实产生新源版本，用户本地编辑不被当源更新。

数据库唯一约束在事务中决定胜者。冲突失败后重新读已存在 receipt，而非把网络重试当新创建。首次成功投递返回 201；已持久保存的相同投递返回 200 与 duplicate=true；内容尚在持久化/媒体未齐时返回 202 和可查询状态，不提前清缓存。

## 4. 保存、媒体与 Git 恢复

统一操作状态：准备（prepared）→文件已写（files_written）→历史已记（history_recorded）→完成（committed）；失败标记可重试。SQLite 保存操作 ID、旧/新版本、预期文件列表及内容摘要；操作暂存内容先落盘，再推进状态。

- 核心串行写入协调器检查基准版本，创建可恢复操作，完成临时文件校验后替换目标文件。
- Git 仅 stage 本操作明确列出的 vault 文件，不用 git add .；提交信息含操作 ID 与执行角色，不带凭证或原文全文。
- 提交成功后记录 commit OID 和版本头，再对读者发布；期间读者读取已完成的旧版本或等待，不暴露半套多页结果。
- 重启检查操作状态、文件摘要及 Git 历史中的 operation_id：补做未完成步骤，已提交的不重复提交。
- 文件与数据库/Git 不可用时暂停写入并报状态；禁止 reset --hard 或清空用户未知改动来“修复”。
- 有未归属本操作的 vault 外部改动时返回 `unmanaged_worktree_changes`，引导通过用户入口导入，不偷偷提交全部文件。
- 首次原文保存进入版本记录可在 T08 补接协调器；此前收集里程碑必须有持久操作日志，不能宣称 Git 验收已通过。

媒体在桥接与核心之间使用受认证流式上传。核心校验大小和内容摘要、写临时文件、完成后原子发布；下载失败标为 media_pending/media_failed。下载器只处理已验证平台附件引用，重定向重新检查，拒绝任意文件路径/本机管理地址，避免把未信任资料当可执行命令或任意网络请求。

缓存确认条件：核心原文已持久，附件要么已转交核心可恢复存储，要么桥接仍保留附件恢复引用/缓存；只有接收 201 或 200 本身不足以证明媒体完整。附件链接过期且无字节副本时明确失败，不展示“全部保存成功”。

## 5. 服务与 CLI 合同

| 方法与路径 | 请求/结果 | 权限 |
| --- | --- | --- |
| POST /v1/captures | CaptureEnvelope → item_id, receipt_id, duplicate, capture_state, media_state | collector |
| GET /v1/receipts/{receipt_id} | 持久状态和缺失项，供缓存确认 | collector 对应来源 |
| POST /v1/receipts/{receipt_id}/attachments/{attachment_id} | 字节流上传，返回 blob_id/状态 | collector 对应来源 |
| GET /v1/items/{item_id} | 原文内容表示、当前 revision、missing_fields、来源引用 | agent/owner |
| GET /v1/items/{item_id}/media/{blob_id} | 已绑定该条目的媒体字节或失败状态 | agent/owner |
| GET /v1/sources | 配置来源及 push/history/import 能力 | agent/owner |
| POST /v1/sources/{source_id}/collect | mode=available/history，历史附 since/until，返回 operation/job/status | agent/owner |
| POST /v1/jobs | item_ids、trigger=manual、request_id、manual_run_once（默认 false）→ job_id | agent/owner |
| GET /v1/jobs/{job_id} | 状态、attempt、错误、变更结果 | agent/owner |
| POST /v1/worker/claims | 按能力领取任务 → job_id, lease_token, run_id | worker |
| POST /v1/worker/jobs/{job_id}/heartbeat | run_id, lease_token → lease 状态 | worker |
| POST /v1/worker/jobs/{job_id}/result | run_id, lease_token, operation_id 或 error | worker |
| GET /v1/pages/{page_id} | 页面、revision、引用 | agent/owner |
| GET /v1/search | q、scope=wiki/raw、分页 → 命中与引用 | agent/owner |
| POST /v1/changesets | Changeset → operation_id、状态、页面版本 | agent/owner |
| GET /v1/operations/{operation_id} | 持久操作状态，用于长任务/超时恢复 | agent/owner |
| GET /v1/history | item_id/page_id、分页 → 版本和操作者 | agent/owner |
| PATCH /v1/owner/items/{item_id}/body | base_revision、content、request_id → revision | owner 独立管理入口 |
| PATCH /v1/owner/controls | background_enabled、auto_organize_enabled → 生效状态 | owner |
| GET /v1/controls | 当前开关与 pending 状态，无凭证 | agent/worker/owner |

401 表示未认证，403 已认证但越权，404 不存在，409 基准版本/事件冲突，422 参数/不支持的模式，503 可重试运行不可用。JSON 错误统一为 code、message、retryable、operation_id（可空）。长操作返回 202，必须轮询确认，不能把接收成功当完成。

CLI 使用 `sourcehub source list`、`source collect`、`item show`、`job submit/status`、`page show`、`search`、`history list` 和 `owner edit/controls`。支持 --json，错误非零退出。owner edit 打开用户临时副本，保存后携带 base_revision 提交管理入口；不把用户编辑程序开放给 agent。临时编辑文件权限受限，不直接改 vault。

## 6. 来源收集和后台开关

来源注册保存 source_instance_id、AstrBot platform instance、群/账号范围、enabled、能力和最近事件位置；不是插件下载管理器。

QQ 首期能力为事件推送（push）。collect available 请求处理桥接已收到的积压，返回监听状态、可用缓存和缺口；没有缓存时可直接返回当前状态。collect history 必须返回 `capability_not_supported`，不能等待一个永远无法执行的任务。其他平台能力先由 AstrBot/现有插件验证，再声明 history/import，不为虚构能力创建空 worker。

后台控制是产品业务启停，不等于 kill 核心 API：
- background_enabled=false：桥接确认新配置后停止新增捕获和自动领取；已持久缓存保留，正在提交的安全写入收束。响应区分 requested/effective/bridge_ack，未收到桥接确认不得显示已全停。
- auto_organize_enabled=false：收集不受影响，新原文留待手动；已在提交的操作完成，未开始的自动任务暂停。
- 重新开启自动：只让新保存资料自动进入任务；既有积压显式提交，不突然耗尽模型额度。
- 手动任务不受自动开关影响。后台暂停时普通提交只入队，只有明确 manual_run_once 才让 worker 为该任务单次执行，不能恢复全局轮询。
- 进程完全停止后无事件可接收；记录停机起止和可能缺口，不把未知消息数写成 0。
- 插件停止时注销本插件轮询和监听器，不停用用户其他 AstrBot 平台或插件。

任务由核心 SQLite 唯一队列维护。AstrBot 只通过受限 worker 接口领取，不扫描独立“待整理目录”。运行租约过期后重试增加 attempt；run_id/lease_token 与提交变更关联，旧执行者不得发布结果。

## 7. 模型工具与二次变更

MCP 适配使用独立低权限进程，只包装同一 API，AstrBot 是客户端。catalog 集中定义：
`read_item`、`read_media`、`list_sources`、`collect_source`、`search`、`read_page`、`submit_changeset`、`submit_organize_job`、`get_job`、`get_operation`、`list_history`、`get_controls`。
不提供原文修改、凭证读取、任意 shell 或来源配置写入工具。

执行器通过 AstrBot 已验证插件上下文的 tool_loop_agent 运行；提供当前条目、结构约定、允许工具，不预先规定必须更新多少页。不得使用只生成文本的 llm_generate 冒充工具循环。任务上下文只为复用现有执行器，不自动向 QQ 发模型长回复。

Changeset 字段：
- request_id：幂等键，重试必须相同；同键不同内容 409。
- job_id/run_id/lease_token：后台执行必须提供且匹配；外部直接编辑使用自己的 agent 身份，不伪造 worker。
- pages：每项 page_id、base_revision（新页 null）、page_type、title、body、source_refs。
- source_refs：item_id、raw_revision、node_path（可空），确保引用对应内容版本，而非用户修改后的另一版原文。
- 模型提交的路径由服务按 page_id 生成，拒绝 raw/、绝对路径和 ..；引用不合法整个变更集拒绝。
- 支持首期 source_summary、topic、answer 三种内容页；index 为程序生成，不让模型破坏索引格式。
- 所有页面校验成功并在同一操作内完成才更新页头与索引。与人工并发修改返回 409，模型应重新读取，不自动猜测合并。
- 非空有效变更集及已完成操作才允许任务 succeeded；模型最终文本说“完成”不足以判完成。无修改结果标 no_change 并记录依据，不谎报已生成页面。

首期检索采用 SQLite FTS5 对原文内容表示和页面做全文索引，返回来源定位与版本；若运行环境无 FTS5，T01 阻断依赖检查或在规格中明确替换，不默默失去搜索。索引从已完成文件/版本重建，不是独立真相源。主题关联由模型判断，程序只执行结构约定与一致性。

## 8. 文件及模块边界

精确目标文件见 tasks。contracts 只定义数据与错误；capture 负责幂等保存；storage 提供数据库/媒体/操作日志；history 负责 Git 与恢复；wiki 负责页面变更和检索；access 决定角色；jobs 管任务控制；api/cli/tools 只转发核心服务。

每个模块按职责拆分，不为不同平台复制核心。桥接 normalizer 初期含 QQ 必要增强，其他平台读取 AstrBot 标准结构；当实际新增平台存在独立复杂逻辑时再拆文件，不先铺空目录。

## 9. 风险、验证和完成门禁

- 真实 QQ 权限与消息内容是先验约束：T07 尽早验证，T14 再验证完整整理；失败回设计，不延后到全部代码完成才发现。
- 部分原文结构缺失需明确记录，不能通过推理重建后当原始事实。
- 不信任消息里“忽略规则、修改原文”的指令；原文工具权限与进程隔离共同执行。
- 数据库、文件、Git 非同一个事务；用持久操作状态与故障注入证明恢复，不能用“使用 Git”概括可靠性。
- 依赖版本以 T01 固定记录为准；QQ 原始事件敏感，不进入代码测试样例，测试只用合成/经用户同意脱敏资料。
- 真实模型服务和数据送模范围由用户配置；未配置只完成可独立验证的任务，不把模拟测试标成真实智能整理通过。
- 许可：复用 AstrBot 插件及外部进程，遵守其 AGPL 要求；不从“独立进程”推导无义务。
- GitHub 同步及日常群筛选范围继承 proposal，无默认上传、无新规则引擎。未知配置不阻塞本轮规格成稿，但对应联调门禁未满足不得关闭实施任务。
