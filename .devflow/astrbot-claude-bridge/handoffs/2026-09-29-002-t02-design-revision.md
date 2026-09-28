# cc-ding 迁移 AstrBot：T02 设计回退交接（Session Handoff）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 00:21:05 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：交接已完成的功能映射、权限实测、设计阻塞、未讨论事项与下一步。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 实施计划（Implementation Plan）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`
- 前一份交接（Previous Handoff）：`.devflow/astrbot-claude-bridge/handoffs/2026-09-28-001-plan-complete-before-apply.md`
- 当前状态（Status）：交接暂停，待设计修订（Handoff / Propose Revision）
- 文档边界（Scope / Boundary）：本文件用于新对话恢复，不替代 `state.md`、`spec/` 或测试证据；未完成实施（Apply）或正式关闭（Close）。

## 当前目标与阶段

目标是复用并模块化迁移 `cc-ding` 通用核心，由 AstrBot 插件替换钉钉平台适配。本轮支持 Claude Code、Codex，QQ 群每群一个固定工作目录并共享代理会话，私聊独立；所有用户均不得读取对应工作目录之外的文件，白名单用户在目录内可读写，非白名单用户在目录内只读，群级策略和工具允许集分别取交集。完整迁移目标含 Web Console 与代理间通信（A2A）。插件需在 Windows／macOS 原生运行，不以 Ubuntu／WSL 为依赖。

当前按 devflow 重型路径（Heavy Route）从实施（Apply）回退到提案修订（Propose Revision）。原因是 T02 原生 Windows 的 Codex 文件读取边界未通过。T03 及后续插件代码任务尚未开始，没有新插件目录、版本提升或本机插件覆盖。本次交接是暂停，不是迁移完成。

## 本轮完成内容

1. 用户明确授权本轮实施；核对需求对齐（Align）、实施计划（Plan）、开放规格（OpenSpec）提案／设计／任务齐备后进入 T01。
2. 完成 `spec/feature-mapping.md`，映射命令、配置、会话、任务、Console、A2A、消息等 `cc-ding` 功能到目标模块与验收方式；T01 在 `spec/tasks.md` 标为已完成。
3. 将 T02 改为 Windows／macOS × Claude Code／Codex × 工具组合的验证矩阵，建立 `spec/permission-probe.ps1` 和 `spec/permission-matrix.md`。
4. 原生 Windows 的 Claude Code 基础文件工具组合通过部分读写与联接目录哨兵；未验证会话恢复、Shell、MCP、Hooks、Skills，因此不能将 T02 标为完成。
5. 原生 Windows 的 Codex 内置 `:read-only` 成功读取工作目录外哨兵。用户允许测试 elevated 沙箱；`:root = deny` 在普通沙箱要求 elevated，在 elevated 沙箱又因有效根目录不可读而被拒绝。由此回退设计，未将不安全组合开放。
6. 更新状态、工作流、计划、提案、设计、任务、决策、问题清单、待讨论事项与明确延期项；根目录 `devflow-handoff.md` 已阅读，未修改。

## 关键决策与原因

| 决策 | 原因与当前边界 |
| --- | --- |
| 保持“工作目录外拒读”硬要求 | 用户明确要求白名单和非白名单都不得访问目录外文件；只读模式只限制写入不足以满足。 |
| 暂停 T03 及后续插件代码迁移 | T02 是计划中的先决门禁，Codex 现有 Windows 方案未通过。 |
| Windows／macOS 原生运行 | 用户明确否定把 Ubuntu／WSL 作为插件运行前提。先前 WSL `bubblewrap` 实验不是产品验收。 |
| 工具权限独立配置并交给代理自主选择 | 有效工具集按用户与群级配置求交；任何工具仍需处于经验证的文件边界内。 |
| OpenCode、Pi 明确延期 | 先完成 Claude Code、Codex；详见 `deferred/agent-expansion.md`。 |
| 其他完整迁移能力暂不擅自延期 | 首版交付范围尚未讨论，Web Console、A2A 等仍属于已确认目标，详见 `backlog.md`。 |

## 关键文件与证据

