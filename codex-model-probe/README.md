# Codex 模型探测（codex-model-probe）

判断 Codex CLI 有没有被「静默降级 / 降智」，并在额度吃紧时提前预警。

**当前状态：用户级路由已指向本机代理，项目级 Stop 钩子已写在仓库根目录 `.codex/hooks.json`。** 代理进程没启动时，Codex 的模型请求会失败。钩子还要在 Codex 里执行 `/hooks` 信任一次，否则会被静默跳过。

---

## 先说最重要的一条结论

**你之前看到的 `gpt-6-luna`，不是降级。**

实测抓到的服务端响应头：

```
x-codex-safety-buffering-enabled: true
x-codex-safety-buffering-faster-model: gpt-6-luna
```

这是 OpenAI 的 **safety buffering** 机制：对部分内容，服务端会先用一个「更快的模型」做安全缓冲处理，再用你选的模型出结果。

关键点在于**服务端明确告知了你**（`enabled: true`），这是设计如此，不是偷偷把你换到弱模型。

本机 `~/.codex/logs_2.sqlite` 里那 93 次 `gpt-5.6-luna` + `low` effort，也是这个机制的产物，出现在 `thread_spawn` 派生的子会话中，**不是主对话被换**。

排查这类问题时，务必按 `thread_id` 分组，分清以下三种情况：

| 现象 | 是不是降级 |
|---|---|
| `safety-buffering-faster-model` 指定的模型 | 否，明示机制 |
| 子会话（compact / title / spawn）用便宜模型 | 否，设计如此 |
| **主对话**的 `response.created.model` 对不上请求值 | **存疑**，见下节 |

---

## 为什么需要抓包：官方检测在你这条路上是瞎的

Codex 二进制里其实**内置**了降级检测：

```
ModelReroutedNotification: thread_id / turn_id / from_model / reason
model/rerouted          ← app-server 通知方法
```

机制是比对「服务端回传的模型」与「你请求的 slug」。但官方 commit `b3a8571` 把判定源改成了依赖 **`OpenAI-Model` 响应头** —— 而 **ChatGPT OAuth 后端根本不返回这个头**。

本机 235MB 的 `logs_2.sqlite` 中，`openai-model` / `rerouted` 记录均为 **0 条**。所以官方检测在你的 OAuth 路径下永远收不到数据、永远不会告警。

同时，本地日志（`logs_2.sqlite` 和 `sessions/*/rollout-*.jsonl`）**只记录你请求的模型**，不记录服务端实际用的模型。光看本地文件，看不出任何降级。

**结论：要拿到服务端侧的证据，必须有一层中间人。** 这个项目就是那层中间人。

---

## 工作原理

```
Codex ──► 本地探测代理 (127.0.0.1:8787) ──► chatgpt.com
                    │
                    ├─ 逐块转发（不破坏流式）
                    └─ 记录服务端信号 ──► ~/.codex-probe/turns.jsonl
                                                  ▲
                    Codex hooks (Stop) ──► check.py ──► 告警
```

选了**反向代理**而不是 mitmproxy 抓包，原因：**不需要往系统信任链装自签根证书**。代理入口是明文 HTTP，出口是正常的 TLS 客户端。

代码里实测确认过是真流式（首字节 0ms / 总时长 3255ms / 52 个分块），不会拖慢长回复。

### 采集到的三类信号

**A 类 · 可信**

```
x-codex-safety-buffering-faster-model   安全缓冲用的模型
x-codex-plan-type                       计划类型
x-codex-primary-used-percent            5 小时窗口用量
x-codex-secondary-used-percent          7 天窗口用量
x-codex-credits-balance                 余额
```

**B 类 · 账户级（事前预警，实际最有用）**

额度百分比是**事前**信号 —— 服务端在额度吃紧时更可能降级，比等到被降级了才发现有用得多。

**C 类 · 存疑**

```
response.created.model     请求什么，它就显示什么
response.completed.model   同上
```

实测：请求 `gpt-6-astra` 显示 `astra`，请求 `gpt-6-sol` 显示 `sol`。**无法区分「服务端如实报告」和「body 回显请求值」。**

为了区分，我让代理把请求体里的模型名改写成 `gpt-6-fake-probe`，服务端返回：

```
HTTP 400
"The 'gpt-6-fake-probe' model is not supported
 when using Codex with a ChatGPT account."
```

说明服务端**会校验模型名，不是无脑回显**。但这**不等于**它降级时会如实报告 —— 那需要一个真实降级样本才能校准，目前拿不到。

所以 `check.py` 默认**不对 C 类报警**，只记录留档（加 `--strict` 可强制开启）。

---

## 文件清单

| 文件 | 作用 |
|---|---|
| `probe_proxy.py` | 流式反向代理。转发 + 采集信号，写 `~/.codex-probe/turns.jsonl` |
| `check.py` | 判定脚本。被 hooks 调用，也可手动 `--report` 查看状态 |
| `hooks.json` | 钩子示例。当前生效的是仓库根目录 `.codex/hooks.json` |
| `../.codex/hooks.json` | 当前生效的项目级 Stop 钩子，调用本仓库的 `check.py` |
| `install-for-agent.md` | 给代理的安装说明。改配置、挂钩子、检查出站代理、后台常驻 |
| `stop.sh` | 停止本机探测代理。只结束监听 `127.0.0.1:8787` 的 `probe_proxy.py` |
| `clean.sh` | 停止代理，删除 config.toml 里的 probe 路由，并删除项目级和全局探测钩子 |
| `调研报告.md` | 本次调研的完整过程与结论 |

