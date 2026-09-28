# QQ 多代理 AstrBot 接入检查点（Checkpoints）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 21:43:08 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录关键阶段切换，支持后续恢复。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：设计回退中（Propose Revision）
- 文档边界（Scope / Boundary）：最近三条阶段记录真相源（source of truth）；恢复时先读当前状态与本文件。

## 2026-09-28 23:58:41 +08:00｜平台目标修正并重定 T02

- 用户明确 Windows／macOS 原生运行，不以 WSL／Ubuntu 为插件依赖；先前 WSL 实验不算产品验收。
- T01 功能清单落盘；T02 改为 Claude Code／Codex × 平台 × 工具组合的权限验证。未经验证的 Shell、MCP、Hooks 等组合默认禁用。
- 仍未修改插件代码或提交；macOS 缺少实机时标记待验证，不得假称通过。

## 2026-09-29 00:10:27 +08:00｜T02 发现设计缺陷并回退提案（Propose）

- 用户授权测试 Codex elevated Windows 沙箱。内置 `:read-only` 读到目录外哨兵；`:root = deny` 在 elevated 启动前被拒绝，详情见 `spec/permission-matrix.md`。
- T01 清单完成；T02 未通过，T03 及后续插件代码迁移未开始，插件版本和本机副本未变化，也未提交。
- 下一步是修订 Windows／macOS 原生执行边界并重新验证 T02；不得降低“目录外拒读”需求来绕过门禁。

## 2026-09-29 00:20:00 +08:00｜本轮交接并暂停（Handoff）

- 用户要求新对话继续；本轮只收束文档并提交当前 mission，不宣称实施（Apply）完成。
- 交接入口为 `handoffs/2026-09-29-002-t02-design-revision.md` 与 `NEXT-SESSION-PROMPT-astrbot-claude-bridge.md`；T02 仍未通过，T03 尚未开始。
- 下次先恢复 `state.md` 和本文件，再核对权限矩阵、候选设计与未讨论项。
