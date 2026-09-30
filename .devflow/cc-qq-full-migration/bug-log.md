# cc-qq 故障记录（Bug Log）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 16:39:25 +08:00
- 更新时间（Updated At）：2026-09-30 15:38:00 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录第一阶段真实 QQ 验收时发现的问题、原因和解决方案。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：三项修复已进入仓库 `0.1.14` 并提交为 `7a714ac`，单元测试通过，安装目录已覆盖。用户声明已经重载。本会话没有再读重载后的 QQ 日志，不能写成三条已经消失。
- 文档边界（Scope / Boundary）：故障调查真相源（source of truth）；不代表代码修复计划或已通过验收。

## 2026-09-29 — 插件加载成功但群聊与私聊均不回复

- 问题现象：AstrBot 16:38:37 收到 QQ `2844973553` 在群 `836229427` 精确 @ 机器人 `1961618848` 的 `hihi`；cc-qq `0.1.12` 已加载，但插件 SQLite 的消息回执、会话、轮次均为 0。
- 问题原因：AstrBot 主配置 `data/cmd_config.json` 的 `plugin_set` 仅包含 `astrbot_plugin_sourcehub_inspector`。该消息快照中的 `event.plugins_name` 也只有此插件；AstrBot 在唤醒检查阶段按 `plugin_set` 筛选处理器，导致 `astrbot_plugin_cc_qq` 的消息处理器未执行。插件自身配置页的群号和白名单不能替代全局可用插件选择。
- 解决方案：由用户在 AstrBot 主配置的“插件配置 → 可用插件”中勾选 `astrbot_plugin_cc_qq`，同时保留需要的其他插件；保存后再发送群内 @ 消息。用户此前明确选择自行在 AstrBot 配置。
- 后续配置问题：当前 `group_rules_json` 中 `agent` 的值含中文弯引号 `“codex"`，不是合法 JSON（JavaScript Object Notation）；应改成 `"agent": "codex"`。群工作目录已经存在。当前 `default_model` 为 `GPT-6-Luna`，真实 CLI 模型可用性尚未验证；若代理报模型错误，先留空使用 CLI 默认模型。
- 当时验证状态：尚未收到修正 `plugin_set` 后的 QQ 消息；后续结果见下一条记录。

## 2026-09-29 16:47 — 消息进入插件后代理进程无法启动

- 问题现象：16:47:41 的群聊 @ 消息及 16:47:51 的私聊消息均写入插件 SQLite 回执，轮次状态为 `error`，回复为“代理命令未安装或不可访问”。
- 问题原因：AstrBot 全局 `plugin_set` 现已包含 `astrbot_plugin_cc_qq`，群规则 JSON 已合法，但插件 `codex_command` 仍为短命令 `codex`；AstrBot 桌面进程的命令搜索路径（PATH）无法解析它。Codex CLI 安装在用户的 nvm 目录中。
- 解决方案：用户在 AstrBot 插件配置中将 `codex_command` 改为当前安装的 macOS arm64 原生可执行文件绝对路径：`/Users/mobius/.nvm/versions/node/v24.13.1/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex`。该文件存在且 `--version` 输出 `codex-cli 0.158.0`；保存后重新发送 QQ 消息进行端到端验收。
- 当时验证状态：原生可执行文件只完成本机版本检查；之后的实际回复见下一条记录。

## 2026-09-29 16:54 — Codex 路径修正后的实际结果

- 问题现象：上述代理路径故障导致的群聊与私聊错误在用户填写绝对路径后不再出现。
- 问题原因：此前的短命令 `codex` 未被 AstrBot 桌面进程解析；用户已在 AstrBot 配置页填入原生可执行文件绝对路径，并为 Claude Code 填入其原生可执行文件路径。
- 解决方案与结果：旧版 `0.1.12` 的 SQLite 在 16:51–16:54 记录 Codex 群聊和私聊多条 `done` 轮次及非空文本回复；会话表两条记录均为 Codex。Claude Code 真实回复、恢复与中断行为及新版 `0.1.13` 独立模型仍待验证，第一阶段不因此关闭。

## 2026-09-30 14:17 — 私聊处理在 24 毫秒内因 ConnectionResetError 失败

