# 下一次对话提示词：cc-qq 0.3.2 发布后收尾（Next Session Prompt）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 11:00:28 +08:00
- 更新时间（Updated At）：2026-11-01 01:00:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：提供可直接复制到新对话的 mission 恢复指令。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：`0.3.2` 已发布并覆盖生产与测试安装目录；Codex 侧 0.2.5 同项、Codex 图片 `-i`、`/start` 与大图真机复测、远端推送待做
- 文档边界（Scope / Boundary）：恢复提示，不代替 `state.md` 或已批准计划。

## 可复制提示词

继续 `.devflow/cc-qq-full-migration/` mission。

先读：
- `.devflow/cc-qq-full-migration/state.md`
- `.devflow/cc-qq-full-migration/checkpoints.md`
- `.devflow/cc-qq-full-migration/handoffs/2026-11-01-011-0.3.2发布与收尾.md`

**硬门禁（最高优先级）**：任何代码修复前必须先「说明问题与根因 → 讨论方案 → 写 Plan 到 `.devflow/<mission>/plans/` → 用户明确批准 → 再 Apply」。`继续验证`、`先测着`、`最后再修复` 都不是修复授权。

## 当前结论（2026-11-01）

- 版本 `0.3.2`；插件单测 165/165 通过。
- `0.3.2` 两处修复：
  - 代理 stdout 改为分块读取（`iter_stdout_lines`），单行上限 8 MiB，超限整行丢弃告警；修复图片 base64 单行 >1 MiB 导致 `ValueError` 与整轮丢失。
  - cc-qq 的 `/new` 更名为 `/start`，避开 AstrBot 内置 `/new`（共享群管理员）在 `waking_check` 阶段的权限拦截；不保留别名。
- 发布：ZIP `integrations/astrbot/astrbot_plugin_cc_qq-v0.3.2-upload.zip`；生产与测试安装目录已覆盖（备份 `plugin-backup-20261101-005050`）；两实例重启后均为「已加载 v0.3.2」。

## 历史结论（2026-10-30）
- 需求 5 已完成 Align → Plan → spec 三件套 → Apply → 真机验证：
  - 媒体输入：直接图片、引用消息（文本＋图片）、合并转发展开。
  - 图片输出：`[[image:<path>]]` 图文混排，路径限工作目录或插件媒体目录。
  - 长文本：本地 T2I 长图，默认 360 字或含围栏代码块触发；`/img on|off` 按会话开关；只发长图，失败回退文本。
  - 只读档：`extra_read_roots` 放行插件媒体目录，写工具与 `Bash` 仍拒绝。
- 真机结果：媒体 suite **6/6**、基础命令 suite **4/4**。
- 真机修复 4 个缺陷：B1 配置 `null` 导致媒体/长图默认关闭；B2 `/help` 被误转长图；B3 NapCat 图片 URL 过期（改用 `get_image` 本地路径）；B4 `[[image:相对路径]]` 按进程 cwd 解析失败（改为 realpath 绝对路径）。详见 `bug-log.md`。
- 发布：ZIP `integrations/astrbot/astrbot_plugin_cc_qq-v0.3.1-upload.zip`；生产与测试安装目录均已覆盖 `0.3.1`（生产备份 `~/.astrbot/data/plugin-backup-20261030-165521/`）。

## 当前环境

- 生产 AstrBot（`6185/6199`）与测试 AstrBot（`6186/6198`）均**正在运行 `0.3.2`**（2026-11-01 00:51 重启）。
- 生产日志 `~/.astrbot/logs/restart-20261101-005110.log`；测试日志 `~/.astrbot-e2e/logs/restart-20261101-005110.log`。
- 两个 NapCat 端口 `6098/6099` 与 OneBot `6200/6201` 仍在监听，两个 QQ 已登录。
- 测试实例 `~/.astrbot-e2e` 配置已按备份恢复（`claude_setting_sources=""`）；要测代理执行需临时改为 `user`。
- 一键启动脚本：`~/.qq-e2e/start-e2e.sh`（本地脚本不入库）。

## 下一步优先级

