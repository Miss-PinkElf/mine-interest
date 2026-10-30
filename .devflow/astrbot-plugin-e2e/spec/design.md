# 通用 AstrBot 插件自动化测试 skill 设计（Design）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-30 14:30:00 CST。
- 更新时间（Updated At）：2026-10-30 14:30:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：固定需求 2 的结构、边界、数据流、接口与关键实现决策。
- 关联项目（Related Repository / Project）：当前仓库 `.`；skill 真源仓库 `/Users/mobius/Documents/111AAA-code/person-config`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 关联提案（Related Proposal）：`./proposal.md`。
- 关联计划（Related Plan）：`../plans/2026-10-30-通用插件测试skill-plan.md`。
- 当前状态（Status）：待用户确认（Pending Approval）。
- 文档边界（Scope / Boundary）：设计真相源；实现步骤与代码以 Plan 为准。
- 归档：第一版设计已归档到 `./archive/2026-10-27-v1/design.md`。

## 一、总体架构

```text
Claude / 用户
   │
   ▼
skill: astrbot-plugin-e2e（person-config 真源）
   ├─ SKILL.md                 流程与门禁
   ├─ scripts/probe_env.py     环境画像（只读）
   ├─ scripts/discover_plugin.py  功能清单
   ├─ scripts/gen_cases.py     用例草案
   ├─ scripts/aggregate_report.py 报告重生成
   ├─ scripts/sync_vendor.py   引擎快照
   └─ vendor/astrbot_e2e/      可移植执行引擎
             │
             ▼
项目内 tools/astrbot_e2e（优先复用）
   ├─ cases.py      用例模型（单轮 + 多轮）
   ├─ runner.py     单用例执行
   ├─ suite.py      批量执行
   ├─ reports.py    报告与脱敏
   ├─ bootstrap.py  实例初始化与插件同步
   ├─ orchestrator.py 启停与健康检查
   ├─ onebot.py     OneBot v11 客户端
   └─ cli.py        命令行入口
             │
             ▼
2 × NapCat + 1 × 测试 AstrBot（独立实例）
```

设计原则：

1. **执行引擎单一真源**：本仓库 `tools/astrbot_e2e`；skill 只带发布快照。
2. **skill 只做编排与生成**：探测、分析、生成、报告；不重复实现 OneBot 客户端。
3. **生产与测试隔离**：不同根目录、不同端口；生产操作需用户确认。
4. **默认安全**：未知进程不杀、不可测项不静默、报告默认脱敏。

## 二、执行引擎设计

### 2.1 用例模型（Cases）

支持两种形状，二选一：

**旧格式（保持兼容）**

```json
{
  "name": "探针回显",
  "plugin": "astrbot_plugin_e2e_probe",
  "send": {"group_id": "{{group_id}}", "text": "/e2e_echo hello", "at_bot": true},
  "expect": {"timeout_seconds": 30, "messages": [{"contains": ["e2e_echo:hello"]}]}
}
```

**新格式（多轮）**

```json
{
  "name": "cc-qq 多轮安全命令",
  "plugin": "astrbot_plugin_cc_qq",
  "steps": [
    {
      "send": {"group_id": "{{group_id}}", "text": "/pwd", "at_bot": true},
      "expect": {"timeout_seconds": 30, "messages": [{"regex": "\\S"}]}
    },
    {
      "send": {"group_id": "{{group_id}}", "text": "/help", "at_bot": true},
      "expect": {"timeout_seconds": 30, "messages": [{"contains": ["/new"]}]}
    }
  ]
}
```

统一规则：

- 顶层字段：`name`、`plugin`、`reload`、`send`、`expect`、`steps`。
- `steps` 与 `send`/`expect` 不能同时出现。
- `steps` 非空，最多 50 步。
- 每步必须有 `send` 与 `expect`；`expect` 至少包含 `messages` / `logs` / `semantic` 之一。
- `group_id` 支持 `{{group_id}}` 占位符，所有步骤统一渲染。
- `case_steps(case)` 把两种形状统一成步骤列表，供 runner 与 suite 复用。

### 2.2 单用例执行（Runner）

`runner.execute_case(cfg, case, run_dir, bot_client, sender_client, log_capture)`：

1. 遍历 `case_steps(case)`。
2. 每步创建 `run_dir/steps/NN/`。
3. 记录日志 mark 与发送时间。
4. 发送群消息（默认 @ bot）。
5. 采集回包；超时后回退到群历史，并用发送时间过滤旧消息。
6. 执行消息断言、日志断言、可选 LLM 语义判定。
7. 写入 `sent.json`、`messages.json`、`log-window.log`、`assertions.json`。
8. 任一步 FAILED 即停止后续步骤，保留已有证据。
9. 返回 `(results, step_summaries)`。

