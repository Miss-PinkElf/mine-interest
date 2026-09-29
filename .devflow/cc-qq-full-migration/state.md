# cc-qq 完整迁移当前状态（Current State）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:10:32 +08:00
- 更新时间（Updated At）：2026-09-29 11:00:28 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：提供本 mission 的短当前快照。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：第一阶段实施暂停、待下次对话续接（Stage 1 Apply Paused for Handoff）
- 文档边界（Scope / Boundary）：当前状态真相源（source of truth）；对齐、计划和开放规格已齐备，按第一阶段任务推进。

## 当前快照

- 新 mission 已初始化，采用重型路径（Heavy Route）。
- 当前阶段：第一阶段实施（Apply）暂停，等待下一次对话续接。T00 功能映射已完成；T01–T03 有 `0.1.2` 骨架代码但未核验，T04 未实现。`main.py` 当前只回复“代理会话功能正在接入”，**还不能与 Claude Code／Codex 对话**。
- `cc-ding/` 是独立 Node.js / TypeScript 项目，仓库已有 `integrations/astrbot/` 下的 Python 插件。
- `.devflow/astrbot-claude-bridge/` 是历史相关 mission；本 mission 独立记录，其权限失败证据仅作参考，不继承其批准状态或额外要求。
- 对齐文档：`plans/2026-09-29-cc-ding原生python迁移qq插件-需求对齐.md`。
- 总体计划：`plans/2026-09-29-cc-ding原生python完整迁移qq插件-总体实施计划.md`；第一阶段计划：`plans/2026-09-29-cc-qq原生python插件第一阶段实施计划.md`。
- 当前开放规格：`spec/proposal.md`、`spec/design.md`、`spec/tasks.md`。
- 功能映射：`spec/feature-mapping.md`（所有目标待实现）。
- 本机 AstrBot 安装副本已由 0.1.1 覆盖为仓库 0.1.2；目录逐文件比较一致。未做真实 QQ／CLI 运行验收。复制操作不会展示 Codex CLI 的 `Added`／`Edited` 内联差异，以仓库补丁和 `git diff` 为准。
- 新增需求：群号白名单（Group Allowlist）与群聊必须 @ 机器人（Mention Gate）。现有 `enabled_group_ids` 已限制群号，`group_rules_json.allowed_user_ids` 可限制群成员，但均未实际验收；@ 门禁尚未设计确认或实现。两者按第一阶段候选增量处理，需先完成 Mini Align → Plan → Spec/Tasks，不能把未实现写成已完成。
- 下一步：先确认 @ 门禁的具体语义及其与命令、消息段的关系，补充对齐／计划／任务；然后继续 T01–T04，将插件做成可对话的第一版。真实 QQ 与双 CLI 结果未取得前不标记阶段完成。最新交接见 `handoffs/2026-09-29-001-第一阶段暂停.md`。

## 本轮不做 / 后续阶段（Deferred Scope）

- 第一版优先完成 QQ 群／私聊与双代理文本闭环、白名单和待确认的 @ 门禁；任务、媒体、`/qa` 等在阶段 1 通过后进入阶段 2，管理页与 A2A 在阶段 2 接口稳定后进入阶段 3，完整性收口在阶段 3 后进入阶段 4。对象、原因和触发条件见 `deferred/阶段二至四功能.md`；这些不是永久放弃项。
