# AstrBot 与 NapCat 终端联启工作流

## Metadata（元数据）
- 创建时间（Created At）：2026-10-01 14:20:00 UTC。
- 更新时间（Updated At）：2026-10-01 14:36:39 UTC。
- 作者（Author）：Codex。
- 目的（Purpose）：管理跨 macOS 与 WSL 的终端联启需求。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-napcat-terminal/`。
- 原始需求（Raw Input）：`zzz-prompt-debug/prompt-2.md`。
- 当前状态（Status）：已暂停（Paused），对齐（Align）未完成。
- 文档边界（Scope / Boundary）：工作流真相源（source of truth）；不代表方案或实施已获批准。

## 路径与门禁
- 用户选择暂时维持现有桌面部署；本轮收口为调研交接，不是功能交付或整个任务完成。
- 使用轻量路径（Light Path）：调研 → 轻量对齐（Mini Align）→ 落盘计划（Plan）→ 任务定义（Tasks）→ 实施（Apply）→ 验证（Verify）。
- 先确认部署组合和“两端一起运行”的含义，再编写联启脚本。
- 不改插件代码、不覆盖应用、不迁移或改写现有配置、不启动第二个机器人实例。
- 批准后再判断是否需要将路径升级为完整规格（OpenSpec）。
- 下次仅在用户明确恢复此任务后继续；没有实施计划或任务定义，不得将候选文档所在的 `plans/` 目录误当作计划门禁已通过。
