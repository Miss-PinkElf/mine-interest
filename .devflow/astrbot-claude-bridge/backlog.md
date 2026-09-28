# 待讨论事项（Open Questions）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 00:21:05 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录尚未对齐的首版细节，避免将开放问题误写成已批准延期。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：待讨论（Open）
- 文档边界（Scope / Boundary）：候选问题清单（Candidate Questions），不代表方案批准、范围缩减或自动触发实施。

## 首版与完整迁移的阶段边界

- 尚未讨论首个可运行版本（First Version）需要交付哪些命令、媒体、任务、Console 与 A2A 能力，以及同一 mission 后续任务的验收顺序。
- 已确认的“完整迁移”目标仍包含 Web Console、A2A、会话、任务、调度、待办、菜单、图片文件、命令和管理能力；没有用户确认前，不能把其中任何能力改成明确延期。
- 推荐在 T02 隔离方案修订后、T03 插件代码迁移前，依据 `spec/feature-mapping.md` 与 `spec/tasks.md` 与用户对齐首版阶段划分。

## 配置与身份细节

- 私聊默认允许的用户范围和首次工作目录配置方式；全局白名单、群级上限及工具允许集的管理入口。
- 群共享历史下，前一位成员的消息、工具结果与工作目录路径是否对群内下一位成员可见；需要结合安全验收明确展示边界。
- AstrBot 插件页面（Plugin Page）如何承载原 Web Console 的远程管理体验，以及钉钉专属命令的用户可见替代文案。
