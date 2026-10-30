# 通用 AstrBot 插件自动化测试 skill — Align（对齐）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-30 14:02:15 CST。
- 更新时间（Updated At）：2026-10-30 14:02:15 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录需求 2「把插件验证流程做成通用 skill」的对齐结论，作为后续 Plan 的输入。
- 关联项目（Related Repository / Project）：当前仓库 `.`；skill 真源仓库 `/Users/mobius/Documents/111AAA-code/person-config`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 原始需求（Raw Input）：`zzz-prompt-debug/插件自动化测试验证/prompt-01.md`（需求 2，第 6–14 行）。
- 当前状态（Status）：计划中（Planned）；Align 已由用户确认，待 Plan。
- 文档边界（Scope / Boundary）：对齐结论与已批准方向；**不触发实施**。实施前必须先产出 Plan 并经用户批准。

## 一、背景

第一版 `tools/astrbot_e2e/` 已完成并通过验证：

- 单测 106/106 通过；探针、`cc_qq /help`、增量重载三项 E2E PASSED。
- 2026-10-29–30 实战：在测试群 `701292201` 验收 cc-qq `0.2.5`，A+B+C 共 44 项，并协助修复 F1。

第一版仍是「手写用例 + 人工编排」：用例要人工写、环境要人工判断、生产要人工暂停、报告要人工汇总。需求 2 要把它固化成可复用的通用 skill。

## 二、已确认决策

| 编号 | 决策点 | 结论 |
| --- | --- | --- |
| D1 | skill 与现有工具的关系 | 混合：skill 自包含探测/流程/模板；优先复用仓库内 `tools/astrbot_e2e`，换机器时用 skill 的 `vendor/` 快照 |
| D2 | 自愈边界 | 自动修复测试侧；生产侧（暂停/恢复生产 AstrBot、改生产 NapCat 配置）必须用户确认 |
| D3 | 功能清单来源 | 自动分析插件源码/元数据 → 生成功能清单与用例草案 → 用户确认后执行 |
| D4 | 平台范围 | macOS 可运行；Linux/Windows 只给探测清单、差异点与适配思路 |
| D5 | 报告形态 | JSON 证据 + Markdown 摘要；默认脱敏 |
| D6 | 安装位置 | 真源放 `person-config/skills/custom/astrbot-plugin-e2e/`，同步一份到本仓库 `.claude/skills/`，并更新 `catalog.json` |
| D7 | 多轮用例 | 首版补齐多轮 `steps` |
| D8 | 清单确认卡点 | 默认必须人工确认；提供 `--yes` 跳过 |
| D9 | 生产暂停/恢复 | 由 skill 执行，但必须用户点确认；生产配置自动备份 |

## 三、目标与非目标

### 目标

1. 探测当前机器环境，输出统一的环境画像（Environment Profile）。
2. 编排 3 个服务（2 个 NapCat + 1 个测试 AstrBot）；生产 AstrBot 暂停/恢复需确认；两个 QQ 由用户人工登录。
3. 分析被测插件，生成功能清单（Feature Inventory）与用例草案，经用户确认后执行。
4. 执行单轮与多轮用例，采集回包与日志，断言并产出报告。
5. 测试侧自愈；生产侧只提示、不自动操作。
6. macOS 可运行；其他平台给出可执行的适配思路。

### 非目标（首版）

- 不自动扫码登录 QQ。
- 不自动修改被测插件源码或修复插件缺陷。
- 不支持富媒体消息（图片、文件、语音、引用）。
- 不支持并行执行、WebUI、CI。
- 不承诺 Linux/Windows 可运行。
- 不替代人工对业务的最终判断。

上述非目标中，不可自动覆盖的功能在报告中标记 `SKIPPED` 并写明原因，不静默丢弃。

## 四、交付物与落点

### 4.1 skill 真源（person-config）

