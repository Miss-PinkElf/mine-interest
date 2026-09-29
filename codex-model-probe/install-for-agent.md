# 给代理的安装说明（install-for-agent）

这份文档给后续代理（agent）执行。按下面的顺序安装 Codex 模型探测（codex-model-probe）。脚本留在本仓库，钩子只写项目级 `.codex/hooks.json`。

## 不要做的事

- 不要把脚本复制到 `~/.codex-probe/`，也不要把钩子写成用户级 `~/.codex/hooks.json`。
- 不要把 `~/.codex/.env` 里的代理地址、账号或 token 写进仓库、日志、提交说明或回复。只报告键是否存在、值是否非空。
- 代理环境没有配好时，不要猜测代理地址，不要改 `probe_proxy.py` 里的上游地址，不要继续把 Codex 指到本机代理。停下来告诉用户，由用户手动改探测脚本。
- 改 `~/.codex/config.toml` 时，只动 `model_provider` 和 `[model_providers.probe]`。保留现有的 `model`、推理强度、项目信任和界面配置。
- 钩子命令不要指向 `~/.codex-probe/check.py`。那个副本不属于这次安装。
- 不要改 `[tui].status_line` 去硬塞「实际 model」。Codex 0.157 的状态栏（status line）只接受内置项，自定义文字会被忽略。
- 不要另写一个钩子去检查探测进程是否已启动。这一项暂不做。
- 没有用户明确要求时，不要提交代码。

## 为什么要做这些配置

Codex 自带的降级检测依赖响应头 `OpenAI-Model`。ChatGPT OAuth 这条路不返回这个头，官方告警收不到数据。本机会话日志只记下你请求的模型，不记下服务端实际使用的模型。

所以要在本机加一层反向代理（reverse proxy）：

```
Codex → http://127.0.0.1:8787 → https://chatgpt.com
```

代理把请求原样流转发出去，并把服务端信号追加到 `~/.codex-probe/turns.jsonl`。项目级 Stop 钩子在每轮结束时运行 `check.py`。它做两件事：额度吃紧或请求异常时通知；向 TUI 送一行 `实际 model: ...`，让用户看见这一轮采到的模型。

这三处缺一不可：

| 配置 | 作用 | 不配会怎样 |
|---|---|---|
| 用户级 `~/.codex/config.toml` 的 `model_provider = "probe"` | 让所有 Codex 模型请求进入本机代理 | 请求仍直连 ChatGPT，探测收集不到数据 |
| 项目级 `.codex/hooks.json` | 每轮结束调用 `check.py`，告警并显示 `实际 model` | 有记录也不会告警，界面上看不到实际模型 |
| `~/.codex/.env` 里的出站代理 | 让 `probe_proxy.py` 能连上 `chatgpt.com` | 本机入口在听，转发超时，Codex 生成失败 |

项目级 `.codex/config.toml` 里的 `model_provider` 和 `model_providers` 会被 Codex 忽略，启动时还会警告。路由只能写在用户级 `~/.codex/config.toml`。这份用户级配置对这台机器上的所有项目生效，不只是当前仓库。

## 安装顺序

先检查出站代理。没有就停。有了再改配置、写钩子、把探测进程留在后台。

### 1. 检查 `~/.codex/.env` 里的出站代理

读取 `~/.codex/.env`。认可的非空键：

- `HTTPS_PROXY` 或 `https_proxy`
- 或者 `ALL_PROXY` 或 `all_proxy`

`HTTP_PROXY`、`NO_PROXY` 一并看是否存在。文件里是 `KEY=value`，通常没有 `export`。值可能被单引号或双引号包住。

下面任一情况都算「没有配置」：

- 文件不存在
- 上面的代理键都不存在
- 键存在但值为空
- 当前进程环境里已经有同名空变量。`probe_proxy.py` 不会用文件里的值覆盖已存在的环境变量，空值会把文件里的有效值挡住

没有配置时，立刻停止安装，并原样告诉用户：

> `~/.codex/.env` 里没有可用的 `HTTPS_PROXY` / `ALL_PROXY`。我没有修改 `config.toml`，也没有启动探测代理。请你手动修改 `codex-model-probe/probe_proxy.py` 的出站代理后再让我继续。

不要替用户编写代理地址。用户改完脚本之前，不要把 `model_provider` 改成 `probe`。如果此时用户配置已经是 `probe`，要明确告诉用户：探测进程还不能连上上游，现在发模型请求会失败。

已有非空代理键时，继续下一步。回复里只写「已检测到非空 HTTPS_PROXY」这类结论。

