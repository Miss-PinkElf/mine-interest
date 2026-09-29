# cc-qq：AstrBot 原生 QQ 代理插件

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:40:00 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：说明 cc-qq 插件的当前能力、配置方式与后续迁移范围。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：实施中（In Progress）
- 文档边界（Scope / Boundary）：插件安装和使用说明；目前仅是第一阶段骨架，不表示完整迁移已经可用。正式任务与范围以当前 mission 的计划和开放规格（OpenSpec）为准。

## 当前状态

当前版本 `0.1.2` 已有配置范围内的 QQ 文本准入，以及独立的 Claude Code／Codex 异步进程适配器。会话服务尚未连接两端，因此当前仍不提供代理回复；会话命令、管理页面和代理间通信（A2A）在后续任务中接入。

## 配置准备

在 AstrBot 中启用插件，并填写 `qq_platform_id`、`enabled_group_ids`、`owner_qq_id` 和各群工作目录。`group_rules_json` 使用 QQ 群号作为键，例如：

```json
{
  "123456789": {
    "work_dir": "data/cc-qq-work/example",
    "agent": "claude",
    "allowed_user_ids": ["10001"]
  }
}
```

私聊需要启用 `private_enabled` 并填写 `private_work_dir`；普通私聊用户另填 `private_user_ids`。空配置默认不处理任何 QQ 群或私聊。

后续代理功能需要在 AstrBot 进程的命令搜索路径（PATH）中安装并可调用 `claude` 或 `codex`。普通会话将沿用源项目 `cc-ding` 的默认执行权限：Claude Code 使用 `bypassPermissions`，Codex 使用 `danger-full-access`；消息白名单只限制谁能发起请求，不限制代理进程对宿主机文件的访问。问答模式（`/qa`）将在第二阶段实现两种代理可验证的只读行为。

## 版本与安装副本

仓库源码位置：`integrations/astrbot/astrbot_plugin_cc_qq/`。AstrBot 用户数据目录下的安装副本位置：`data/plugins/astrbot_plugin_cc_qq/`。每次修改插件代码都会提升版本，并将仓库插件覆盖到安装副本。

## 后续阶段

- 第一阶段：QQ 消息、授权、双代理、会话与基础命令。
- 第二阶段：任务、调度、辅助命令、媒体与问答模式。
- 第三阶段：管理控制台（Web Console）、跨实例管理与代理间通信（A2A）。
- 第四阶段：逐项验收、文档和部署收口。

各阶段均属 `.devflow/cc-qq-full-migration/` 的完整目标，阶段性交付不代表提前完成。
