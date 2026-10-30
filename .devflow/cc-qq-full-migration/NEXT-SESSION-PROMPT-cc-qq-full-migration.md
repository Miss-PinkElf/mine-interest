# 下一次对话提示词：cc-qq 需求 5 发布后收尾（Next Session Prompt）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 11:00:28 +08:00
- 更新时间（Updated At）：2026-10-30 17:20:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：提供可直接复制到新对话的 mission 恢复指令。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：`0.3.1` 需求 5 已开发、真机测试并覆盖安装目录；Codex 侧 0.2.5 同项、Codex 图片 `-i` 与远端推送待做
- 文档边界（Scope / Boundary）：恢复提示，不代替 `state.md` 或已批准计划。

## 可复制提示词

继续 `.devflow/cc-qq-full-migration/` mission。

先读：
- `.devflow/cc-qq-full-migration/state.md`
- `.devflow/cc-qq-full-migration/checkpoints.md`
- `.devflow/cc-qq-full-migration/handoffs/2026-10-30-010-需求5媒体与长图代码完成待真机.md`

**硬门禁（最高优先级）**：任何代码修复前必须先「说明问题与根因 → 讨论方案 → 写 Plan 到 `.devflow/<mission>/plans/` → 用户明确批准 → 再 Apply」。`继续验证`、`先测着`、`最后再修复` 都不是修复授权。

## 当前结论（2026-10-30）

- 版本 `0.3.1`；插件单测 159/159 通过。
- 需求 5 已完成 Align → Plan → spec 三件套 → Apply → 真机验证：
  - 媒体输入：直接图片、引用消息（文本＋图片）、合并转发展开。
  - 图片输出：`[[image:<path>]]` 图文混排，路径限工作目录或插件媒体目录。
  - 长文本：本地 T2I 长图，默认 360 字或含围栏代码块触发；`/img on|off` 按会话开关；只发长图，失败回退文本。
  - 只读档：`extra_read_roots` 放行插件媒体目录，写工具与 `Bash` 仍拒绝。
- 真机结果：媒体 suite **6/6**、基础命令 suite **4/4**。
- 真机修复 4 个缺陷：B1 配置 `null` 导致媒体/长图默认关闭；B2 `/help` 被误转长图；B3 NapCat 图片 URL 过期（改用 `get_image` 本地路径）；B4 `[[image:相对路径]]` 按进程 cwd 解析失败（改为 realpath 绝对路径）。详见 `bug-log.md`。
- 发布：ZIP `integrations/astrbot/astrbot_plugin_cc_qq-v0.3.1-upload.zip`；生产与测试安装目录均已覆盖 `0.3.1`（生产备份 `~/.astrbot/data/plugin-backup-20261030-165521/`）。

## 当前环境

- 生产 AstrBot 与测试 AstrBot 当前都**没有运行**（`6185/6186` 无监听）；覆盖后需用户启动或重载才生效。
- 两个 NapCat 端口 `6098/6099` 与 OneBot `6200/6201` 仍在监听，两个 QQ 已登录。
- 测试实例 `~/.astrbot-e2e` 配置已按备份恢复（`claude_setting_sources=""`）；要测代理执行需临时改为 `user`。
- 一键启动脚本：`~/.qq-e2e/start-e2e.sh`（本地脚本不入库）。

## 下一步优先级

1. **用户启动生产 AstrBot 并重载 `0.3.1`**，确认日志出现「已加载 v0.3.1」。
2. **Codex 侧真机验收**：0.2.5 的只读／工作区／完全权限（T05.10）；补验 T03-M.4b、T04.4、T04.5。
3. **Codex 图片 `-i`**：确认 `codex exec resume` 是否接受 `-i`；不接受则改为仅首轮传图。
4. **推送远端**：`0.3.1` 代码与文档尚未推送；`v0.3.0`／`v0.3.1` 的发布策略由用户决定。
5. 合并转发触发规则：群聊中合并转发无法与 @bot 同时发送，当前静默；需要时单独对齐。
6. 图片来源与合理性（搜索图片、表情包）由用户后续 skill 解决；插件侧协议已就绪。
7. 第三测试 QQ 账号、生产暂停自动化、F2（@bot 空文本被 LLM 抢占）。
8. 流式输出：优先级由用户决定。

## 必须记住的约束

- **修复前必须走 Align → Plan → 用户明确批准 → Apply**；规则已写入 `.claude/CLAUDE.md` 开头、中间、结尾三处。
- 测试期间若生产 AstrBot 与测试共用 `17号`，生产会响应测试群的内置命令与 LLM；需暂停生产或改用独立测试账号。
- 代理类测试需把测试实例 `claude_setting_sources` 设为 `user`，否则 Claude 未登录、MCP 不加载；测完恢复。
- NapCat 图片 URL 会过期，必须优先用 `file` + `get_image` 换本地路径。
- 长图只对会启动代理的输入生效；同步命令（`/help` 等）永远保持文本。
- AstrBot 未填写配置是 `null`，读取时必须把 `None` 当默认值。
- `allowed_work_dirs` 为空时 `/cd` 只能测「未配置」负向；测序号切换需临时配置 3 个测试目录。
- 相同回复文案 10 秒内被去重，批量验收需间隔 ≥11 秒。
- NapCat 的 `onebot11_*.json` 带 UTF-8 BOM，用 `utf-8-sig`；改完必须重启 QQ。
- 会话 JSONL 的 `timestamp` 是 UTC，本地 +8；工具调用统计按 `tool_use.id` 去重。

## 恢复读取建议

- 日常恢复：`state.md` → `checkpoints.md` → 最新 handoff。
- 完整过程：`development-overview.md` + `decision-log.md` + `plans/`。
- 逾期项：`deferred/第一版边界与未讨论项.md` 的「2026-10-30 需求 5」一节；轻量想法：`backlog.md`。
- 原始输入与新增需求：`origin.md`、`zzz-prompt-debug/接入agent/prompt-01.md`。