`probe_proxy.py` 启动时会自己读 `~/.codex/.env`，并把尚未存在的键放进进程环境。启动命令前面不用再加 `set -a; . ~/.codex/.env; set +a`。

### 2. 修改用户级 `~/.codex/config.toml`

先备份一份到 `~/.codex/config.toml.bak-<时间戳>`，再改原文件。

`model_provider` 是根键，必须写在所有 `[table]` 之前。表可以紧跟在根键后面：

```toml
model_provider = "probe"

[model_providers.probe]
name = "probe"
base_url = "http://127.0.0.1:8787/backend-api/codex"
wire_api = "responses"
supports_websockets = false
requires_openai_auth = true
```

字段含义：

- `base_url`：Codex 把模型请求发到本机 `8787`，路径前缀是 `/backend-api/codex`。代理再拼到 `https://chatgpt.com`。
- `wire_api = "responses"`：走 Responses API。
- `supports_websockets = false`：改用 HTTP SSE，代理才能逐块转发并采集信号。
- `requires_openai_auth = true`：继续用现有 ChatGPT OAuth，不需要 API key。

已经是上述内容时，不要重复改写。根键 `model_provider` 若已指向别的供应商，停下来把现有值告诉用户，得到确认后再覆盖。

改完用本机可用的 Python 3.11+ `tomllib` 解析该文件，确认能读到 `model_provider == "probe"` 和上面的 `base_url`。然后告诉用户重启 Codex。不重启的话，正在运行的 Codex 仍走旧路由。

这一步的影响：之后这台机器上所有 Codex 模型请求都先进入 `127.0.0.1:8787`。探测进程不在，请求就会失败。

### 3. 写项目级钩子（hooks）

写入仓库根目录 `.codex/hooks.json`，不要写 `~/.codex/hooks.json`。

