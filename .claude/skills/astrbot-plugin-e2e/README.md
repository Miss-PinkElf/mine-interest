# AstrBot 插件端到端测试 Skill（AstrBot Plugin E2E）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-30 14:45:00 CST。
- 更新时间（Updated At）：2026-10-30 14:45:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：说明本 skill 的安装同步、配置、脚本用法、退出码、已知边界与排障方式。
- 关联仓库或项目（Related Repository / Project）：`person-config`；执行引擎位于本仓库 `tools/astrbot_e2e/`。
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：实施中（In Progress）。
- 文档边界（Scope / Boundary）：使用说明，非真相源；方案与决策以 `.devflow/astrbot-plugin-e2e/plans/2026-10-30-通用插件测试skill-plan.md` 为准。

## 目录结构

```text
astrbot-plugin-e2e/
├─ SKILL.md                 提供给 AI 的主流程（S0–S7）
├─ README.md                本文件
├─ references/              环境、兼容性、自愈、覆盖、报告、安全细则
├─ scripts/
│  ├─ engine_path.py        定位执行引擎（tools/astrbot_e2e 优先，vendor 兜底）
│  ├─ probe_env.py          环境探测（Environment Probe）
│  ├─ discover_plugin.py    功能清单提取（Feature Inventory）
│  ├─ gen_cases.py          用例草案生成（Case Generation）
│  ├─ aggregate_report.py   重新生成 suite 报告（Aggregate Report）
│  └─ sync_vendor.py        同步执行引擎快照（Vendor Sync）
├─ templates/
│  ├─ config.template.json  配置模板
│  ├─ case.template.json    多轮用例模板
│  └─ report.template.md    人工补充报告骨架
├─ tests/                   脚本单测
└─ vendor/astrbot_e2e/      可移植执行引擎快照（由 sync_vendor.py 生成）
```

## 安装与同步

### 1. 同步执行引擎（可选）

执行引擎仍以本仓库 `tools/astrbot_e2e/` 为准。换机或脱离仓库使用时，用 `sync_vendor.py` 生成快照：

```bash
cd <repo_root>
python3 <skill_root>/scripts/sync_vendor.py \
  --source tools/astrbot_e2e \
  --dest <skill_root>/vendor/astrbot_e2e
```

- 生成 `vendor/astrbot_e2e/VERSION.json`（来源、同步时间、sha256）。
- 快照不包含 `reports/`、`config.local.json`、`tests/`、`__pycache__`。
- 查找顺序：当前目录向上找 `tools/astrbot_e2e/`，找不到再用 `vendor/astrbot_e2e/`。

### 2. 同步到本仓库副本

`person-config` 是 skill 真源（source of truth）；本仓库 `.claude/skills/astrbot-plugin-e2e/` 是运行副本：

```bash
rsync -a --delete \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  <person-config>/skills/custom/astrbot-plugin-e2e/ \
  <repo_root>/.claude/skills/astrbot-plugin-e2e/
```

安装登记与校验以 `person-config` 的 `skills/catalog.json` 与 `sync/sync.py` 为准。

## 配置

```bash
cp <skill_root>/templates/config.template.json tools/astrbot_e2e/config.local.json
```

- 填写所有 `<...>` 占位符；`config.local.json` 含 QQ 号、OneBot token、WebUI 密码与 LLM key，**不要提交**。
- `test_root` 默认 `~/.astrbot-e2e`，不能等于生产根 `~/.astrbot`。
- 测试端口不能与生产端口重叠（生产 WebUI `6185`、OneBot `6199`；测试 WebUI `6186`、OneBot `6198`）。
- `plugin_sources` 可选；插件源解析优先级：`plugin_sources.<name>` → `<repo>/integrations/astrbot/<name>` → `~/.astrbot/data/plugins/<name>` → `<repo>/tools/astrbot_e2e/fixtures/<name>`。

## 脚本用法与退出码

所有脚本仅依赖 Python 标准库（Python `3.9+`），直接以 `python3 scripts/<name>.py` 运行。

| 脚本 | 用法 | 退出码 |
| --- | --- | --- |
| `probe_env.py` | `--config <json>`（可选）、`--output <json>`（可选） | `0` 探测完成（环境缺失不报错，需检查字段）；异常 `1` |
| `discover_plugin.py` | `--plugin-dir <dir> --output <json>` | `0` 成功；插件目录不存在等异常 `1` |
| `gen_cases.py` | `--features <json> --out <dir> [--timeout 30]` | `0` 成功；输入/写入异常 `1` |
| `aggregate_report.py` | `--suite-dir <dir> [--config <json>] [--no-redact]` | `0` 成功；`report.json` 不存在 `2`；引擎不可用等异常 `1` |
| `sync_vendor.py` | `--source <dir> --dest <dir>` | `0` 成功；源目录非法等异常 `1` |
| `engine_path.py` | 库，无命令行接口 | 导入失败抛 `RuntimeError` |

