# Codex 模型探测钩子（codex-model-probe hook）加载失败排查交接

## Metadata（元数据）

- 更新时间（Updated At）：2026-09-29 12:34:34 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：保存项目级钩子（project hook）安装及加载失败的实测过程，供下次继续排查。
- 关联仓库或项目（Related Repository / Project）：本仓库 `.`，分支 `rin-source-hub/dev`。
- 关联任务（Related Mission）：无；此问题独立于现有 `.devflow/multi-source-hub/`。
- 关联原始说明（Related Input）：`codex-model-probe/install-for-agent.md`。
- 当前状态（Status）：暂停（Paused）；用户要求先记录，回头再说。
- 文档边界（Scope / Boundary）：本文件是本次调查的交接真相源（source of truth），只记录已观察的事实、待验证假设和续查步骤；不代表根因或修复方案已确认，不自动触发实施（Apply）。

## Current State Summary（当前状态摘要）

按安装说明新增了 `.codex/hooks.json`，但 Codex CLI 0.158.0 在当前工作树的 `/hooks → Stop` 中仍显示 **Installed 0 / Active 0**，详情为 **No hooks installed for this event**。用户明确允许增加当前工作树的受信任（trusted）记录；修改用户级配置并重新启动 CLI 后仍是 0。因此问题发生在钩子发现（discovery）阶段，具体原因**尚未查明**。用户要求暂停排查；不要把信任记录缺失当成已确认根因，也不要宣称安装完成。

## Architecture Overview（涉及的运行链路）

