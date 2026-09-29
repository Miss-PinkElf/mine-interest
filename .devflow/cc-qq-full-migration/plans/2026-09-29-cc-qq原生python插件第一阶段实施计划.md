# cc-qq 原生 Python 插件第一阶段实施计划（Implementation Plan）

> 执行者（Agentic Worker）：先核对本文件与当前开放规格（OpenSpec）的 `proposal.md`、`design.md`、`tasks.md`，再按复选框推进。实施中使用单会话顺序执行与里程碑审查；每次插件代码变更都提升版本并覆盖 AstrBot 插件副本。提交代码需用户明确允许。

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:29:00 +08:00
- 更新时间（Updated At）：2026-09-29 10:53:02 +08:00
- 收尾核对时间（Handoff Reviewed At）：2026-09-29 11:00:28 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：把 QQ、身份、双代理、会话和基础命令拆为可实施的第一阶段任务。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 已确认对齐（Aligned Design）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-ding原生python迁移qq插件-需求对齐.md`
- 总体计划（Master Plan）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-ding原生python完整迁移qq插件-总体实施计划.md`
- 当前状态（Status）：计划中（Planned）
- 文档边界（Scope / Boundary）：本阶段实施步骤真相源（source of truth）；只覆盖总体计划 T00–T04，不把后续任务、媒体、Console 和 A2A 从完整范围剔除。未生成开放规格三件套前不得实施。

**目标（Goal）：**让已配置的 QQ 群聊和私聊通过 AstrBot 原生 Python 插件分别调用 Claude Code、Codex，完成多轮、恢复、中断、基本命令与准入控制。

**架构（Architecture）：**AstrBot 回调归一为 `IncomingMessage`，准入通过后交给 `SessionService`；它用每会话锁管理代理执行，并把统一 `AgentEvent` 交给回复适配器。代理 CLI 仅在 `AgentRunner` 内启动，业务模块不解析其原生流格式。

**技术栈（Tech Stack）：**AstrBot Python API、`asyncio`、`sqlite3`、Claude Code CLI、Codex CLI。首阶段无新增第三方 Python 运行依赖。

---

## 当前实施基线与下一批顺序

- 当前源码版本为 `0.1.2`，本机 AstrBot 插件副本已同步为同版本。`main.py` 仍只回复“代理会话功能正在接入”；插件骨架、准入、SQLite 建表和代理适配器虽已有代码，T01–T03 尚需核对加载与实际行为，不能据文件存在勾选完成。
- 下一批先核对 AstrBot 是否加载、QQ 事件字段与回复接口，再核对 Claude Code 和 Codex 当前 CLI 的参数、事件、取消及错误行为。发现不符时先修订本计划和开放规格（OpenSpec），随后补代码；每次插件代码补丁同时提升版本并覆盖安装副本。
- 会话闭环按 `storage.py` 的事务接口 → `sessions.py` 的会话锁、恢复与队列 → `commands/registry.py` 和 `commands/session.py` 的基础命令 → `service.py` 的完整编排 → `main.py` 接线的顺序实施。每一步都以当前会话键、消息 ID 和统一代理事件为输入输出契约。
- 阶段验收记录 QQ 群聊、私聊、Claude Code、Codex 的首次对话与恢复，中断、重复消息、未授权输入和插件重载；缺少真实 QQ 或 CLI 条件时保留未验证状态，不把静态代码核对写成运行通过。
- 用户随后新增群号白名单和“群聊必须 @ 机器人才能对话”的要求。群号白名单已有 `enabled_group_ids` 配置与 `policy.py` 准入逻辑，但仍须实际验收；@ 门禁的命令范围、机器人身份识别和消息清理尚未完成 Mini Align。本计划暂保留原已批准范围，下一次对话确认细节后再修订任务，不把此要求误写为已实现或永久延期。

## 前置事实与文件边界

