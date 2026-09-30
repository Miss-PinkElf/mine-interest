# cc-qq 原生 Python 插件第一阶段任务（Tasks）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:33:00 +08:00
- 更新时间（Updated At）：2026-09-29 17:00:00 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：按计划跟踪第一阶段可独立核验的实施任务。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 总体计划（Master Plan）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-ding原生python完整迁移qq插件-总体实施计划.md`
- 阶段计划（Stage Plan）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-qq原生python插件第一阶段实施计划.md`
- 群聊对齐（Group Admission Alignment）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-qq群聊白名单与必须@对齐.md`
- 当前状态（Status）：代码已接通、待真实 QQ 验收（Implementation Complete / Runtime Verification Pending）
- 文档边界（Scope / Boundary）：当前阶段任务真相源（source of truth）；只跟踪总体计划 T00–T04，阶段 2–4 仍按总体计划继续。

以下勾选只表示源码实施及静态审查已完成；第一阶段通过仍以真实 QQ、AstrBot 加载和双代理运行证据为准。

## T00 功能映射基线（已完成 / Completed）

- [x] T00.1 逐项登记 `cc-ding/src/biz/commands.ts` 的注册命令和其他 `parse*Command`、`types.ts` 字段、`console.ts` 路由、`bin/cc-ding.ts` 子命令、`a2a/` 操作与消息形态，写入 `spec/feature-mapping.md`。
- [x] T00.2 每项记录原行为、目标 QQ／AstrBot 行为、目标阶段、验收动作和状态；钉钉／PM2 专属能力写明等价操作，不静默删项。
- [x] T00.3 标记普通权限默认值和 `/qa` 修正，确认阶段 1 只验收 QQ／双代理文本闭环。

## T01 插件骨架与配置（待运行验收 / Runtime Verification Pending）

- [x] T01.1 在 `integrations/astrbot/astrbot_plugin_cc_qq/` 建立 `main.py`、`metadata.yaml`、`_conf_schema.json`、`constants.py`、`contracts.py` 和 README；版本常量与插件元信息一致。
- [x] T01.2 配置平台 ID、启用群／私聊、owner、管理员、白名单、工作目录、代理与模型；空配置不接收任何会话。
- [x] T01.3 用 `StarTools.get_data_dir()` 和 `sqlite3` 建立插件专属数据区；定义复合会话键及统一输入、授权、代理事件结构。
- [x] T01.4 本机 AstrBot 已于 16:23 安装并加载 `0.1.12`；后续仓库源码已升至 `0.1.13`，需由用户上传新 ZIP。README 明示阶段 1 能力和普通模式权限。

## T02 QQ 事件、准入与回复

- [x] T02.1 `platform/qq_events.py` 解析 QQ 群／私聊、平台实例、QQ 用户和消息 ID；同号群／私聊及多平台实例不串会话。
- [x] T02.2 `policy.py` 按已配置范围、owner、管理员和白名单判断消息与命令准入；拒绝时不启动 CLI。
- [x] T02.3 `platform/replies.py` 发送分段文本最终回复与错误；失败状态可追踪，聊天与日志不泄露凭据。即时确认提示属第二阶段消息体验。
- [x] T02.4 非文本输入给出明确暂不支持提示，指向阶段 2 媒体能力，不静默吞消息。
- [x] T02.5 群号白名单沿用 `enabled_group_ids`；群聊普通文本和命令须精确 @ 当前机器人，未 @、@ 他人或机器人 QQ ID 无法确定时静默且不产生副作用；私聊不要求 @。机器人 @ 段不传给命令或代理。

## T03 Claude Code 与 Codex 进程

- [x] T03.1 `agents/process.py` 用参数数组启动异步子进程，支持输出逐行读取、中断、超时和退出清理。
- [x] T03.2 `agents/claude.py` 解析 Claude `stream-json`、保存会话 ID 并用 `--resume` 继续；普通模式使用 `bypassPermissions`。
- [x] T03.3 `agents/codex.py` 解析 Codex JSON Lines、保存线程 ID 并用 `exec resume` 继续；普通模式使用 `danger-full-access`。
- [x] T03.4 两种适配器输出同一 `AgentEvent`，进程失败时得到明确错误且不残留运行中状态。

## T03-M 双代理独立默认模型（代码已接通 / Runtime Verification Pending）

- [x] T03-M.1 AstrBot 配置表单提供 `default_claude_model` 和 `default_codex_model`，移除旧共享 `default_model`；空值不指定 CLI 模型。
- [x] T03-M.2 群规则 `model` 优先，其次按所选代理读取相应默认模型；私聊按 `default_agent` 读取。
- [x] T03-M.3 持久化会话代理与当前规则不一致时，运行该会话仅使用其自身代理默认模型，不串用另一代理模型。
- [x] T03-M.4a 版本提升至 `0.1.13`，更新说明并生成可手动上传的 ZIP。
- [ ] T03-M.4b 用户安装 `0.1.14` 后，在真实 QQ 中分别验证两代理独立默认模型、群规则覆盖和空值行为。

## T04 会话和基础命令

- [x] T04.1 `sessions.py` 与 `storage.py` 保存会话、历史、队列和去重状态；同会话串行，不同会话独立。
- [x] T04.2 `commands/registry.py` 和 `commands/session.py` 实现 `/help`、`/info`、`/new`、`/resume`、`/end`、`/goon`、`/cc`、`/!`。第一阶段这些基础命令对获准用户一致可用；管理员专属命令与按角色展示进入第二阶段。
- [x] T04.3 `service.py` 按“准入 → 去重 → 命令 → 会话 → 代理 → 回复”连接模块；普通自然语言由代理处理，不增加硬编码意图分类。
- [ ] T04.4 旧版 `0.1.12` 已有 Codex 群／私聊真实回复；仍需验证 Claude Code、两代理多轮、重载恢复、中断、结束和继续，结果回填 `spec/feature-mapping.md`。
- [ ] T04.5 群号白名单、群成员白名单、群聊 @ 与私聊无 @ 的组合行为取得运行证据；未 @ 群消息不发送提示，也不启动 CLI。
- [x] T04.6 私聊空文本静默且不进代理；群聊 @ 后空文本仍回复原提示。
- [x] T04.7 插件设置 `stale_message_max_age_seconds` 默认 180。OneBot 原始 `time` 早于收到时刻超过该值时停止事件，不回复、不写回执。填 0 关闭这条过滤。`queued` 重放不使用这条规则。非法值回落到 180。代码与单元测试已完成。用户声明已重载，真实 QQ 留到下一对话验收，本轮未读重载后日志。
- [x] T04.8 标准输入 `ConnectionResetError` / `BrokenPipeError` / `ConnectionAbortedError` 变成带退出码的代理错误，日志保留截断后的 stderr 尾部。单元测试覆盖重置路径，真实代理早退仍待运行验收。
- [x] T04.9 版本与元数据升至 `0.1.14`，生成根层含 `metadata.yaml` 的上传 ZIP。用户要求后已覆盖安装目录，并声明已经重载。真实 QQ 验收留到下一对话。
- [x] T04.10 私聊未在 `private_user_ids` 且不是 owner／管理员时按范围外静默，不回复未授权文案。群聊 @ 后未授权仍提示。代码与单元测试已完成。
- [x] T04.11 私聊同一发送者同一正文（含空文本）在 10 秒内只处理一次；相同回复不连发。私聊范围外会停止事件。代码与单元测试已完成。

## 每次插件代码变更的固定门禁

- [x] 同步提升 `metadata.yaml` 与 Python 版本常量至 `0.1.16`。覆盖安装目录后需用户重载才生效。
- [x] 补丁编辑仓库文本；复制动作的差异以 `git status --short` 与相关相对路径的 `git diff` 展示，并在回复中说明内联差异限制。
- [x] 2026-09-30 收尾时用户明确要求先提交再写交接。代码提交为 `7a714ac`，未推送。

## 阶段验证与下一步

- [ ] 核对 T00–T04 的实际结果、插件加载和 QQ 群／私聊双代理运行证据；做聚焦审查并更新 `state.md`、`checkpoints.md`。
- [ ] 第一阶段通过后，依总体计划进入阶段 2 的详细计划和开放规格；阶段 2–4 的对象、原因和触发条件见 `proposal.md` 的“本阶段不做 / 后续阶段”。
