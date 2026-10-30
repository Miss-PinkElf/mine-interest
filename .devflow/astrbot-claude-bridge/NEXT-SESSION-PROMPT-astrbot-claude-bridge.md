# 下次对话提示词：cc-ding 迁移 AstrBot 插件

## Metadata（元数据）

- 更新时间（Updated At）：2026-10-30 14:40:00 +08:00
- 作者（Author）：Claude
- 目的（Purpose）：供下一次对话直接复制，恢复 T02 设计选型工作。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 实施计划（Implementation Plan）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`（待修订）
- 最新交接（Latest Handoff）：`.devflow/astrbot-claude-bridge/handoffs/2026-10-30-003-dsh-qqbot-research.md`
- 调研产出（Research Output）：`.devflow/astrbot-claude-bridge/spec/2026-10-30-腾讯dsh-qqbot对比调研.md`（候选项）
- 当前状态（Status）：待设计选型（Awaiting Decision）
- 文档边界（Scope / Boundary）：恢复提示词，不替代当前仓库事实、`state.md`、计划或开放规格（OpenSpec）；不代表实施完成。

## 可直接复制到新对话的提示词

请继续 `mine-interest` 仓库的 `.devflow/astrbot-claude-bridge/` mission，使用 devflow 重型路径（Heavy Route）。先读 `.devflow/astrbot-claude-bridge/state.md` 与 `checkpoints.md`，再读 `handoffs/index.md` 和最新 `handoffs/2026-10-30-003-dsh-qqbot-research.md`，以及 `spec/2026-10-30-腾讯dsh-qqbot对比调研.md`。按需读 `spec/design.md`、`spec/permission-matrix.md`、`backlog.md`、`bug-log.md`、计划和开放规格（OpenSpec）。先核对 Git 状态和实际文件。

当前进度：T01 `spec/feature-mapping.md` 已完成；T02 原生 Windows 权限验证未通过（Codex `:read-only` 能读目录外文件，`:root = deny` 在普通与 elevated 沙箱均无法启动），已从实施（Apply）回退提案修订（Propose）。2026-10-30 完成腾讯官方 `@tencent-connect/dsh-qqbot` 0.5.4 的源码级对比调研，结论是：官方实现没有只读档、没有工具级白名单、没有进程级目录外拒读，靠「白名单准入 + 独立 workspace + 审批卡片」兜底，**不能为 T02 提供技术方案，只能提供需求取舍先例**。本轮未修改任何插件代码，未升版本，未覆盖本机 AstrBot 插件目录。

任务目标：复用并模块化迁移 `cc-ding` 通用核心，由 AstrBot 插件替换钉钉平台适配。本轮支持 Claude Code、Codex；QQ 群每群一个固定工作目录并共享会话，私聊独立；所有用户均不能读取工作目录外文件，白名单用户最多在目录内读写，非白名单只读；群级与用户级文件／工具权限取交集。完整迁移目标仍包括 Web Console 和代理间通信（A2A）。最终插件原生运行于 Windows／macOS，不要求 WSL／Ubuntu。

**立即下一步（阻塞项）**：与用户确认 T02 走哪条路——A（需求降级：非白名单用户不服务，"只读"降为可选体验档，参照官方做法）还是 B（维持需求、缩小可开放面：Windows 不开放 Codex，Claude Code 只开已实测的基础文件工具）。C（容器／沙箱进程／WSL）与原生运行要求冲突，仅作对照。**选型未确认前，不得修改设计、计划或代码。**

未讨论事项（均不是已批准延期，见 `backlog.md`）：首版（First Version）交付边界；调研中 8 项可借鉴设计（流式双轨、审批 nonce、被动回复兜底、交付物投递、扫码绑定即授权、空闲会话回收、命令 per-scope 可见性、节流而非防抖）如何分级；图片理解与视觉能力是否要做；`cc-qq` 三条跨 mission 缺口是否登记（群级与用户级未取交集、`allowed_work_dirs` 不约束群规则初始 `work_dir`、Codex 无逐次审批）；macOS 仍无实机证据。

明确延期项仍只有 OpenCode、Pi，见 `deferred/agent-expansion.md`；延期不是永久放弃。

提交与环境：只提交本 mission 相关文件，提交信息用中文。默认不提交 `config.ts`、`.gitignore`、`tsconfig.json`。`cc-ding/` 只作只读参考。`tmp/refs/dsh-qqbot` 是被 gitignore 的本地克隆，新环境需重新执行 `git clone --depth 50 https://github.com/tencent-connect/dsh-qqbot.git tmp/refs/dsh-qqbot`。未来每次修改插件代码要使用补丁编辑、提升插件版本并覆盖本机 AstrBot 插件目录。根目录 `devflow-handoff.md` 是只读收尾指导，不修改。

不要把这轮调研当成安全验收通过；T02 未通过不得进入 T03。
