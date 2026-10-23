# cc-qq 完整迁移当前状态（Current State）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:10:32 +08:00
- 更新时间（Updated At）：2026-10-23 00:00:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：提供本 mission 的短当前快照。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：权限分级代码已实施、待提交与真机验收（Implemented / Runtime Verification Pending）
- 文档边界（Scope / Boundary）：当前状态真相源（source of truth）。不代表已在 AstrBot/QQ 上验收通过，也不代表已提交或已覆盖安装目录。

## 当前快照

- 仓库插件版本升至 `0.2.0`，新增权限分级、危险操作审批、`/cd`、`/pwd`、`/initbase`、审计表与基础模板。83 个单元测试通过；尚未提交，安装目录仍不是这一版。
- 权限模型：群内非白名单为 `readonly`，群／私聊白名单为 `workspace`，owner／管理员为 `full`；档位按每轮发言者计算，不写入会话记录。
- Claude Code：只读用 `dontAsk + --tools`；工作区用 `acceptEdits + Seatbelt/bubblewrap 沙箱 + PreToolUse 审批 hook`；完全权限用 `dontAsk + 守护 hook`（实测 `bypassPermissions` 不执行 deny 规则）。默认 `--setting-sources ""`。
- Codex：只读/工作区改用权限档案 `ccqq-readonly`、`ccqq-workspace`，工作区外读写与 `/tmp` 被拒绝；完全权限用 `sandbox_mode="danger-full-access"`。Codex 本轮没有逐次审批。
- 本机 CLI 实测：Claude Code 2.1.202 的 hook 能向本机 broker 请求并放行/拒绝 `rm`；Codex 0.162.1 的权限档案能阻止读取 `~/.codex/config.toml`，工作区档能写当前目录并阻止写 `/tmp`。
- 审批：`/approve`、`/deny` 在 `main.py` 会话队列前处理，避免与等待审批的代理死锁；超时、异常、broker 不可达一律拒绝；`permission_audit` 记录审批与拒绝。
- 管理员 `/cd` 只能进入 `allowed_work_dirs` 的 realpath 子目录；`/initbase` 只补缺失模板，不覆盖已有文件。

## 本轮不做 / 后续阶段（Deferred Scope）

- 真机验收 T05.10：需要用户决定是否提交、是否生成 `v0.2.0` ZIP、是否覆盖安装目录并重载 AstrBot。
- Codex 逐次危险操作审批：`codex exec` 的非交互审批仍为 under development。
- 审批卡片私聊通知管理员、私聊短时聚合与上下文截断（需求3.3）、工作目录人格、图形化权限页：见 `deferred/阶段二至四功能.md`。
- 阶段 2 到阶段 4 的其余功能仍按总体计划继续。
