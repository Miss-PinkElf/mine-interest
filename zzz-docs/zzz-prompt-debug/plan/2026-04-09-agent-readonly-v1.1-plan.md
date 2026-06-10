# 2026-04-09 只读分析助手 v1.1 计划（Read-only Agent v1.1 Plan）

## 1. 当前基线（Current Baseline）

- 已完成：只读智能外层（Read-only Agent Sidecar）MVP
  - `POST /api/agent/plan`
  - `POST /api/agent/run`（默认 `dry_run=true`）
- 已确定：核心内核（Core）不改写，继续规则主链（rule-based core loop）。

## 2. 本轮目标（Goals）

- 在不新增执行能力（no execution）的前提下，提升只读输出质量（read-only output quality）。
- 固化“看得懂、可决策”的统一输出模板（Output Template）。
- 为下一阶段半执行（Semi-execution）准备清晰的门禁（Gates）。

## 3. 范围（Scope）

### 3.1 工具范围（Tool Scope）

- 仅使用 3 个只读工具（read_only tools）：
  1. `context_snapshot`（上下文快照）
  2. `memory_kernel_overview`（记忆内核总览）
  3. `heart_evaluate_preview`（主动关心预览）

### 3.2 输出结构（Output Structure）

- 固定四段输出：
  1. `Now`（当前状态）
  2. `Heart Decision Preview`（主动关心预览）
  3. `Evidence`（证据）
  4. `Next Actions`（下一步建议）

## 4. 非目标（Non-Goals）

- 不开放 `dry_run=false`
- 不新增写工具（write_safe tools）
- 不引入 Agent 框架迁移（LangChain/LangGraph migration）
- 不改 Core 规则触发逻辑（Heart rules, memory pipeline）

## 5. 验收标准（Acceptance Criteria）

- `plan/run` 返回内容满足四段结构，且字段含义稳定。
- 每次输出必须包含：
  - 当前是否可触发主动关心（triggered or not）
  - 未触发原因或触发原因（reason）
  - 至少 1 条具体证据（event/profile/note）
  - 2-3 条可执行建议（actionable next steps）
- 回退场景（fallback）下依然产出可读结果，不影响现有功能。

## 6. 风险与门禁（Risks & Gates）

- 风险：输出过技术化，用户难懂
  - 门禁：术语必须中文 + 英文（Chinese + English）
- 风险：LLM 输出不稳定
  - 门禁：保留规则回退模板（fallback template）
- 风险：越界到执行
  - 门禁：路由层继续强制 `dry_run=true`

## 7. 执行顺序（Execution Order）

1. 先讨论并确认四段输出模板细节（discussion only）
2. 再确认“证据排序规则”（evidence priority）
3. 确认后才进入 Apply（实施）
4. 实施后补测试并回写验证证据

## 8. 审批点（Approval Gate）

- 本计划通过后，下一轮先按讨论结论落地输出模板；仍遵守硬门禁：先 Plan 再 Apply。
