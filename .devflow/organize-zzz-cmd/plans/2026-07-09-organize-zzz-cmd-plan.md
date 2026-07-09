# zzz-cmd 文档整理 Implementation Plan（实施计划）

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans or inline execution to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## Metadata（元数据）

- 创建时间（Created At）：2026-07-09 15:23:15 CST
- 作者（Author）：Codex
- 目的（Purpose）：为 `zzz-cmd.md` 分类整理提供轻量实施计划。
- 关联仓库或项目（Related Repository / Project）：mine-interest
- 关联 mission（Related Mission）：organize-zzz-cmd
- 当前状态（Status）：已完成（Completed）
- 文档边界（Scope / Boundary）：这是本轮已确认的实施计划（Plan），会触发对 `zzz-cmd.md` 的结构整理；不是长期命令规范。
- 关联原始需求（Related Raw Request）：`zzz-cmd.md` 文档整理，分门别类，不变动原文。

**Goal:** 整理 `zzz-cmd.md`，让命令、提示词、验证要求和工具入口按类别可扫描。

**Architecture:** 不引入新工具或脚本，只在 Markdown（Markdown）层面增加标题与分类。已有正文内容保持原文字面表达，不做语义改写。

**Tech Stack:** Markdown（Markdown）、Git diff（差异检查）。

---

## 文件结构

- 修改：`zzz-cmd.md`
  - 责任：承载常用命令、提示词、验证要求与工具入口。
- 创建/维护：`.devflow/organize-zzz-cmd/*`
  - 责任：记录本轮轻量 devflow（开发流程）过程、计划与决策。

## 分类方案

1. Agent / CLI 启动与权限参数。
2. 初始化脚本与本地开发入口。
3. Electron 下载链接与沙箱配置。
4. devflow / handoff 收尾提示词。
5. 怠惰相关固定提示词。
6. 验证与测试要求。
7. React / TSX apply 提示词。
8. 知识总结文档提示词。
9. Quick Test 页面想法。
10. OpenClaw 网关命令。

## 任务

### Task 1: 整理 Markdown 分类

**Files:**

- Modify: `zzz-cmd.md`

- [x] **Step 1: 新增文档标题与分类标题**

  在现有文本外层增加 `#`、`##` 或 `###` 标题，让内容按用途分组。

- [x] **Step 2: 保留原文内容**

  不修改已有命令、URL、提示词、编号、错别字或代码块内容。

- [x] **Step 3: 查看差异**

  Run: `git diff -- zzz-cmd.md`

  Expected: diff 只体现新增标题、分类与必要空行；没有原文语义改写。

### Task 2: 更新 mission 状态

**Files:**

- Modify: `.devflow/organize-zzz-cmd/state.md`
- Create: `.devflow/organize-zzz-cmd/checkpoints.md`

- [x] **Step 1: 标记计划完成并进入验证**

  更新 `state.md` 中的阶段状态。

- [x] **Step 2: 写入 checkpoint（检查点）**

  记录本轮整理完成、验证方式与是否存在延期项（Deferred Scope）。