1. 用户级 `~/.codex/config.toml` 已有 `model_provider = "probe"`，其 `base_url` 指向 `http://127.0.0.1:8787/backend-api/codex`。该模型供应商（model provider）路由对所有 Codex 项目生效。
2. 本机反向代理（reverse proxy）监听 8787，转发模型请求并把服务端信号写入 `~/.codex-probe/turns.jsonl`。
3. 项目级 `.codex/hooks.json` 配置 Stop 事件调用本仓库 `codex-model-probe/check.py`；脚本读取记录，向 Codex 输出包含 `systemMessage` 的一行 JSON。
4. [OpenAI Docs 的 Codex Hooks 文档](https://developers.openai.com/codex/hooks/)确认项目级 `<repo>/.codex/hooks.json` 是受支持的来源，项目配置层须受信任；被发现的新命令还须经 `/hooks` 审查信任。目前列表为 0，尚未进入命令运行或命令信任阶段。

## Critical Files（关键文件）

| 路径 | 用途 | 当前状态 |
|---|---|---|
| `codex-model-probe/install-for-agent.md` | 安装步骤与约束 | 本轮修正了“当前仓库已受信任”的断言，并记录独立信任记录仍未解决问题；未提交。 |
| `.codex/hooks.json` | 当前工作树的 Stop 钩子 | 上轮新增，JSON 有效，命令指向本仓库脚本；目前未被 Codex 发现，文件未跟踪。 |
| `codex-model-probe/check.py` | Stop 钩子目标脚本 | 未修改；`--report` 运行退出码为 0。 |
| `codex-model-probe/probe_proxy.py` | 探测代理脚本 | 未修改；目前监听进程来自另一仓库的同名脚本。 |
| `~/.codex/config.toml` | 用户级路由与项目信任 | 用户授权后仅追加当前工作树的信任记录；TOML 有效。 |
| `~/.codex/config.toml.bak-20260929-113133` | 用户配置修改前的备份 | 已存在；未核实影响前不要直接覆盖当前配置。 |

## Investigation Timeline（调查时间线）

### 初次安装

1. 检查 `~/.codex/.env`：`HTTPS_PROXY`、`HTTP_PROXY`、`NO_PROXY` 均为非空。只报告键状态，没有记录任何代理值、账号或令牌。
2. 用户级配置原本已指向 `probe`，并已有正确的 `base_url`、`wire_api = "responses"`、`supports_websockets = false`、`requires_openai_auth = true`。安装时未重写这些字段。
3. `127.0.0.1:8787` 原本已有 PID `59932` 监听。`ps` 显示其命令是另一仓库的 `codex-model-probe/probe_proxy.py`，因此依安装说明未重复启动。`lsof` 显示标准输出、错误连到 `/dev/ttys011`，没有独立的 `~/.codex-probe/proxy.log`；关掉该终端可能导致模型请求失败。2026-09-29 12:29 再次确认该 PID 正在监听。
4. 通过补丁新增 `.codex/hooks.json`。`python3 -m json.tool` 解析通过，钩子命令路径存在，`check.py --report` 退出码为 0。没有真实 Stop 执行证据。

### 用户报告“没有识别到 hooks”后

1. `codex --version` 为 **0.158.0**。查阅官方 OpenAI Docs，确认项目级钩子位置与受信任要求。
2. 在当前工作树以 `codex --no-daemon --no-alt-screen` 启动 CLI，打开 `/hooks → Stop`，实测 **Installed 0 / Active 0**，详情为 **No hooks installed for this event**。这排除了“已安装但仅未信任命令”的解释。
3. 当时 `~/.codex/config.toml` 没有当前工作树完整路径的独立 `[projects."…"]` 条目，但有主仓库路径、`/Users/mobius` 和 `person-config` 的受信任条目。曾推测独立信任记录缺失是原因；后续试验证明该判断至少**不是充分解释**。
4. 尝试用 CLI `-c 'projects."…".trust_level="trusted"'` 做临时覆盖。Codex 启动警告明确说 `session-flags: projects."…" is ignored`；该次试验无效，不应作为信任行为的证据。
5. 对照试验：在明确受信任的 `person-config` 仓库，以同版本 CLI 查看 `/hooks`，Stop 为 **Installed 1 / Active 1**。可确定 0.158.0 能加载某些项目级 Stop 钩子；仍不能证明两仓库只差一个信任条目。
6. 用户明确授权添加当前工作树的信任记录。先备份 `~/.codex/config.toml` 到 `~/.codex/config.toml.bak-20260929-113133`，再仅追加当前路径的 `[projects."…"]` 与 `trust_level = "trusted"`。用 Python 3.11 的 `tomllib` 解析通过；写入后程序核对只发生预期追加，模型供应商配置未变。
7. 重新启动当前工作树 CLI，再看 `/hooks → Stop`，**仍是 Installed 0 / Active 0**，详情仍为 **No hooks installed for this event**。没有继续尝试其他修复写入。

### 其他诊断与限制

- 项目级 `.codex/config.toml` 存在但为空；尚未验证它是否影响同目录 `hooks.json` 的发现。
- 当前目录是 Git 工作树（worktree）根。`git rev-parse --show-toplevel` 为当前工作树，`git rev-parse --git-common-dir` 指向主仓库 `.git`。尚未验证 Codex 钩子扫描是否跟随 Git common directory 或其他项目根规则。
- 沙箱内启动交互式 Codex 曾因 `~/.codex` 中 SQLite 数据库只读而失败；之后的 CLI 实测都在获准的非沙箱环境进行。该限制不等于用户 CLI 的钩子根因。
- `codex doctor --summary` 显示配置已加载，但该诊断环境下供应商端点不可达。尚无证据表明这会导致 `/hooks` 列表为 0。
- 系统 `python3` 为 3.9.6，不支持 `tomllib`；本机另有 `python3.11` 用于 TOML 校验。Stop 命令仍按安装说明使用 `/usr/bin/python3`。

## Problem List（问题清单）

| 问题现象 | 原因或证据 | 解决方案状态 |
|---|---|---|
| 当前工作树 `/hooks → Stop` 为 0 个已安装钩子。 | Codex 未发现此项目级来源；具体发现失败的原因未知。JSON、脚本路径、`--report` 均正常，追加独立信任记录后仍为 0。 | 暂停；下次先核对配置层与工作树项目根解析，找到单一可验证原因后再做最小修复。 |
| 现有代理输出连接终端设备。 | PID `59932` 命令来自另一仓库的 `probe_proxy.py`，文件描述符 1/2 指向 `/dev/ttys011`。 | 本轮不调整；钩子加载问题解决且用户需要常驻稳定性时再评估。 |

## Files Modified（本轮变更文件）

| 路径 | 变更意图 | 备注 |
|---|---|---|
| `.codex/hooks.json` | 配置当前工作树的 Stop 钩子。 | 上轮新增，尚未提交。 |
| `codex-model-probe/install-for-agent.md` | 更正信任假设，记录信任配置未解决加载问题。 | 本轮补丁修改，尚未提交。 |
| `codex-model-probe/handoffs/2026-09-29-123003-codex-model-probe-hooks.md` | 保存调查过程和续查路径。 | 本交接文件，尚未提交。 |
| `~/.codex/config.toml` | 在用户明确同意后增加当前工作树受信任记录。 | 仓库外文件，已有时间戳备份。 |

工作区另外有 `.devflow/multi-source-hub/`、`.vscode/controlled-explorer.json`、压缩包和 `zzz-prompt-debug/` 的独立变更。本次没有编辑这些内容；下次不要将它们当作本问题的改动清理或提交。

## Decisions Made（决策与理由）

| 决策 | 理由 | 当前限制 |
|---|---|---|
| 复用现有 8787 进程。 | 安装说明要求已有 `probe_proxy.py` 监听时不要再启动第二份。 | 现有进程来自另一仓库且连着终端。 |
| 不安装用户级 `~/.codex/hooks.json`。 | 原始安装说明明确要求只用项目级 Stop 钩子。 | 项目级加载失败仍待解决。 |
| 经用户授权添加当前路径的受信任记录。 | 用备份后单项变更检验信任假设。 | 实测 Stop 仍为 0，不可将信任缺失写成根因。 |
| 按用户要求暂停。 | 当前证据不足以安全宣布修复。 | 等用户要求恢复后继续。 |

## Important Context（下次接手必须知道）

**根因未查明。** 上次助手一度把“缺少当前工作树的独立信任记录”判断为原因；用户授权补上后，重新运行的 CLI 仍显示 Stop 0。下次不要重复宣称“加信任即可解决”，也不要把“未安装”混同为“已安装但未信任”。官方文档的项目信任要求仍是背景条件，但没有解释本次实测结果。所有其他线索目前都是待验证假设。

不要因为钩子未加载就运行 `codex-model-probe/stop.sh` 或 `codex-model-probe/clean.sh`；现有用户级 `probe` 路由可能让其他项目也依赖 8787 代理。用户明确要求“回头再说”，交接写完即停止排查。

## Immediate Next Steps（用户要求恢复时的顺序）

1. 先读本交接，再核对 `git status --short`、`.codex/hooks.json`、用户级信任记录及 8787 监听状态。配置和进程可能已变化；不得输出代理地址、账号或令牌值。
2. 查明 Codex 对此 Git 工作树实际使用的项目根和配置层，以及 `.codex/hooks.json` 是否被扫描。优先用可观测的配置诊断和官方文档核对；只把 `person-config` 当只读对照。
3. 验证明确原因后做最小修复，重新启动 CLI，先在 `/hooks → Stop` 看到 **Installed ≥ 1**，再经钩子命令信任流程确认 **Active ≥ 1**，最后验证真实 Stop 输出。若仍为 0，不宣布修复。
4. 据实更新 `codex-model-probe/install-for-agent.md`；修改仓库文件后按仓库规则询问用户是否提交，未经允许不得 commit。

## Blockers/Open Questions（未解问题）

- [ ] Codex 对该 Git 工作树实际采用哪个项目根和配置层？当前 `.codex/hooks.json` 是否进入扫描范围？
- [ ] 此工作树与 `person-config` 在 `.codex/` 结构、Git 状态和配置来源上有什么差异导致 Stop 0 与 Stop 1？
- [ ] 空的 `.codex/config.toml` 是否影响同层 `hooks.json` 的加载？尚未测试，不能直接修改当作修复。
- [ ] 用户看到问题的客户端是 CLI、桌面还是 VS Code？本轮只实测了 CLI 0.158.0；其他客户端需分别核对。

## Deferred Items（本轮不做，后续阶段）

- **完成钩子加载排查与真实 Stop 验证**：用户要求先记录、回头再说，因此暂停；触发条件是用户明确要求恢复。
- **整理代理的常驻运行方式**：本轮聚焦钩子发现，且安装说明要求复用已有监听；待钩子加载解决、用户希望增强稳定性时再评估。
- **提交仓库变更**：用户没有授权提交；待问题修复、验证完成且用户明确同意后使用中文提交信息。

## Assumptions Made（假设及状态）

- “当前路径有独立受信任记录，项目钩子就会加载”：**被实测否定为充分条件**。
- “`/hooks` 为 0 是脚本运行报错”：**与实测不符**；Codex 尚未列出该钩子。
- “现有代理可复用”：符合安装说明；但进程连接终端，长期存活性未验证。

## Potential Gotchas（容易误判之处）

- `codex-model-probe/hooks.json` 是示例；当前项目实际钩子文件是 `.codex/hooks.json`。
- CLI `-c 'projects.…trust_level=…'` 在 0.158.0 被明确忽略，不能作为信任试验。
- 沙箱内交互式 Codex 因用户级 SQLite 只读而失败，是诊断环境限制；不能据此推断用户 CLI 的钩子问题。
- 全局 `git diff --check` 曾报告 `.devflow/multi-source-hub/checkpoints.md` 的末尾空行，那是其他任务的并存改动，不要顺手处理。
- 只报告 `~/.codex/.env` 中代理键是否非空，不要记录具体值。

## Environment State（环境状态）

- macOS；日期 2026-09-29，时区 Asia/Shanghai。
- Codex CLI 0.158.0；交互复现命令为 `codex --no-daemon --no-alt-screen`。
- 系统 `python3` 为 3.9.6；`python3.11` 可用于 `tomllib` 校验。
- 最后检查时 PID `59932` 监听 `127.0.0.1:8787`，命令包含另一仓库的 `codex-model-probe/probe_proxy.py`，输出连接 `/dev/ttys011`。
- Git 分支 `rin-source-hub/dev`；最近提交 `fd240ae`。本次未执行 commit。

## Related Resources（关联资料）

- `codex-model-probe/install-for-agent.md`：安装约束与示例。
- `codex-model-probe/README.md`：模型探测设计。
- `codex-model-probe/check.py`：钩子脚本。
- [OpenAI Docs：Codex Hooks](https://developers.openai.com/codex/hooks/)：项目级来源、信任与 `/hooks` 行为。