`run_case` 负责实例准备、启动、登录校验、等待就绪、reload、清理，再调用 `execute_case`。

### 2.3 批量执行（Suite）

`suite.run_suite(cfg, case_paths, reload, reports_dir, attach, keep_running)`：

1. 加载并渲染全部用例；校验同一插件。
2. 创建 suite 目录。
3. `--attach` 时复用实例；否则停止残留实例并启动新实例。
4. 连接 bot/sender 客户端，校验账号，等待就绪。
5. 逐用例：创建子目录 → 可选 reload → `execute_case` → 记录状态。
6. 聚合为 suite 结构，调用 `write_suite_report`。
7. 清理客户端；非 attach 且未 `--keep-running` 时停止实例。

退出码：`0` 全部通过，`1` 存在失败，`2` 用例/配置/环境错误，`3` 存在跳过。

### 2.4 插件源解析（Bootstrap）

优先级：

1. `cfg["plugin_sources"][name]`
2. `<repo>/integrations/astrbot/<name>`
3. `~/.astrbot/data/plugins/<name>`
4. `<repo>/tools/astrbot_e2e/fixtures/<name>`

复制时忽略 `__pycache__`、`*.pyc`、`tests`。只读复制，不修改源目录。

### 2.5 报告与脱敏（Reports）

suite 结构：

```json
{
  "suite": "<timestamp>-<plugin>-suite",
  "plugin": "astrbot_plugin_cc_qq",
  "status": "PASSED",
  "duration_seconds": 12.3,
  "started_at": "2026-10-30 14:30:00",
  "config": {"bot": {"qq": "32********68", "token": "***"}},
  "cases": [
    {"case": "命令 /help", "status": "PASSED", "run_dir": "...", "steps": [...]}
  ],
  "ops": ["2026-10-30 14:30:00 已停止残留测试实例"]
}
```

脱敏规则：

- 配置中的 `token`、`password`、`api_key`、`secret` 等键 → `***`。
- 配置中的 bot/sender QQ 号在任意字符串中出现 → 中间掩码。
- 超过 500 字符的字符串截断并标注。
- `--no-redact` 可关闭，但不在默认流程中使用。

输出：

- `report.json`：机器可读。
- `report.md`：摘要、用例表、失败摘要、操作记录。

### 2.6 自愈与安全（Healing & Safety）

自动执行（测试侧）：

- 停止残留测试实例（PID 文件 + 工作目录校验）。
- 启动失败重试 1 次。
- reload 失败改用重启实例。
- 插件副本不同步时重新复制。
- 历史消息假通过时用发送时间过滤。

必须用户确认（生产侧）：

- 暂停/恢复生产 AstrBot。
- 修改生产 NapCat 配置。
- 删除测试数据或报告。

永不自动：

- 杀未知进程。
- 修改被测插件源码。
- 修复插件缺陷。

自愈上限：同一故障最多自动修复 2 次；全部动作写入 `ops` 与 `report.md`。

## 三、skill 设计

### 3.1 环境探测（probe_env）

输入：`--config`（可选）、`--home`（测试注入）。

输出 `environment.json`：

- `platform`：系统、版本、架构、是否 macOS。
- `python`：版本与解释器。
- `astrbot`：命令路径、版本、数据根。
- `napcat`：安装目录、版本、工作目录。
- `qq`：App 路径、是否运行。
- `plugins`：生产插件目录与可用插件。
- `ports`：生产/测试端口占用。
- `config`：测试根、账号、群号、端口（不含密钥）。

macOS 已知路径：

- AstrBot 数据根：`~/.astrbot`
- NapCat：`~/Library/Containers/com.tencent.qq/Data/Documents/napcat`
- QQ 容器：`~/Library/Containers/com.tencent.qq/Data/Library/Application Support/QQ`

### 3.2 功能清单（discover_plugin）

输入：插件目录。

来源：

- `metadata.yaml`：名称、版本、作者、描述、平台。
- `_conf_schema.json`：配置项。
- `*.py`：命令、命令组、事件、LLM 钩子注册点。
- `README.md`：反引号包裹的命令文本。

输出 `features.json`：

