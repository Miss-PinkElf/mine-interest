# Metadata（元数据）

- 更新时间（Updated At）：2026-09-20 19:10:00 +08:00
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：记录当前工作路径。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`。
- 当前状态（Status）：交接中（Handoff）。
- 文档边界（Scope / Boundary）：本任务记录；诊断插件不代表完整信息中心已获准实施。

# 当前工作流（Workflow）

- 主线：整体对齐与计划已有，完整规格待审；14 项业务任务未完成。
- 当前分支：**检查插件（0.4.0）在个人号协议（aiocqhttp + NapCat）上跑通**，嵌套转发展开已解决；暂停交接。
- 平台：QQ 官方机器人已停用（DNS 失败），现用 NapCat + OneBot v11（平台 id `Test-01`，机器人 `1961618848`）。**不要再用官方机器人的前提做判断**，也不要重复询问是否已安装/登录。
- 恢复：state.md → checkpoints.md → 最新 handoff（003）→ 按需查 `bug-log.md`、`deferred/`、本机适配器实现。
- 验证方法：优先用「带唯一内外层标记的转发样例」实测，看插件日志的展开摘要（层数/条数/段类型）与 `forwards/` 产物；不靠展示文本猜层级。
- 工程顺序：对齐（Align）→计划（Plan）→实施（Apply）→验证（Verify）。**改代码前必须先落盘 plan**（本轮两次新增功能均遵守）。
- 修改源码后按用户偏好覆盖本机安装目录（`~/.astrbot/data/plugins/astrbot_plugin_sourcehub_inspector/`），然后 WebUI 热重载；安装目录不是仓库，不要在两份源码各自修改。
- 私人数据边界：真实快照、媒体、`sourcehub-image-urls.json`（含 `rkey`）**不上传、不提交、不外传**。
- 根 devflow-handoff.md 只读。本次用户已授权提交并推送相关源码与记录。
