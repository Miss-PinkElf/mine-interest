# QQ 多代理 AstrBot 接入检查点归档（Checkpoints Archive）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 22:34:37 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：保存已退出恢复热路径的历史阶段检查点。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：历史归档（Archived History）
- 文档边界（Scope / Boundary）：历史检查点真相源（source of truth）；日常恢复优先读取 `checkpoints.md`。

## 2026-09-28 21:43:08 +08:00｜进入需求对齐（Align）

- 已读取原始需求、本地 `cc-ding/` 参考项目及现有 AstrBot 插件结构。
- 已初始化重型路径（Heavy Route）mission 工作区。
- 初步发现：`cc-ding` 的白名单是访问门禁，当前 Codex 适配使用完全访问沙箱，无法直接满足“白名单外可聊且工作目录只读”。
- 下一步：确认只读的实际权限边界，再比较实现架构。

## 2026-09-28 22:09:11 +08:00｜确认迁移方向与本轮范围

- 迁移 `cc-ding` 通用核心，由 AstrBot 插件承接平台适配；本轮只支持 Claude Code、Codex。
- 每个 QQ 群固定工作目录并共享会话；白名单用户在目录内可读写，其他用户只读；群级和私聊权限另行对齐。
- OpenCode、Pi 延期到本轮迁移与权限验收后，已记入 `decision-log.md` 与 `state.md`。
- 下一步：确认权限叠加规则和功能迁移清单，然后完成对齐设计。
## 2026-09-28 22:25:40 +08:00｜对齐完成并落盘计划（Plan）

- 用户确认完整迁移包含 Web Console、代理间通信（A2A），权限为白名单与群级策略交集，群共享会话且每次执行重算权限。
- 对齐文档与强相关计划均已落入 `plans/`；用户明确要求写完对齐后直接写计划。
- 计划将隔离可行性放在最先验收门禁，后续才抽取核心、接入 AstrBot、迁移功能与真实 QQ 验收。
- 尚未创建开放规格（OpenSpec）三件套，尚未修改插件代码；下一步为规格与任务阶段。

## 2026-09-28 22:34:37 +08:00｜开放规格（OpenSpec）草稿已写，未批准实施

- `spec/proposal.md`、`spec/design.md`、`spec/tasks.md` 已写为草稿，任务从 T01 到 T17。
- 用户明确要求的是对齐（Align）后直接写计划（Plan），并未批准进入实施（Apply）；先前的实施中标记已撤回，插件代码未改。
- 等待用户审阅计划与规格草稿。未来进入实施后，T02 仍是代码迁移门禁：若真实目录隔离不成立，回退设计。

## 2026-09-28 23:45:44 +08:00｜用户授权进入实施（Apply）

- 用户改变“下次对话再实施”的安排，明确要求本轮直接实施；计划与开放规格（OpenSpec）三件套已核对齐备。
- T01 逐项功能映射开始；随后 T02 真实隔离验证。T02 不通过时停止代码迁移并回退设计。
- 本次阶段切换时尚未修改插件代码或执行提交（Commit）。