| 文件 | 用途 |
| --- | --- |
| `state.md`、`checkpoints.md` | 恢复热路径（Resume Hot Path）与当前门禁。 |
| `plans/2026-09-28-cc-ding迁移astrbot需求对齐.md` | 已确认需求边界。 |
| `plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md` | 阶段顺序与 T02 隔离门禁；当前待修订。 |
| `spec/proposal.md`、`spec/design.md`、`spec/tasks.md` | 开放规格（OpenSpec）真相源；T02 设计待修订，T03 后续暂停。 |
| `spec/feature-mapping.md` | T01 功能清单与目标模块。 |
| `spec/permission-matrix.md`、`spec/permission-probe.ps1` | T02 已执行样本和可复现探针；探针仍需完善验证断言。 |
| `bug-log.md`、`backlog.md`、`deferred/agent-expansion.md` | 已观察问题、未讨论范围与已确认延期，三者含义不同。 |

测试宿主为 Windows 10 企业版 LTSC 10.0.19044；Claude Code CLI 2.1.282、Codex CLI 0.158.0。Claude Code 的目录内读取成功、目录外与联接目录读取被拒；文件工具允许写时目录内写入成功，目录外与联接目录写入被拒。Codex `:read-only` 读取目录外哨兵输出 `OUTSIDE_CANARY`，退出码为 0；`:root = deny` 两种 Windows 沙箱组合均未启动测试命令。`spec/permission-matrix.md` 有完整命令、观察与限制。macOS 没有实机证据，不得宣称通过。

## 阻塞、开放问题与未完成任务

- **T02 阻塞：**尚无经实测满足用户要求的 Codex 原生 Windows 进程级目录隔离；需重新设计、做越权样本、修订 OpenSpec，然后才可恢复 T03。不要把 `:root = read` 或内置 `:read-only` 当成合格配置。
- **工具边界：**Claude Code 原生 Windows 官方 Shell 沙箱不支持；Shell、Skills、MCP、Hooks、后台恢复均未验证，保持关闭。macOS 两种代理均未实测。
- **首版范围：**哪些命令和完整迁移能力进入第一个可运行版本，哪些按同一 mission 后续任务交付尚未讨论。Web Console 与 A2A 不属于已批准延期；讨论入口见 `backlog.md`。
- **后续已明确延期：**OpenCode、Pi 和其他代理，触发条件见 `deferred/agent-expansion.md`。
- **遗留环境：**此前在 WSL Ubuntu 安装 `bubblewrap`，并在 `/tmp/cc-bridge-proof` 放置权限实验材料；这不是插件依赖或仓库改动。下一次若清理，先核对准确目标与状态，避免误删；不影响 T02 设计判断。

## 当前仓库边界

- 本轮没有修改 `integrations/astrbot/` 下插件代码，也没有改变插件版本或部署本机副本。
- `.gitignore` 与 `zzz-prompt-debug/接入agent/prompt-01.md` 在本轮开始前已有改动；按用户本次提交范围，均不纳入当前 mission 文档提交。`config.ts`、`tsconfig.json` 也未纳入。
- `cc-ding/` 是本地只读参考且被忽略；需要迁移的源码未来放入可追踪插件目录并保留 MIT 许可。
- 用户本次已明确允许提交当前 mission 相关文件，提交信息使用中文；交接文件写作时提交尚未执行，以后续 Git 实际记录为准。

## 立即下一步

1. 按恢复热路径核对仓库状态和 T02 证据；以 `spec/permission-matrix.md` 的失败样本为基准研究 Windows／macOS 原生隔离候选，不降低目录外拒读要求。
2. 与用户对齐可实施的替代隔离设计及首版阶段边界；把确认结果依次写入需求对齐／计划／OpenSpec，重跑 T02 全矩阵。
3. T02 对拟开放组合全部通过后，恢复 T03 插件骨架与后续迁移；每次插件代码变更须提升版本并覆盖本机 AstrBot 对应位置。

## 恢复指引

新对话默认先读 `state.md`、`checkpoints.md`，再读 `handoffs/index.md` 与本文件。继续设计时读取 `spec/permission-matrix.md`、`bug-log.md`、`backlog.md` 及当前计划／设计。需要完整历史才读 `development-overview.md`（若存在）、`origin.md`、`checkpoints-archive.md` 或前一份 handoff。以最新仓库事实和用户指令为准。