```text
person-config/skills/custom/astrbot-plugin-e2e/
├─ SKILL.md                     触发条件、主流程、安全门禁
├─ README.md                    安装、配置、快速开始
├─ references/
│  ├─ environment-probe.md      各平台探测清单
│  ├─ compatibility-matrix.md   NapCat / AstrBot 版本差异
│  ├─ self-healing.md           故障 → 诊断 → 允许动作
│  ├─ coverage-analysis.md      功能清单提取规则
│  ├─ report-template.md        报告结构
│  └─ safety-rules.md           生产侧人工确认规则
├─ scripts/
│  ├─ probe_env.py              环境画像（只读）
│  ├─ discover_plugin.py        插件源码 → features.json
│  ├─ gen_cases.py              features.json → 用例 JSON
│  ├─ aggregate_report.py       JSON 证据 → Markdown 摘要 + 脱敏
│  └─ sync_vendor.py            tools/astrbot_e2e → vendor 快照
├─ vendor/astrbot_e2e/          执行引擎快照（由 sync_vendor.py 生成）
└─ templates/
   ├─ config.template.json
   ├─ case.template.json
   └─ report.template.md
```

### 4.2 本仓库副本

- `.claude/skills/astrbot-plugin-e2e/`：与现有 skill 部署方式一致，使用副本而不是软链。
- 副本由 person-config 真源同步而来，不单独修改。

### 4.3 person-config 登记

- 更新 `skills/catalog.json`：新增条目、`source`、`category`、`version`、`origin`、`targets`、`mode`、`sha256`、`copies`。
- 如需同步到 `agents/claude/skills`，按 `sync/sync.py` 的流程执行；一期只做 dry-run 对账。

### 4.4 执行引擎增强（本仓库 `tools/astrbot_e2e/`）

- 用例模型支持多轮 `steps`，保持对 `send` / `expect` 的向后兼容。
- 新增批量执行入口 `run-suite`：一次启动测试实例，串行执行同一插件的全部用例。
- 报告聚合：suite 级 JSON + Markdown 摘要 + 脱敏。
- 新增对应单测；不破坏现有 106 个测试。

### 4.5 混合形态的边界

- 执行引擎真源：本仓库 `tools/astrbot_e2e/`。
- skill 的 `vendor/astrbot_e2e/` 是一次发布快照，由 `sync_vendor.py` 生成，不手工编辑。
- 运行时优先使用项目内 `tools/astrbot_e2e/`，找不到时回退到 `vendor/`。
- 不维护两套独立实现。

## 五、主流程

| 阶段 | 动作 | 门禁 |
| --- | --- | --- |
| S0 环境探测 | `probe_env.py` 输出环境画像 | 缺关键项 → 停止并给出修复命令 |
| S1 安全闸 | 识别生产实例、备份生产配置 | 暂停/恢复生产必须用户确认 |
| S2 起服务 | 启动 2 个 NapCat + 测试 AstrBot | 等待用户登录两个 QQ；轮询在线状态 |
| S3 覆盖分析 | 扫描插件 → `features.json` | 功能清单必须用户确认（`--yes` 可跳过） |
| S4 生成用例 | `gen_cases.py` → `cases/generated/<plugin>/` | 用例校验通过 |
| S5 执行 | `run-suite`：一次启动、逐用例执行、支持多轮 | 失败先自愈，超过上限则停止 |
| S6 报告 | JSON 证据 + Markdown 摘要 + 脱敏 | 失败项归类为环境 / 用例 / 插件缺陷 |
| S7 收尾 | 恢复生产（用户确认）、可选停止测试实例 | 不留未处理的残留进程 |

## 六、执行引擎设计要点

### 6.1 多轮 steps（向后兼容）

```json
{
  "name": "cc-qq 会话流程",
  "plugin": "astrbot_plugin_cc_qq",
  "steps": [
    {"send": {"text": "/new", "at_bot": true},
     "expect": {"messages": [{"contains": ["会话"]}], "timeout_seconds": 20}},
    {"send": {"text": "/cc 你好", "at_bot": true},
     "expect": {"messages": [{"contains": ["已发送"]}], "timeout_seconds": 60}},
    {"send": {"text": "/end", "at_bot": true},
     "expect": {"messages": [{"contains": ["结束"]}]}}
  ]
}
```

