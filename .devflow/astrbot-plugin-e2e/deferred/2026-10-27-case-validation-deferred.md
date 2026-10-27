# 用例值形状校验延期项（Case Shape Validation Deferred）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 20:32:00 CST。
- 更新时间（Updated At）：2026-10-27 20:32:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录 Task 2 质量复审识别、但本轮不做的更深值形状校验项与后续触发条件。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：延期（Deferred），不是永久放弃。
- 文档边界（Scope / Boundary）：延期项真相源；不代表 Task 2 验收失败。

## 暂不做的对象

1. **`expect.messages` / `expect.logs` 元素内部形状**
   - 当前只保证存在且是非空 list，不校验每个元素是否为含 `contains` / `regex` 的 dict。
   - 相关代码：`tools/astrbot_e2e/cases.py` 的 `validate_case`。
   - 后续消费方：Task 3 `assertions.py`、Task 12 `runner.py`。

2. **`expect.timeout_seconds` 类型与范围**
   - 当前不校验是否为数字、是否大于 0。
   - 相关代码：`cases.py` 与 Task 12 `runner.py` 的 timeout 读取。

3. **`send.group_id` 类型**
   - 当前只要求 `send.text` 非空；`group_id` 允许任意类型/占位符。
   - 后续 `runner.py` 会做 `int(send["group_id"])`，非法值会在运行时失败。
   - 相关代码：`cases.py`、Task 12 `runner.py`。

4. **`expect.semantic` 内部字段**
   - 当前只要求 `semantic` 存在且是 dict，不校验 `enabled` 是否 bool、`criteria` 是否非空字符串。
   - 后续消费方：Task 11 `llm_judge.py`、Task 12 `runner.py`。

## 本轮不做的原因

- Task 2 的验收范围是“用例结构白名单 + 必填项 + 占位符渲染”，更深的值形状属于断言层与运行层的职责。
- Task 3 会定义 `contains` / `regex` 断言的实际结构，届时在校验层与断言层之间确定边界更合适。
- 避免在 Task 2 过度校验，把未来可能演进的断言结构提前写死。

## 当前已有思路

- 在 `assertions.py` 的断言求值入口对 spec 做一次运行时结构校验，非法结构抛 `AssertionError` 或返回 `ERROR`，不要静默跳过。
- 在 `runner.py` 发送前校验 `group_id` 可转为整数、`timeout_seconds` 为正数。
- 在 `llm_judge.py` 调用前校验 `semantic.enabled` 与 `criteria`。

## 后续触发条件

- **Task 3（断言模块）开始前/中**：确定 `messages`/`logs` 元素的合法结构，并决定是否前移到 `cases.py`。
- **Task 6（OneBot）建连前**：确认 `send.group_id` 的归一化策略。
- **Task 11（LLM 判定）开始前**：校验 `semantic` 内部字段。
- **Task 12（Runner）开始前**：统一处理 timeout 与非法值的 `ERROR` 退出码。

## 推荐进入阶段

- Task 3、Task 11、Task 12 开始前逐项评估；若任一风险被实际触发，立即停止并回到本文件对应项，不要静默跳过。
