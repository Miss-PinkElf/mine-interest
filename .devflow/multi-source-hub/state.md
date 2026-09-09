# Metadata（元数据）

- 创建时间（Created At）：2026-09-09 11:14:50 +08:00
- 更新时间（Updated At）：2026-09-09 15:37:05 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：提供当前任务的简短恢复入口。
- 关联仓库或项目（Related Repository / Project）：mine-interest-source-hub（`.`）
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`
- 当前状态（Status）：用户暂停（Paused），规格待审（Spec Pending Review）
- 文档边界（Scope / Boundary）：当前状态真相源（Source of Truth）；候选方向不代表批准方案。

# 当前状态

- 当前阶段：暂停于规格提案（Propose）；用户明确“现在不太想 apply”，不得自动开始实施。
- 路径：用户指定的重型路径（Heavy）。
- 目标：把多渠道有用内容、图片和个人想法统一收集、整理，并支持笔记及智能体（Agent）管理。
- 已确认编辑权限：原始数据（Raw Data）保留且只有用户可编辑；二次处理内容（Derived Content）由用户和人工智能（AI）共同编辑。旧候选推荐已撤回。
- 已确认：默认自动整理且有开关，同时支持手动；Git 为修改历史的当前方向；产品面向外部智能体使用。
- 已确认：支持后台独立运行且有开关，提供按指定信息源收集的工具（Tool），重复收集不得重复入库。
- 已确认框架分工：用户同意借用 AstrBot 的机器人接入及智能体执行能力；信息中心独立提供数据与工具接口，不绑定 AstrBot 内置知识库。
- 首期已确认：主动转发到现有专用收藏群，群内两三个账号均属用户；私聊入口已被更正。详见 `plans/2026-09-09-QQ主动收藏首期范围-align.md`。
- 延期项（Deferred Scope）：从日常群消息流按规则、正则与 LLM 辅助判断进行筛选；不含首期专用收藏群接收。详见 `deferred/QQ指定群持续收集与规则筛选.md`，推荐首期验收后继续。
- 最新确认：转发即收藏，无需 @/命令；群主为本人；QQ 权限仍未实测。
- 最新产物：`spec/proposal.md`、`spec/design.md`、`spec/tasks.md`；14 项业务任务未执行，本轮无业务代码/安装/联调。
- 下一步：新对话先恢复并讨论/审阅规格；仅用户明确恢复实施意图且门禁满足时进入 Apply。
- 范围澄清：AstrBot 原有适配器承接多平台，一个桥接插件统一投递；GitHub 远端同步单独记 `backlog.md`，不阻塞本地首期也不默认上传。
- 工作区外部改动：`.codex/config.toml`、`AGENTS.md`、`devflow-handoff.md`、原始需求笔记为修改，`.codex/model-catalog.json` 为删除，未触碰。
- 最新交接：`handoffs/2026-09-09-001-规格待审暂停.md`；可复制 `NEXT-SESSION-PROMPT-multi-source-hub.md` 恢复。
- 未定问题：实现复杂度、开关积压策略、QQ 权限/转发结构、模型配置、媒体与 Git、GitHub 远端及其他来源范围，详见交接和 backlog。
- 本轮收尾：用户明确授权提交相关文档；提交事实以 Git 日志核验，无 push。之前状态见 `state-history.md`。