- 参考 `integrations/astrbot/astrbot_plugin_sourcehub_inspector/main.py` 的 `Star`、`@filter.event_message_type` 与 `get_group_id()` 模式；参考 `integrations/astrbot/astrbot_plugin_sourcehub_bilibili/main.py` 的 `StarTools.get_data_dir()` 与页面注册模式。
- 参考 `cc-ding/src/biz/cc-ding-cli.ts` 的消息入口、`session.ts` 的会话行为、`claude-process.ts` 和 `codex-agent.ts` 的 CLI 参数与事件解析。`cc-ding/` 是忽略目录，不能作为新插件实际运行依赖。
- 第一阶段目标文件按总体计划文件地图中的 `main.py`、`constants.py`、`contracts.py`、`policy.py`、`storage.py`、`sessions.py`、`service.py`、`platform/`、`agents/`、`commands/` 建立；每个文件只承担对应单一职责。
- 插件包名定为 `astrbot_plugin_cc_qq`，仓库源码位置为 `integrations/astrbot/astrbot_plugin_cc_qq/`；本机副本位置是 AstrBot 用户数据目录下的 `data/plugins/astrbot_plugin_cc_qq/`，不把机器绝对路径写进仓库配置。

## Task 0：固定第一阶段功能基线

**文件：**创建 `.devflow/cc-qq-full-migration/spec/feature-mapping.md`；只读 `cc-ding/src/biz/commands.ts`、`types.ts`、`console.ts`、`a2a/`、`bin/cc-ding.ts`。

- [ ] 列出每个原命令、配置字段、Console 操作、CLI 子命令、A2A 操作和消息形态，记录源路径、目标阶段、QQ 目标行为、验收动作和当前状态。命令源以 `COMMAND_REGISTRY` 加额外 `parse*Command` 为准；Console 以 HTTP 路由为准。
- [ ] 标明本阶段最低闭环项：`/help`、`/info`、`/new`、`/resume`、`/end`、`/goon`、`/cc`、`/!`，QQ 群／私聊、白名单、两种代理和文本回复；其余项列入后续阶段，不写“已完成”。
- [ ] 核对源代码的权限事实：Claude 回退 `bypassPermissions`，Codex 使用 `danger-full-access`；`/qa` 只读修正留在阶段 2，但阶段 1 的文档不得宣称它已可用。

**完成判据：**六类来源都有条目，且本阶段与后续阶段状态清楚。

## Task 1：插件骨架与契约

**文件：**创建 `integrations/astrbot/astrbot_plugin_cc_qq/__init__.py`、`main.py`、`metadata.yaml`、`_conf_schema.json`、`constants.py`、`contracts.py`、`README.md`。

- [ ] 在 `metadata.yaml`、`constants.py` 和 `@register` 使用同一版本；`main.py` 的 `initialize()` 读取配置并初始化服务，`terminate()` 关闭任务与进程。默认不启用任何 QQ 群和私聊。
- [ ] 配置至少包含平台 ID、启用群、私聊开关、owner、管理员、全局及群白名单、群／私聊工作目录、默认代理和模型；必要默认值放 `constants.py`，配置 schema 给中文说明。
- [ ] 在 `contracts.py` 定义不可变的输入事件、会话键、授权结果和代理事件。输入契约应有 `platform_id`、`conversation_kind`、`conversation_id`、`sender_id`、`message_id`、`text`；会话键由平台实例、群／私聊类别和 ID 共同组成。
- [ ] 在 README 写阶段 1 能力、CLI 安装要求、原项目高权限默认值、当前未实现功能和本机副本位置；避免把阶段 1 宣称为完整迁移。

**完成判据：**插件可被 AstrBot 识别，空配置不会启动代理；三处版本一致。每次代码编辑后同步本机副本。

## Task 2：事件转换、准入和回复

**文件：**创建 `platform/qq_events.py`、`platform/replies.py`、`policy.py`；修改 `main.py`。

- [ ] 事件转换只使用 AstrBot 提供的稳定身份与消息接口，区分 QQ 群和私聊，拒绝未配置平台或群；消息 ID 用于幂等键，不用昵称作身份。
- [ ] `policy.py` 将 owner、管理员、全局白名单和群白名单归为统一授权结果；owner／管理员可执行管理命令，普通白名单用户可发起代理会话。自由模式和 `/qa` 的完整业务在阶段 2 实现，不提前开放空白权限分支。
- [ ] `replies.py` 用 AstrBot 事件或 `Context.send_message` 发送文本；超过平台长度的内容分段并保留顺序，发送异常返回明确失败状态，避免服务误以为已送达。
- [ ] `main.py` 只做事件转换、服务调用与回复；逻辑不直接读取 CLI JSON 或 SQLite 表。

**完成判据：**相同数字 ID 在不同群、私聊和平台实例下成为不同会话；未授权者不会进入代理调用；文本回复可达。

## Task 3：持久会话与代理进程

