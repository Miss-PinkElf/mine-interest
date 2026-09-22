# Metadata（元数据）

- 创建时间（Created At）：2026-09-22 00:00:00 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：定义 QQ 日收集与异步媒体子变更的业务范围。
- 关联仓库（Related Repository）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联计划（Related Plan）：`.devflow/multi-source-hub/plans/2026-09-22-QQ日收集与异步媒体实施-plan.md`。
- 当前状态（Status）：已批准实施（Approved for Apply）。
- 文档边界（Scope / Boundary）：本子规格是真相源（Source of Truth）；不覆盖 `.devflow/multi-source-hub/spec/tasks.md` 中暂停的外层任务。

# 提案（Proposal）：日收集、异步媒体与 B 站可读投影

## 背景

QQ 表情包会话收口时同步下载图片，曾长期占用事件循环，造成 B 站轮询超时。普通 QQ 消息目前逐条成条，无法形成用户期望的“当天持续收集、统一整理”。B 站专栏和动态已采集，但 Vault 的 Markdown 缺少内容结构。

## 目标

- 普通 QQ 消息按北京时间日收集，并由手动整理或午夜任务无重复成条。
- 媒体下载移到可恢复、有限并发的后台工作路径。
- B 站专栏和动态在 Vault 中可按内容结构阅读，并可回填已有档案。

## 范围

- QQ 日账本、单一整理器、`@bot 整理` 和午夜触发。
- 转发和标记会话保留独立 Item 行为。
- 媒体任务的持久状态、失败缺口与后台下载。
- B 站专栏/动态的结构化内容节点与 Markdown 投影。

## 非目标

- 知识整理（Knowledge Organization）、标签、摘要、模型判断。
- 外层 14 项服务/API/权限体系。
- 自动提交或推送开发仓库。

## 边界场景

- 同一日消息被手动与定时任务同时整理时，稳定 `message_id` 只允许一次成条。
- 插件重启后保留日账本与未完成媒体任务。
- 图片下载失败保留 URL 和缺口，不阻塞后续任务。
- 午夜时没有新消息也必须可处理前一天未整理内容。

## 开放问题

无。用户已确认按 `Asia/Shanghai` 的每日 00:00 整理。