```json
{
  "plugin": "astrbot_plugin_cc_qq",
  "features": [
    {
      "id": "command-help",
      "title": "命令 /help",
      "kind": "command",
      "trigger": "/help",
      "testability": "text",
      "risk": "medium",
      "notes": "README.md:77"
    }
  ],
  "summary": {"total": 30, "commands": 15, "events": 1, "hooks": 0, "config": 14, "manual": 15}
}
```

规则：

- 命令去重。
- 高风险命令（`/cc`、`/goon`、`/!`、`/new`、`/end`、`/initbase`、`/approve`、`/deny`）标 `risk=high`。
- 事件、钩子、配置标 `testability=manual/config`，不自动生成用例。
- 静态扫描负责不漏注册点；AI 负责补预期与风险说明。

### 3.3 用例生成（gen_cases）

规则：

- 只生成 `kind=command`、`testability=text` 的命令。
- 跳过高风险命令、带参数占位符的命令、事件/钩子/配置。
- 生成用例：`{{group_id}}`、`at_bot=true`、非空回复正则、默认 30 秒超时。
- 跳过项写入 `SKIPPED.md`，包含原因。
- 多轮流程由 AI 根据 `features.json` 手写，放入 `cases/manual/`。

### 3.4 报告重生成（aggregate_report）

- 读取已有 suite `report.json`。
- 调用执行引擎的 `write_suite_report` 重新渲染。
- 注意：已脱敏的报告无法恢复原文；原始证据在各步骤目录。

### 3.5 vendor 快照（sync_vendor）

- 输入：`tools/astrbot_e2e`。
- 输出：`vendor/astrbot_e2e`，忽略 `reports/`、`config.local.json`、`tests/`、`__pycache__`。
- 写入 `VERSION.json`：源路径、同步时间、目录哈希。
- 运行时优先项目内引擎，找不到再用 vendor。

## 四、安装与同步

```text
person-config/skills/custom/astrbot-plugin-e2e/   ← 唯一真源
        │  rsync --delete
        ▼
本仓库 .claude/skills/astrbot-plugin-e2e/          ← 使用副本
```

- 只修改真源；副本由同步生成。
- `catalog.json` 增加 `categories.custom` 条目与 `skills.astrbot-plugin-e2e` 元数据。
- 不自动 commit。

## 五、数据流

```text
probe_env.py
   → environment.json
discover_plugin.py
   → features.json
gen_cases.py
   → cases/*.json + SKIPPED.md
run-suite
   → suite/cases/NN/*.json|log
   → report.json + report.md
aggregate_report.py
   → 重新渲染 report.md
```

## 六、测试策略

- 单元测试：改动用 TDD，先写失败测试，再实现。
- 引擎测试：`PYTHONPATH=tools backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools`。
- skill 测试：`PYTHONPATH=. python3 -m unittest discover -s tests -t .`（在 skill 根目录）。
- 真实环境验收：Task 12，需要用户启动三服务并扫码登录。

## 七、兼容性

已验证组合：

- macOS（Darwin 25.2.0）
- AstrBot `4.29.3`
- NapCat `4.18.28`
- Python 3.12（`backend/.venv`）

其他平台只输出探测清单与适配思路：

- Linux：systemd/docker、路径差异、进程检查。
- Windows：路径、进程检查、QQ 客户端差异。

## 八、关键决策

| 编号 | 决策 | 依据 |
| --- | --- | --- |
| D1 | 混合形态：自包含 + 优先复用 | 复用已验证代码，同时可移植 |
| D2 | 测试侧自愈，生产侧确认 | 安全边界 |
| D3 | 自动分析 + 人工确认 | 覆盖与可控的平衡 |
| D4 | macOS 可运行，其他平台给思路 | 只有 macOS 可验证 |
| D5 | JSON + Markdown，默认脱敏 | 机器可读与人工可读 |
| D6 | person-config 真源 + 仓库副本 | 统一 skill 管理 |
| D7 | 多轮 steps 首版 | 覆盖会话类功能 |
| D8 | 清单默认必确认，`--yes` 可跳过 | 防误测 |
| D9 | 生产暂停/恢复由 skill 执行但需确认 | 效率与安全 |

## 九、风险与边界

- 生产 bot 兼任测试机器人，测试群流量会进入生产 bot（`backlog.md` Q1）。
- 生产 NapCat 的 `6198` 客户端在测试实例停止时会重试（Q2）。
- 报告保留与清理策略未定（Q5）。
- LLM 语义判定单次调用，无重试与阈值（Q6）。
- 日志断言依赖插件日志文案（Q10）。
- 跨仓库同步依赖人工执行 `rsync`，无自动守护。