1. **`0.3.2` 真机复测**：群内 `@机器人 /start` 建会话；私聊让代理 `Read` 一张 >750 KB 图片，确认不再出现 `ValueError`、能正常回复。
2. **Codex 侧真机验收**：0.2.5 的只读／工作区／完全权限（T05.10）；补验 T03-M.4b、T04.4、T04.5。
3. **Codex 图片 `-i`**：确认 `codex exec resume` 是否接受 `-i`；不接受则改为仅首轮传图。
4. **推送远端**：提交 `b2f80b2`（`0.3.2`）尚未推送；`v0.3.0`／`v0.3.1`／`v0.3.2` 的 tag 与发布策略由用户决定。
5. 合并转发触发规则：群聊中合并转发无法与 @bot 同时发送，当前静默；需要时单独对齐。
6. 图片来源与合理性（搜索图片、表情包）由用户后续 skill 解决；插件侧协议已就绪。
7. 第三测试 QQ 账号、生产暂停自动化、F2（@bot 空文本被 LLM 抢占）。
8. 流式输出：优先级由用户决定。

## 未讨论 / 明确延期（禁止当成已批准）

- 不把 owner `1961618848` 加入 AstrBot 核心 `admins_id`：会让内置 `/new` 与插件双执行，并放开内置管理命令；需要内置 `/name`、`/provider` 时再评估，且须先禁用内置 `/new`。
- 不全局关闭内置命令：会失去 `/sid`、内置 `/help` 等；只有确认完全不需要内置命令时才考虑。
- 旧 `/new` 不保留别名；群里旧习惯 `/new` 仍会命中内置命令并提示权限不足，可在 WebUI「指令管理」单独禁用内置 `/new`（可选配置，本轮未执行）。
- 超过 8 MiB 的单行仍整行丢弃；只有实际出现「日志告警丢弃且用户没收到关键内容」时，再评估「保留头部 + 截断标记」。
- 内置 `/help` 与插件 `/help` 双处理器并存；目前无重复回复，出现异常再清理内置 `/help`。
- 两实例重启目前是手工 kill + `nohup astrbot run`；是否写成发布脚本待定。

## 必须记住的约束

- **修复前必须走 Align → Plan → 用户明确批准 → Apply**；规则已写入 `.claude/CLAUDE.md` 开头、中间、结尾三处。
- 测试期间若生产 AstrBot 与测试共用 `17号`，生产会响应测试群的内置命令与 LLM；需暂停生产或改用独立测试账号。
- 代理类测试需把测试实例 `claude_setting_sources` 设为 `user`，否则 Claude 未登录、MCP 不加载；测完恢复。
- NapCat 图片 URL 会过期，必须优先用 `file` + `get_image` 换本地路径。
- 长图只对会启动代理的输入生效；同步命令（`/help` 等）永远保持文本。
- AstrBot 未填写配置是 `null`，读取时必须把 `None` 当默认值。
- cc-qq 的会话命令是 `/start`（不是 `/new`）。AstrBot 内置 `/new` 要求核心 `admins_id`（当前仍是默认 `["astrbot"]`），在群里会先于插件拦截并回复「权限不足」；如需彻底消除旧 `/new` 提示，在 WebUI「指令管理」单独禁用内置 `/new`。
- 代理 stdout 现在按块读取；单行超过 8 MiB 会整行丢弃并告警，不再中断整轮执行。
- `allowed_work_dirs` 为空时 `/cd` 只能测「未配置」负向；测序号切换需临时配置 3 个测试目录。
- 相同回复文案 10 秒内被去重，批量验收需间隔 ≥11 秒。
- NapCat 的 `onebot11_*.json` 带 UTF-8 BOM，用 `utf-8-sig`；改完必须重启 QQ。
- 会话 JSONL 的 `timestamp` 是 UTC，本地 +8；工具调用统计按 `tool_use.id` 去重。

## 恢复读取建议

- 日常恢复：`state.md` → `checkpoints.md` → 最新 handoff。
- 完整过程：`development-overview.md` + `decision-log.md` + `plans/`。
- 逾期项：`deferred/第一版边界与未讨论项.md` 的「2026-11-01 `0.3.2`」与「2026-10-30 需求 5」两节；轻量想法：`backlog.md`。
- 原始输入与新增需求：`origin.md`、`zzz-prompt-debug/接入agent/prompt-01.md`。
