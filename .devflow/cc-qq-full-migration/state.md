# cc-qq 完整迁移当前状态（Current State）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:10:32 +08:00
- 更新时间（Updated At）：2026-10-30 17:00:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：提供本 mission 的短当前快照。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：`0.3.1` 代码、单测（159/159）与媒体真机 suite（6/6）、基础命令 suite（4/4）均通过；Codex 侧 0.2.5 同项与 ZIP 仍待做
- 文档边界（Scope / Boundary）：当前状态真相源（source of truth）。不代表已在 AstrBot/QQ 上验收通过，也不代表已生成 ZIP。

## 当前快照

- **2026-10-30 需求 5 真机测试（astrbot-plugin-e2e）**：媒体 suite 6/6、基础命令 suite 4/4 通过。测试中发现并修复 4 个缺陷：B1 配置 `null` 导致媒体/长图默认关闭；B2 `/help` 命令回复被误转长图；B3 NapCat 图片 URL 过期导致落盘失败（改用 `get_image` 本地路径）；B4 `[[image:相对路径]]` 按进程 cwd 解析导致发送失败（改为 realpath 绝对路径）。单测 159/159。详见 `bug-log.md` 与两份 suite 报告。
- **2026-10-30 需求 5 实施与发布（0.3.1）**：新增媒体输入（直接图片、引用消息、合并转发）、图片输出 `[[image:<path>]]`、长文本本地 T2I 长图（默认 360 字或含代码块触发）与 `/img on|off`。只读档通过 `extra_read_roots` 额外放行插件媒体目录，写工具与 `Bash` 仍拒绝。真机修复后发布 `0.3.1`：生产与测试安装目录已覆盖（生产备份 `~/.astrbot/data/plugin-backup-20261030-165521/`），ZIP 为 `integrations/astrbot/astrbot_plugin_cc_qq-v0.3.1-upload.zip`。计划见 `plans/2026-10-30-cc-qq-需求5-媒体输入输出与长文本渲染实施计划.md`。
- 仓库插件版本升至 `0.2.4`（`0.2.1` 配置页文案，`0.2.2` MCP 放行，`0.2.3` `/cd list` 序号切换，`0.2.4` `/goon` 静默修复与执行回执）。105 个单元测试通过；安装目录已同步到 `0.2.4`（备份在 `~/.astrbot/data/plugin-backup-20261028-005725/`）；未生成 ZIP。
- **2026-10-29 命令与权限真机验收（A+B 完成）**：测试实例 `~/.astrbot-e2e` 已加载 `v0.2.4`，在群 `701292201` 验收 34 项：32 通过、1 项因测试实例内置 LLM 抢占未取得预期回复、2 项暴露同一缺陷（执行回执早于权限/参数校验）。`/cd list` 与序号切换真机通过；guest/member/owner 三级命令门禁符合设计。生产 AstrBot 测试期间暂停并已恢复（PID `38223`）。详见 `plans/2026-10-29-cc-qq-0.2.4-命令与权限验收结果.md`。
- **2026-10-30 C 阶段验收 + 0.2.5 修复 F1**：真实代理执行（普通消息 1.1s 回执 / 6.5s 回复）、`/cc` 透传、`/goon` 前缀、执行中 `/!` 中断、guest 只读、workspace 内写、目录外审批 approve/deny、deepseek 搜索（1 次 `deepseek_search`，0 次原生联网）均通过。F1 已在 `0.2.5` 修复：`will_run_agent` 增加 role 门禁、`/cc` 空参不触发回执、`/goon` 无活跃会话不回执；单测 113/113，真机复验通过。生产 AstrBot 已恢复（PID `61792`）。修复过程未先取得明确批准，用户已要求后续严格执行硬门禁。
- `0.2.4` 修复三个执行反馈缺陷：`/goon` 取消后返回空串导致「标 done 且静默」；`/goon` 中断动作不告知；长任务执行期间零反馈。现 `goon` 取消时明确回「已中断当前代理执行」，中断了上一轮时回复带前缀；会启动代理的输入先回一条执行回执。
- 回执判定唯一真相源：`commands/registry.py::will_run_agent`。`/goon`、`/cc <消息>`、带参数的 `/new` 与 `/!`、普通文本会触发；同步返回命令不触发。
- NapCat 生产配置 `onebot11_3254276668.json` 的 `AstrBot-E2E`（`ws://127.0.0.1:6198/ws`）已改为 `enable: false`（备份 `onebot11_3254276668.json.bak-20261028`），需重启 QQ 生效。
- 群 `701292201` 是 `astrbot-plugin-e2e` 的专用测试群，只配在 `~/.astrbot-e2e`；本轮不加进生产 `enabled_group_ids`。生产群仍为 `836229427`、`209267585`、`432199252`。
- **排查耗时分析（本轮新增产出）**：实测单轮排查 16.4 分钟（扣除 93 秒用户决策等待后 893 秒），其中模型生成 680s（76%）、工具执行 213s（24%）；160 次工具调用**全部串行**（并行度 1.00），127 次模型往返，平均每步 7.8 秒。单条命令中位仅 1.93 秒、单次 API 往返中位仅 1.0 秒——**慢在次数不在单点**。文档见 `2026-10-28-排查耗时分析与优化方案.md`。该结论同时说明：`0.2.4` 的执行回执只解决「怀疑没反应」，不解决「等待久」。
- 运行时校验：用 AstrBot 自带的 Python 3.12.13 直接加载安装目录的插件模块，导入与列表输出均正常。
- `/cd list`：按 `allowed_work_dirs` 配置顺序编号输出并标记当前目录；`/cd <序号>` 切换；`/cd <目录>` 行为不变；权限仍为 owner／管理员。序号以当次配置顺序为准，配置调整后需重新 list。
- MCP 联网：workspace／full 放行服务器级 `mcp__deepseek-web`；只读档由 `readonly_mcp_enabled`（默认开）控制；原生 `WebSearch`／`WebFetch` 与本机 `mcp__fetch` 全档禁用。实测 `""` setting-sources 不加载用户级 MCP，配置需 `claude_setting_sources=user`（同时解决 `ANTHROPIC_AUTH_TOKEN` 鉴权）。
- 权限模型：群内非白名单为 `readonly`，群／私聊白名单为 `workspace`，owner／管理员为 `full`；档位按每轮发言者计算，不写入会话记录。
- Claude Code：只读用 `dontAsk + --tools`；工作区用 `acceptEdits + Seatbelt/bubblewrap 沙箱 + PreToolUse 审批 hook`；完全权限用 `dontAsk + 守护 hook`（实测 `bypassPermissions` 不执行 deny 规则）。默认 `--setting-sources ""`。
- Codex：只读/工作区改用权限档案 `ccqq-readonly`、`ccqq-workspace`，工作区外读写与 `/tmp` 被拒绝；完全权限用 `sandbox_mode="danger-full-access"`。Codex 本轮没有逐次审批。
- 本机 CLI 实测：Claude Code 2.1.202 的 hook 能向本机 broker 请求并放行/拒绝 `rm`；Codex 0.162.1 的权限档案能阻止读取 `~/.codex/config.toml`，工作区档能写当前目录并阻止写 `/tmp`。
- 审批：`/approve`、`/deny` 在 `main.py` 会话队列前处理，避免与等待审批的代理死锁；超时、异常、broker 不可达一律拒绝；`permission_audit` 记录审批与拒绝。
- 管理员 `/cd` 只能进入 `allowed_work_dirs` 的 realpath 子目录；`/initbase` 只补缺失模板，不覆盖已有文件。

