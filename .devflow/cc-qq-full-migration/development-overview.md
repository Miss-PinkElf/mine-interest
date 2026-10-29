# cc-qq 完整迁移开发总览（Development Overview）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-23 00:00:00 +08:00
- 作者（Author）：Claude（Fable 5）
- 目的（Purpose）：用较短篇幅记录 cc-qq 从骨架到权限分级的演进脉络，供深度恢复时阅读。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：0.2.5 已完成命令、权限与工具级真机验收（A+B+C），F1 已修复（Completed for A+B+C）
- 文档边界（Scope / Boundary）：过程总览，不代替 `state.md`、`spec/` 或 `plans/`。

## 演进时间线

| 时间 | 版本 / 提交 | 主要变化 |
| --- | --- | --- |
| 2026-09-29 | `0.1.2`–`0.1.12` | 建立原生 Python AstrBot 插件、QQ 事件归一、双代理进程、SQLite 会话与基础命令；首次真机 Codex 群聊／私聊回复。 |
| 2026-09-29 | `0.1.13` | Claude Code 与 Codex 独立默认模型。 |
| 2026-09-30 | `0.1.14` / `7a714ac` | 过期消息过滤、私聊空文本静默、标准输入重置错误处理。 |
| 2026-09-30 | `0.1.16` / `107409f` | 非白名单私聊静默、同一句 10 秒去重。 |
| 2026-10-23 | `0.2.0` / `0ad479e` | 权限分级、危险操作审批、Codex 权限档案、`/cd`、`/pwd`、`/initbase`、审计与基础模板。 |
| 2026-10-27 | `0.2.1` / `0.2.2` | 配置页按 ①–⑦ 分组重写文案；放行 deepseek-web MCP 搜索、禁用原生 `WebSearch`／`WebFetch` 与本机 `mcp__fetch`，只读档新增 `readonly_mcp_enabled`。 |
| 2026-10-28 | `0.2.3` | 新增 `/cd list`（按 `allowed_work_dirs` 配置顺序编号并标记当前目录）与 `/cd <序号>` 切换；路径形式保持不变，三种入口共用同一套边界校验。 |
| 2026-10-28 | `0.2.4` | 修 `/goon` 取消后被误标 `done` 且静默的问题；新增执行回执（会启动代理的输入先回一条）；首轮产出排查耗时分析文档，把「串行往返过多」与「长任务无中间输出」关联起来。 |
| 2026-10-29–30 | `0.2.5` | 在专用测试群完成 A+B+C 真机验收：三级命令门禁、`/cd` 序号切换、真实代理执行、`/goon` 前缀、执行中 `/!` 中断、guest 只读、工作区写入、目录外审批、deepseek 搜索。修复 F1（执行回执必须晚于权限、参数与会话校验），113 个单测通过。 |

## 当前架构脉络

```
QQ/AstrBot 事件
  → qq_events 归一
  → policy 判定角色与每轮权限档
  → service 命令/会话编排
  → agents/profiles 生成 Claude/Codex 参数与策略
  → Claude：readonly_hook / approval_hook + 沙箱 / guard_hook
  → Codex：ccqq-readonly / ccqq-workspace / danger-full-access
  → approval broker + QQ /approve /deny
```

## 关键决策

- 2026-09-29：用户先选 Python + TypeScript 双进程，随后改为原生 Python AstrBot 插件；`cc-ding` 只作参考。
- 2026-09-29：群聊必须精确 @ 当前机器人；私聊不要求 @；群号白名单沿用 `enabled_group_ids`。
- 2026-09-30：普通会话曾沿用 `cc-ding` 的 `bypassPermissions` / `danger-full-access`。
- 2026-10-23：权限按角色分级，普通会话不再一律完全权限；非白名单群成员改为只读。
- 2026-10-23：Claude `bypassPermissions` 实测不执行 deny，完全权限改为 `dontAsk + guard_hook`。
- 2026-10-23：Codex 传统 `read-only` 不限读取，改用权限档案。
- 2026-10-27：MCP 联网按「服务端搜索放行、本机 fetch 禁用、原生联网工具禁用」收口；MCP 与鉴权都要求 `claude_setting_sources=user`。
- 2026-10-27：群内 @bot 管理私聊白名单仅提出未讨论完，不实施；配置页只做文案与顺序改造，不重构配置结构。
- 2026-10-28：`/cd list` 按用户要求做成最小版——直接输出 `allowed_work_dirs` 配置项并按序编号，不扫描磁盘、不展开子目录；用户明确否决了「根目录 + 一级子目录」与两级列表方案。

## 当前未完成主线的边界

- Claude 侧 T05.10／T05.11／T05.12／T05.13 已完成真机验收；**Codex 侧同项验收**与先前遗留 T03-M.4b、T04.4、T04.5 仍待做。
- `v0.2.5` 未生成 ZIP、未推送远端；测试机器人仍与生产共用 `17号`，第三个测试账号待有。
- 需求 2（通用插件测试 skill：双 QQ、暂停生产、按插件生成测试流程与报告、自愈能力）已由用户提出并记录，未实施。
- Codex 逐次审批、审批卡片可靠通知、私聊聚合、历史查询、多代理扩展、人格与图形化权限页。
- 群内 @bot 管理私聊白名单（候选，4 个问题未确认）、群规则缺失的准确报错、Codex 原生 web search 关闭键、MCP 细粒度开关。
- `/cd list` 的扩展能力（一级子目录、两级列表、分页、序号持久化）本轮明确不做；需求 4.2（diff 转 HTML）、需求 5（guest 与白名单是否共享上下文）、未来需求（上下文长度提示）本次未讨论。
- 详细延期原因与触发条件见 `deferred/` 与 `backlog.md`。
