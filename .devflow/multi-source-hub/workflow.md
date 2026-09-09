# Metadata（元数据）

- 创建时间（Created At）：2026-09-09 11:14:50 +08:00
- 更新时间（Updated At）：2026-09-09 15:37:05 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录多源信息中心的重型开发流程与阶段门禁。
- 关联仓库或项目（Related Repository / Project）：mine-interest-source-hub（`.`）
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`
- 当前状态（Status）：暂停（Paused），规格待审（Spec Pending Review）
- 文档边界（Scope / Boundary）：流程真相源（Source of Truth）；只确认流程，不代表产品方案已批准，不触发实施。

# 多源信息中心工作流

- 路径：重型路径（Heavy），由用户明确指定。
- 当前阶段：暂停于规格提案（Propose）；用户明确不进入 Apply，新对话默认讨论/审阅。
- 已确认框架分工：借用 AstrBot 负责机器人接入及智能体执行，信息中心保持独立；当前收敛 QQ 场景及首期范围。
- 首期 QQ 场景：主动收藏；指定群持续收集与规则筛选已延期，详见 `deferred/QQ指定群持续收集与规则筛选.md`。推荐首期闭环验收后另启阶段。
- 入口澄清：主动收藏发生在用户现有专用收藏群，不是私聊；该群消息接收属于首期。延期仅指日常信息源群的规则/模型筛选采集。
- 推进顺序：需求对齐（Align）→ 计划（Plan）→ 提案/设计/任务（Proposal / Design / Tasks）→ 实施（Apply）→ 审查（Review）→ 验证（Verify）→ 阶段收束（Close）。
- 对齐技能：`.codex/skills/devflow/skills/superpowers-brainstorming/SKILL.md`。
- 对齐目标：承接已有产品需求文档（PRD），明确面向智能体的命令行接口（CLI）与服务边界、自动整理执行者、信息源接入和首期范围。编辑权限及自动开关已明确，不重复讨论。
- 计划位置：`.devflow/multi-source-hub/plans/`；文件名须包含多源信息中心及本次阶段主题。
- 正式规格位置：`.devflow/multi-source-hub/spec/proposal.md`、`design.md`、`tasks.md`。
- 实施门禁：对齐确认、计划落盘已满足；规格三件套齐备，需用户审阅/授权实施后进入 Apply。真实账号和模型配置不影响本轮文档成稿，但对应联调任务不能伪标通过。
- 提交规则：未得到用户明确许可，不执行代码提交（Commit）。
- 本次例外授权：用户明确要求直接提交本轮任务相关文件，不再询问；不授权远端推送或未来实施提交。
- 恢复入口：state.md → checkpoints.md；按需读最新 handoff，只有用户恢复实施意图才继续生命周期。
- 文档判断：需要新增本任务记录；已有需求草案保留，确认差异后再决定如何更新。
