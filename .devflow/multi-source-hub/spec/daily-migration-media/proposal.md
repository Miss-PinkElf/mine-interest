# Metadata（元数据）

- 创建时间（Created At）：2026-09-22 00:00:00 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：定义全量日期目录迁移与直连媒体下载变更。
- 关联仓库（Related Repository）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联计划（Related Plan）：`.devflow/multi-source-hub/plans/2026-09-22-全量按天迁移与直连媒体实施-plan.md`。
- 当前状态（Status）：已批准实施（Approved for Apply）。
- 文档边界（Scope / Boundary）：本子规格是真相源（Source of Truth），不替代外层暂停规格。

# 提案（Proposal）

将 QQ 与 B 站资料按采集时间迁移至北京时间日目录，在每日 `content.md` 中提供索引；B 站子目录使用标题-ID。媒体下载扩展至图片、视频和附件，使用无代理直连且限制为 100 MiB。逻辑 Item 身份不变，迁移提供预演与原子执行。
