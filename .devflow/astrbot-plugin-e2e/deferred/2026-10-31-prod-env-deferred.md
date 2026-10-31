# 生产环境一键脚本延期项（2026-10-31）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-31 22:55:00 CST。
- 更新时间（Updated At）：2026-10-31 22:55:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录 `tools/prod_env/` 首版未做、后续可能需要的能力与触发条件。
- 关联仓库或项目（Related Repository / Project）：当前仓库 `.`。
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 关联计划（Related Plan）：`../plans/2026-10-31-生产环境一键启动脚本-plan.md`。
- 当前状态（Status）：延期（Deferred），不是永久放弃。
- 文档边界（Scope / Boundary）：明确延期项的真相源；未决问题与候选仍见 `../backlog.md`。

## 暂不做的对象

| 对象或能力 | 本轮不做的原因 | 后续触发条件或推荐阶段 |
| --- | --- | --- |
| `restart` 子命令别名、未知命令提示、`status` 短别名 | 首版保持单一入口形态，先保证正确用法可文档化；用户已出现一次误用，但尚未要求改代码 | 用户再次误用，或希望降低命令记忆成本时；对应 `backlog.md` Q18 |
| `start --restart --no-iterm` 清理旧 iTerm 窗口 | 无 GUI 模式与窗口生命周期解耦，首版不做额外窗口操作 | 需要无 GUI 重启且不想残留窗口时；对应 Q19 |
| 自动扫码登录、登录态失效通知 | QQ 风控与人工确认不可绕过；本次还需手机 QQ 恢复安全风险 168 | 明确 QQ 登录稳定流程后；仍不承诺自动扫码 |
| 生产 AstrBot Dashboard 收口到 `127.0.0.1` | 会改变远程访问能力，涉及生产配置与安全策略，需用户决策 | 安全加固阶段；对应 Q21 |
| 生产启动前自动停 `napcat-e2e-sender` | 发送者 C# 与生产 17号 不冲突；首版只处理机器人账号冲突 | 需要彻底清理 E2E 或端口 6201/16398 冲突时；对应 Q22 |
| 手动关闭单个 iTerm 标签的感知与自动补标签 | 需要记录每个 tab/session 的 ID，复杂度高于首版收益 | 需要更精细的窗口生命周期管理时；对应 Q23 |
| Linux/Windows 生产启动脚本 | 当前只在 macOS + iTerm2 验证；Windows 无 iTerm、Linux 无 AppleScript | 出现跨平台需求时；先做独立探测与适配 |
| 生产与 E2E 并行运行 | 同一 17号 不能双端在线；需要独立测试 bot 账号 | 需要并行回归时；对应 `../backlog.md` Q13 |
| 生产 AstrBot 自动暂停/恢复 | 与 E2E 脚本联动会扩大生产侧自动化风险；当前人工控制 | 高频回归或无人值守时 |

## 触发条件

- 用户明确要求进入对应能力，或 `state.md` / `NEXT-SESSION-PROMPT` 指向该延期项。
- 生产登录恢复后，先复测 `prod.sh start` 的 OneBot 就绪路径，再讨论自动扫码。
- 若要改生产 AstrBot Dashboard host，先确认远程访问与安全边界，再做配置备份与回滚方案。

## 与未决问题、首版限定的边界

- 本文件只记录**明确延期**的能力：已判断本轮不做、后续可做且有触发条件。
- **未决问题**（如别名、Dashboard 收口、发送者清理）见 `../backlog.md` Q18–Q23，尚未形成批准结论。
- **首版限定**（只管理生产 NapCat/AstrBot、macOS + iTerm2、人工扫码）见 `../backlog.md` 首版限定表。

## 恢复原则

- 不把“本轮不做”写成永久放弃。
- 每次恢复先读 `state.md`、`checkpoints.md`、最新 handoff，再决定进入哪个延期项。