**文件：**创建 `storage.py`、`sessions.py`、`agents/base.py`、`agents/process.py`、`agents/claude.py`、`agents/codex.py`。

- [ ] `storage.py` 在 `StarTools.get_data_dir(PLUGIN_NAME)` 下建立 `sqlite3` 数据库，至少保存会话键、代理类型、代理会话 ID、工作目录、状态和最近消息 ID；事务提交后才把消息视为已处理。
- [ ] `sessions.py` 为每个会话键维护一个异步锁与内存队列，重载时只恢复持久的代理会话标识，不复活已结束的子进程；`/end` 关闭当前会话，`/resume` 只能使用同会话范围的历史。
- [ ] `agents/process.py` 通过参数数组调用 `asyncio.create_subprocess_exec`；子进程标准输出按行读，标准错误单独收集，取消时先终止再清理；不把用户文本拼入 Shell 命令。
- [ ] `agents/claude.py` 使用原项目的 `--print --output-format stream-json --verbose` 交互模式，保留默认 `bypassPermissions`，解析会话 ID、文本和完成／错误事件；恢复时使用原生 `--resume`。
- [ ] `agents/codex.py` 使用 `codex exec --json` 和 `exec resume`，保留原项目 `danger-full-access` 与无需终端审批的普通模式；解析 `thread.started`、文本、`turn.completed`、`turn.failed`。
- [ ] 两代理适配器共同输出 `AgentEvent`；`sessions.py` 只识别统一事件和会话 ID，不读取代理私有 JSON。

**完成判据：**同一会话串行、不同会话可并行；两代理的首轮与恢复使用正确 ID；取消和异常退出后进程被清理。

## Task 4：基础命令和端到端编排

**文件：**创建 `commands/registry.py`、`commands/session.py`、`service.py`；修改 `main.py`、`README.md`、`metadata.yaml`、`constants.py`。

- [ ] 命令注册表包含名称、描述、用法和所需角色；`/help` 根据用户授权列出命令，未知斜杠文本遵循原 `/cc` 或普通代理输入规则，不擅自吞掉。
- [ ] `/new` 创建新代理会话；`/resume` 限当前群／私聊历史；`/end` 关闭；`/goon` 使用当前代理 ID 重启；`/!` 中断当前执行并处理排队消息；`/cc` 透传原始消息；`/info` 展示非敏感状态。
- [ ] `service.py` 的固定顺序为“身份与配置 → 去重 → 显式命令 → 会话队列 → 代理事件 → QQ 回复”；普通自然语言交给代理原生工具选择，不新增关键词意图路由。
- [ ] 插件重载前保存当前会话状态，取消在运行的子进程；重载后按持久 ID 继续。更新 README 的实际配置与使用示例。

**完成判据：**真实 QQ 群聊与私聊均可对两种代理完成新建、多轮、继续、中断和结束；阶段 1 映射条目有实际结果记录。

## 每个任务的版本、覆盖与记录门禁

- [ ] 每次修改插件代码，在同一补丁中更新 `metadata.yaml`、`constants.py` 和入口装饰器使用的版本；按仓库补丁规则检查本次差异。
- [ ] 将当前源码覆盖到本机 AstrBot 用户数据目录的 `data/plugins/astrbot_plugin_cc_qq/`，确认副本的 `metadata.yaml` 与仓库一致；复制使用脚本／批量工具时展示 `git status --short` 和 `git diff -- <相对路径>`，并在回复说明该方式的内联差异限制。
- [ ] 一个阶段里程碑完成后，按 devflow 写检查点（Checkpoint）；必要时更新问题清单的现象、原因、解决方案。完成声明前取得新的实际运行证据，不用旧 mission 的测试替代。
- [ ] 代码修改完成后询问用户是否需要提交；未经明确允许不执行 `git commit`。

## 本轮不做 / 后续阶段（Deferred Scope）

- 阶段 2 的任务／调度／媒体／辅助命令：当前阶段先固化 QQ 与代理会话接口；Task 4 的真实多轮和恢复通过后进入总体计划 T05–T07，必须继续。
- 阶段 3 的 Web Console／跨实例管理／A2A：依赖前两阶段的数据与身份接口；T05–T07 稳定后进入总体计划 T08–T09，必须继续。
- 阶段 4 的完整收口：依赖前三阶段产物；T08–T09 验收后进入总体计划 T10，必须继续。