规则：

- 顶层只能二选一：`send` + `expect`（旧格式）或 `steps`（新格式）。
- 每步独立记录发送时间、日志 mark、回包与断言结果。
- 断言结果带 `step` 序号；任一步失败即停止后续步骤，保留已有证据。
- 每步支持 `timeout_seconds`；默认沿用配置的 `message_seconds`。
- `reload` 仍在用例级生效，执行前统一处理。

### 6.2 run-suite

- 一次启动测试实例，串行执行同一插件的全部用例。
- 用例间复用实例，避免每个用例重启。
- 单个用例失败不终止整个 suite；suite 结束输出汇总。
- 退出码：`0` 全部通过，`1` 存在失败，`2` 用例/配置错误，`3` 环境错误。

## 七、功能清单提取（Coverage）

### 7.1 输入

- `metadata.yaml`：插件名、显示名、版本、作者、描述、支持平台。
- `_conf_schema.json`：配置项及默认值。
- `*.py`：命令、命令组、事件、LLM 钩子等注册点。
- `README.md`：使用说明与功能描述。

### 7.2 输出 `features.json`

每项包含：

- `id`、`title`、`kind`（命令 / 命令组 / 事件 / 钩子 / 配置）。
- `trigger`：触发方式（命令文本、事件类型、配置项）。
- `expected`：预期现象。
- `testability`：文本可测 / 需多轮 / 需富媒体 / 需外部服务。
- `risk`：高 / 中 / 低。
- `notes`：依赖与前置条件。

### 7.3 提取方式

- 脚本负责静态扫描与配置解析，保证不漏注册点。
- AI 负责补语义、预期与风险分级。
- 用户确认后才生成用例；不可测项标记 `SKIPPED` 并写原因。

## 八、自愈边界（Self-healing）

### 8.1 自动执行

- 端口被本工具启动的旧进程占用 → 读 PID 文件后停止。
- 测试实例启动超时 → 重试一次并采集日志。
- WebUI reload 返回 401 → 重新登录获取 Bearer token。
- 插件副本与源不一致 → 重新同步。
- 历史消息导致假通过 → 调整 `since_time`。
- NapCat 离线 → 提示用户重新登录，不尝试自动扫码。

### 8.2 必须用户确认

- 暂停 / 恢复生产 AstrBot。
- 修改生产 NapCat 配置。
- 删除测试数据或报告。

### 8.3 永不自动

- 杀未知进程。
- 修改被测插件源码。
- 修复插件缺陷。

### 8.4 自愈上限

- 同一故障最多自动修复 2 次；仍失败则停止并输出证据与修复建议。
- 所有自动动作写入报告的操作日志，便于复盘。

## 九、安全规则

1. 生产实例与测试实例必须使用不同的根目录与端口；配置模块拒绝明显冲突。
2. 任何生产侧操作前必须备份配置，并在报告中记录备份路径。
3. 只停止由本工具记录 PID 的进程；不按端口盲目 kill。
4. 测试实例默认关闭内置命令，避免与被测插件命令叠加。
5. 报告默认脱敏；`--no-redact` 仅限明确需要时使用。
6. 不提交 `config.local.json`、报告与含密钥的日志。

## 十、报告与脱敏

### 10.1 目录

```text
reports/<timestamp>-<plugin>-suite/
├─ report.json
├─ report.md
├─ cases/<case-name>/{assertions,messages,sent,log-window,judge}.json|log
└─ ops.log
```

### 10.2 report.json

- 环境画像与版本。
- 用例结果：PASSED / FAILED / SKIPPED / ERROR。
- 断言明细与证据路径。
- 自愈动作记录。
- 失败归因：环境 / 用例 / 插件缺陷 / 未知。

