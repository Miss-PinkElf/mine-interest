# 代码注释与可读性实施计划

## Metadata（元数据）

- 创建时间（Created At）：2026-07-10 17:25:19 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：为当前已创建的前后端基础代码补充职责型注释，并将该规则写入仓库协作规范。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 当前状态（Status）：已完成（Completed）
- 文档边界（Scope / Boundary）：本计划只约束注释和可读性整理，不改变功能、API、领域模型或延期范围。

## 目标

让配置、环境入口、常量和函数的意图可快速扫描，同时避免逐行翻译式注释。

## 实施步骤

1. 修改 `backend/app/core/config.py`、`constants.py`、`main.py`、`domain/models.py` 与 `domain/enums.py`：为配置项、常量组、工厂函数和关键业务规则补充简短职责注释。
   - 验证：后端健康检查与领域模型测试通过。
2. 修改 `frontend/src/main.tsx`、`App.tsx` 与 `frontend/vite.config.ts`：为挂载入口、骨架组件、开发代理和常量补充简短职责注释，不增加 JSX 复杂度。
   - 验证：`npm run build` 通过。
3. 修改 `AGENTS.md`：增加“注释与可读性”规则，明确何时需要注释及禁止逐行解释。
   - 验证：检查规则覆盖函数、配置/环境变量、常量与可读性优先原则。

## 本轮不做 / 后续阶段

- 不为测试断言、枚举成员、数据类字段或 CSS 规则添加重复注释；原因是这些位置由命名与结构已能直接表达意图。
- 不重构领域模型或前端结构；后续只有在复杂度实质增加时再拆分模块。
