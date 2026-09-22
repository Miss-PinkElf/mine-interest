# Metadata（元数据）

- 更新时间（Updated At）：2026-09-22 18:35:00 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：为下一次对话提供短恢复入口和明确的未完成边界。
- 关联仓库（Related Repository）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 最新交接（Latest Handoff）：`handoffs/2026-09-22-007-按天归档与直连媒体首版.md`。
- 当前状态（Status）：等待下一阶段对齐（Awaiting Align）。
- 文档边界（Scope / Boundary）：恢复入口；不自动授权实施（Apply）。

# 下一次对话提示词

请恢复 `.devflow/multi-source-hub/`。默认先读 `state.md` 与 `checkpoints.md`，再读：

`.devflow/multi-source-hub/handoffs/2026-09-22-007-按天归档与直连媒体首版.md`

需要理解整体演进时再读 `development-overview.md`；所有明确延期先读 `deferred/按天归档与媒体首版未做.md`。

## 已完成且无需重做

- QQ 当天总文档实时扩充，`@bot 整理` 与午夜整理不会重复成条。
- QQ / B 站按采集日归档；历史 27 项和后续发现的 2 条旧路径 QQ 转发均已迁移，真实 Vault 预演剩余 0。
- QQ 媒体默认 100 MiB 直连队列；B 站可解析视频播放流 URL；插件已重载为检查器 0.5.4、B 站 0.2.4。
- 全量离线回归 75 项通过。

## 未完成 / 必须先讨论

1. QQ 最终目录要不要改成 `日期/message|forward|session/条目`。当前实现是 `日期/items/类型-ID`，不能静默当作符合最新需求。
2. B 站下载要不要接入持久媒体队列（Media Job Queue），以避免大媒体阻塞轮询。
3. 链接筛选与格式化：需要确认 GitHub、Gitee、百度网盘、夸克网盘等首批规则和输出样式。
4. 自动推送到 `git@github.com:Miss-PinkElf/data-hub.git`：先确认访问、私有资料范围、媒体策略和失败重试。

## 注意

- 不要提交 Cookie、真实快照或 `sourcehub-image-urls.json`。
- 不要开始外层 14 项信息中心任务。
- 改动插件运行文件时同步递增 `metadata.yaml` 与注册版本，并同步到本机插件目录后重载。
