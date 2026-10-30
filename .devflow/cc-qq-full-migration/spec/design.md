# cc-qq 原生 Python 插件第一阶段设计（Design）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:33:00 +08:00
- 更新时间（Updated At）：2026-10-30 15:00:00 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：约定第一阶段的模块边界、数据契约、调用顺序与异常处理。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 总体计划（Master Plan）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-ding原生python完整迁移qq插件-总体实施计划.md`
- 阶段计划（Stage Plan）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-qq原生python插件第一阶段实施计划.md`
- 群聊对齐（Group Admission Alignment）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-qq群聊白名单与必须@对齐.md`
- 当前状态（Status）：代码已实施、待运行验收（Implemented / Runtime Verification Pending）
- 文档边界（Scope / Boundary）：本 mission 第一阶段设计真相源（source of truth）；只规定 QQ 与双代理闭环，后续阶段依总体计划继续。

## 总体思路

```
QQ／AstrBot 事件
  → main.py 生命周期与事件入口
  → platform/qq_events.py 输入归一
  → policy.py 群号／身份准入
  → 群聊 @ 当前机器人门禁
  → service.py 命令与会话编排
  → sessions.py 持久会话和同会话队列
  → agents/claude.py 或 agents/codex.py
  → 统一 AgentEvent
  → platform/replies.py 通过 AstrBot 回复
```

`main.py` 不处理 CLI JSON、数据库表或具体命令。代理适配器不依赖 AstrBot 事件类型；业务层不直接调用钉钉或 QQ 协议 URL。普通自然语言直接交给所选代理，由代理根据原生工具和后续插件工具元数据自行选择工具；只有显式斜杠命令进入命令注册表。

## 结构与边界

| 模块 | 输入 | 输出 | 不承担的职责 |
| --- | --- | --- | --- |
| `main.py` | AstrBot 消息与配置 | 生命周期调用、回复 | 权限细节、会话 SQL、CLI 解析 |
| `platform/qq_events.py` | `AstrMessageEvent` | `IncomingMessage` | 业务命令判断 |
| `policy.py` | QQ 身份、会话配置 | `AuthorizationDecision` | 文件系统隔离声明 |
| `service.py` | 已归一消息和授权结果 | 回复事件或排队结果 | 代理私有 JSON 解析 |
| `sessions.py`、`storage.py` | 会话键、执行请求与状态 | 会话记录、队列、历史 | 平台消息发送 |
| `agents/base.py`、`process.py` | 代理请求与参数 | 统一 `AgentEvent`、进程句柄 | 用户准入 |
| `agents/claude.py`、`codex.py` | 代理原生流 | 文本、会话 ID、完成／错误事件 | AstrBot 类型 |
| `commands/registry.py`、`session.py` | 显式命令、角色、会话 | 命令结果 | 自然语言意图猜测 |
| `platform/replies.py` | 回复事件、原消息来源 | QQ 发送结果 | 模型执行 |

配置使用 AstrBot 的 `_conf_schema.json` 和插件配置；阶段 1 包含平台 ID、已启用群、私聊开关、owner、管理员、全局／群白名单、会话工作目录、代理类型和模型。默认启用范围为空。数据使用 `StarTools.get_data_dir(PLUGIN_NAME)` 下的 SQLite；会话表包含复合会话键、代理类型、代理会话 ID、工作目录和状态，已处理消息表以平台实例加消息 ID 去重。配置与状态键集中在 `constants.py`。

模型配置增量：`default_claude_model` 与 `default_codex_model` 分别对应 Claude Code、Codex。`policy.py` 先确定代理类型，再按“群规则 `model` → 对应代理默认模型 → CLI 默认模型”取值；旧 `default_model` 停止读取。`sessions.py` 执行已有会话时以持久化的 `agent_type` 为准；如果当前群规则改用了另一代理，该旧会话只使用原代理的独立默认模型，避免跨代理传参。私聊按 `default_agent` 决定代理。增量对齐及计划见 `plans/2026-09-29-cc-qq双代理独立默认模型对齐.md`、`plans/2026-09-29-cc-qq双代理独立默认模型实施计划.md`。

## 数据流与接口

1. `qq_events.py` 从 AstrBot 事件取得平台 ID、群／私聊类型、会话 ID、发送者 QQ ID、消息 ID 和文本；复合会话键为“平台实例 + 群／私聊 + 对应 ID”。群聊还需读取当前机器人 QQ ID 和 `At` 段目标，以精确匹配判断是否 @ 当前机器人；无法可靠读取时不通过门禁。只移除当前机器人 @ 段，保留其他文本；私聊不要求 @。阶段 1 的非文本段在通过准入后给出明确提示，阶段 2 再提取附件。
2. `policy.py` 先检查平台与群／私聊启用范围，再检查 owner／管理员或白名单。群号白名单使用 `enabled_group_ids`，群成员名单使用 `group_rules_json.allowed_user_ids`。群聊 @ 门禁在命令和代理分派前统一执行，未命中时静默；拒绝结果不会调用 `ConversationService` 或 CLI。消息准入和代理执行权限分别保存；不能把白名单说成文件系统限制。
3. `service.py` 用消息 ID 做去重，匹配显式命令。普通文本进入当前会话的异步锁和队列；同一会话按到达顺序执行，不同会话独立。会话及消息处理状态在 SQLite 事务中更新。
4. `ProcessRunner` 用 `asyncio.create_subprocess_exec` 启动 CLI，参数以数组传递、消息通过标准输入（stdin）传递。Claude 使用 `--print --output-format stream-json --verbose` 与 `--resume`；Codex 使用 `exec --json` 与 `exec resume`。代理参数按每轮权限档位生成：只读、工作目录读写、完全权限。代理输出映射为统一事件，服务仅识别统一事件。
5. CLI 发出的会话 ID／线程 ID 持久化；`/new` 创建新历史，`/resume` 限当前复合会话键，`/end` 标为结束，`/goon` 用当前 ID 重新执行，`/!` 中断当前进程并恢复队列推进。插件重载时终止进程，但保留可恢复的会话 ID。
6. 回复模块对长文本顺序分段，并通过 AstrBot 的消息来源标识发送。发送失败写入回执状态并记录脱敏错误类型；不在群中回显密钥或完整环境变量。即时确认和进度提示进入第二阶段。

## 权限分级与审批（Permission Profiles & Approval）

```
QQ 消息
  → policy.py 判定角色（owner/admin/member/guest）与每轮档位
  → sessions.py 将档位、发送者、来源写入 AgentRequest
  → agents/profiles.py 生成 CLI 参数与 Claude settings
  → Claude：dontAsk / acceptEdits + 沙箱 / dontAsk + 守护 hook
  → Codex：read-only / workspace-write / danger-full-access
