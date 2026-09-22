# Metadata（元数据）

- 创建时间（Created At）：2026-09-22 00:00:00 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：定义子变更的模块边界、数据流和失败处理。
- 关联仓库（Related Repository）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联提案（Related Proposal）：`.devflow/multi-source-hub/spec/daily-collection-async/proposal.md`。
- 当前状态（Status）：已批准实施（Approved for Apply）。
- 文档边界（Scope / Boundary）：本设计是本子变更技术真相源（Source of Truth），不改变外层系统架构。

# 设计（Design）：可恢复日收集与后台媒体

## 总体思路

日收集账本（Daily Ledger）在 Vault 的 `spool/` 下按群和北京时间日期保存原始已解析消息与已完成 `message_id`。单一整理器读取尚未完成消息，生成确定性日 Item，成功 upsert 后才标记完成。手动命令和午夜调度都调用它。

媒体任务队列（Media Job Queue）持久保存待下载节点；检查插件在 Item 入库后只入队。一个生命周期 worker 以具名并发上限将阻塞下载转入线程，完成后重新 upsert 相同 Item。

## 结构与边界

- `daily.py`：日期计算、账本原子读写、待整理查询和完成标记；不依赖 AstrBot。
- `grouping.py`：把普通消息批量投影为日 Item；不处理文件 I/O 或调度。
- `media_jobs.py`：任务状态和 worker；不解析 QQ 事件。
- `collect.py`：协调 QQ 解析、规则分流、Vault 与两个基础模块。
- `main.py`：AstrBot 命令与定时生命周期；不持有业务状态。
- `bili_ingest.py`/`markdown.py`：内容节点与显示投影；不重新抓取 B 站数据。

## 数据流与接口

```text
事件 -> parse_onebot_message -> 会话/转发即时成条 | 日账本.append
@bot 整理 或 00:00 -> finalize_day -> Vault.upsert -> 日账本.mark_finalized
即时成条 -> MediaJobQueue.enqueue -> Worker -> persist_image_nodes -> Vault.upsert
既有 B 站 record -> record_to_fragment -> ContentNode -> render_content_md -> Vault.upsert
```

`finalize_day(conversation_id, day)` 是唯一生成日 Item 的入口。`enqueue(item_id, node_path, url)` 以 `(item_id, node_path, url)` 去重。worker 只有在 Vault 回写成功后将任务写为 `done`。

## 复用点

- 复用 `GroupingEngine` 的会话标记与转发处理，不复制规则。
- 复用 `Vault.upsert`、`persist_image_nodes`、`fetch_bytes` 与已有媒体哈希格式。
- 复用 B 站 `record_to_fragment` 与 `merge_work_envelope` 的作品合并身份。

## 风险与权衡

- 午夜循环必须可取消，避免插件卸载后残留任务；以生命周期任务统一管理。
- 日 Item 在第二次整理时仅包含新增未完成消息，避免改写已存在 item 的正文；同日可生成多个确定性批次 Item。
- 后台下载可能延迟显示本地图片，期间保留原 URL 和可观察的待处理状态。
