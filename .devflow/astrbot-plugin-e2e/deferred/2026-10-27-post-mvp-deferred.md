# 第一版之后延期项（Post-MVP Deferred）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 22:29:58 CST。
- 更新时间（Updated At）：2026-10-27 22:40:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录第一版完成后明确延期、后续应继续的能力与触发条件。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：延期（Deferred），不是永久放弃。
- 文档边界（Scope / Boundary）：延期项真相源；未决问题与首版限定见 `../backlog.md`。

## 暂不做的对象

| 对象或能力 | 本轮不做的原因 | 后续触发条件或推荐阶段 |
| --- | --- | --- |
| `cc_qq` 长任务（`/new`、`/cc`、`/end`） | 耗时长、涉及 Claude/Codex 会话与工作目录清理；首版先验证 Runner 闭环 | Runner 稳定后，单独设计长任务用例与超时/清理策略 |
| 审批流程（`/approve`、`/deny`） | 依赖长任务与超时控制 | 长任务用例稳定后单独设计 |
| 多轮对话与上下文断言 | 首版只支持单步 send/expect | 用例模型引入 `steps` 后实现 |
| 富媒体（图片/文件/语音/引用） | NapCat native addon 警告；文本链路优先 | 先解决 native addon/签名问题，再扩展消息段 |
| WebUI 页面 | 首版 CLI 足够 | 有可视化需求时再评估 |
| CI 集成 | 依赖双开环境与人工登录 | 本地稳定后，再评估自托管 Runner |
| 并行用例 | 测试实例与 QQ 通道单实例，易互相干扰 | 串行稳定后，再评估多实例池 |
| 更深配置/用例形状校验 | 首版只校验外层结构与必填项 | 见 `2026-10-27-config-validation-deferred.md` 与 `2026-10-27-case-validation-deferred.md` |
| 自动扫码登录 | QQ 风控与人工确认 | 不承诺自动化；保持人工登录 |
| 测试实例常驻与 6198 重试日志 | 用例结束后 Runner 会停止测试实例；生产 bot 的 6198 客户端会重试 | 若需要常驻，使用 `start-instance`；若要彻底静默，可禁用生产 bot 的 `AstrBot-E2E` 客户端（需备份并重启生产 QQ） |
| 生产 bot 的 E2E 客户端清理 | 保留用于后续测试 | 若不再测试，按备份恢复 `onebot11_3254276668.json` 并重启生产 QQ |

## 触发条件

- 用户明确要求进入下一阶段，或 `state.md`/`NEXT-SESSION-PROMPT` 指向对应项。
- 出现 native addon/富媒体需求时，先做独立技术验证，不要直接扩展 Runner。
- 若要接入 CI，先确认测试实例、QQ 登录与测试群的稳定运行方式。

## 与未决问题、首版限定的边界

- 本文件只记录**明确延期**的能力：已判断本轮不做、后续要做，且有触发条件。
- **未决问题**（例如生产 bot 是否长期兼任测试机器人、`6198` 客户端是否保留、报告脱敏策略）见 `../backlog.md` 的 Q1–Q10；它们尚未形成批准结论。
- **首版限定**（CLI、单发单断言、串行、单群、文本、人工登录、macOS）见 `../backlog.md`；不是延期项，是否扩展由后续需求决定。

## 恢复原则

- 不把“本轮不做”写成永久放弃。
- 每次恢复先读 `state.md`、`checkpoints.md`、最新 handoff，再决定进入哪个延期项。
