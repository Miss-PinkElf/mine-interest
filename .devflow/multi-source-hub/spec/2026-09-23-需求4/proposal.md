# Metadata（元数据）

- 创建时间（Created At）：2026-09-23 15:33:49 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：定义需求 4 的目标、范围和异常边界。
- 关联仓库（Related Repository）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38 行。
- 关联对齐（Related Align）：`../../plans/2026-09-23-QQ目录直连重试与安全自动推送-align.md`。
- 关联计划（Related Plans）：`../../plans/2026-09-23-QQ标题分层目录迁移-plan.md`、`../../plans/2026-09-23-直连下载重试与历史补救-plan.md`、`../../plans/2026-09-23-Vault安全自动发布-plan.md`。
- 当前状态（Status）：首版已实现，真实运行验收待完成（Implemented; Runtime Verification Pending）。
- 文档边界（Scope / Boundary）：本子变更的规格真相源（Source of Truth）；只覆盖需求 4。

# 需求 4 提案（Proposal）

## 背景

QQ 条目仍位于 `日期/items/类型-ID`；B 站与 QQ 虽已默认直连，但缺少统一的最多 5 次重试和历史失败补救；Vault 只有本地 Git 提交，尚不能安全自动推送。

## 目标与范围

1. 所有新旧 QQ 条目进入 `日期/message|forward|session/标题-ID`，稳定逻辑 ID、catalog 和每日索引保持可用。
2. 媒体下载默认不走系统代理；可恢复错误最多尝试 5 次；给历史 B 站失败图片提供幂等补救入口；保存可取得的 B 站播放流 MP4。
3. 资料更新后自动发布允许的 Markdown、索引和非敏感元数据到指定私有远端，使用独立 Git 历史。

## 非目标

不接入模型判断（LLM Judgment）决定下载重试；不推送现有 Vault Git 历史、原始封套、Cookie、快照、数据库、日志或媒体；不做链接筛选、显式代理配置及 B 站持久媒体队列。

## 边界场景

迁移目标冲突时整体停止；下载超限或主机不被允许时不重试；远端未证明私有、敏感内容检查失败或普通推送非快进时保留本地待发布状态，不影响采集。

## 开放问题

匿名 GitHub API 返回 404 且 SSH 可读取目标仓库，私有性核验已通过；首次真实推送及 AstrBot 新消息端到端（End-to-End）验收尚未完成。播放流首版取现有接口返回的单段 MP4，多分段、画质选择及断点续传另行对齐。
