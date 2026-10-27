# cc-qq 轻量后续想法（Backlog）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-30 15:38:00 +08:00
- 更新时间（Updated At）：2026-10-28 01:20:00 +08:00
- 作者（Author）：Grok
- 目的（Purpose）：用一句话记下还没展开的后续想法，方便交接引用。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：未展开（Not Started）
- 文档边界（Scope / Boundary）：轻量索引，不是已批准计划（Plan），也不会单独触发实现。明确延期见 `deferred/`。

- 私聊短时间多条消息聚合成一条，上下文过长再截断或交给代理压缩；窗口和阈值都还没讨论，见 `deferred/第一版边界与未讨论项.md`。
- 机器人号 `1961618848` 尽量只留给 NapCat，减少空白事件；这是操作建议，不是代码任务。
- 为权限审计增加 QQ 查询命令（如 `/audit 20`），方便管理员查看最近审批与拒绝。
- 把 `/qa` 作为显式只读命令复用到 `readonly` 档，而不是再写一套权限。
- 评估用 Codex 权限档案替代传统 `sandbox_mode` 后的跨平台兼容性（Linux／Windows）。
- 评估把审批卡片可靠发到管理员私聊：持久化管理员来源，而不是内存记录。
- 群在 `enabled_group_ids` 但缺 `group_rules_json` 条目时，把「插件配置无效」改成「该群未配置 work_dir」的准确提示。
- 确认 codex-cli 0.162.1 关闭原生 web search 的配置键，并在 `codex_args` 统一追加。
- 评估只读档 MCP 是否需要进一步细分（搜索开、服务端抓取关），当前是一个总开关。
- 群内 @bot 管理私聊白名单（候选）：先补齐 4 个待确认问题，见 `deferred/第一版边界与未讨论项.md`。
- 需求 4.2：代码 diff 转 HTML 上传 GitHub Pages 或用语雀 MCP 展示长文本（QQ 不渲染 Markdown），见 `deferred/第一版边界与未讨论项.md`。
- 需求 5：确认群内 guest 与白名单成员是否应该共享对话上下文，当前按会话共享。
- 未来需求：长时间不对话时提示上下文长度并推荐 `/new`。
- 流式输出（Streaming）：`_execute` 攒齐后一次性返回，长任务只有开头一条回执。详见 `2026-10-28-排查耗时分析与优化方案.md` 第八节；触发条件已满足，建议排期。
- 把「排查任务并行化」写成可复用行为规范：同一批独立查询必须并发、专用工具优先于 Bash、宽泛扫荡交给子代理。详见 `2026-10-28-排查耗时分析与优化方案.md` 第七节。
- 需求 7（用户在 `prompt-01.md` 新增，本次对话未讨论）：通过 ACP 或对话数据共享实现并行。
- e2e 用例收尾自动回滚 NapCat 的 `onebot11` 配置，否则 `6198` 重连日志会复发（对应 `astrbot-plugin-e2e` 的 `backlog.md` Q2）。
- `permissions.py:141` 的关键路径正则对 `/System`、`/Library` 一律 deny，连只读的 `ls` 也拦；上一轮画图任务因此反复重试。评估收紧到写操作。
