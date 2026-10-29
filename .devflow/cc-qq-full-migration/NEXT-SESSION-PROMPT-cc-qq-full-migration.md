# 下一次对话提示词：cc-qq 0.2.5 验收后收尾（Next Session Prompt）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 11:00:28 +08:00
- 更新时间（Updated At）：2026-10-30 00:40:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：提供可直接复制到新对话的 mission 恢复指令。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：0.2.5 已完成 A+B+C 真机验收，F1 已修复；Codex 侧与发布待做
- 文档边界（Scope / Boundary）：恢复提示，不代替 `state.md` 或已批准计划。

## 可复制提示词

继续 `.devflow/cc-qq-full-migration/` mission。

先读：
- `.devflow/cc-qq-full-migration/state.md`
- `.devflow/cc-qq-full-migration/checkpoints.md`
- `.devflow/cc-qq-full-migration/handoffs/2026-10-30-009-0.2.5命令权限验收与F1修复.md`

**硬门禁（最高优先级）**：任何代码修复前必须先「说明问题与根因 → 讨论方案 → 写 Plan 到 `.devflow/<mission>/plans/` → 用户明确批准 → 再 Apply」。`继续验证`、`先测着`、`最后再修复` 都不是修复授权。

## 当前结论（2026-10-30）

- 版本 `0.2.5`；插件单测 113/113 通过。
- A+B 真机验收（群 `701292201`）：34 项，32 通过；1 项环境限制（@bot 空文本被 AstrBot 内置 LLM 抢占，F2）；2 项暴露 F1。
- C 阶段全部通过：真实代理执行（1.1s 回执 / 6.5s 回复）、`/cc` 透传、`/goon` 前缀、执行中 `/!` 中断、guest 只读、workspace 内写、目录外审批 `/approve`/`/deny`、deepseek 搜索（1 次 `deepseek_search`，0 次原生联网）。
- F1 已修复并复验：`will_run_agent` 增加 role 门禁、`/cc` 空参不回执；`/goon` 无活跃会话不回执。
- 证据：`plans/2026-10-29-cc-qq-0.2.4-命令与权限验收结果.md`（A/B/C/D 节）；原始 JSON 在 `tools/astrbot_e2e/reports/20261029-ccqq-accept/`（gitignored）。

## 当前环境

- 生产 AstrBot：PID `61792`，`6185/6199` 正常；测试 AstrBot：PID `31955`，`6186/6198`，插件副本 `0.2.5`。
- 两个 QQ 在线：`3254276668（17号）`、`1961618848（C#）`；NapCat `6099/6200`、`6098/6201`。
- 测试实例配置已恢复：owner=`1961618848`、`full`、`allowed_work_dirs=[]`、`claude_setting_sources=""`。
- 生产 NapCat 的 `AstrBot-E2E`（`6198`）已启用；测试群 `701292201` 只在测试实例。
- 一键启动脚本：`~/.qq-e2e/start-e2e.sh`（iTerm2 单窗口三标签，自动启用 6198；本地脚本不入库）。

## 下一步优先级

1. **Codex 侧真机验收**：T05.10 的只读、工作区、完全权限；补验 T03-M.4b、T04.4、T04.5。
2. **发布决定**：是否生成 `v0.2.5` ZIP、提交并推送远端。
3. **需求 2**（用户 2026-10-29 在 `zzz-prompt-debug/插件自动化测试验证/prompt-01.md` 新增）：把插件测试流程做成通用 skill（双 QQ、暂停生产、按插件生成测试流程与报告、具备自愈能力、适配不同 NapCat/AstrBot/运行环境）。需先 Align，不要直接实施。
4. **测试拓扑**：第三个 QQ 测试账号（一个生产、两个测试）；E2E 期间自动暂停/恢复生产；F2（@bot 空文本被 LLM 抢占）。
5. 流式输出：触发条件已满足，优先级由用户决定。

## 必须记住的约束

- **修复前必须走 Align → Plan → 用户明确批准 → Apply**；本次 F1 修复就是因为跳过了明确批准，规则已写入 `.claude/CLAUDE.md` 开头、中间、结尾三处。
- 测试期间若生产 AstrBot 与测试共用 `17号`，生产会响应测试群的内置命令与 LLM；需暂停生产或改用独立测试账号。
- 代理类测试需把测试实例 `claude_setting_sources` 设为 `user`，否则 Claude 未登录、MCP 不加载；测完恢复。
- `allowed_work_dirs` 为空时 `/cd` 只能测「未配置」负向；测序号切换需临时配置 3 个测试目录。
- 相同回复文案 10 秒内被去重，批量验收需间隔 ≥11 秒。
- NapCat 的 `onebot11_*.json` 带 UTF-8 BOM，用 `utf-8-sig`；改完必须重启 QQ。
- 会话 JSONL 的 `timestamp` 是 UTC，本地 +8；工具调用统计按 `tool_use.id` 去重。

## 恢复读取建议

- 日常恢复：`state.md` → `checkpoints.md` → 最新 handoff。
- 完整过程：`development-overview.md` + `decision-log.md` + `plans/`。
- 延期项：`deferred/2026-10-30-post-0.2.5-deferred.md`；轻量想法：`backlog.md`。
- 原始输入与新增需求：`origin.md`、`zzz-prompt-debug/插件自动化测试验证/prompt-01.md`。
