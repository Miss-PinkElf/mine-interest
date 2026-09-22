# Metadata（元数据）

- 创建时间（Created At）：2026-09-22 00:00:00 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：追踪本子变更实施和验证。
- 关联仓库（Related Repository）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联设计（Related Design）：`.devflow/multi-source-hub/spec/daily-migration-media/design.md`。
- 当前状态（Status）：首版完成（Completed First Version）。
- 文档边界（Scope / Boundary）：本文件是任务真相源（Source of Truth）。

# 任务（Tasks）

- [x] 路径投影与标题清理。
- [x] Vault 日期目录与每日索引。
- [x] 历史迁移 dry-run 与执行（初始 27 项、无冲突；另补迁移重载前写入的 2 条 QQ 转发）。
- [x] 100 MiB 直连媒体：QQ 图片和带直链文件走持久队列；B 站已解析视频播放流 URL 并下载。
- [x] 插件同步、版本、完整回归与 QQ 新目录真实验收。

## 延期说明（Deferred Scope）

- B 站下载仍在采集协程中执行，尚未接入持久媒体队列；详见 `../../deferred/按天归档与媒体首版未做.md`。
- QQ 最终目录尚未改为“日期 / message|forward|session / 条目”层级；当前为“日期 / items / 类型-ID”，需重新对齐后迁移。
