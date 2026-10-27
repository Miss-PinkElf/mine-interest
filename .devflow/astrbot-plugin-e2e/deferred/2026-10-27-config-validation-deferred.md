# 配置校验延期项（Config Validation Deferred）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 18:30:00 CST。
- 更新时间（Updated At）：2026-10-27 18:30:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录 Task 1 代码质量审查中识别、但本轮不做的配置校验增强项与后续触发条件。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：延期（Deferred），不是永久放弃。
- 文档边界（Scope / Boundary）：延期项真相源；不代表 Task 1 验收失败。

## 暂不做的对象

1. **生产根包含关系判断**
   - 当前只判断 `test_root == ~/.astrbot`，不判断 `test_root` 是否包含生产根（例如 `test_root=~` 会被接受）。
   - 相关代码：`tools/astrbot_e2e/config.py` 的 `validate_config`。

2. **OneBot URL scheme 校验**
   - 当前只校验 host 与端口，`http://127.0.0.1:6200/...` 也会被接受。
   - 相关代码：`tools/astrbot_e2e/config.py` 的 `_url_port`。

3. **四个端口互异性校验**
   - 当前只检查是否命中生产端口，不检查 `webui.port`、`astrbot.reverse_ws_port`、`bot.onebot_ws`、`sender.onebot_ws` 之间是否重复。

## 本轮不做的原因

- 三项都不在 Task 1 的验收范围内，属于防御性增强。
- 当前任务不会按 `test_root` 递归清理或删除目录，生产根“包含关系”风险尚未触发。
- OneBot scheme 与端口互异可以在 Task 6/7 建连与实例编排时自然暴露，届时补校验更有针对性。
- 避免在 Task 1 扩大范围，保持配置模块的最小可用。

## 当前已有思路

- 生产根包含：在 `validate_config` 中增加 `PRODUCTION_ROOT.is_relative_to(test_root)`（或反向判断）并拒绝 `test_root` 为 `~`、`/`、`PRODUCTION_ROOT` 的父目录。
- Scheme：要求 `parsed.scheme in {"ws", "wss"}`。
- 端口互异：`len(set(ports.values())) != len(ports)` 时抛 `ConfigError`。

## 后续触发条件

- **Task 7/8 前**：开始按 `test_root` 清理或重建测试实例数据前，必须补生产根包含判断，避免误删生产目录。
- **Task 6 前**：OneBot 客户端正式建连前，补 scheme 校验或至少在建连失败时给出明确错误。
- **Task 7 前**：测试实例编排开始使用多个端口前，补端口互异校验。

## 推荐进入阶段

- Task 6（OneBot）与 Task 7/8（Bootstrap / Orchestrator）开始前，逐项评估并决定是否提前实现。
- 若在 Apply 过程中发现任何一项风险被触发，立即停止并回到本文件对应项，不要静默跳过。

## Task 1 代码质量复审新增（2026-10-27）

| 对象 | 本轮不做的原因 | 后续触发条件 |
| --- | --- | --- |
| 畸形 URL 的 `urlparse` `ValueError` 未包装 | 正常配置不会出现；不影响合法配置的校验结果 | 下次触碰 `_url_port`，或 Task 6 OneBot 建连前 |
| 相对 `test_root` 的解析基准（当前按进程 CWD） | 当前配置使用绝对路径或 `~`；风险低 | Task 7 开始按 `test_root` 清理前确定，并在示例/文档写明 |
| `test_root` 在 `load_config` 与 `validate_config` 重复归一化 | 幂等无害；属于 DRY 细节 | 下次触碰 config 时收敛到 `validate_config` |
| 测试中的 `assertRaisesRegex` 中文文案耦合 | 当前错误信息即用户体验；保留少量文案契约可接受 | 后续重构错误文案时再调整 |
