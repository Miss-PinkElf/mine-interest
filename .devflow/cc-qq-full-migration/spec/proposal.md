# cc-qq 原生 Python 插件第一阶段提案（Proposal）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:33:00 +08:00
- 更新时间（Updated At）：2026-09-29 16:55:23 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：定义本次子变更的动机、边界和完成条件。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 已确认对齐（Aligned Design）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-ding原生python迁移qq插件-需求对齐.md`
- 群聊对齐（Group Admission Alignment）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-qq群聊白名单与必须@对齐.md`
- 总体计划（Master Plan）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-ding原生python完整迁移qq插件-总体实施计划.md`
- 阶段计划（Stage Plan）：`.devflow/cc-qq-full-migration/plans/2026-09-29-cc-qq原生python插件第一阶段实施计划.md`
- 当前状态（Status）：代码已实施、待运行验收（Implemented / Runtime Verification Pending）
- 文档边界（Scope / Boundary）：本 mission 当前第一阶段子变更的正式提案真相源（source of truth）；用户已授权完整迁移，但本文件不表示后续阶段已完成。

## 背景

`cc-ding/` 通过钉钉消息入口、身份规则和回复接口把本机 Claude Code／Codex CLI 接入聊天。用户希望借鉴这条链路，用原生 Python AstrBot 插件在 QQ 中逐步做出完整能力；源项目的钉钉入口类与业务高度耦合，不适合直接嵌入新插件。本阶段先建立 QQ、身份、双代理和会话的可运行闭环，为后续任务、媒体、Web Console 和 A2A 提供稳定接口。

## 目标

- 在 `integrations/astrbot/astrbot_plugin_cc_qq/` 建立可追踪、可被 AstrBot 管理的原生 Python 插件。
- 已配置的 QQ 群聊和私聊可调用 Claude Code 与 Codex，完成文本多轮、会话恢复、结束、中断和基础命令。
- owner、管理员和白名单按 QQ 稳定 ID 管理；未配置平台／群及未授权用户不能启动代理。
- 群号白名单沿用 `enabled_group_ids`；白名单内群的普通文本和命令仅在 @ 当前机器人后触发。未 @ 或 @ 目标不符时静默；私聊不要求 @。
- 原普通会话权限默认值与源代码一致：Claude Code `bypassPermissions`，Codex `danger-full-access`；在配置和文档中明确展示。
- Claude Code 与 Codex 分别配置默认模型；群规则模型保持优先，旧共享模型字段停用，空值使用各自 CLI 默认模型。
- 建立覆盖 `cc-ding` 命令、配置、管理、CLI、消息与 A2A 的逐项功能清单，作为完整 mission 的验收追踪表。

## 范围

- AstrBot 事件接入、平台／会话／用户身份归一、文本回复。
- 机器人 QQ ID 与 @ 目标的结构化解析、群聊提及门禁及机器人 @ 段清理。
- 插件配置、数据目录、会话持久化、消息去重与同会话串行队列。
- 双代理独立默认模型字段及按实际会话代理类型选择模型；增量计划见 `plans/2026-09-29-cc-qq双代理独立默认模型实施计划.md`。
- 两种 CLI 的异步进程、事件解析、代理会话 ID、恢复、中断、错误与退出处理。
- `/help`、`/info`、`/new`、`/resume`、`/end`、`/goon`、`/cc`、`/!` 的首阶段可用行为。
- 插件版本提升、本机 AstrBot 副本覆盖和阶段结果记录。

## 本阶段不做 / 后续阶段（Deferred Scope）

| 对象或能力 | 本阶段原因 | 后续触发条件 |
| --- | --- | --- |
| 任务、调度、待办、菜单、密钥、媒体、录制和其余命令 | 先稳定 QQ 与双代理会话契约。 | 第一阶段双代理多轮和恢复验收通过后进入总体计划阶段 2。 |
| `/qa` 可验证只读、自由模式与完整管理命令 | 依赖阶段 1 的代理运行和权限入口。 | 阶段 1 完成后进入阶段 2；普通模式仍保持源默认权限。 |
| Web Console、跨实例管理和 A2A | 依赖稳定的身份、数据和业务接口。 | 阶段 2 接口稳定后进入总体计划阶段 3。 |
| 全量逐项收口与最终部署验收 | 需要前三阶段产物。 | 阶段 3 验收完成后进入阶段 4；本阶段不得宣称完整迁移。 |

以上均为本 mission 必做后续阶段，不代表永久放弃。

## 边界场景

- QQ 群与私聊使用相同数字 ID，或两个 QQ 平台实例使用相同群号时，必须形成不同会话。
- 重复消息 ID、插件重载后的旧消息或同群并发请求不得重复启动代理。
- `/resume` 只能访问当前会话范围的历史；结束或取消后不会继续发送旧进程结果。
- CLI 未安装、认证失败、超时、退出异常和 QQ 发送失败时，返回明确状态并保留可恢复信息；密钥不得出现在 QQ 回复中。
- 文本以外的消息段在阶段 2 接入；阶段 1 收到不支持内容时给出可理解的提示，不静默忽略。
- 群聊消息先经过群号白名单和 @ 门禁；未 @ 当前机器人、@ 他人或无法可靠识别目标时静默，且不得启动代理或执行命令。命中门禁后，非文本段才得到上述暂不支持提示。

## 开放问题

当前没有阻止第一阶段进入实施的产品问题。AstrBot 事件字段、两种 CLI 的实际流事件与本机插件加载路径在实施时按本机版本核验；若与设计契约不符，先更新设计和任务再继续。