## 本轮不做 / 后续阶段（Deferred Scope）

- 真机验收 T05.10：**Claude 侧已验收（命令/权限 + 工具级只读、工作区写入、目录外审批）**；Codex 侧同项仍待测；未生成 ZIP。
- T05.11 MCP 搜索：**已真机通过**（deepseek 搜索 1 次 `mcp__deepseek-web__deepseek_search`，原生 WebSearch/WebFetch 0 次）。
- T05.12 `/cd list` 与序号切换：**已真机通过（2026-10-29）**，含当前目录标记、`/cd 2`、越界、非目录、目录外拒绝。
- T05.13 执行反馈：C 阶段已验证 `/goon` 前缀与执行中 `/!` 中断；F1 已在 `0.2.5` 修复并复验（owner `/cc` 空参、无会话 `/goon`、guest `/cc`/`/goon` 均不再先发回执）。
- **流式输出（Streaming）本轮不做**：`_execute` 仍攒齐所有 TEXT 事件后一次性返回，长任务期间只有开头一条回执。本轮用「执行回执」缓解等待焦虑，未改消息链路。暂不做的原因：改为边收边发需重构 `main.py` 的回复链路与 `send_text` 分段策略，与 AstrBot 消息链耦合深。
  - **原触发条件「单轮经常超过 5 分钟」已满足**：实测 `3fe53f78` 单轮 15 分钟、`b94f6bc6` 排查单轮 16.4 分钟。且排查耗时分析表明：即使把并行化做到极致，复杂任务仍需 8–9 分钟，**并行化压缩不了用户感知的等待**。建议从延期提为待排期，最终优先级由用户决定（本轮未擅自提级）。
