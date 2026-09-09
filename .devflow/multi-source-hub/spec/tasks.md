# Metadata（元数据）

- 创建时间（Created At）：2026-09-09 15:19:34 +08:00
- 更新时间（Updated At）：2026-09-09 18:55:33 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：按依赖顺序拆解实施任务及验收证据
- 关联仓库或项目（Related Repository / Project）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`。
- 关联需求草案（Related PRD）：`zzz-docs/多源信息中心PRD.md`。
- 关联对齐（Related Align）：`../plans/2026-09-09-多源信息中心-QQ收藏群首期整体对齐-align.md`。
- 关联计划（Related Plan）：`../plans/2026-09-09-多源信息中心-通用接入与QQ收藏闭环-plan.md`。
- 当前状态（Status）：暂停（Paused），规格待审（Spec Pending Review），未实施。
- 文档边界（Scope / Boundary）：追踪实施与验证，不以复选框替代证据，属于当前任务规格真相源（Source of Truth）；用户授权本轮编写规格，不等于批准实施（Apply）。

# QQ 收藏群首期任务清单（Tasks）

> 2026-09-09 18:55:33 +08:00 状态补充：用户已授权独立检查插件并完成部分真实 QQ 接收探测，源码见 integrations/astrbot/astrbot_plugin_sourcehub_inspector/；不属于完整核心实施。旧文“无业务代码/无真实联调”仅描述 15:37 当时。T07 有局部证据但未验收，14 项任务仍未完成，设计建议仍待审。后续优先查嵌套缺失和媒体保存，见 handoff 002 / bug-log.md。

用户当前不想实施，14 项业务任务全部未执行。下面命令均为未来验证，不是本轮已执行证据。恢复时先讨论/审阅，明确恢复实施意图后才重新检查门禁。

所有复选框初始未完成。当前只生成规格，没有创建以下业务文件或执行测试。T 编号是执行真相源，对应计划任务列保留追溯；不按计划旧编号机械串行。

## 进入实施门禁

- [ ] 用户已批准规格或明确授权实施。
- [ ] proposal/design/tasks 与已确认对齐和收口计划一致。
- [ ] 工作区现有用户修改已记录，不覆盖；Python 使用 backend/.venv，文本修改使用 apply_patch。
- [ ] 无业务阶段依赖未定义的测试夹具；平台和模型前置条件分别在 T07、T12 处理。
- [ ] 不默认启动子代理；若后续采用委派，遵守对应执行技能与用户授权。代码提交须单独确认。

## T01：环境和兼容基线

对应计划：01；依赖：无。

文件：

- `backend/pyproject.toml`
- `backend/uv.lock`
- `deploy/versions.md`
- `docs/sourcehub/verification.md`

- [ ] T01.1 核验可用 AstrBot 正式版本的群全量事件和原始对象能力，固定标签及提交，不使用浮动 latest。
- [ ] T01.2 生成后端 Python 3.12 依赖锁，检查 SQLite FTS5、Git、FastAPI/Pydantic/HTTPX/Typer 和 MCP SDK 能力。
- [ ] T01.3 记录 QQ 账号入群、全量权限、模型配置前置条件；真实资料不写测试库。

验证：uv sync --project backend --locked；backend/.venv/bin/python -c "import sqlite3; c=sqlite3.connect(':memory:'); c.execute('CREATE VIRTUAL TABLE probe USING fts5(body)')"。退出 0；首次锁定先运行 uv lock --project backend，后运行 locked 校验。

通过标准：存在可复现版本和兼容记录；没有真实账号条件不伪造已联调。

## T02：捕获和来源契约

对应计划：02；依赖：T01。

文件：

- `backend/src/sourcehub/contracts/capture.py`
- `backend/src/sourcehub/contracts/source.py`
- `backend/src/sourcehub/config.py`
- `backend/src/sourcehub/constants.py`
- `schema/capture.schema.json`
- `schema/source.schema.json`
- `backend/tests/unit/test_capture_contract.py`
- `backend/tests/fixtures/qq_capture.json`
- `docs/sourcehub/adapter-contract.md`

- [ ] T02.1 按 design 定义版本化封套与有序嵌套节点，保留未知节点和缺失字段。
- [ ] T02.2 先写未知版本拒绝、空来源时间不伪造、嵌套转发往返测试；运行观察目标断言失败，再实现模型。
- [ ] T02.3 导出 JSON Schema 并校验合成样例；来源能力明确 push/history/import，QQ 首期仅 push。

验证：backend/.venv/bin/python -m pytest backend/tests/unit/test_capture_contract.py -q

通过标准：schema 与模型一致，不能将时间戳混用或把 QQ 字段写进核心业务分支。

## T03：最小服务和测试夹具

对应计划：05a；依赖：T02。

文件：

- `backend/src/sourcehub/api/app.py`
- `backend/src/sourcehub/api/capture.py`
- `backend/src/sourcehub/access/policy.py`
- `backend/tests/conftest.py`
- `backend/tests/integration/test_api_bootstrap.py`

- [ ] T03.1 创建 app 工厂，测试每次隔离数据根及 SQLite，配置使用具名 Settings。
- [ ] T03.2 定义 collector/agent/worker/owner 权限依赖，先测 401/403，禁止接受自报角色。
- [ ] T03.3 创建 client、collector_headers、agent_headers、capture_payload 夹具；existing_item 按需调用捕获服务，T04 实现前不伪返回成功。

验证：backend/.venv/bin/python -m pytest backend/tests/integration/test_api_bootstrap.py -q

通过标准：服务夹具先于捕获和权限测试，不留下跨任务循环依赖。

## T04：持久捕获和媒体去重

对应计划：03；依赖：T03。

文件：

- `backend/src/sourcehub/storage/database.py`
- `backend/src/sourcehub/storage/blobs.py`
- `backend/src/sourcehub/storage/operations.py`
- `backend/src/sourcehub/capture/service.py`
- `backend/src/sourcehub/capture/deduplication.py`
- `backend/tests/integration/test_capture_idempotency.py`
- `backend/tests/integration/test_capture_recovery.py`

- [ ] T04.1 先测同事件并发、同键不同内容、同正文不同来源、已保存未回报时中断。
- [ ] T04.2 实现唯一投递约束与资料/投递分离；媒体流校验后原子发布，不重复物理存储相同字节。
- [ ] T04.3 实现持久准备日志和查询状态，附件未齐返回 pending；401/403 不写任何文件。
- [ ] T04.4 重试返回原 item_id/receipt_id；可证明同来源转发复用条目，无法确定仅标疑似重复。

验证：backend/.venv/bin/python -m pytest backend/tests/integration/test_capture_idempotency.py backend/tests/integration/test_capture_recovery.py -q

通过标准：无重复条目、无半文件假成功，缺失媒体可观察；Git 完整验收留到 T08。

## T05：一个 AstrBot 桥接插件

对应计划：06；依赖：T04。

文件：

- `integrations/astrbot/astrbot_plugin_sourcehub/main.py`
- `integrations/astrbot/astrbot_plugin_sourcehub/normalizer.py`
- `integrations/astrbot/astrbot_plugin_sourcehub/client.py`
- `integrations/astrbot/astrbot_plugin_sourcehub/spool.py`
- `integrations/astrbot/astrbot_plugin_sourcehub/metadata.yaml`
- `integrations/astrbot/astrbot_plugin_sourcehub/_conf_schema.json`
- `backend/tests/unit/test_qq_normalizer.py`
- `backend/tests/integration/test_bridge_spool.py`

- [ ] T05.1 按固定 SDK 版本注册消息监听器；收藏群与本人账号范围配置，不要求命令或 @。
- [ ] T05.2 从原始对象取来源时间、引用与全部可获取节点，不以第一段文本代替合并转发。
- [ ] T05.3 未知/缺失结构显式保留，媒体转交确认后清相应缓存；收到事件先持久缓存，重启复用原身份。
- [ ] T05.4 同一插件复用 AstrBot 标准结构，QQ 只做必要补充；不创建新的多平台登录/协议系统。
- [ ] T05.5 排除机器人自身事件，停用插件清理自己的监听和任务，不停用其他插件。

验证：backend/.venv/bin/python -m pytest backend/tests/unit/test_qq_normalizer.py backend/tests/integration/test_bridge_spool.py -q

通过标准：关闭模型聊天仍可保存；模拟缓存重放、附件链接失败、嵌套与多个本人账号。

## T06：来源工具、后台开关与持久队列

对应计划：07；依赖：T05。

文件：

- `backend/src/sourcehub/sources/registry.py`
- `backend/src/sourcehub/sources/capabilities.py`
- `backend/src/sourcehub/contracts/job.py`
- `backend/src/sourcehub/jobs/repository.py`
- `backend/src/sourcehub/jobs/worker.py`
- `backend/src/sourcehub/jobs/controls.py`
- `backend/src/sourcehub/api/sources.py`
- `backend/src/sourcehub/api/jobs.py`
- `backend/tests/integration/test_source_capabilities.py`
- `backend/tests/integration/test_job_controls.py`

- [ ] T06.1 按 design 建立唯一任务队列、租约、run_id 和旧 worker 拒绝规则。
- [ ] T06.2 测试 auto 关闭继续收集、后台暂停确认状态、手动 run_once 不恢复全局后台、重新开启不自动扫积压。
- [ ] T06.3 collect available 只处理可用缓存/返回监听状态；QQ collect history 明确不支持。
- [ ] T06.4 桥接断联时控制状态不能假装已生效，离线缺口记录 unknown 而非零。

验证：backend/.venv/bin/python -m pytest backend/tests/integration/test_source_capabilities.py backend/tests/integration/test_job_controls.py -q

通过标准：两个 worker 无双领，控制状态持久恢复；本阶段不要求真实模型。

## T07：尽早验证真实 QQ 最小接入链路

对应计划：01/11 前置；依赖：T06。

文件：

- `docs/sourcehub/verification.md`
- `deploy/versions.md`

- [ ] T07.1 准备可审阅配置与已验证插件，再由用户完成平台必要授权；不索取聊天中的密钥。
- [ ] T07.2 用户在自有群转发文本、图片、文件、引用和合并记录，无 @/命令；核验实际原始事件及附件。
- [ ] T07.3 对到达的事件重放，验证保存、来源定位和去重；记录下载失败及消息结构缺失。
- [ ] T07.4 若全量权限或关键内容不可获取，记录现象/原因/方案并回 design，不默改私聊或登录个人号。

验证：真实 QQ 联调记录：版本、时间、样例类别、预期与实测、脱敏证据定位。

通过标准：真实链路通过才宣称平台接入可用；未授权或未配置仅完成其他独立工作。

## T08：用户原文权限、Git 和可恢复变更

对应计划：04；依赖：T04；T07 成功后继续真实链路。

文件：

- `backend/src/sourcehub/access/owner.py`
- `backend/src/sourcehub/history/git_store.py`
- `backend/src/sourcehub/history/recovery.py`
- `backend/src/sourcehub/wiki/changesets.py`
- `backend/src/sourcehub/api/owner.py`
- `backend/tests/integration/test_permissions.py`
- `backend/tests/integration/test_git_recovery.py`
- `backend/tests/integration/test_page_conflicts.py`

- [ ] T08.1 先测 agent 原文写拒绝、owner 可修订、采集重试不覆盖修订。
- [ ] T08.2 以单写协调器连接文件、数据库、Git 状态；故障注入覆盖每次推进前后崩溃。
- [ ] T08.3 只 stage 本操作列表，Git commit 含 operation_id；检测未知修改时报错，不 reset 或全目录 add。
- [ ] T08.4 基准 revision 过时返回 409；恢复旧版本产生新记录；原始引用可定位历史版本。

验证：backend/.venv/bin/python -m pytest backend/tests/integration/test_permissions.py backend/tests/integration/test_git_recovery.py backend/tests/integration/test_page_conflicts.py -q

通过标准：数据版本可恢复、不会吞入无关文件；此处产品 Git 历史不授权开发仓库提交。

## T09：完整 API 与命令行

对应计划：05b；依赖：T08。

文件：

- `backend/src/sourcehub/api/pages.py`
- `backend/src/sourcehub/cli/app.py`
- `backend/src/sourcehub/cli/client.py`
- `backend/tests/integration/test_api_cli.py`

- [ ] T09.1 按 design 路由表补齐读原文、媒体、状态、历史和管理端，鉴权与错误一致。
- [ ] T09.2 CLI 只调用服务，JSON 输出与非零失败退出；owner edit 用临时副本和 base_revision 提交。
- [ ] T09.3 测试管理路由在 worker 网络入口不可达，核心下行响应不暴露临时附件凭证。

验证：backend/.venv/bin/python -m pytest backend/tests/integration/test_api_cli.py -q

通过标准：相同操作 API/CLI 返回一致身份，长任务 202 可轮询，不误报完成。

## T10：外部工具和模型结构约定

对应计划：08；依赖：T09。

文件：

- `backend/src/sourcehub/tools/catalog.py`
- `backend/src/sourcehub/tools/mcp_server.py`
- `schema/AGENTS.md`
- `backend/tests/integration/test_tool_contracts.py`

- [ ] T10.1 集中注册 design 第 7 节工具及参数，MCP 服务只包装 API，模型不获得 owner 工具。
- [ ] T10.2 独立 MCP 测试客户端完成发现、参数错误、读取、收集状态和越权拒绝。
- [ ] T10.3 结构约定明确来源引用、语义由模型判断、外部资料不覆盖系统规则；不放固定主题关键词映射。

验证：backend/.venv/bin/python -m pytest backend/tests/integration/test_tool_contracts.py -q

通过标准：客户端实际调用成功，不仅进程启动；catalog 和服务路由一致。

## T11：二次页面、检索和变更集

对应计划：10；依赖：T10。

文件：

- `backend/src/sourcehub/contracts/page.py`
- `backend/src/sourcehub/wiki/service.py`
- `backend/src/sourcehub/wiki/search.py`
- `schema/page.schema.json`
- `schema/changeset.schema.json`
- `backend/tests/integration/test_wiki_changesets.py`
- `backend/tests/acceptance/test_knowledge_flow.py`

- [ ] T11.1 实现 source_summary/topic/answer、程序生成索引与全文检索，所有变更调用 T08 协调器。
- [ ] T11.2 先测无效原文版本引用、raw 路径、旧页面版本、重复 request_id 与同键不同内容；全组拒绝而非部分成功。
- [ ] T11.3 同主题合成变更更新已有页面，原文回链带 raw_revision/node_path；外部手动变更不依赖模型。
- [ ] T11.4 模型提交的任务变更需 run_id/lease_token 校验，过期运行者不能通过工具绕过 result 验证写入。

验证：backend/.venv/bin/python -m pytest backend/tests/integration/test_wiki_changesets.py backend/tests/acceptance/test_knowledge_flow.py -q

通过标准：确定性写入与引用通过，不把合成变更冒充模型质量证据。

## T12：AstrBot 整理执行与任务回报

对应计划：09；依赖：T11。

文件：

- `backend/src/sourcehub/agents/contract.py`
- `backend/src/sourcehub/agents/prompts.py`
- `integrations/astrbot/astrbot_plugin_sourcehub/runner.py`
- `backend/tests/integration/test_runner_lifecycle.py`

- [ ] T12.1 worker 领取核心任务，提供受限 tools 和结构约定，复用 tool_loop_agent，不另建模型代理循环。
- [ ] T12.2 先用伪执行器验证心跳/超时/失败/重试/no_change/重复结果，检查 operation 已提交才标 succeeded。
- [ ] T12.3 模型服务由用户指定并配置允许送模范围，不读其他应用的认证来代替。
- [ ] T12.4 真实模型用允许的样例读取原文、搜已有主题、提交变更，再核查引用质量；关闭外部交互式智能体仍能运行。

验证：backend/.venv/bin/python -m pytest backend/tests/integration/test_runner_lifecycle.py -q；另记真实模型工具执行证据。

通过标准：模型最终文字不算提交成功；失败原文保留，无未经授权的群自动长回复。

## T13：隔离部署与运行文档

对应计划：11；依赖：T12。

文件：

- `deploy/compose.yaml`
- `deploy/sourcehub.env.example`
- `docs/sourcehub/operations.md`
- `backend/tests/acceptance/test_runtime_permissions.py`

- [ ] T13.1 配置核心私有卷、worker 独立卷和本机管理入口；agent 无原始目录写挂载和 owner 凭证。
- [ ] T13.2 凭证示例只给变量名，无真实默认 secret；服务启动缺必要凭证时明确拒绝。
- [ ] T13.3 记录后台暂停、auto 关闭、进程退出差别及缺口；验证恢复与半操作修复。

验证：backend/.venv/bin/python -m pytest backend/tests/acceptance/test_runtime_permissions.py -q；真实隔离环境验证卷与网络可见性。

通过标准：API 越权和文件系统绕过均在配置边界内阻断，记录宿主全权限执行者不受应用隔离的限制。

## T14：完整验收、审查和文档收口

对应计划：11/12；依赖：T13。

文件：

- `backend/tests/acceptance/test_collection_flow.py`
- `docs/sourcehub/quickstart.md`
- `docs/sourcehub/verification.md`
- `zzz-docs/多源信息中心PRD.md`
- `zzz-docs/多源信息中心结构图.md`
- `zzz-docs/多源信息中心与LLM-Wiki知识预编译讨论整理.md`

- [ ] T14.1 用 R01–R10 逐项记录自动测试与真实证据，重放/并发/媒体失败/开关/原文权限/知识引用均有结果。
- [ ] T14.2 同步旧 PRD 与结构图中过时权限与人工确认描述；历史纪要加状态指针，不改写历史为已批准。
- [ ] T14.3 旧图片如仍冲突明确标旧版；图片更新另按图像工具要求执行，不以错误图片继续代表当前方案。
- [ ] T14.4 进行聚焦代码审查与新鲜验证，更新任务状态/检查点和延期项；未过项目不能勾完成。
- [ ] T14.5 代码完成后询问用户是否提交，不在任务中自行 commit 或上传私人数据。

验证：uv sync --project backend --locked；backend/.venv/bin/python -m pytest backend/tests/unit backend/tests/integration backend/tests/acceptance -q；git diff --check。

通过标准：自动测试全过且真实 QQ、模型、隔离证据齐备才完成；无全局 ESLint，无无关 TS 修复。

## 验证边界和延期

本轮规格文档自审不等于执行这些未来测试。实施遵循测试驱动开发（TDD）时先观察目标行为失败，再最小实现，不把“模块不存在”作为唯一行为证据。测试应实际覆盖崩溃点、并发和权限，不仅断言 mock 调用。

G（GitHub 远端同步）不在上述实施任务：保留于 `../backlog.md`，明确目标、内容及媒体后另建计划规格。不能将本地 Git 自动记录等同于默认授权 push。

日常 QQ 群的规则/正则/LLM 筛选继续按 `../deferred/QQ指定群持续收集与规则筛选.md` 延期：首期主动收藏闭环验收后另启阶段；不影响专用收藏群事件接收。其他 AstrBot 平台使用同一个桥接插件，未经真实验证不宣称已接通。

任务完成须更新证据位置；失败写现象、原因、解决方案。出现设计缺陷回规格，不在实现中暗改范围。
