# 下一次对话提示词：cc-qq 0.3.3 发布与补验（Next Session Prompt）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 11:00:28 +08:00
- 更新时间（Updated At）：2026-11-01 02:45:00 +08:00
- 作者（Author）：Claude / Grok
- 目的（Purpose）：提供可直接复制到新对话的 mission 恢复指令。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：`0.3.3` 单测 181/181、真机 suite 12/12 通过；测试实例已装，生产仍 `0.3.2`，待发布
- 文档边界（Scope / Boundary）：恢复提示，不代替 `state.md` 或已批准计划。

## 可复制提示词

继续 `.devflow/cc-qq-full-migration/` mission。

先读：
- `.devflow/cc-qq-full-migration/state.md`
- `.devflow/cc-qq-full-migration/checkpoints.md`
- `.devflow/cc-qq-full-migration/handoffs/2026-11-01-012-0.3.3回复媒体自动识别真机通过.md`

**硬门禁（最高优先级）**：任何代码修复前必须先「说明问题与根因 → 讨论方案 → 写 Plan 到 `.devflow/<mission>/plans/` → 用户明确批准 → 再 Apply」。`继续验证`、`先测着`、`最后再修复` 都不是修复授权。

## 当前结论（2026-11-01）

- 版本 `0.3.3`；插件单测 **181/181**。
- 新增「回复媒体自动识别与发送」：显式 `[[image:<path>]]` 之外，自动识别可信本地图片/视频路径与公网媒体 URL；本地仅限 `work_dir`/插件媒体目录，图片 PIL 实检，视频 `.mp4/.mov/.webm` + 100 MiB；URL 拦截回环/私网；本地优先去重；含媒体回复不再整体转长图；新增 `auto_send_media`（默认开）。
- 真机（astrbot-plugin-e2e，测试 bot `3299987672`、发送者 `1961618848`、群 `701292201`）：suite **12/12** 通过；另显式跑通 `rc-draw-generate`（`run.sh` 生成 1254×1254 PNG 并自动发送）。
- 报告：`tools/astrbot_e2e/reports/20261101-022711-060610-astrbot_plugin_cc_qq-suite/`、`.../20261101-022956-010523-cc-qq-rc-draw-generate-skill/`。
- 生产仍运行 `0.3.2`；测试实例 `~/.astrbot-e2e` 已装 `0.3.3`；ZIP 未生成、未推送。

## 下一步优先级

1. **发布决定**：是否生成 `0.3.3` ZIP、备份并覆盖生产/测试安装目录、重启并核对「已加载 v0.3.3」、推送远端。
2. **补验**：`auto_send_media=false` 回退、视频发送（执行引擎无视频断言、本机无 ffmpeg，需手工或扩展 e2e）。
3. **`0.3.2` 遗留复测**：群内 `@机器人 /start`；私聊让代理读取 >750 KB 图片，确认无 `ValueError`。
4. **Codex 侧同项验收**：0.2.5 只读／工作区／完全权限（T05.10），补验 T03-M.4b、T04.4、T04.5。
5. 代理协议提示（system prompt / `initbase` 模板）是否与自动识别并存。
6. 旧 `/new` 提示、第三个测试账号、生产暂停自动化、F2（@bot 空文本被 LLM 抢占）。
7. 流式输出：优先级由用户决定。

## 当前环境

- 生产 AstrBot（6185/6199）运行 `0.3.2`，未重启、未覆盖。
- 测试 AstrBot（6186/6198）PID 约 99530，运行 `0.3.3`；Docker `napcat-e2e-bot` / `napcat-e2e-sender`。
- 测试配置：`tools/astrbot_e2e/config.local.json`；测试工作目录 `~/.astrbot-e2e/workdir`；已复制 `rc-draw-generate`（含 `.env`，测试侧临时资产）。
- 测试用例：`tools/astrbot_e2e/cases/ccqq-v033/`（suite）与 `ccqq-v033-manual/`（显式 skill）；跳过项见 `cases/ccqq-v033/SKIPPED.md`。

## 必须记住的约束

- **修复前必须走 Align → Plan → 用户明确批准 → Apply**。
- 自动识别只信任 `work_dir` 与插件媒体目录；不要把信任范围放宽到任意本地路径。
- 同一回复本地媒体优先，URL 丢弃；含媒体回复不整体转长图。
- `/help` 是纯文本，不会转长图（同步命令 `will_run_agent=False`）。
- 代理不会自动知道 `[[image:]]`；要验证 rc-draw 必须显式给 `SKILL.md` 与 `run.sh` 路径。
- e2e 的 `images` 断言区分不了本地原图与长文本截图；需要时查生成目录或代理会话 JSONL。
- NapCat 图片 URL 会过期；发图优先本地路径。
- AstrBot 未填写配置是 `null`，读取时必须把 `None` 当默认值。
- 相同回复文案 10 秒内被去重，批量验收需间隔 ≥11 秒。
- 报告默认脱敏；报告与测试配置不入库。
- 未获明确批准禁止提交代码；提交信息用中文。

## 恢复读取建议

- 日常恢复：`state.md` → `checkpoints.md` → 最新 handoff。
- 完整过程：`development-overview.md` + `decision-log.md` + `plans/`。
- 延期项：`deferred/2026-11-01-post-0.3.3-deferred.md`；轻量想法：`backlog.md`。
- 原始输入：`origin.md`。
