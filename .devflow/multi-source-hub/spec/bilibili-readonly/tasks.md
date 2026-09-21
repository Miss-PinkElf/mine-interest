# Metadata（元数据）

- 创建时间（Created At）：2026-09-21 11:00:00 +08:00
- 更新时间（Updated At）：2026-09-21 15:51:15 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：追踪 B 站采集实现及验证。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联计划（Related Plan）：`../../plans/2026-09-21-B站只读提及采集-plan.md`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md`。
- 当前状态（Status）：首版已验收（Completed First Version）。
- 文档边界（Scope / Boundary）：本子变更任务真相源（Source of Truth），不修改外层 14 项任务状态。

# 任务（Tasks）

- [x] 对齐（Align）：用户确认只采集、不公开回复、复用 AstrBot。
- [x] 计划（Plan）：计划及子规格已落盘。
- [x] T1 只读客户端及接口契约。
- [x] T2 评论关系、作品正文和附件提取。
- [x] T3 通知分页、去重、失败重试与原子保存。
- [x] T4 AstrBot 生命周期、配置与安全停用默认值。
- [x] T5 离线测试及聚焦审查（Review）。33 项合成测试通过。
- [x] T5b 审查四项回归：字段合并、异常隔离、空正文、关系字段缺失。
- [x] T6 使用文档、安装包及本地安装。
- [x] T7 五类真实样本验收：视频顶层、回根评、回子评、专栏、图文动态均为完整。可选续测见 `qq-bilibili-capability-boundary.md`。
