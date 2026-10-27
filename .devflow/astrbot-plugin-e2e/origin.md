# 原始输入索引（Origin）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 16:47:08 CST。
- 更新时间（Updated At）：2026-10-27 22:40:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录当前 mission 的原始提示词、需求草稿与参考文件来源。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：持续追加。
- 文档边界（Scope / Boundary）：来源索引；不是需求规格（Spec）或实施计划（Plan）。

## 定位

本文件记录当前 mission 的原始提示词、需求草稿和参考文件来源。它允许追加，不是冻结文件。

## 来源列表

| 序号 | 来源路径 | 时间 | 用途 | 吸收状态 |
| --- | --- | --- | --- | --- |
| 1 | `zzz-prompt-debug/插件自动化测试验证/prompt-01.md` | 2026-10-27 | 初始需求：AstrBot 插件自动化测试验证 | 已吸收，第一版完成 |
| 2 | `.devflow/astrbot-napcat-terminal/` | 2026-10-01 | 终端联启调研与候选方案（已暂停） | 已参考，不直接沿用为已批准方案 |
| 3 | `.devflow/multi-source-hub/bug-log.md` | 2026-09-20 至 2026-10-01 | 机器人自身消息上报问题、NapCat `reportSelfMessage` 相关记录 | 已参考，作为风险输入 |
| 4 | `.devflow/cc-qq-full-migration/` | 2026-09-30 起 | cc_qq 插件迁移与测试记录 | 已参考，作为被测插件的背景 |
| 5 | `devflow-handoff.md` | 2026-09-09 | 收尾流程指导（回顾、更新 devflow 文档、生成下次提示词） | 已执行，按用户要求未修改 |

## 备注

- 优先记录相对路径。
- 原始 prompt 已在仓库文件中时，不强制复制全文。