- **AI 排查任务的并行化规范**：分析文档第七节给出 4 条改进方向（强制并行、专用工具优先于 Bash、一次读全、先定位再深挖），均为候选项，未写成强约束，也未用其他样本复测。待用户确认后再决定是否写入 `learnings.md` 或项目级规则。
- **`/goon` 中断排队消息的语义**本轮不改：`/goon` 连带取消同会话排队中的普通消息，属于「中断当前执行」的固有语义（同会话串行、无独立队列）。若后续需要「只中断当前、保留队列」，属需求变更，需重新对齐。
- **6198 重连日志的复发风险**：本轮只在生产 NapCat 配置里关掉 `AstrBot-E2E` 客户端；e2e 用例重新 bootstrap 时会再次写入。后续应在 `astrbot-plugin-e2e` 的用例收尾里自动回滚 NapCat 的 `onebot11` 配置（对应其 `backlog.md` Q2）。
- `/cd list` 的扩展能力本轮不做：一级子目录展开、两级列表（先列根目录再展开）、分页、序号持久化。原始需求只要「按配置顺序列出 + 序号切换」，用户明确否决了子目录展开。后续若目录数量增长到一屏放不下，再考虑分页；触发条件为实际列表中超过 20 项。
- 群内 @bot 管理私聊白名单（候选）：用户 2026-10-27 提出后中断，4 个关键问题未回答（名单类型、@ 或 QQ 号、命令集、私聊总开关关闭时行为），本轮未实现。详见 `deferred/第一版边界与未讨论项.md`。
- 群未配置 `group_rules_json` 时的报错仍是笼统的「插件配置无效」；更准确的提示本轮未改。
- Codex 原生 web search 的关闭方式待确认 0.162.1 配置键；MCP 按服务器/工具的细分开关延期。
- Codex 逐次危险操作审批：`codex exec` 的非交互审批仍为 under development。
- 审批卡片私聊通知管理员、私聊短时聚合与上下文截断（需求3.3）、工作目录人格、图形化权限页：见 `deferred/阶段二至四功能.md`。
- 阶段 2 到阶段 4 的其余功能仍按总体计划继续。
- **需求 5 延期项**：图片来源与合理性（搜索图片、表情包）、合并转发在群聊中的触发规则、GitHub Pages／语雀网页版、群会话按成员隔离、长图样式配置、单张图片大小与保留期配置、outbox 自动附发、媒体用例入库。逐项原因与触发条件见 `deferred/第一版边界与未讨论项.md` 的「2026-10-30 需求 5」一节。
