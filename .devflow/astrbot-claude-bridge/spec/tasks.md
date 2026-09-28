# cc-ding 迁移 AstrBot 插件任务（Tasks）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 22:26:33 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：把已确认的对齐和计划拆为有顺序、可验证的实施任务。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 对齐文档（Aligned Requirement）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding迁移astrbot需求对齐.md`
- 实施计划（Implementation Plan）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`
- 提案与设计（Proposal / Design）：`.devflow/astrbot-claude-bridge/spec/proposal.md`、`.devflow/astrbot-claude-bridge/spec/design.md`
- 当前状态（Status）：设计回退中（Propose Revision）
- 文档边界（Scope / Boundary）：本 mission 的任务真相源（source of truth）；T02 的 Codex 严格拒读方案未通过，T03 及后续代码任务暂停。

## 执行规则

- 依赖顺序按任务编号推进；T02 的安全工具组合未通过时停止对应能力并回退设计，只有已验证组合可进入代码迁移。
- 每完成一个任务，记录验证命令、结果与差异；失败时先查根因，再修复。
- 每次修改插件代码需提升可感知版本并覆盖本机 AstrBot 对应插件目录；所有 Git Commit 必须事先征得用户明确允许且使用中文提交信息。
- 原始 `cc-ding/` 只读；迁移文件写入可追踪的 `integrations/astrbot/astrbot_plugin_cc_bridge/`。

## 阶段 1：清单与隔离

### T01｜逐项功能映射（已完成清单，Mapped）

- [x] 枚举 `cc-ding/src/biz/commands.ts` 命令、`types.ts` 配置、Console、A2A、消息能力，创建 `spec/feature-mapping.md`；每项注明保留、AstrBot 等价映射或取消理由。
- [x] 核对迁移清单覆盖会话、任务、Cron、Timer、Todo、Menu、模型、密钥、图片文件、日志、看门狗、Console、A2A 和管理员能力。
- 验收：清单无未分类项；每项有目标模块和可执行验收动作。

### T02｜Windows／macOS 权限组合可行性（设计回退中，Design Revision）

- [ ] 在原生 Windows 本机验证 Claude Code、Codex 的启动、认证、会话恢复和候选权限配置；为 macOS 建立独立待验证矩阵，不以 Windows 结果替代。
- [ ] 按代理与工具组合分别验证目录内读取、目录外读取、只读写入、目录内写入、符号链接／联接目录逃逸、Shell、Skills、MCP、Hooks、恢复后权限降级。
- [ ] 形成可重复运行的验证脚本和结果记录；仅开放全部越权样本被拒绝的组合。原生 Windows Claude Code 的 Shell 等未验证工具默认禁用；失败组合回退设计，不因其他组合通过而开放。
- 验收：拟开放组合中非白名单只读、白名单目录内读写，两者均不能读取目录外用户文件；macOS 未实测时不宣称跨平台完成。
- 当前证据：`spec/permission-matrix.md`。Codex CLI 0.158.0 的 Windows 内置只读可读目录外文件；`:root = deny` 在普通后端要求 elevated，在 elevated 后端又被启动前校验拒绝。修订执行隔离方案并重新验证前，T03 不启动。

## 阶段 2：核心边界

### T03｜插件骨架与许可

- [ ] 建立 `integrations/astrbot/astrbot_plugin_cc_bridge/` 的 Python 插件、Node 包、插件配置、元信息、README 与 `LICENSE.cc-ding`。
- [ ] 明确版本、Node 依赖、代理 CLI、插件数据目录和隔离先决条件；源代码进入 Git 可追踪路径。
- 验收：AstrBot 可加载空骨架，Node 包能构建；许可可追溯，版本和本机插件副本一致。

### T04｜平台无关契约与进程通信

- [ ] 实现 `runner/src/contracts.ts`、`runner/src/transport/stdio.ts`、`bridge/events.py`、`bridge/process.py` 的请求、事件、错误、取消和握手协议。
- [ ] 使用伪造进程测试乱序响应、超时、子进程退出、重启和协议版本不匹配。
- 验收：插件与核心可往返一条文本消息；核心契约不含钉钉工号、Webhook 或 Token。

### T05｜会话、数据区与队列

- [ ] 从 `cc-ding/src/biz/session.ts`、`dedup.ts` 抽取群／私聊会话、持久化、去重、队列和中断；会话数据迁入插件专属数据区。
- [ ] 验证群共享、私聊按用户隔离、Claude／Codex 原生会话 ID 分离、进程重启后恢复及重复消息不重复执行。
- 验收：项目工作目录内不出现会话、密钥或审计文件；恢复与队列测试通过。

## 阶段 3：权限与代理

### T06｜统一权限决策

- [ ] 实现 `runner/src/policy/evaluate.ts` 与配置解析：用户读写上限、群级上限、私聊独立配置、工具允许集交集和失败关闭。
- [ ] 队列出队、定时任务、A2A、管理页代理操作全部调用同一权限决策；审计记录不包含密钥。
- 验收：白名单在只读群仍只读、非白名单在可写群仍只读、工具必须双方允许、权限变更后旧排队请求不会越权。

### T07｜隔离运行器

- [ ] 将 T02 验证通过的平台／代理权限配置封装为 `runner/src/runtime/isolation.ts`，输入规范化工作目录、本次只读／读写策略与工具允许集。
- [ ] 用真实进程再次运行目录外读取、只读写入、符号链接／联接目录和子进程逃逸测试。
- 验收：代理所有文件访问与其子进程都受边界限制；失败返回错误而不降级为完全访问。

### T08｜Claude Code 与 Codex 适配

- [ ] 迁移 Claude Code 流式、恢复、Skills、MCP、Hooks 与 Codex JSON 事件、线程恢复；两者只通过隔离运行器启动。
- [ ] 提供本次有效工具元数据，让代理在已允许工具中自行选择；保留模型选择、取消和超时反馈。
- 验收：两种真实 CLI 都能连续对话并恢复；同群权限升降交替时不会沿用旧进程权限。

## 阶段 4：AstrBot 与通用功能

### T09｜QQ 群聊和私聊接入

- [ ] 实现 `main.py`、`bridge/events.py`、`bridge/replies.py` 的群与私聊路由、身份映射、消息段输入和平台回复。
- [ ] 验证只响应已配置群／私聊，消息发送失败可记录与重试，不把内部路径或密钥发到群。
- 验收：真实 QQ 群和私聊能对 Claude Code、Codex 完成一轮及多轮对话。

### T10｜命令与会话管理

- [ ] 按 T01 清单迁移会话、帮助、信息、日志、授权、模型、目录、消息队列和中断命令；用命令注册表管理权限与帮助文案。
- [ ] 验证普通用户不能执行管理命令，旧钉钉参数收到明确替代说明。
- 验收：逐命令清单中所有仍有意义的命令通过群／私聊测试。

### T11｜任务、调度与协作

- [ ] 迁移任务队列、Cron、Timer、Todo、Menu、模型与密钥轮换、看门狗和错误恢复。
- [ ] 后台任务保存创建者身份并在实际执行时重验权限；配置变化或账号移出白名单后不得继续写入。
- 验收：任务、提醒、待办和菜单均有真实或可控制时间的验证；重试不重复副作用。

### T12｜图片、文件与回复体验

- [ ] 迁移图片、文件、引用、提及与结果进度反馈；以 AstrBot 消息能力决定具体格式。
- [ ] 为平台不支持的消息段提供文本降级与日志，避免静默丢失。
- 验收：QQ 文本、图片、文件、引用和提及样本可验证，无法支持的样本有明确反馈。

## 阶段 5：管理与 A2A

### T13｜AstrBot 插件管理页面

- [ ] 在 `pages/console/` 与 `bridge/web.py` 迁移原 Console 的状态、群／私聊配置、会话、模型、密钥、任务和日志管理。
- [ ] 验证后台鉴权、管理员角色、密钥脱敏和配置写入后权限重算。
- 验收：T01 管理功能逐项通过，非管理员不能修改配置或读取密钥。

### T14｜代理间通信（A2A）

- [ ] 迁移 A2A Hub、注册、任务路由、状态查询与结果回传，目标群必须显式指定。
- [ ] 验证无身份、错误目标群、权限高于来源、跨群工作目录访问和重试重复任务均被拒绝或去重。
- 验收：合法 A2A 任务成功，非白名单或只读来源无法经 A2A 写入目标群。

## 阶段 6：发布与收尾

### T15｜回归、版本与本机覆盖

- [ ] 运行 Python 适配、Node 核心、隔离、真实 CLI、插件加载和逐功能回归；不处理无关全局 ESLint 或 TypeScript 问题。
- [ ] 提升插件元信息和内部版本，整份覆盖到本机 AstrBot 插件目录并重载；验证运行版本与仓库一致。
- 验收：测试和构建有新鲜通过记录，AstrBot 日志确认加载正确版本。

### T16｜真实 QQ 验收与文档

- [ ] 用白名单／非白名单成员及私聊对 Claude Code、Codex、任务、图片文件、权限升降、Console 和 A2A 做端到端验证。
- [ ] 更新 README、配置示例、功能映射表、权限操作说明和 devflow 状态、检查点；记录任何真实平台差异。
- 验收：对齐文档六项成功标准逐项有证据，缺口不能标记完成。

### T17｜审查与完成门禁

- [ ] 按任务和最近差异做聚焦代码审查（Code Review），逐条核验反馈并修复必要问题。
- [ ] 用新鲜验证结果确认源码、本机插件副本和真实行为一致，再关闭本轮变更。
- [ ] 代码修改完成后询问用户是否提交；未经明确允许不执行 Git Commit。
- 验收：审查、验证与版本同步均通过，用户能根据文档恢复与维护插件。

## 本轮不做 / 后续阶段（Deferred Scope）

| 对象或能力 | 本轮暂不做的原因 | 后续触发条件或推荐阶段 |
| --- | --- | --- |
| OpenCode、Pi 及其他代理适配 | 本轮先完成 Claude Code、Codex 与平台权限迁移。 | T16 真实 QQ 与权限验收通过后，进入多代理扩展阶段。 |
