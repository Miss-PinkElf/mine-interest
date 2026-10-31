# cc-qq 完整迁移最近检查点（Checkpoints）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:23:07 +08:00
- 更新时间（Updated At）：2026-11-01 02:45:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：记录本 mission 最近的阶段切换与继续位置。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：`0.3.3` 回复媒体自动识别单测 181/181、真机 suite 12/12 通过；测试实例已装，生产仍 `0.3.2`，待发布（Verified / Release Pending）
- 文档边界（Scope / Boundary）：最近检查点真相源（source of truth）；仅保留最近三条，更早记录见 `checkpoints-archive.md`。

## 2026-11-01 01:50:00 +08:00 — 回复媒体自动识别与发送（0.3.3，待真机）

- 已修复“代理生成了图片但 QQ 收不到”：根因是 `[[image:<path>]]` 协议未进入代理运行时上下文，生产 196 个回合 0 次使用；374 字回复又被整体转成文字长图。
- 新增 `reply_media.py`：显式标记 + 自动识别可信本地图片/视频路径（绝对、`~/`、`./`、Markdown、反引号）与公网媒体 URL；本地仅限 `work_dir`/插件媒体目录，图片 PIL 实检，视频 `.mp4/.mov/.webm` ≤100 MB；URL 拦截回环与私网；本地优先去重，单条最多 10 个。
- `platform/replies.py` 新增 `send_parts()`，支持 `Image`/`Video` 组件与 URL；`main.py::_deliver()` 先解析媒体，含媒体时不再整体转长图；新增 `auto_send_media` 开关（默认开）。
- 验证：全量单测 **181/181**；真实回合 196 回复离线复放，解析出 1 张图片并按「文本 → 图片 → 文本」构造消息链。
- **真机验收（2026-11-01 02:27–02:32，astrbot-plugin-e2e）**：suite **12/12 通过**（104 秒，测试 bot `3299987672`、发送者 `1961618848`、群 `701292201`）。覆盖 `/help`、`/pwd`、`/info`、`/start` 多轮、执行回执、`/!` 中断、本地图片自动发送、公网 URL 自动发送、越权/私网拒绝、显式标记回归。另单独执行显式 `rc-draw-generate` 用例：实际调用 `run.sh` 生成 `rc-20261101-023122.png`（1254×1254，1.1 MB）并自动发送。报告：`tools/astrbot_e2e/reports/20261101-022711-060610-astrbot_plugin_cc_qq-suite/`、`.../20261101-022956-010523-cc-qq-rc-draw-generate-skill/`。
- 待办：决定是否发布 `0.3.3` 并覆盖生产安装目录；视频真机因执行引擎无视频断言且本机无 ffmpeg，标 SKIPPED；`auto_send_media=false` 回退需改测试配置并重载，未执行。
- 提交：`feat(cc-qq): 回复媒体自动识别与发送并完成真机验收`（收尾提交，未推送）。
- 计划：`plans/2026-11-01-cc-qq-回复媒体自动识别与发送计划.md`。

## 2026-11-01 00:55:00 +08:00 — 超长输出崩溃修复 + `/new` 更名为 `/start`

- 已修复私聊「用skill画」`ValueError`：Claude `stream-json` 单行（图片 base64，1,050,933 字节）超过 `StreamReader` 1 MiB 上限，`readline()` 抛 `ValueError`，整轮代理工作丢失。改为 `agents/process.py::iter_stdout_lines()` 分块读取、按换行切分、超限整行丢弃告警；上限提升到 8 MiB；`main.py` 失败日志补充异常消息与堆栈。新增 `tests/test_process_stream.py` 5 项，真实子进程 1.05 MB 单行复现通过。
- 已规避群内 `/new` 权限冲突：AstrBot 内置 `/new`（共享群管理员）在 `waking_check` 阶段先于插件拦截，核心 `admins_id` 仍为默认 `["astrbot"]`。cc-qq 的 `/new` 更名为 `/start`，不保留别名；`README`、帮助文案与测试同步。
- 验证：AstrBot Python 3.12.13 全量单测 **165/165** 通过。
- 发布：`0.3.2` ZIP 已生成（`astrbot_plugin_cc_qq-v0.3.2-upload.zip`）；生产与测试安装目录已覆盖，备份为 `plugin-backup-20261101-005050`；两实例已重启，日志均为「已加载 v0.3.2」（生产 3 群/私聊开，测试 1 群/私聊关）。
- 待办：真机复测私聊大图读取与群内 `@bot /start`；如仍介意旧 `/new` 提示，可在 WebUI「指令管理」单独禁用内置 `/new`。
- 计划：`plans/2026-11-01-cc-qq-代理输出超长行导致ValueError修复计划.md`、`plans/2026-11-01-cc-qq-new命令更名为start计划.md`。

## 2026-10-30 17:00:00 +08:00 — 需求 5 真机测试完成（媒体 suite 6/6）

- 已用 `astrbot-plugin-e2e` skill 完成真机测试：媒体 suite 6/6、基础命令 suite 4/4 通过。
- 修复 4 个真机缺陷：B1 配置 `null` 导致媒体/长图默认关闭；B2 `/help` 被误转长图；B3 NapCat 图片 URL 过期（改用 `get_image` 本地路径）；B4 `[[image:相对路径]]` 按进程 cwd 解析失败（改为 realpath 绝对路径）。
- 单测 159/159；e2e 工具扩展了图片发送、图片断言、`reply_to: last`、回执识别与时间过滤。
- 合并转发在群聊中无法与 @bot 同时发送，按设计不会触发，本轮标记 SKIPPED。
- 收尾：测试实例配置已按备份恢复，测试实例已停止；生产 AstrBot 本轮未运行、无需恢复。
- 报告：`tools/astrbot_e2e/reports/20261030-164735-823213-astrbot_plugin_cc_qq-suite/`（媒体 6/6）、`.../20261030-164654-829047-astrbot_plugin_cc_qq-suite/`（基础 4/4）。

（更早检查点见 `checkpoints-archive.md`。）
