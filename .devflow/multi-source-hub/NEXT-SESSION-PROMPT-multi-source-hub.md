# Metadata（元数据）

- 创建时间（Created At）：2026-09-09 15:37:05 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：提供可直接复制的新会话恢复指令
- 关联仓库或项目（Related Repository / Project）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`。
- 关联计划（Related Plan）：`.devflow/multi-source-hub/plans/2026-09-09-多源信息中心-通用接入与QQ收藏闭环-plan.md`。
- 当前状态（Status）：可用（Ready），实施暂停。
- 文档边界（Scope / Boundary）：恢复提示，不是实施授权；以 state.md 和检查点为准。

# 下一次对话提示词

请继续本仓库的开发流程（devflow）任务 `.devflow/multi-source-hub/`。

**我上次明确不想进入实施（Apply），请先恢复上下文和讨论，不要自动开工、装依赖、接入账号或提交。**

先只读：
1. `.devflow/multi-source-hub/state.md`
2. `.devflow/multi-source-hub/checkpoints.md`

需要交接细节再读 `handoffs/index.md` 和 `handoffs/2026-09-09-001-规格待审暂停.md`（均位于任务目录）。需要完整过程读 development-overview.md；不要默认全量读取所有 plans。

当前进度：整体对齐已确认、计划已收口，spec/proposal.md、design.md、tasks.md 已写出但待审，14 项实施任务未执行。上轮只做文档并获授权提交本任务相关文件，没有业务代码、部署或远端推送。

已定方向：AstrBot 承接多平台，一份桥接插件连接独立信息中心；首期往自有 QQ 收藏群转发即收藏（无 @/命令，群主和两三个账号都是本人）。原文只有我可编辑，二次内容我与 AI 都可编辑；默认自动整理及开关、独立后台开关、手动操作、去重和本地 Git 历史。

明确延期：日常群按规则/正则/LLM 判断筛选，详见 deferred/QQ指定群持续收集与规则筛选.md；专用收藏群消息接收不能误延期。

未讨论完：具体技术栈/隔离/存储和恢复设计、开关积压行为、模型服务与送模范围、真实 QQ 权限与合并转发、重复转发身份缺失、Git 媒体策略。GitHub 远端同步、其他来源/旧历史/手记界面保留在 backlog，不能静默说已完成或永久放弃。

请先简短汇报状态，和我讨论规格里最需要收敛的点。只有我明确要求恢复实施、相关规格获准，才进入实施。不要重复讨论已确认 AstrBot 选择和收藏群入口。遵守 AGENTS.md 的中文、双语术语、相对路径、apply_patch 文本编辑及提交授权要求。