- 问题现象：QQ `2844973553` 私聊两次发送 `hihi`（14:17:49.664、14:18:22.157）。插件日志只有 `消息处理失败：ConnectionResetError`，QQ 收到固定文案“处理消息时发生错误，请联系插件管理员查看日志。”。约 300 毫秒后 AstrBot 有 `Prepare to send`，说明这句错误回复本身已送出。同一私聊会话在 14:27:29 再次发送 `hihi`，14:27:54 送出正常回复“嗨嗨”，没有再次出现该错误。
- 问题原因：运行中的仍是 `0.1.12`（14:17:30 重载后日志写明该版本；`0.1.13` 尚未装上）。两条失败回执状态为 `error`，没有对应轮次（turn）。Codex 会话 `01a0ec5c-092b-7312-91af-7a873451c43e` 的 rollout 在这两次没有新事件，成功那次才在 14:27:32 写入 `thread_settings_applied`。异常出在 `service.handle()` 内部，而不是 QQ 发送。`agents/process.py` 把启动失败包成 `AgentProcessError`，但标准输入 `write()` / `drain()` 不在这个捕获里。CPython 3.12 的 `StreamWriter.drain()` 在管道已被对端关闭时抛出 `ConnectionResetError('Connection lost')`。这个异常冒泡到 `main.py` 第 157 行，日志只记了类型名，子进程 stderr 被丢掉，`finally` 还会在进程尚未退出时把它杀掉。同分钟 Codex 自己的日志没有这条线程，但有模型列表刷新失败：`timeout waiting for child process to exit`（14:18:34）和 `request timed out`（14:26:00）。因此子进程在写出会话日志前就结束或重置了标准输入；具体 stderr 文本这次日志里没有。
- 解决方案：`0.1.14` 的 `agents/process.py` 把标准输入上的 `BrokenPipeError` / `ConnectionResetError` / `ConnectionAbortedError` 收成“代理进程在接收消息前退出，退出码 N”，stderr 尾部只进日志。单元测试已通过。插件目录已覆盖为 `0.1.14`，代码已提交为 `7a714ac`。用户声明已经重载，但本会话没有再读日志，所以还没有修复后的 QQ 证据。网络超时仍不是这条错误的唯一根因。

## 2026-09-30 14:31 — 机器人号与 1968401530 私聊时反复发出“请在 @ 后输入”

- 问题现象：真人 QQ `1968401530`（昵称风刀霜剑）在和机器人对话。用户自己的 QQ 客户端和 NapCat 同时登录的是同一个机器人号 `1961618848`，不是 `1961618848` 与 `1968401530` 两个号一起当机器人在线。聊天里反复出现“请在 @ 机器人后输入文本或命令。”。日志里对应事件显示为 `1968401530/1968401530:`，正文为空。14:31 之后这段日志里，这类空白事件 66 条，`Prepare to send - 1968401530/1968401530` 也是 66 条，一一对应，间隔大约 300 毫秒。同一窗口里带昵称“风刀霜剑”的有正文消息是 21 条，插件 SQLite 只为这些正文建立了私聊会话，代理类型是 `claude`。
- 问题原因：只有一个插件进程，平台 `Test-01`，账号 `1961618848`。同一机器人号在官方客户端和 NapCat 上同时在线时，和真人的私聊会多出一批没有正文、发送者编号仍是对方 `1968401530` 的事件。插件只丢弃 `sender_id == self_id` 的消息，所以这批事件被当成白名单私聊。私聊不要求 @。正文为空且没有图片等非文本段时，`main.py` 直接回复 `EMPTY_MESSAGE_REPLY`。这句文案是写给群聊的，私聊里看起来就像无意义复读。NapCat 的 `reportSelfMessage` 为 true，机器人自己发出的消息也会上报，但发送者是 `1961618848` 时会被丢掉，对不上这批空白事件。`event.stop_event()` 之后没有写入事件结果，AstrBot 管道仍可能继续走到发送阶段，所以日志里还能看到一条正文为空的 `Prepare to send`。
- 解决方案：`0.1.14` 对私聊空文本不再回复，群聊 @ 后空文本仍用原提示。插件目录已覆盖，用户声明已经重载。本会话没有再读日志，修复后的 QQ 证据还没有。这条和 14:17 的标准输入重置不是同一条路径。

## 2026-09-30 15:20 — 断网恢复后会回复断网期间的消息

- 问题现象：用户观察到机器人断网再恢复后，会把断网期间收到的消息逐条回复。本次 `~/.astrbot/logs/backend.log` 里的“适配器已连接”之后没有成批的 `1968401530` 旧私聊；插件 SQLite 现有 30 条回执，按分钟散落在正常对话里（最多一分钟 8 条），没有一次“离线积压一次性入库”的记录。因此这次日志没有抓到那次补回，结论来自收消息代码。
- 问题原因：这算产品缺陷。AstrBot 平台 `Test-01` 用反向 WebSocket（WebSocket）`6199` 收 NapCat。`aiocqhttp_platform_adapter.py` 对每条 `message` 事件直接 `handle_msg`，并把 `timestamp` 改成收到时刻，不看 OneBot 事件里原来的 `time`。插件只按已入库的 `message_id` 去重；断网期间没收到的消息没有回执，恢复后一旦被当成新消息推过来，白名单私聊或群里 @ 机器人的消息都会进代理。插件启动时重放的只是状态仍为 `queued` 的回执，处理中的只发中断通知，不是把断网期间全部历史再答一遍。NapCat 正向 WebSocket `3001` 上的 `enableForcePushEvent` 当前没有接到 AstrBot。
- 解决方案：`0.1.14` 增加插件设置 `stale_message_max_age_seconds`，默认 180。超过该秒数的消息停止事件且不进代理；填 0 关闭。`queued` 重放不套这条规则。代码和单元测试已完成，插件目录已覆盖，用户声明已经重载。这次调查没有抓到断网补回的原始日志，本会话也没有再读重载后的日志。