- `aggregate_report.py` 不传 `--config` 时只按键名脱敏；QQ 号掩码依赖配置中的 `bot.qq` / `sender.qq`，建议始终传 `--config`。

执行引擎命令行（`astrbot_e2e.cli`）退出码：`0` 通过、`1` 失败、`2` 配置/用例/环境错误、`3` 跳过。

## 快速开始

```bash
# 1. 环境探测
python3 <skill_root>/scripts/probe_env.py \
  --config tools/astrbot_e2e/config.local.json --output /tmp/environment.json

# 2. 功能清单
python3 <skill_root>/scripts/discover_plugin.py \
  --plugin-dir integrations/astrbot/<plugin_name> --output /tmp/features.json

# 3. 用例草案（安全命令）
python3 <skill_root>/scripts/gen_cases.py \
  --features /tmp/features.json --out /tmp/cases

# 4. 执行 suite（需两个 QQ 已扫码，测试实例已启动）
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run-suite \
  --cases-dir /tmp/cases --config tools/astrbot_e2e/config.local.json \
  --attach --keep-running

# 5. 重新渲染报告（可选）
python3 <skill_root>/scripts/aggregate_report.py \
  --suite-dir tools/astrbot_e2e/reports/<时间戳>-<插件>-suite \
  --config tools/astrbot_e2e/config.local.json
```

## 已验证版本

| 组件 | 版本 | 平台 |
| --- | --- | --- |
| AstrBot | `4.29.3` | macOS |
| NapCat | `4.18.28` | macOS |
| Python | `3.9.6` | macOS（Darwin 25.2.0） |

macOS 下两个 QQ 实例共享同一个 App Sandbox 容器，只隔离 `NAPCAT_WORKDIR` 与端口。

## 已知边界

- 仅验证 macOS 双开路径；Linux/Windows 需自行适配路径与进程检查。
- QQ 登录必须人工扫码，不承诺自动登录。
- 自动生成用例只覆盖安全文本命令；高风险命令、带参数命令、事件/钩子/配置项需人工设计。
- `run-suite` 只扫描 `--cases-dir` 顶层 `*.json`；子目录中的手写用例需单独执行。
- 一个 suite 只支持同一插件。
- 主要验证文本消息；富媒体与并行执行不在本轮范围。
- 报告默认脱敏；`report.json` 重新生成不会恢复原文，原始证据在各 `cases/*/steps/*` 目录。
- 非 attach 模式结束会停止由工具启动的测试实例；生产 bot 的 `6198` 客户端重试属预期。

## 排障

| 现象 | 可能原因 | 处理 |
| --- | --- | --- |
| `probe_env.py` 显示 `astrbot.available=false` | PATH 中没有 `astrbot` | 安装 AstrBot 或把可执行文件加入 PATH |
| `napcat.available=false` | NapCat 未安装到 QQ 容器 | 检查 `~/Library/Containers/com.tencent.qq/Data/Documents/napcat` |
| `config.error` 非空 | JSON 格式或编码错误 | 用 UTF-8 保存，核对模板字段 |
| `doctor` 提示 OneBot 不可用 | QQ 未登录/反向 WS 未连接 | 重新扫码，检查 NapCat 客户端启用状态 |
| `EPERM mkdir .../NapCat/logs` | macOS App Sandbox 拒绝沙盒外写入 | `NAPCAT_WORKDIR` 放到 QQ 容器内 |
| 端口 `6186` 被占用 | 旧测试实例未退出或被未知进程占用 | 用 `stop-instance` 停止自有实例；未知进程只报告不杀 |
| Reload 返回 `401` | Secure cookie 在 http 下不回传 | 使用登录响应的 Bearer token（工具已实现） |
| 历史消息导致假通过 | 测试群存在旧回复 | 按 `since_time` 与 `timeouts.log_window_padding_seconds` 过滤 |
| `report.json` 中 QQ 号/密钥为 `***` | 默认脱敏 | 属于预期；不要为省事关闭脱敏 |

## 参考

- `references/environment-probe.md`
- `references/compatibility-matrix.md`
- `references/self-healing.md`
- `references/coverage-analysis.md`
- `references/report-template.md`
- `references/safety-rules.md`
