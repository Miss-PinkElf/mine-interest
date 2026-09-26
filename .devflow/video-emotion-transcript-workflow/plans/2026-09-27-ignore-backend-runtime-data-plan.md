# 忽略后端运行数据计划（Plan）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-27 01:25:29 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录 `backend/data/` 忽略规则的最小对齐（Mini Align）、实施步骤和验收方式。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联文件（Related File）：`.gitignore`、`backend/data/`
- 当前状态（Status）：已完成（Completed），2026-09-27 已验证；用户后续明确授权提交。
- 文档边界（Scope / Boundary）：本轮轻量计划真相源；不授权删除运行数据。提交授权来自用户后续明确消息。

## 最小对齐（Mini Align）

- 目标：本地任务数据库（SQLite）和任务产物不再出现在 Git 未跟踪文件列表中。
- 已确认：`backend/data/` 目前没有 Git 已追踪文件；用户明确要求加入 `.gitignore`。
- 边界：保留现有数据，不改变任务运行和数据存储路径。

## 任务与验收

1. 在 `.gitignore` 中用 `backend/data/` 替换已有的子目录规则 `backend/data/perception/`。验证：`git check-ignore` 命中数据库与产物。
2. 查看 `git status --short` 和 `git diff --check`。验证：`backend/data/` 不再作为未跟踪目录出现，其他工作区改动保持原状。

## 验证结果

- `git check-ignore -v` 命中 `backend/data/jobs.sqlite` 与任务导出文件。
- `git status --short` 不再显示 `backend/data/`；`git diff --check` 通过。
