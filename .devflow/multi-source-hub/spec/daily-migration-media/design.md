# Metadata（元数据）

- 创建时间（Created At）：2026-09-22 00:00:00 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：定义路径投影、迁移和媒体队列技术边界。
- 关联仓库（Related Repository）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联提案（Related Proposal）：`.devflow/multi-source-hub/spec/daily-migration-media/proposal.md`。
- 当前状态（Status）：已批准实施（Approved for Apply）。
- 文档边界（Scope / Boundary）：本设计是本子变更技术真相源（Source of Truth）。

# 设计（Design）

`paths.py` 根据封套采集时间、平台、作品类型和标题计算目录；`Vault` 以该路径写入但 catalog 继续以 `item_id` 查询。`migration.py` 枚举旧封套，dry-run 输出源/目标/冲突，再原子移动和更新索引。媒体队列保存任务身份和 URL，worker 用 `ProxyHandler({})` 直连获取不超过 100 MiB 的任何媒体，再写入公共哈希库。
