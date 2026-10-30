# AstrBot 插件测试报告（人工补充骨架）

> 本文件是 `report.md` 的人工补充骨架；自动部分由执行引擎的 `render_markdown` 生成。
> 复制到 suite 目录后补充「未覆盖项」「人工结论」等小节，不要修改自动生成的证据路径。

## 摘要（Summary）

- 插件：`{{plugin}}`
- 状态：`{{status}}`
- 开始时间：`{{started_at}}`
- 用例：`{{total}}` 个（通过 `{{passed}}` / 失败 `{{failed}}` / 跳过 `{{skipped}}` / 错误 `{{error}}`）
- 耗时：`{{duration_seconds}}` 秒

## 用例结果（Cases）

| # | 用例 | 状态 | 证据 |
| --- | --- | --- | --- |
| 1 | `{{case_name}}` | `{{case_status}}` | `{{case_run_dir}}` |

## 失败摘要（Failures）

- 用例：`{{case_name}}`
- 状态：`{{case_status}}`
- 证据：`{{case_run_dir}}`
- 失败步骤与断言：`{{failed_step_detail}}`

## 操作记录（Ops）

- `{{ops_line}}`

## 未覆盖项（Not Covered）

| 功能 | 类型 | 原因 | 后续动作 |
| --- | --- | --- | --- |
| `{{feature}}` | `{{kind}}` | `{{reason}}` | `{{next_action}}` |

## 脱敏说明（Redaction）

- 默认脱敏，报告中以下内容以 `***` 或掩码出现：
  - `webui.password`、`bot.token`、`sender.token`、`judge.api_key`、`astrbot.reverse_ws_token`。
  - 键名含 `password`、`token`、`api_key`、`secret`、`jwt` 的字段。
  - 配置中的机器人 QQ 与发送者 QQ（保留前 2 位与后 2 位；需传入 `--config`）。
  - 超过 500 字符的文本会被截断并标注截断长度。
- `report.json` 可能已被脱敏；重新生成不会恢复原文，原始证据在 `cases/*/steps/*`。
- `--no-redact` 仅在用户明确要求时使用。
