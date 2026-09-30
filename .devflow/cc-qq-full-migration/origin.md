# 原始输入索引（Origin）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:10:32 +08:00
- 更新时间（Updated At）：2026-09-30 15:38:00 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录需求与参考材料来源。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：持续更新中（In Progress）
- 文档边界（Scope / Boundary）：原始输入索引真相源（source of truth）；不代表已批准实现方案。

## 来源列表

| 序号 | 来源路径 | 用途 | 吸收状态 |
| --- | --- | --- | --- |
| 1 | `zzz-prompt-debug/完整迁移cc-ding/prompt-01.md` | 本次迁移原始需求 | 已纳入对齐文档与总体计划 |
| 2 | `cc-ding/` | 待完整理解和迁移的源项目 | 已建立功能映射，具体行为仍需逐项核验 |
| 3 | `integrations/astrbot/` | 仓库已有 AstrBot 插件结构参考 | 已用于第一阶段骨架设计 |
| 4 | `.devflow/astrbot-claude-bridge/` | 历史相关结论与问题线索 | 仅供参考，不继承其额外要求 |
| 5 | 本次对话新增要求（无独立源文件） | 用户要求群号白名单、群聊必须 @ 才能对话，并询问当前是否可对话 | 已完成对齐与代码接入，待运行组合验收 |
| 6 | `devflow-handoff.md` | 本次暂停与交接的收尾指导，不修改原文件 | 已按其流程生成 mission 交接 |
| 7 | 本次对话新增要求（无独立源文件） | 用户选择自行上传插件 ZIP 并在 AstrBot 配置；随后要求 Claude Code 与 Codex 分开配置默认模型 | 手动安装边界与独立默认模型已纳入对齐、计划和代码；新版待用户安装验收 |
| 8 | 本次对话收尾要求（无独立源文件） | 用户要求先提交本 mission 相关代码，再按只读 `devflow-handoff.md` 生成交接并保存未完事项 | 代码已提交，交接与下一次对话提示词已写入当前 mission |
| 9 | 2026-09-30 对话（无独立源文件） | 用户要求先看断网补回、空白私聊和标准输入重置，并明确“好的先写plan”；随后要求秒数可配置、按计划写代码、覆盖安装目录 | 计划已实施到 `0.1.14` 并提交为 `7a714ac`；真实 QQ 验收留到下一对话 |
| 10 | 根目录 `devflow-handoff.md`（只读，未修改） | 2026-09-30 收尾指导。用户要求上下文过长时新开对话，先提交再收尾，并记下只做第一版和明确延期的事项 | 已按该流程更新本 mission 交接；该指导文件本身未改 |
| 11 | `zzz-prompt-debug/完整迁移cc-ding/prompt-01.md` 工作区增补（尚未提交） | 私聊短时间多条消息聚合成一条，上下文超限后截断或交给代理压缩 | 本轮未讨论、未实现；记入 `deferred/第一版边界与未讨论项.md`。该文件改动不纳入这次提交 |