命令使用本仓库 `codex-model-probe/check.py` 的绝对路径。把下面路径里的仓库根换成当前机器上的实际绝对路径：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/usr/bin/python3 <仓库绝对路径>/codex-model-probe/check.py",
            "timeout": 30,
            "statusMessage": "检查 Codex 模型与额度状态"
          }
        ]
      }
    ]
  }
}
```

`.codex/hooks.json` 里如果已经有别的钩子，只合并这条 Stop 命令，不要整文件覆盖。文件里只有这条探测钩子时，把 `command` 校正为当前仓库的绝对路径。

这个项目必须在用户级配置里是 `trust_level = "trusted"`，项目级 `.codex/` 才会被加载。当前仓库已经是 trusted。不要为了装钩子去改信任级别。

装完后告诉用户：在这个项目里打开 Codex，执行 `/hooks` 并信任这条命令。不信任时钩子被静默跳过，没有告警，也没有报错。

钩子只在这个项目的每轮结束时运行。用户级路由仍会让其他项目的模型请求经过本机代理，但其他项目不会触发这条告警，也看不到下面这行。`check.py` 在没有新记录时最多等待约 2 秒。

#### 每轮结束后显示实际模型

这条显示已经写在 `codex-model-probe/check.py` 里。安装时不要再改显示逻辑，只要钩子命令指向这份脚本。

Stop 钩子的 stdout 必须是一行 JSON。`check.py` 固定输出：

```json
{"systemMessage": "实际 model: gpt-5.6-luna"}
```

`systemMessage` 会作为界面提示出现在 TUI 里，样式接近底部状态栏，用 ` · ` 分隔。它不会嵌进截图里那条内置状态栏。不要把这行改成纯文本；Stop 事件把纯文本当成非法输出。

文案规则：

| 采到的数据 | 显示 |
|---|---|
| 服务端标注了模型 | `实际 model: gpt-5.6-luna` |
| 服务端标注和请求不一致 | `实际 model: gpt-5.6-luna · 请求 gpt-6-sol` |
| 只有请求侧模型 | `实际 model: gpt-6-sol · 仅请求侧` |
| 这一轮没有记录 | `实际 model: 未采集到` |

额度或请求异常仍接在同一行后面，例如 `实际 model: gpt-5.6-luna · 5 小时窗口已用 90%`。桌面通知逻辑保持原样。

服务端标注优先用 `response.completed.model`，没有再用 `response.created.model`。这个字段会跟着请求值走，在拿到真实降级样本前，不要把它说成已经证实的降级。

装完后告诉用户：信任钩子之后，每一轮回复结束都会看到这行。看到 `未采集到` 时，先确认后台探测进程还在，并且本轮请求确实走了 `probe`。

### 4. 让探测脚本一直留在后台

`probe_proxy.py` 是常驻进程。Codex 的 `model_provider` 已经指向它之后，这个进程必须一直活着。

- 进程在：请求被转发到 `chatgpt.com`，信号写入 `~/.codex-probe/turns.jsonl`。
- 进程退出、终端关掉、机器休眠后进程没了：Codex 的模型请求失败。本地文件、登录和工具执行还在，断的是模型这一跳。
- 只启动一次就退出，等于没装。

启动前先看 `127.0.0.1:8787`。已经是命令行包含 `probe_proxy.py` 的监听进程时，不要再起一个。占用该端口的是别的程序时，停下来告诉用户，不要结束那个进程。

确认出站代理可用后，在仓库根目录把进程放到后台，并记下 PID：

```bash
mkdir -p ~/.codex-probe
nohup python3 codex-model-probe/probe_proxy.py >> ~/.codex-probe/proxy.log 2>&1 &
echo $! > ~/.codex-probe/probe_proxy.pid
```

然后确认三件事：

1. `lsof -nP -iTCP:8787 -sTCP:LISTEN` 能看到 `probe_proxy.py`。
2. `~/.codex-probe/proxy.log` 里有「已从 ~/.codex/.env 读取代理变量」和「listening on 127.0.0.1:8787」。出现 `未检测到 HTTPS_PROXY` 时，进程虽然在听，上游仍会失败。停掉它，回到第 1 步告诉用户。
3. 把 PID、日志路径和「这个进程必须一直留在后台」告诉用户。

停止时用仓库里的脚本，它只结束监听 `8787` 且命令行包含 `probe_proxy.py` 的进程：

```bash
codex-model-probe/stop.sh
```

只想停进程时运行 `codex-model-probe/stop.sh`。要同时去掉路由和钩子，运行下一节的 `clean.sh`。只停进程而不改配置，模型请求会一直失败。

## 装完后向用户复述

用简体中文说明这四项的实际结果：

1. `~/.codex/.env` 里出站代理是否可用。不可用时说明你停在了哪一步。
2. `~/.codex/config.toml` 是否已指向 `probe`。提醒用户重启 Codex。
3. `.codex/hooks.json` 是否已指向本仓库的 `check.py`。提醒用户执行 `/hooks` 并信任。信任后，每轮结束会在 TUI 看到 `实际 model: ...`，这行来自钩子的 `systemMessage`，不在底部内置状态栏里。
4. 后台 PID、日志路径，以及进程退出后 Codex 模型请求会失败。

手动查看最近一轮记录：

```bash
python3 codex-model-probe/check.py --report
```

还没有请求经过代理时，输出「暂无记录」是正常的。

## 卸载

用户要求停用，或安装做到一半需要撤回时，运行：

```bash
codex-model-probe/clean.sh
```

不要手改 `config.toml` 和钩子来代替这个脚本。脚本按这个顺序做完三件事：

1. 调用 `stop.sh` 停止监听 `127.0.0.1:8787` 且命令行包含 `probe_proxy.py` 的进程。端口上是别的程序时，拒绝结束，并继续清理配置和钩子，最后以非 0 退出。
2. 清理用户级 `~/.codex/config.toml`：
   - 删除值为 `probe` 的根键 `model_provider`。
   - 删除 `[model_providers.probe]` 表。
   - 删除指向本次钩子文件的 `[hooks.state."…"]` 信任记录。父表 `[hooks.state]` 若因此变空，一并删除。
   - `model_provider` 若指向别的供应商，保留那个根键，只删除 `probe` 表。
   - 改文件前复制一份 `~/.codex/config.toml.bak-<时间戳>`。改完无法解析时，用这份备份恢复。
3. 删除项目级和全局钩子。两边都认命令里包含 `codex-model-probe/check.py` 或 `.codex-probe/check.py` 的处理函数。
   - 项目级：仓库根目录 `.codex/hooks.json`。删空后删除整个文件。
   - 全局：`~/.codex/hooks.json`。同样删探测命令；文件里不再剩钩子时，删除整个文件。里面还有别的钩子时，只留下那些，不整份抹掉。文件不存在就跳过。
   - `~/.codex/config.toml` 里如果用 `[hooks.*]` / `[[hooks.*]]` 写了指向上述脚本的全局钩子，一并删除。`hooks.state` 里项目级和全局这两份文件的信任记录都删除。

脚本不删除这些东西：

- `~/.codex/.env` 里的出站代理
- `~/.codex-probe/turns.jsonl`、`state.json`、`proxy.log`
- 仓库里的 `probe_proxy.py`、`check.py`、`hooks.json`、`stop.sh`

跑完用简体中文告诉用户：代理是否已停、配置里是否还剩 `probe`、钩子文件是否已删，并提醒重启 Codex。不重启的话，当前会话仍会把模型请求发到 `127.0.0.1:8787`。
