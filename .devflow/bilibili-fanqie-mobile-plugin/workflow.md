# 当前工作流（Workflow）

## Metadata（元数据）

- 更新时间（Updated At）：2026-10-11 12:03:00 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：区分既有实现状态与本轮探索的后续门禁。
- 关联仓库或项目（Related Repository / Project）：mine-interest-bilibili。
- 关联任务（Related Mission）：`.devflow/bilibili-fanqie-mobile-plugin/`。
- 关联输入：`origin.md`；新探索为 `zzz-prompt-debug/下载番茄b站/prompt-1.md`。
- 当前状态（Status）：探索交接；新方案待对齐，整体未关闭。
- 文档边界（Scope / Boundary）：滚动流程快照，不替代 `plans/` 和 `spec/`。

## 当前路径

```text
既有 Android：对齐 → 计划 → 规格 → 源码落地 → 部分用户验证
                                              → BUG-001 / 其余验证待续
本轮番茄：探索 → 源码核对 / 结论修正 → 总结 / 交接
                                    → 下会话讨论首版 → 计划 → 规格 → 实施 → 验证
```

- 分支：`rin-bilibili-fanqie-mobile/dev`。
- 本轮没有新的批准计划，没有更新原规格任务的实现状态。
- 第一版载体和正文获取方式未定；原 Official-API / 搜索等延期保持，探索允许重新评估，不能自动恢复实施。
- 本次收尾只完成研究记录和会话交接，不能宣布整个任务关闭（Close）。

## 门禁与恢复

先读 `state.md`、`checkpoints.md`，按需读独立总结和最新交接。新需求确认后完成计划（Plan）再实施（Apply）。只提交本轮相关文件；本轮用户已明确授权直接提交推送，无需再次确认。
