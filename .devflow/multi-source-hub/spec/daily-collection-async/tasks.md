# Metadata（元数据）

- 创建时间（Created At）：2026-09-22 00:00:00 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：追踪日收集、异步媒体和 B 站投影子变更的实施与验证。
- 关联仓库（Related Repository）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联设计（Related Design）：`.devflow/multi-source-hub/spec/daily-collection-async/design.md`。
- 当前状态（Status）：已完成（Completed）。
- 文档边界（Scope / Boundary）：本文件是当前子变更任务真相源（Source of Truth）。

# 任务（Tasks）

- [x] T1：以失败测试定义日账本、游标、重启恢复与手动/午夜无重复整理。
- [x] T2：实现日账本、日 Item 投影和检查插件命令/调度接入。
- [x] T3：以失败测试定义媒体持久队列、有限并发与失败恢复。
- [x] T4：实现媒体队列并替换无上限下载任务。
- [x] T5：以失败测试定义专栏/动态结构化节点与 Markdown 投影。
- [x] T6：实现 B 站投影和已有档案 Vault 回填。
- [x] T7：同步插件内置包并运行全量离线回归。

## 验证（Verification）

- QQ 日收集、媒体队列、B 站投影新增测试通过；2026-09-22 全量离线回归 75 项通过。
- 两插件已同步、递增至检查器 0.5.4 / B 站 0.2.4，并在本机 AstrBot 重载。
- QQ 新转发实测按日期入库；重载前旧路径的 2 条遗漏已通过迁移器补齐。
