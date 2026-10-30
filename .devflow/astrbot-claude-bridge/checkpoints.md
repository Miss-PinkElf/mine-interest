# QQ 多代理 AstrBot 接入检查点（Checkpoints）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 21:43:08 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录关键阶段切换，支持后续恢复。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：交接暂停，待设计选型（Awaiting Decision）
- 文档边界（Scope / Boundary）：最近三条阶段记录真相源（source of truth）；恢复时先读当前状态与本文件。

## 2026-09-29 00:10:27 +08:00｜T02 发现设计缺陷并回退提案（Propose）

- 用户授权测试 Codex elevated Windows 沙箱。内置 `:read-only` 读到目录外哨兵；`:root = deny` 在 elevated 启动前被拒绝，详情见 `spec/permission-matrix.md`。
- T01 清单完成；T02 未通过，T03 及后续插件代码迁移未开始，插件版本和本机副本未变化，也未提交。
- 下一步是修订 Windows／macOS 原生执行边界并重新验证 T02；不得降低“目录外拒读”需求来绕过门禁。

## 2026-09-29 00:20:00 +08:00｜本轮交接并暂停（Handoff）

- 用户要求新对话继续；本轮只收束文档并提交当前 mission，不宣称实施（Apply）完成。
- 交接入口为 `handoffs/2026-09-29-002-t02-design-revision.md` 与 `NEXT-SESSION-PROMPT-astrbot-claude-bridge.md`；T02 仍未通过，T03 尚未开始。
- 下次先恢复 `state.md` 和本文件，再核对权限矩阵、候选设计与未讨论项。

## 2026-10-30 14:40:00 +08:00｜完成官方 dsh-qqbot 对比调研并交接

- 完成腾讯官方 `@tencent-connect/dsh-qqbot` 0.5.4 源码级调研（克隆 `tmp/refs/dsh-qqbot`，已 gitignore），产出 `spec/2026-10-30-腾讯dsh-qqbot对比调研.md`（候选项，非批准方案、不触发实施）。
- 核心结论：官方实现无只读档、无工具级白名单、无进程级目录外拒读；靠「白名单准入 + 独立 workspace + 审批卡片」兜底，**不能为 T02 提供技术方案**，只提供需求取舍先例。
- T02 现有三个候选项 A（需求降级为"非白名单不服务"）/ B（维持需求、缩小可开放面）/ C（引入外部隔离），**均未获批准**；未选型前不进入 T03。
- 本轮未修改插件代码、未升版本、未覆盖本机插件；未提交 `.devflow/astrbot-plugin-e2e/` 与 `zzz-prompt-debug/` 的既有改动（与本次对话无关）。
