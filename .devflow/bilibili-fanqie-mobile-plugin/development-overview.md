# 开发与探索总记录（Development Overview）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-11 12:03:00 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：连接原 Android 开发与本轮番茄公开方法探索，提供完整过程入口。
- 关联仓库或项目（Related Repository / Project）：mine-interest-bilibili。
- 关联任务（Related Mission）：`.devflow/bilibili-fanqie-mobile-plugin/`。
- 原始输入：`origin.md`；本轮 `zzz-prompt-debug/下载番茄b站/prompt-1.md`。
- 当前状态（Status）：既有实现待补验证；新目标探索已记录，首版待对齐。
- 文档边界（Scope / Boundary）：长期脉络记录，当前态以 `state.md` 为准；不代替批准计划及规格。

## 阶段脉络

| 阶段 | 目标与结果 | 追溯入口 |
| --- | --- | --- |
| 2026-08-07 对齐（Align）与计划（Plan） | Kotlin 原生 Android 单 App；链接解析、B站导出、番茄自配正文到 TXT；正式计划及规格落盘 | `plans/`、`spec/`、交接 001 |
| 2026-08-07 实施（Apply）及验证（Verify） | 源码落地；B站下载 / 保存目录获用户确认；仍有音量 BUG-001，完整门禁未全部关闭 | 交接 002 / 003、`bug-log.md` |
| 2026-08-07 范围延期 | Official-API、搜索、零配置正文等延期；当时优先 B站 | D018、`deferred/番茄-Official-API与搜书名零配置正文.md` |
| 2026-10-11 重新探索（Explore） | 用户希望理解下载全过程并复用到软件或 CLI；补查 11 仓库，纠正历史源码遗漏；第一版未批准 | 独立总结、四份调研、交接 004 |

## 对长期理解的变化

“缺少底层正文依赖”不能概括为“没有公开下载思路”。本轮已找到网页还原公开实现、POf-L 历史 CLI，以及 Tomato 当前公开下载编排。需要选择正文来源并实际验证，才能判断哪种方案适合新目标。

原 App 的阶段范围仍保留；新的 CLI 候选没有替换原批准规格。下会话需要明确是新增工具阶段还是扩展 App，再建立对应计划。待讨论和后续阶段见 `deferred/番茄下载探索待讨论与后续阶段-2026-10-11.md`。

## 完整调查入口

`番茄小说下载探索与本次对话总结-2026-10-11.md` 是本轮详细汇总，含完整流程、源码版本表、登录书架证据、验证边界及首版问题。默认恢复只读 `state.md` 与 `checkpoints.md`，需要背景再读总记录和总结。
