# T02 平台与代理权限矩阵（Permission Matrix）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 00:06:23 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录原生 Windows 的可复现权限证据，并定义 macOS 和高权限工具组合的待验证边界。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 实施计划（Implementation Plan）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`
- 开放规格（OpenSpec）：`.devflow/astrbot-claude-bridge/spec/tasks.md`
- 当前状态（Status）：验证失败，待重新设计（Design Revision Required）
- 文档边界（Scope / Boundary）：本文件是 T02 当前证据记录，不代表 T02 全部通过，也不授权启用未验证工具或宣称 macOS 已验收。

## 目标与判断方式

测试采用系统临时目录下的 `astrbot-cc-bridge-t02/work` 和同级 `outside` 哨兵。具体绝对路径由运行机器生成，仓库中的路径一律以相对路径记录。测试文件不含真实用户数据；`permission-probe.ps1` 可复现基础矩阵，但 Claude 调用可能产生模型费用。

一个组合要被标记“可开放”，必须同时证明：目录内读取成功、目录外读取失败、只读写入失败、目录内允许写入成功、目录外／联接目录写入失败、恢复会话后降权仍有效；如组合允许 Shell、Skills、MCP、Hooks，还要各自证明相同边界。未执行的样本记为“未验证”，不能靠代理口头拒绝代替权限拒绝证据。

## 2026-09-29 原生 Windows 实测

宿主为 Windows 10 企业版 LTSC，版本 10.0.19044；Claude Code CLI 2.1.282、Codex CLI 0.158.0。Windows 两种 CLI 均已登录；未读取或记录认证密钥。命令在系统临时测试目录执行，未修改插件代码。

| 代理与组合 | 测试动作和观察 | 结论 |
| --- | --- | --- |
| Claude Code：`--safe-mode --strict-mcp-config --tools Read,Glob,Grep --permission-mode dontAsk`，并启用 `permissions.blockReadsOutsideWorkingDirectories` | `inside.txt` 成功读取；`../outside/outside.txt` 返回 `Read` 权限拒绝；通过 `outside-link` 联接目录读取同样被拒，JSON 输出含 `permission_denials`。 | 基础只读文件工具候选通过目录读取边界；未测会话恢复，不标记 T02 全通过。 |
| Claude Code：同上，仅暴露只读工具 | 请求创建 `should-not-exist.txt` 后文件仍不存在，代理确认没有可用写工具。 | 只读写入样本通过。 |
| Claude Code：增加 `Write,Edit`，只允许 `Edit(//c/.../work/**)` | `Write` 在工作目录内创建 `allowed.txt` 成功；对 `../outside/claude-outside.txt` 的 `Write` 返回权限拒绝且文件不存在；对联接目录目标的 `Write` 返回权限拒绝且文件不存在。 | 文件工具的读写组合有初步证据；规则需按每台机器生成，不能硬编码本机盘符或用户路径。恢复、其他工具未验证。 |
| Codex：内置 `:read-only` | `codex sandbox -P ':read-only' -C <work> -- powershell ...` 可读取工作目录内测试文件，也**成功读取**同级 `outside/outside.txt`；写入工作目录时收到 `Access denied`，文件不存在。 | 只读不等于限制读取工作目录外，**不能按原需求开放给非白名单**。 |
| Codex：自定义权限，`:root = deny`、`:minimal = read`、`:workspace_roots = read` | `codex sandbox -P t02 ...` 返回 `Restricted read-only access requires the elevated Windows sandbox backend`，未执行测试命令。 | 本机普通原生沙箱不支持该严格拒读组合；后续 elevated 实测也失败，详见下一行。未通过 T02。 |
| Codex：同一自定义权限，启用 `windows.sandbox="elevated"` | 返回 `elevated Windows sandbox requires effective ':root' read access`，退出码 `1`；测试命令未启动。用户已授权系统级初始化，但提升权限后仍无法应用根目录拒读。 | 已验证的 elevated 配置与本轮“工作目录外拒读”要求冲突；不能继续按现有设计实现。 |
| Codex：elevated 加 `:root = read` | 在仓库目录可启动并读取当前位置；在系统临时测试目录启动时返回 `CreateProcessWithLogonW failed: 267`。 | 根目录可读配置可启动，但不满足目录外拒读；临时目录的额外启动错误尚未解释，不能用来推断权限安全。 |
| Claude Code／Codex：Shell、Skills、MCP、Hooks、后台恢复 | 尚无原生 Windows 安全证据。Claude Code 官方内置 Shell 沙箱不支持原生 Windows。 | 默认禁用这些未验证组合；不能从基础文件工具通过推断其安全。 |
| Claude Code／Codex：macOS | 当前没有 macOS 实机测试。 | 全部标为未验证；不能宣称跨平台验收。 |

