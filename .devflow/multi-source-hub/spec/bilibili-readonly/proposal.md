# Metadata（元数据）

- 创建时间（Created At）：2026-09-21 11:00:00 +08:00
- 更新时间（Updated At）：2026-09-21 15:51:15 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：定义 B 站只读采集子变更。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联计划（Related Plan）：`../../plans/2026-09-21-B站只读提及采集-plan.md`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md`。
- 当前状态（Status）：首版已验收（Completed First Version）。
- 文档边界（Scope / Boundary）：本子变更真相源（Source of Truth）；不覆盖外层待审 QQ 规格。

# 提案（Proposal）

收到 B 站 @ 通知后，独立保存通知、触发评论、直接父评论、根评论及来源作品详情，动态/专栏包括全文和图片。AstrBot 承担配置、启停和运行环境；实现不提供公开回复或其他对外写操作。

正文获取失败、图片下载失败、评论不存在、未知格式均显式记录，禁止保存摘要后宣称全文完整。没有登录态时插件保持停用，开发验证使用模拟响应；真实平台验收必须使用本地账号。

范围与延期以关联计划为准。用户已批准本方向，按计划连续推进实现，不重复请求方向确认。
