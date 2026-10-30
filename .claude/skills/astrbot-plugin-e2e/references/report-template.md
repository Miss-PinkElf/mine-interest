# 报告结构与脱敏（Report Template）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-30 14:45:00 CST。
- 更新时间（Updated At）：2026-10-30 14:45:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：说明 suite 报告的小节结构、证据位置与脱敏字段。
- 关联仓库或项目（Related Repository / Project）：`person-config` 与本仓库 `tools/astrbot_e2e/`。
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：实施中（In Progress）。
- 文档边界（Scope / Boundary）：参考说明，非真相源；不触发实现。

## 报告位置

- suite 目录：`reports/<YYYYMMDD-HHMMSS-微秒>-<插件>-suite/`
- 自动产物：`report.json`、`report.md`
- 用例证据：`cases/<序号>-<用例名>/steps/<步骤>/`（消息、日志、断言结果）
- 人工骨架：`templates/report.template.md`

## 小节结构

`render_markdown` 当前输出：

1. 摘要（Summary）：插件、状态、开始时间、用例计数、耗时。
2. 用例结果（Cases）：编号、用例名、状态、证据目录。
3. 失败摘要（Failures）：失败/错误用例的步骤与断言详情。
4. 操作记录（Ops）：启动、停止、重载、自愈等带时间戳的操作。

人工补充骨架额外包含：

5. 未覆盖项（Not Covered）：功能、类型、原因、后续动作。
6. 脱敏说明（Redaction）。

> 未覆盖项当前由人工补充；`render_markdown` 不自动输出该小节。

## 脱敏字段

| 类别 | 规则 |
| --- | --- |
| 密钥字段 | 键名为 `password`、`token`、`api_key`、`jwt_secret`、`secret`，或键名包含 `password`、`token`、`api_key`、`secret`、`jwt` 时，值替换为 `***` |
| 配置中的密钥值 | `webui`、`bot`、`sender`、`judge`、`astrbot` 下的密钥值在文本中替换为 `***` |
| QQ 号 | 机器人 QQ 与发送者 QQ 保留前 2 位与后 2 位，中间用 `*` 掩码；长度不超过 4 时整体替换为 `***`。该掩码依赖 `--config` 提供的 `bot.qq` / `sender.qq`，不传时仅按键名脱敏 |
| 长文本 | 超过 500 字符的字符串截断，并标注被截断的字符数 |

## 重新生成

```bash
python3 scripts/aggregate_report.py --suite-dir <suite_dir> --config <config.local.json>
```

- 依赖执行引擎：优先项目内 `tools/astrbot_e2e`，其次 `vendor/astrbot_e2e`。
- `report.json` 不存在时退出码 `2`；引擎不可用时抛出异常，退出码 `1`。
- `report.json` 可能已经脱敏；重新生成不会恢复原文，原始证据在 `cases/*/steps/*`。

## 注意

- `--no-redact` 只在用户明确要求时使用。
- 分享报告前再次人工检查 QQ 号、群号、token、内网地址。
- 报告默认不入库。
