# cc-qq 完整迁移开发总览（Development Overview）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-23 00:00:00 +08:00
- 作者（Author）：Claude（Fable 5）
- 目的（Purpose）：用较短篇幅记录 cc-qq 从骨架到权限分级的演进脉络，供深度恢复时阅读。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：0.2.2 已覆盖安装目录，待重载与 AstrBot/QQ 真机验收
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

## 当前未完成主线的边界

- AstrBot/QQ 真机验收（T05.10）与先前遗留 T03-M.4b、T04.4、T04.5；T05.11 的 MCP 搜索仅完成 CLI 实测。
- Codex 逐次审批、审批卡片可靠通知、私聊聚合、历史查询、多代理扩展、人格与图形化权限页。
- 群内 @bot 管理私聊白名单（候选，4 个问题未确认）、群规则缺失的准确报错、Codex 原生 web search 关闭键、MCP 细粒度开关。
- 详细延期原因与触发条件见 `deferred/` 与 `backlog.md`。