## 可复现命令与退出状态

- `claude --version` → `2.1.282`，退出码 `0`；`claude auth status` → `loggedIn: true`，退出码 `0`。
- `codex --version` → `codex-cli 0.158.0`，退出码 `0`；`codex login status` → 已登录，退出码 `0`。
- `claude -p ... --tools Read,Glob,Grep --permission-mode dontAsk --safe-mode --strict-mcp-config --settings <临时配置> --output-format json`：目录外和联接目录读取均在 JSON 的 `permission_denials` 中，CLI 自身退出码为 `0`；CLI 退出码表示对话成功结束，不表示文件访问成功。
- Claude Code 的目录内 `Write` 成功且文件存在；目录外／联接目录 `Write` 被拒，输出有一个 `permission_denials`，目标文件不存在；CLI 自身退出码为 `0`。
- `codex sandbox -P ':read-only' -C <work> -- powershell ...`：目录外读取输出 `OUTSIDE_CANARY`，退出码 `0`。该结果是明确越权样本。
- `codex sandbox -c 'permissions.t02.filesystem={":root"="deny",":minimal"="read",":workspace_roots"={"."="read"}}' -P t02 -C <work> -- powershell ...`：返回 elevated 沙箱要求，退出码 `1`。
- 同一配置再加 `-c 'windows.sandbox="elevated"'`：返回 `elevated Windows sandbox requires effective ':root' read access`，退出码 `1`。
- elevated 配置改为 `:root = read` 后，在仓库目录可执行 `Get-Location`，退出码 `0`；该配置允许广泛读取，不符合本轮文件边界。

## 根因、处理与下一门禁

- **问题现象：**Codex 内置只读模式能读取工作目录外文件。**原因：**内置模式约束写入，不自动对所有非工作目录路径拒读。**解决方案：**保持该组合关闭；重新设计可在宿主层执行目录隔离的方案并实测。
- **问题现象：**严格拒读配置在普通 Windows 沙箱要求 elevated；启用 elevated 后又要求根目录有效读取权限。**原因：**当前 CLI 0.158.0 的两个 Windows 后端均未接受本轮要求的 `:root = deny` 配置；elevated 的启动前校验明确拒绝。**解决方案：**回退开放规格（OpenSpec）设计，寻找原生 Windows 可运行且真实拒读的执行边界；在完整越权样本通过前，不开放 Codex 代理执行。
- **问题现象：**Claude Code 原生 Windows 缺少官方 Shell 沙箱。**原因：**官方内置沙箱只支持 macOS、Linux 和 WSL2。**解决方案：**Windows 先仅开放实际验证的内置文件工具；Shell、MCP、Hooks 及可间接操作文件的 Skills 需独立安全方案和逐项验证，未通过前保持关闭。

官方依据：

- [Claude Code 权限与文件规则](https://code.claude.com/docs/en/permissions)
- [Claude Code Shell 沙箱平台限制](https://code.claude.com/docs/en/sandboxing)
- [Codex 权限配置与目录外拒读示例](https://learn.chatgpt.com/docs/permissions)
- [Codex 原生 Windows 沙箱和 elevated 后端](https://learn.chatgpt.com/docs/windows/windows-sandbox)

## 当前执行边界

T02 因 Codex 原生 Windows 文件边界设计缺陷而暂停，并按 devflow 从实施（Apply）回退到提案（Propose）。现有设计要求两种代理都满足同一目录边界，因此尚未进入插件代码迁移。**不得启用 Codex 代理执行，不得开放任何未验证的 Shell／MCP／Hooks 等工具，也不得把原生 Windows 的 Claude Code 基础文件工具结果推广到 macOS**。后续重新设计并验证通过后再更新本矩阵和任务状态。
