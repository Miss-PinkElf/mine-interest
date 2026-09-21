# Metadata（元数据）

- 创建时间（Created At）：2026-09-21 15:51:15 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：记录 B 站只读采集首版不做、以及还可选实测的项目。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联计划（Related Plan）：`.devflow/multi-source-hub/plans/2026-09-21-B站只读提及采集-plan.md`。
- 关联说明（Related Note）：`.devflow/multi-source-hub/qq-bilibili-capability-boundary.md`。
- 当前状态（Status）：延期（Deferred），非永久放弃。
- 文档边界（Scope / Boundary）：延期真相源。不代表已批准下一轮实现。

# B 站首版未做与可选实测

首版目标是：收到 @ 后采集评论关系和作品原文，不公开回复。下列项目本轮明确不做或未测完。

## 首版明确不做（后续阶段）

| 暂不做 | 原因 | 后续触发 |
| --- | --- | --- |
| 扫码登录（QR Login）与 Cookie 自动刷新 | 首版只支持本地填写 `SESSDATA`/`buvid3` | 登录经常过期或用户要求降低填写成本时 |
| 自动批量下载视频文件 | 首版只保存页面链接、标识和简介 | 用户确认体积、清理和下载器策略后单独计划 |
| 发送者白名单 | 未讨论；当前谁 @ 都采 | 出现噪音或需要限制来源时 |
| 弹幕、私信、点赞、回复我的 | 入口只是 `/x/msgfeed/at` | 用户扩展通知类型时 |
| 用完整 BiliBot 自动回复代替采集 | 职责冲突，已禁止 | 不作为后续方向 |

工程默认值（停用、120 秒、50 MiB、不清理）仍是工程默认，不是用户确认的长期策略。

## 可选实测（代码已有，线上未覆盖）

详见 `qq-bilibili-capability-boundary.md` 的 B1–B10。优先：

- 专栏里回复已有评论再 @（父/根）
- 动态里回复子评论再 @
- @ 带附言的转发动态
- 纯图片动态、评论配图、分 P 视频、删评、过期 Cookie、重复轮询、网络中断恢复

这些不是永久放弃，用户随时可测；测完对照 `content.md` / `record.json`，不要把 Cookie 发到聊天。