### 10.3 report.md

- 通过率与统计。
- 失败项摘要与证据链接。
- 未覆盖项与原因。
- 下一步建议。

### 10.4 脱敏

- QQ 号：中间掩码。
- Token / 密码：整体替换为 `***`。
- 长消息：超长截断并标注长度。
- 默认开启；报告不入库。

## 十一、跨环境与版本适配

- `probe_env.py` 输出环境画像：OS、Python、AstrBot 版本与安装方式、NapCat 版本与工作目录、QQ 客户端、端口、实例根目录、插件目录。
- 按画像选择执行路径：
  - macOS：走已验证脚本。
  - Linux / Windows：输出差异点、推荐命令、需人工确认项；不假装可运行。
- `compatibility-matrix.md` 记录 NapCat / AstrBot 版本差异与已知坑（App Sandbox、端口、WebUI token、日志格式）。

## 十二、验收标准

1. **可复现**：在本机用 cc-qq 从零跑完 S0–S7 并产出报告；关键命令可重跑。
2. **覆盖**：cc-qq 的命令、事件、会话流程（多轮）至少达到已验收的 A+B+C 范围；不可测项有 `SKIPPED` 原因。
3. **自愈**：人为制造端口占用、残留实例、reload 失败，能自动恢复或明确要求人工。
4. **安全**：默认不自动暂停/恢复生产；生产配置有备份；不杀未知进程。
5. **脱敏**：报告默认不含完整 QQ 号与 Token。
6. **单测**：新增脚本与 `steps` / `run-suite` 有单测，全量通过。
7. **可移植**：把 skill 目录复制到另一台 macOS 机器，按 README 能完成探测与配置生成（不承诺无人工步骤）。

## 十三、本轮不做 / 后续阶段（Deferred Scope）

| 暂不做 | 原因 | 后续触发条件 |
| --- | --- | --- |
| 自动扫码登录 | QQ 风控与人工确认不可替代 | 官方提供稳定免扫码方案时 |
| 富媒体消息 | 首版聚焦文本链路；现有工具未验证 | 被测插件核心功能依赖图片/文件时 |
| 并行执行 | 单实例串行更稳定；并行需实例隔离 | 用例数量导致回归时间不可接受时 |
| WebUI 报告 | JSON + Markdown 已满足当前需求 | 需要非技术同学直接查看时 |
| CI 集成 | 依赖人工登录与固定测试群 | 需要每日回归或发布前自动回归时 |
| Linux / Windows 可运行 | 无验证环境，避免假承诺 | 用户提供可验证的 Linux/Windows 环境时 |
| 自动修复插件缺陷 | 测试工具应报告而非修改被测代码 | 明确需要 AI 辅助修复时单独立项 |
| 多插件同时测试 | 插件监听同一测试群会互相干扰 | 需要插件组合兼容性验证时 |

以上为**本轮暂不做**，不是永久放弃。

## 十四、风险与未决

- **生产 bot 兼任测试机器人**（`backlog.md` Q1）：测试群流量会进入生产 bot。
- **生产 NapCat `6198` 客户端**（Q2）：测试实例停止时会每 30 秒重试。
- **测试实例常驻策略**（Q3）：常驻省心但占资源。
- **报告脱敏与保留**（Q5）：需定义保留天数与清理命令。
- **LLM 语义判定稳定性**（Q6）：单次调用，无重试与阈值。
- **日志断言稳定性**（Q10）：依赖插件日志文案，插件改日志会破坏用例。
- skill 真源跨仓库（person-config 与本仓库）同步：需明确“只改真源、副本由同步生成”。

## 十五、下一步

1. 用户审阅本文档。
2. 审阅通过后，进入 Plan：产出 `plans/2026-10-30-通用插件测试skill-plan.md`，按任务排序并定义验证方式。
3. Plan 批准后，按重型路径产出 `spec/proposal.md`、`spec/design.md`、`spec/tasks.md`，再进入 Apply。
