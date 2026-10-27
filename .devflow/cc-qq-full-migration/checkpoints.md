# cc-qq 完整迁移最近检查点（Checkpoints）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:23:07 +08:00
- 更新时间（Updated At）：2026-10-28 01:00:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：记录本 mission 最近的阶段切换与继续位置。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：0.2.4 已实施，待重载与真机验收（Runtime Verification Pending）
- 文档边界（Scope / Boundary）：最近检查点真相源（source of truth）；仅保留最近三条，更早记录见 `checkpoints-archive.md`。

## 2026-10-28 01:00:00 +08:00 — 0.2.4 执行反馈修复已实施，待重载

- 已完成：`/goon` 去掉 `or ""`，取消时不再伪装成功；被取消时明确回「已中断当前代理执行」；中断了正在执行的上一轮时回复带「已中断上一条执行」前缀。新增执行回执：会启动代理的输入先回一条「已收到，正在处理」，判定唯一真相源为 `commands/registry.py::will_run_agent`。
- 根因：`sessions.py:153` 的 `or ""` 让 `_execute` 的取消（`None`）变成空串，`service.py` 判 `reply is not None` 标 `done`、`main.py` 判 `if reply:` 不发，形成「显示成功、用户收不到」。
- 本机验证：105 个单元测试通过（原 94 + 新增 11，集中在 `tests/test_execution_feedback.py`）；`py_compile` 全部通过；安装目录已同步到 `0.2.4`，用 AstrBot 自带 Python 加载验证常量与判定函数正常。
- 配置层：NapCat `onebot11_3254276668.json` 的 `AstrBot-E2E` 客户端已改为 `enable: false`（备份 `.bak-20261028`），消除 `6198 ECONNREFUSED` 每 30 秒重连日志；需重启 QQ 生效。
- 当前阶段：安装目录已是 `0.2.4`，AstrBot 尚未重载；未生成 ZIP。
- 下一步：重载后确认 `已加载 v0.2.4`，实测执行回执、`/goon` 前缀、`/!` 中断，再补 T05.10／T05.11／T05.12 真机验收。
- 注意：`/goon` 连带取消同会话排队消息属于固有语义，本轮未改；流式输出延期，触发条件是单轮经常超过 5 分钟。

## 2026-10-28 00:20:00 +08:00 — 0.2.3 `/cd list` 已实施，待重载

- 已完成：`/cd list` 按 `allowed_work_dirs` 配置顺序编号列出并标记当前目录；`/cd <序号>` 切换；`/cd <目录>` 行为不变。新增常量集中在 `constants.py`，展示逻辑在 `commands/session.py::cd_list_text`。94 个单元测试通过。
- 当前阶段：仓库与安装目录都是 `0.2.3`，AstrBot 尚未重载；本轮未生成 ZIP。
- 下一步：用户确认后重载，在 QQ 内实测 `/cd list`、`/cd 2` 与越界提示。
- 注意：序号以当次配置顺序为准，配置调整后旧序号失效；纯数字目录名需用 `/cd ./123` 形式。
- 本轮未讨论 / 未实现的议题已记入 `deferred/第一版边界与未讨论项.md` 的「2026-10-28 `/cd list` 与需求收口」小节。

## 2026-10-27 15:45:00 +08:00 — 0.2.2 MCP 搜索放行已实测，安装目录已覆盖

- 已完成：`0.2.1` 重排配置页分组与文案；`0.2.2` 放行 `mcp__deepseek-web`（workspace/full）、只读档新增 `readonly_mcp_enabled` 开关（默认开）、原生 `WebSearch`／`WebFetch` 与本机 `mcp__fetch` 全档禁用。87 个单元测试通过。
- 本机验证：Claude 2.1.202 下 deepseek 搜索在 readonly（开关开）/workspace/full 可调用；开关关时不可见；原生 WebSearch 与本机 fetch 在工具列表中不存在；`--setting-sources ""` 不加载用户级 MCP，`user` 才加载。
- 当前阶段：安装目录已覆盖到 `0.2.2`，AstrBot 尚未重载；`claude_setting_sources` 已为 `user`；`readonly_mcp_enabled` 待重载后由 schema 补齐。`0.2.1`／`0.2.2` 在 2026-10-27 收尾提交（未推送），未打包。
- 下一步：重载后确认 `已加载 v0.2.2`，在 QQ 群内验证一次 deepseek 搜索问答与 guest 只读边界；再补 T05.10 其余验收。
- 注意：本机 `mcp__fetch` 被禁用是故意的（防内网访问）；deepseek-web 的抓取在服务端执行，可访问公网但不能碰本机内网。
