# cc-qq 原生 Python 插件第一阶段任务（Tasks）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:33:00 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：按计划跟踪第一阶段可独立核验的实施任务。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 总体计划（Master Plan）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-ding原生python完整迁移qq插件-总体实施计划.md`
- 阶段计划（Stage Plan）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-qq原生python插件第一阶段实施计划.md`
- 当前状态（Status）：待实施（Planned）
- 文档边界（Scope / Boundary）：当前阶段任务真相源（source of truth）；只跟踪总体计划 T00–T04，阶段 2–4 仍按总体计划继续。

## T00 功能映射基线（已完成 / Completed）

- [x] T00.1 逐项登记 `cc-ding/src/biz/commands.ts` 的注册命令和其他 `parse*Command`、`types.ts` 字段、`console.ts` 路由、`bin/cc-ding.ts` 子命令、`a2a/` 操作与消息形态，写入 `spec/feature-mapping.md`。
- [x] T00.2 每项记录原行为、目标 QQ／AstrBot 行为、目标阶段、验收动作和状态；钉钉／PM2 专属能力写明等价操作，不静默删项。
- [x] T00.3 标记普通权限默认值和 `/qa` 修正，确认阶段 1 只验收 QQ／双代理文本闭环。

## T01 插件骨架与配置（进行中 / In Progress）

- [ ] T01.1 在 `integrations/astrbot/astrbot_plugin_cc_qq/` 建立 `main.py`、`metadata.yaml`、`_conf_schema.json`、`constants.py`、`contracts.py` 和 README；版本常量与插件元信息一致。
- [ ] T01.2 配置平台 ID、启用群／私聊、owner、管理员、白名单、工作目录、代理与模型；空配置不接收任何会话。
- [ ] T01.3 用 `StarTools.get_data_dir()` 和 `sqlite3` 建立插件专属数据区；定义复合会话键及统一输入、授权、代理事件结构。
- [ ] T01.4 本机 AstrBot 识别并加载插件，插件副本的版本和仓库一致；README 明示阶段 1 能力和普通模式权限。

## T02 QQ 事件、准入与回复

- [ ] T02.1 `platform/qq_events.py` 解析 QQ 群／私聊、平台实例、QQ 用户和消息 ID；同号群／私聊及多平台实例不串会话。
- [ ] T02.2 `policy.py` 按已配置范围、owner、管理员和白名单判断消息与命令准入；拒绝时不启动 CLI。
- [ ] T02.3 `platform/replies.py` 发送分段文本、确认与错误；失败状态可追踪，聊天与日志不泄露凭据。
- [ ] T02.4 非文本输入给出明确暂不支持提示，指向阶段 2 媒体能力，不静默吞消息。

## T03 Claude Code 与 Codex 进程

- [ ] T03.1 `agents/process.py` 用参数数组启动异步子进程，支持输出逐行读取、中断、超时和退出清理。
- [ ] T03.2 `agents/claude.py` 解析 Claude `stream-json`、保存会话 ID 并用 `--resume` 继续；普通模式使用 `bypassPermissions`。
- [ ] T03.3 `agents/codex.py` 解析 Codex JSON Lines、保存线程 ID 并用 `exec resume` 继续；普通模式使用 `danger-full-access`。
- [ ] T03.4 两种适配器输出同一 `AgentEvent`，进程失败时得到明确错误且不残留运行中状态。

## T04 会话和基础命令

- [ ] T04.1 `sessions.py` 与 `storage.py` 保存会话、历史、队列和去重状态；同会话串行，不同会话独立。
- [ ] T04.2 `commands/registry.py` 和 `commands/session.py` 实现 `/help`、`/info`、`/new`、`/resume`、`/end`、`/goon`、`/cc`、`/!`，并按角色控制可见与可用命令。
- [ ] T04.3 `service.py` 按“准入 → 去重 → 命令 → 会话 → 代理 → 回复”连接模块；普通自然语言由代理处理，不增加硬编码意图分类。
- [ ] T04.4 插件重载后两种代理会话可恢复；真实 QQ 群／私聊完成新建、多轮、中断、结束和继续，结果回填 `spec/feature-mapping.md`。

## 每次插件代码变更的固定门禁

- [ ] 同步提升 `metadata.yaml` 与 Python 版本常量，覆盖 AstrBot 对应插件目录，核对两个副本版本一致。
- [ ] 补丁编辑仓库文本；如复制或生成动作不能显示 Codex CLI 内联差异，展示 `git status --short` 与相关相对路径的 `git diff`，并在回复中说明限制。
- [ ] 完成代码修改后询问用户是否需要提交；未经明确允许不提交。

## 阶段验证与下一步

- [ ] 核对 T00–T04 的实际结果、插件加载和 QQ 群／私聊双代理运行证据；做聚焦审查并更新 `state.md`、`checkpoints.md`。
- [ ] 第一阶段通过后，依总体计划进入阶段 2 的详细计划和开放规格；阶段 2–4 的对象、原因和触发条件见 `proposal.md` 的“本阶段不做 / 后续阶段”。