---

## 安装

给代理安装时，按 `install-for-agent.md` 执行。

人工对照时，仍然是下面 3 步：

**1. 配置 provider**（只能写用户级 `~/.codex/config.toml`）

```toml
model_provider = "probe"

[model_providers.probe]
name                 = "probe"
base_url             = "http://127.0.0.1:8787/backend-api/codex"
wire_api             = "responses"
supports_websockets  = false      # 走 HTTP SSE，代理才好写
requires_openai_auth = true       # 继续用你的 OAuth，不需要 API key
```

项目级 `.codex/config.toml` 里的 `model_provider` 和 `model_providers` 会被 Codex 忽略，启动时还会警告。探测路由因此写在用户级 `~/.codex/config.toml`。这份配置已经指向 `probe`，代理进程必须保持运行，否则模型请求会失败。

**2. 启动代理**（必须常驻，另开终端）

```bash
python3 ~/Documents/111AAA-code/person-config/codex-model-probe/probe_proxy.py
```

脚本启动时会自己读取 `~/.codex/.env`。当前进程里已经有的同名变量不会被覆盖。

**3. 信任钩子** —— 项目级钩子已经写在仓库根目录 `.codex/hooks.json`。在这个项目里打开 Codex，执行 `/hooks` 并信任它。

> 这一步不做，钩子会被**静默跳过**，你永远收不到告警，而且不会有任何报错提示。这个项目在用户配置里已经是 trusted，所以项目级 `.codex/` 会被加载。

钩子每轮结束会往 TUI 送一行 `实际 model: ...`，样式接近底部状态栏（status line）的 ` · ` 分隔。Codex 0.157 的 `status_line` 只能选内置项，这行显示为钩子的 `systemMessage`，不会嵌进底部那一栏。没有采集到记录时显示 `实际 model: 未采集到`。

### 停止代理

在项目目录执行，不依赖 `~/.codex-probe` 是否已安装：

```bash
cd ~/Documents/111AAA-code/person-config/codex-model-probe
./stop.sh
```

端口可用 `PROBE_PORT` 覆盖，需与启动时一致。脚本只向命令行包含 `probe_proxy.py` 的监听进程发 `SIGTERM`；约 3 秒仍不退出才发 `SIGKILL`。端口上若是别的程序，脚本拒绝结束并以非 0 退出。

### 验证

```bash
python3 ~/Documents/111AAA-code/person-config/codex-model-probe/check.py --report
```

---

## 局限性（务必读完）

1. **hooks 抓不到网络数据。** Codex hooks 的输入 JSON 里只有 `session_id` / `transcript_path` / `cwd` / **请求侧 model**，没有响应头、没有服务端模型。hooks 只能当**触发器**，采集必须靠常驻代理。

   另外 `Stop` 触发时那一轮的 HTTP 响应**早已结束**，所以「靠 hooks 临时抓包」在时序上不成立。

2. **测不出「同型号被削弱」。** 本项目能发现的是「模型被换成了另一个型号」。如果服务端用的是同一个模型但砍了推理、做了量化或限速，**任何客户端手段都测不出来**，因为客户端拿不到服务端的执行参数。这也是所有同类工具（is-gpt-nerfed / ModelTrace / codex-degrade-guard）的共同天花板。

3. **C 类信号未校准。** 见上文，拿到真实降级样本前不要据此下结论。有旁证表明它可能不可信：官方 commit 的标题是 `remove response model check and rely on header model` —— 如果 body 里的 model 可信，官方没有移除的理由。

4. **代理经手 OAuth token。** 脚本不落盘 token（只记录 header 名字），但进程内存里有。用自己看得懂的代码。

5. **代理是单点。** 代理挂了 Codex 就用不了。恢复方式见「回滚」。

---

## 踩坑记录

**代理连不上 chatgpt.com。** Codex 会读取 `~/.codex/.env`，里面配置了 `HTTPS_PROXY` / `HTTP_PROXY` / `NO_PROXY`。早期直接启动 Python 时，进程不会继承这个文件，直连会超时（`Errno 60`）。现象是 Codex 正常，代理转发全部超时。

`probe_proxy.py` 现在会在启动时读取这个文件。读到代理变量会打印「已从 ~/.codex/.env 读取代理变量」；文件缺失或里面没有代理变量时仍打印警告。

**另外**：`codex exec` 的 stdout **不会**输出网上流传的那行 `model: xxx`，在 0.157.1 上实测为空。不要照抄那些一行命令。

---

## 回滚

```bash
codex-model-probe/clean.sh
```

这会停止探测进程，从 `~/.codex/config.toml` 去掉 `probe` 路由和钩子信任记录，并删除项目级 `.codex/hooks.json` 和全局 `~/.codex/hooks.json` 里的探测钩子。改完要重启 Codex。

`clean.sh` 不删除 `~/.codex/.env`，也不删除 `~/.codex-probe` 里的记录。记录目录要自己删：

```bash
rm -rf ~/.codex-probe
```
