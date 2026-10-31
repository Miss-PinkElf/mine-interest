# cc-ding 完整迁移为 cc-qq 工作流（Workflow）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:10:32 +08:00
- 更新时间（Updated At）：2026-11-01 02:40:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：记录本次完整迁移的阶段与门禁。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：`0.3.3` 代码完成、单测 181/181、真机 e2e 12/12 通过；测试实例已装，生产仍 `0.3.2`，待发布（Verified / Release Pending）
- 文档边界（Scope / Boundary）：本 mission 的流程真相源（source of truth）。对齐、计划和第一阶段开放规格已落盘，不代表第一阶段已验收。

## 目标与路径

- 目标：理解 `cc-ding/` 的完整能力，借鉴其运行链路，用原生 Python 实现基于 AstrBot 的 QQ 插件并分阶段补齐功能，保持模块化。
- 路径：重型路径（Heavy Route），依次进行对齐（Align）→ 计划（Plan）→ 开放规格（OpenSpec）→ 实施（Apply）→ 审查与验证（Review / Verify）→ 收尾（Close）。
- 当前阶段：`0.3.3` 已完成「回复媒体自动识别与发送」——显式 `[[image:]]` 之外，自动识别可信本地图片/视频路径与公网媒体 URL；含媒体回复不再整体转长图；新增 `auto_send_media` 开关。单测 181/181；真机 suite 12/12 通过（测试 bot `3299987672`），并显式跑通 `rc-draw-generate` 生成→发送。生产仍为 `0.3.2`，发布待用户决定。
- 新增产出：`2026-10-28-排查耗时分析与优化方案.md` 把「串行往返过多」量化为长耗时主因，并据此把流式输出的触发条件更新为已满足；该结论待用户决定是否提级。

## 下一步（Next Steps）

1. 决定是否发布 `0.3.3`：生成 ZIP、备份后覆盖生产与测试安装目录、重启并核对「已加载 v0.3.3」。
2. 真机补验：`auto_send_media=false` 回退、视频发送（需执行引擎视频断言或手工验证）。
3. `0.3.2` 遗留：群内 `@robot /start` 与私聊 >750 KB 图片读取复测。
4. Codex 侧同项真机验收（T05.10／T04.4／T04.5）仍待做。
5. 评估代理协议提示（system prompt / `initbase` 模板）是否与自动识别并存。

## 阶段门禁

- 先与用户讨论候选方案并取得对齐确认，再写对齐文档与计划。
- 计划落盘后才创建 `spec/proposal.md`、`spec/design.md`、`spec/tasks.md`。
- 三件套齐备后才修改插件代码。插件代码变更后的安装覆盖，以用户当次明确要求为准。
- 完成声明前取得新的验证证据。代码提交以用户当次明确允许为准；2026-09-30 两次收尾用户都要求先提交再写交接。

## 下一步

1. 决定是否发布 `0.3.3`：生成 ZIP、备份后覆盖生产与测试安装目录、重启并核对「已加载 v0.3.3」。
2. 真机补验：`auto_send_media=false` 回退、视频发送（需执行引擎视频断言或手工验证）。
3. `0.3.2` 遗留：群内 `@机器人 /start` 与私聊 >750 KB 图片读取复测。
4. 做 Codex 侧 0.2.5 同项真机验收（只读、工作区、完全权限），并补验 T03-M.4b、T04.4、T04.5。
5. 视需要处理 AstrBot 内置 `/new` 的遗留提示；评估代理协议提示是否与自动识别并存。
6. 评估第三个测试 QQ 账号、生产暂停自动化、@bot 空文本被 LLM 抢占（F2）。
