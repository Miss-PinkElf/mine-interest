# 2026-04-09 Agent Sidecar MVP 计划（Plan）

## 1. 背景（Background）

- 当前桌宠后端已经有稳定内核（Core）：
  - 观察记录（Observation）
  - 信号层（Signal）
  - 事件层（Event）
  - 画像/关系（Profile/Relationship）
  - 主动关心（Heart / Proactive Care）
- 当前诉求是：在不推翻 Core 的前提下，引入智能外层（Agent Layer），让系统具备“规划（Planning）+ 工具调用（Tool Calling）+ 总结（Summarization）”能力。

## 2. 目标（Goals）

- 新增只读分析助手（Read-only Analysis Agent）最小能力：
  - `POST /api/agent/plan`：产出计划（plan）与建议工具（suggested_tools）
  - `POST /api/agent/run`：默认 `dry_run=true`，产出工具调用轨迹（tool_trace）和最终总结（final_summary）
- 保持核心内核（Core）完全不改写：
  - 规则链继续作为主决策来源（rule-based primary path）
- 失败可回退（fallback）且不影响现有功能：
  - 聊天（Chat）
  - 记忆内核（Memory Kernel）
  - 主动关心（Heart）

## 3. 非目标（Non-Goals）

- 不做自动执行（autonomous execution）
- 不做高风险系统操作（high-risk actions）
- 不做 Agent 全量接管 Core（no full agent takeover）
- 不在本轮接入向量检索（vector retrieval）或外部记忆框架（external memory framework）

## 4. 方案对比（Approaches）

### 方案 A：只读侧挂（Read-only Sidecar）【推荐】

- Agent 只读取上下文（context）、记忆内核总览（memory-kernel overview）、主动关心预览（heart preview）
- 不触发写入，不触发行为执行
- 优点：风险最低、可快速验收、可解释性强
- 缺点：短期“执行能力”不足

### 方案 B：半自动执行（Semi-automatic Execution）

- 在 A 基础上加入有限写工具（write-safe tools）
- 优点：实用性更高
- 缺点：需要权限系统与回滚机制，复杂度上升

### 方案 C：全量 Agent 接管（Full Agent-native）

- Core 决策转为 Agent 工作流
- 优点：理念统一
- 缺点：交付风险最高，不符合当前稳定性目标

## 5. 本轮范围（Scope）

- 新增协议（Agent Schema）
- 新增工具注册表（Tool Registry）
- 新增协调器（Agent Coordinator）
- 新增路由（Agent Route）
- 接入服务装配（Service Wiring）
- 补测试（Tests）与门禁（Guards）

## 6. 验收标准（Acceptance Criteria）

- 接口可用：
  - `POST /api/agent/plan` 返回 `plan/suggested_tools/final_summary`
  - `POST /api/agent/run` 返回 `tool_trace/final_summary`
- 默认安全：
  - `dry_run=true` 默认开启
  - `dry_run=false` 直接拒绝（422）
- 可观测：
  - 返回 `request_id`
  - 返回 `used_fallback/errors`
- 回退稳定：
  - LLM 不可用时，走规则回退计划（fallback plan）

## 7. 执行步骤（Execution Steps）

1. 定义 Agent 请求/响应协议（Schema）
2. 实现只读工具注册表（Tool Registry）
3. 实现协调器（Coordinator）：
   - LLM 规划
   - JSON 解析
   - 回退策略
4. 实现路由（Route）与 `dry_run` 门禁
5. 接入 `AppServices` 与 `main.py` 路由注册
6. 编写测试：
   - 协调器测试（coordinator tests）
   - 路由测试（route tests）
7. 运行验证并记录结果

## 8. 风险与回退（Risks & Fallback）

- 风险：LLM 返回非 JSON
  - 回退：使用本地规则计划（fallback plan）
- 风险：工具调用超时或异常
  - 回退：记录 error，跳过该工具，继续输出可解释结果
- 风险：误开启执行能力
  - 回退：路由层强制 `dry_run=true`，拒绝非 dry-run

## 9. 本轮输出物（Deliverables）

- Agent Schema（协议文件）
- Agent Coordinator（协调器）
- Agent Tool Registry（只读工具注册）
- Agent Route（调试路由）
- 装配接入（wiring）
- 测试与验证证据

## 10. 审批点（Approval Gate）

- 本计划通过后，才进入后续 Apply（实施）与下一阶段能力扩展。