```

- 角色与档位：guest=`readonly`，member=`workspace`，owner／管理员=`full`；群规则可覆盖 guest／member 档位。档位按每轮发言者计算，不写入会话记录，避免同群用户继承权限。
- Claude 只读：`--permission-mode dontAsk` + `--tools "Read,Grep,Glob,TodoWrite"`；默认 `--setting-sources ""`，不让工作区自带 settings 参与。
- Claude 工作区读写：`--permission-mode acceptEdits` + `--settings` 注入 Seatbelt/bubblewrap 沙箱、`autoAllowBashIfSandboxed`、`allowUnsandboxedCommands`、关键路径 deny 与 PreToolUse 审批 hook。
- Claude 完全权限：`--permission-mode dontAsk` + 全量守护 hook。2.1.202 实测 `bypassPermissions` 不执行 deny 规则，因此改为「默认放行、只拦凭据/系统目录与系统级危险命令」，hook 异常时拒绝。
- Codex：`readonly`/`workspace` 使用权限档案（`ccqq-readonly`、`ccqq-workspace`）收紧读写范围并排除 `/tmp`；`full` 使用 `sandbox_mode="danger-full-access"`；统一 `approval_policy="never"`。
- 审批：PreToolUse hook 读取 stdin 工具调用，经本机 127.0.0.1 JSON 行协议请求 `ApprovalBroker`；broker 在来源会话发送审批号，owner／管理员用 `/approve`、`/deny` 回复。审批命令在 `main.py` 队列前处理，避免与会话锁死锁；超时、异常、broker 不可达一律拒绝。
- 工作目录：管理员 `/cd` 仅能进入 `allowed_work_dirs` 的 `realpath` 子目录；覆盖值按复合会话键存入 SQLite；下次新会话生效。
- 审计：`permission_audit` 表记录审批和拒绝事件；摘要截断，不记录密钥。
- 已知边界：Codex `exec` 的非交互审批仍为 under development，本轮只依赖 OS 沙箱硬边界；字符串危险命令规则有绕过空间，OS 沙箱才是主边界。

## 关闭与恢复细节

- `SessionManager` 关闭时先设置门禁；已经排队并等待会话锁的请求在改为 `processing` 前退出，保留 `queued` 回执供新实例重新核验授权后处理。
- 已开始执行的请求在关闭时中断；旧实例等待任务和子进程结束后保留 `processing` 回执，新实例标为 `interrupted` 并通知用户，不自动重复执行。
- 关闭门禁之后才到达旧插件入口的全新消息是否会由 AstrBot 重投，取决于平台重载时序；该边缘窗口需在真实加载与重载验收中观察，不能用静态审查替代。

## 需求 5：媒体输入输出与长文本渲染（Media I/O & Long-text Rendering）

### 数据流

```
QQ 事件
  → qq_events.py 收集文本、Image、Reply、Forward(id)
  → media.py 展开转发、下载图片、校验类型／大小／数量、落盘
  → service.py 编排（媒体随消息进入会话）
  → sessions.py 组装带媒体清单的 prompt
  → Claude（Read 工具读图）或 Codex（-i 参数）
  → 统一 AgentEvent
  → render.py 判断是否需要长图
  → replies.py 解析 [[image:path]] 并图文混排发送
