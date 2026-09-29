# cc-qq 故障记录（Bug Log）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 16:39:25 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录第一阶段真实 QQ 验收时发现的问题、原因和解决方案。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：先前配置故障已修正；新版独立模型待运行验收（Configuration Fixed / New Runtime Pending）
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
