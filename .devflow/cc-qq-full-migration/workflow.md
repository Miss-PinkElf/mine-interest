# cc-ding 完整迁移为 cc-qq 工作流（Workflow）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:10:32 +08:00
- 更新时间（Updated At）：2026-10-28 01:30:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：记录本次完整迁移的阶段与门禁。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：0.2.5 已完成 A+B+C 真机验收，F1 已修复（Verified / Pending Codex）
- 文档边界（Scope / Boundary）：本 mission 的流程真相源（source of truth）。对齐、计划和第一阶段开放规格已落盘，不代表第一阶段已验收。

## 目标与路径

- 目标：理解 `cc-ding/` 的完整能力，借鉴其运行链路，用原生 Python 实现基于 AstrBot 的 QQ 插件并分阶段补齐功能，保持模块化。
- 路径：重型路径（Heavy Route），依次进行对齐（Align）→ 计划（Plan）→ 开放规格（OpenSpec）→ 实施（Apply）→ 审查与验证（Review / Verify）→ 收尾（Close）。
- 当前阶段：`0.2.5` 已在专用测试群完成 A+B+C 真机验收（三级权限、`/cd`、真实代理执行、`/goon` 前缀、`/!` 中断、guest 只读、目录外审批、deepseek 搜索）；F1（回执早于权限/参数校验）已修复，113 个单测通过。Codex 侧同项未验；ZIP 与推送未做。
- 新增产出：`2026-10-28-排查耗时分析与优化方案.md` 把「串行往返过多」量化为长耗时主因，并据此把流式输出的触发条件更新为已满足；该结论待用户决定是否提级。

## 阶段门禁

- 先与用户讨论候选方案并取得对齐确认，再写对齐文档与计划。
- 计划落盘后才创建 `spec/proposal.md`、`spec/design.md`、`spec/tasks.md`。
- 三件套齐备后才修改插件代码。插件代码变更后的安装覆盖，以用户当次明确要求为准。
- 完成声明前取得新的验证证据。代码提交以用户当次明确允许为准；2026-09-30 两次收尾用户都要求先提交再写交接。

## 下一步

1. 做 Codex 侧同项真机验收（只读、工作区、完全权限），并补验 T03-M.4b、T04.4、T04.5。
2. 决定是否生成 `v0.2.5` ZIP、提交并推送远端。
3. 按用户新增需求 2，评估把插件测试流程做成通用 skill（双 QQ、暂停生产、按插件生成用例与报告、自愈能力）。
4. 评估第三个测试 QQ 账号、生产暂停自动化、@bot 空文本被 LLM 抢占（F2）。
5. 群内 @bot 管理私聊白名单等候选需求，先补齐 4 个待确认问题再进入对齐。