```

### 媒体输入

- `IncomingMessage` 增加 `images`、`quoted_text`、`quoted_images`、`forward_text`、`forward_images`。
- 直接图片与引用图片复用 `Image.convert_to_file_path()` 落盘；合并转发复用 `OneBotClient.get_forward_msg` 与 `OneBotPayloadParser`。
- 落盘目录：`<插件数据目录>/media/<会话键哈希>/<YYYYMMDD>/<message_id>/`；保留 7 天，启动时清理。
- 上限：单条 6 张、单张 10 MB、转发 30 条／8000 字。
- `parse_qq_event` 保持同步纯函数；转发展开与图片下载在 `media.materialize()` 中异步完成。

### 只读档媒体根（M1）

- `permissions.classify_tool_call()` 增加 `extra_read_roots` 参数；只读档的 `Read`／`Grep`／`Glob` 在 `work_dir` 或媒体根内放行，写工具与 `Bash` 仍拒绝。
- `sessions.py` 通过环境变量 `CC_QQ_MEDIA_ROOT` 把媒体根注入 hook；`hooks/readonly_hook.py` 读取后传入分类函数。
- 媒体根只包含插件自己下载的图片，`realpath` 严格校验。

### 图片输出

- 协议：回复文本中的 `[[image:<path>]]`。
- 路径必须经 `media.is_trusted_path()` 校验（工作目录或媒体根内）；否则剔除该图片并记录日志。
- `replies.send_reply()` 按原顺序构造 `MessageChain([Plain, Image, ...])`；文本段继续按 1500 字分段。

### 长文本渲染

- 判定：`len(text) >= 360`（可配置）或含围栏代码块；且本会话 `/img` 开关为开。
- 渲染：复用 AstrBot `HtmlRenderer.render_t2i(..., use_network=False)` 的本地 Pillow 实现；在线程中执行，避免阻塞事件循环。
- 输出：只发长图，不再发全文；高度超过 4000px 时垂直切分。
- 回退：渲染或发送失败 → 退回文本分段。
- 开关：`/img on|off`（owner／管理员），按会话存储在 `conversation_flags` 表；全局配置提供默认值与阈值。



- AstrBot 事件、回复与插件数据目录的具体调用方式参考 `integrations/astrbot/astrbot_plugin_sourcehub_inspector/` 和 `integrations/astrbot/astrbot_plugin_sourcehub_bilibili/`。
- `cc-ding/src/biz/cc-ding-cli.ts` 提供消息路由行为参考；`session.ts` 提供会话命令语义；`claude-process.ts`、`codex-agent.ts` 提供 CLI 参数与原生事件参考；`commands.ts` 提供命令名和帮助文案参考。
- 不直接复制 `DingClaude`、DingTalk SDK、钉钉身份解析或原 Console 服务。需要引用上游代码片段时保留 MIT 许可和原版权信息。

## 风险与权衡

- 普通模式与源项目一致，代理进程可访问宿主机上运行账号可访问的资源。QQ 白名单只控制调用入口；README 与管理配置必须明确提示实际执行权限。
- 代理 CLI 的流事件结构或恢复参数可能随版本变化。适配器单独处理原生事件；本机版本不符合预期时停止该代理并记录具体差异，不在业务层猜测输出。
- AstrBot 事件与发送接口依实际安装版本校验；接口不一致先更新 `qq_events.py`／`replies.py` 及设计，不扩大 `main.py` 职责。
- 阶段 1 只实现文本闭环和基础命令；媒体、完整业务命令、`/qa` 只读、管理页面与 A2A 的原因和触发条件见 `proposal.md` 与总体计划，后续必须继续。
