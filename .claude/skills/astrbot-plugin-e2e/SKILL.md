---
name: astrbot-plugin-e2e
description: "对 AstrBot 插件做真实 QQ 端到端验证：探测本机环境、拉起两个 QQ 与独立测试 AstrBot、按被测插件生成功能清单与用例、执行多轮用例、产出脱敏报告，并对测试侧故障自愈。触发词：测试 AstrBot 插件、插件端到端测试、e2e、验证插件功能、跑插件回归、生成测试报告、双 QQ 测试。适用于 macOS；其他平台给出适配思路。"
---

# AstrBot 插件端到端测试（AstrBot Plugin E2E）

## 什么时候用

- 用户要验证某个 AstrBot 插件的真实 QQ 行为。
- 用户要跑插件回归、生成测试报告。
- 用户要把测试流程复用到另一台 macOS 机器。

## 前置条件

1. macOS，已安装 AstrBot 与 NapCat。
2. 两个 QQ 号：一个作为机器人（bot），一个作为测试发送者（sender）。
3. 一个专用测试群。
4. 用户能手动扫码登录两个 QQ。

## 主流程（S0–S7）

> 下文 `scripts/` 均指本 skill 根目录下的脚本；`config.local.json` 指执行引擎所在仓库的本地配置（默认 `tools/astrbot_e2e/config.local.json`）。

### S0 环境探测

```bash
python3 scripts/probe_env.py --config <config.local.json> --output environment.json
```

- 读取 `environment.json`，检查 `astrbot.available`、`napcat.available`、`config.error`。
- 脚本退出码 `0` 只代表探测完成，不代表环境可用；必须逐项检查字段。
- 关键项缺失时停止，并给出修复命令；不要猜。

### S1 安全闸

- 识别生产实例（默认 `~/.astrbot`，端口 `6185/6199`）。
- **暂停/恢复生产必须用户明确确认**；执行前备份生产配置。
- 不杀未知进程；只停止有 PID 文件且校验属于测试实例的进程。

### S2 起服务

- 指导用户执行 `~/.qq-e2e/start-e2e.sh`（或等价脚本）拉起 2 个 QQ（内含 NapCat）与 1 个测试 AstrBot。
- 等待用户扫码登录两个 QQ。
- 用 `doctor` 验证两个账号在线与插件源可用：

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor \
  --config tools/astrbot_e2e/config.local.json
```

### S3 覆盖分析

```bash
python3 scripts/discover_plugin.py --plugin-dir <plugin_dir> --output features.json
```

- 把功能清单摘要给用户确认；重点列出 `risk=high` 与 `testability=manual/config` 的项。
- 脚本本身不交互；确认由 AI 在生成用例前向用户完成。

### S4 生成用例

```bash
python3 scripts/gen_cases.py --features features.json --out cases/ --timeout 30
```

- 自动生成的用例只覆盖安全命令；高风险命令、带参数命令与非命令功能写入 `cases/SKIPPED.md`。
- 多轮功能（如 `/new` → `/cc` → `/end`）由 AI 根据 `features.json` 手写，放入独立目录（如 `cases/manual/`）。
- 向用户展示生成与跳过清单。
- 注意：`run-suite` 只扫描 `--cases-dir` 顶层的 `*.json`；`cases/manual/` 需单独作为一次 suite 执行，或把文件移到同一目录。

### S5 执行

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run-suite \
  --cases-dir cases/ --config <config.local.json> --attach
```

- 退出码：`0` 通过、`1` 失败、`2` 配置/用例/执行错误、`3` 跳过。
- 失败时先按 `references/self-healing.md` 自愈；同一故障最多自动修复 2 次。
- 环境类失败停止并报告；插件类失败继续跑完剩余用例。

### S6 报告

- `run-suite` 已生成 `report.json` 与 `report.md`（位于 `reports/<时间戳>-<插件>-suite/`）。
- 检查 `report.md` 的失败摘要、未覆盖项、操作记录。
- 需要重新渲染时：

```bash
python3 scripts/aggregate_report.py --suite-dir <suite_dir> --config <config.local.json>
```

- `aggregate_report.py` 依赖执行引擎 `astrbot_e2e`：优先使用项目内 `tools/astrbot_e2e`，其次使用 `vendor/astrbot_e2e`。
- 重新渲染时始终传 `--config`，否则只能按键名脱敏，QQ 号无法掩码。
- **默认脱敏**；不要关闭脱敏，除非用户明确要求。

### S7 收尾

- 恢复生产 AstrBot 需用户确认。
- 按用户意愿保留或停止测试实例。
- 报告保留在本地，不入库。

## 铁律

1. 生产侧操作必须用户确认。
2. 不自动扫码登录。
3. 不自动修改被测插件源码。
4. 不杀未知进程。
5. 不可测项标 `SKIPPED` 并写原因，不静默丢弃。
6. 报告默认脱敏。

## 参考

- `references/environment-probe.md`
- `references/compatibility-matrix.md`
- `references/self-healing.md`
- `references/coverage-analysis.md`
- `references/report-template.md`
- `references/safety-rules.md`
