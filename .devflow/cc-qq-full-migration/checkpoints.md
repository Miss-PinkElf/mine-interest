# cc-qq 完整迁移最近检查点（Checkpoints）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:23:07 +08:00
- 更新时间（Updated At）：2026-11-01 00:55:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：记录本 mission 最近的阶段切换与继续位置。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：两处缺陷已修复且单测通过（165/165），未升版、未覆盖安装目录（Release Pending）
- 文档边界（Scope / Boundary）：最近检查点真相源（source of truth）；仅保留最近三条，更早记录见 `checkpoints-archive.md`。

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

## 2026-10-30 15:45:00 +08:00 — 需求 5 媒体与长图代码完成（0.3.1）

- 已完成：媒体输入（直接图片、引用、合并转发）、图片输出 `[[image:<path>]]`、长文本本地 T2I 长图（默认 360 字或含代码块）、`/img on|off`、只读档媒体根放行。
- 单测 154/154；`py_compile` 与 `_conf_schema.json` 校验通过；本地 T2I 已用 AstrBot Python 实测出图。
- 用户明确真机由其本人执行；本轮不做真机验收、不覆盖安装目录、不生成 ZIP。
- 待真机风险：`codex exec resume` 是否接受 `-i`；guest 只读档能否按媒体根读图；长图临时文件依赖 AstrBot 清理。
- 证据与交接：`handoffs/2026-10-30-010-需求5媒体与长图代码完成待真机.md`；计划 `plans/2026-10-30-cc-qq-需求5-媒体输入输出与长文本渲染实施计划.md`。

（更早检查点见 `checkpoints-archive.md`。）
